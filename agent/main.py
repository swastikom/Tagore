import json
from graph import build_graph
from db import CanonDatabase



def load_outline(filepath="outline.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    formatted_chapters = {}
    for ch_num, ch_data in data.get("chapters", {}).items():
        scenes_dict = {int(sc_num): brief for sc_num, brief in ch_data.get("scenes", {}).items()}
        formatted_chapters[int(ch_num)] = {
            "title": ch_data.get("title", f"Chapter {ch_num}"),
            "scenes": scenes_dict
        }
    return data, formatted_chapters


def _print_draft_for_review(values):
    print(f"\n================ HUMAN CHECKPOINT: Ch {values.get('current_chapter')} "
          f"Sc {values.get('current_scene')} ================")
    print(f"Passed Critic: {values.get('passed_critic')} | Passed Canon: {values.get('passed_canon')}")
    if values.get("canon_violations"):
        print(f"Canon Violations: {values['canon_violations']}")
    if values.get("critic_feedback"):
        print(f"Critic Feedback: {values['critic_feedback']}")
    print(f"\n--- Draft ---\n{values.get('current_draft', '')}\n")
    print("=====================================================================")


def _handle_checkpoint(app, config):
    """
    Handles the paused human_checkpoint node.
    Returns (should_continue: bool, human_override: bool).

    human_override is True only when the human approved a scene that had NOT
    already passed both automated checks — main.py uses this to decide whether
    to save the scene even though the automated pass flags say False.
    """
    snapshot = app.get_state(config)
    if not snapshot.next:
        return False, False
    if "human_checkpoint" not in snapshot.next:
        return True, False  # paused elsewhere unexpectedly; just keep going

    _print_draft_for_review(snapshot.values)
    choice = input("Approve this scene? [y]es / [n]o / [r]evise with notes: ").strip().lower()

    if choice == "y":
        was_auto_passed = bool(snapshot.values.get("passed_critic")) and bool(snapshot.values.get("passed_canon"))
        app.update_state(config, {"human_approved": True, "human_revision_notes": None})
        return True, not was_auto_passed
    elif choice == "r":
        notes = input("Revision notes for the writer: ").strip()
        app.update_state(config, {
            "human_approved": False,
            "human_revision_notes": notes,
            "retry_count": 0  # give the revision a fresh retry budget
        })
    else:
        app.update_state(config, {
            "human_approved": False,
            "human_revision_notes": "Rejected. Rewrite with stronger adherence to canon and quality standards.",
            "retry_count": 0
        })
    return True, False


def init_app():
    outline_data, chapters_dict = load_outline("outline.json")

    db = CanonDatabase()
    for char_name, char_details in outline_data.get("characters", {}).items():
        db.set_character(char_name, char_details)

    app = build_graph()
    config = {"configurable": {"thread_id": "novel_gen_thread_1"}}
    output_filename = "generated_novel.md"

    current_saved_state = app.get_state(config)

    # These track the state of the scene currently in flight. They're seeded
    # either from a resumed checkpoint (FIX: see below) or fresh defaults.
    latest_draft = ""
    latest_passed_critic = False
    latest_passed_canon = False
    pending_human_override = False

    if current_saved_state.values:
        print("\n🔍 Existing checkpoint found in 'state_checkpoint.db'!")
        stream_input = None
        last_ch = current_saved_state.values.get("current_chapter", 1)
        last_sc = current_saved_state.values.get("current_scene", 1)
        print(f"📍 Resuming at Chapter {last_ch}, Scene {last_sc}\n")
        active_chapter = last_ch

        # FIX: reload draft/pass-flags from the persisted checkpoint in case
        # the process was killed while paused at a human checkpoint (e.g. you
        # closed the terminal overnight). Without this, latest_draft/etc.
        # reset to "" / False on restart, so an approval typed after restart
        # would compute should_save against a stale empty draft and silently
        # skip the file write — even though you just approved it.
        latest_draft = current_saved_state.values.get("current_draft", "")
        latest_passed_critic = current_saved_state.values.get("passed_critic", False)
        latest_passed_canon = current_saved_state.values.get("passed_canon", False)
    else:
        print(f"\n🚀 Starting fresh novel generation for '{outline_data.get('title')}'...\n")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(f"# {outline_data.get('title', 'Untitled Novel')}\n\n")

        stream_input = {
            "master_outline": {
                "Title": outline_data.get("title", "Untitled Novel"),
                "Premise": outline_data.get("premise", ""),
                "chapters": chapters_dict,
                "canon_ledger": outline_data.get("canon_ledger", {}),
                "continuity": outline_data.get("continuity", {}),
                "characters": outline_data.get("characters", {}),
                "story_engine": outline_data.get("story_engine", {}),
                "prose_style": outline_data.get("prose_style", {})
            },
            "novel_title": outline_data.get("title", "Untitled Novel"),
            "genre": outline_data.get("genre", "Fiction"),
            "prose_style": outline_data.get("prose_style", {}),
            "current_chapter": 1,
            "current_scene": 1,
            "rolling_context": [],
            "recent_scene_texts": [],
            "continuity_ledger": [],
            "flagged_scenes": [],
            "retry_count": 0,
            "human_approved": False,
            "is_complete": False
        }
        active_chapter = 1

    while True:
        # Extra keys (run_name, tags) are LangSmith-only metadata — they ride
        # alongside "configurable" and don't affect checkpointing/threading,
        # which is still keyed purely off config["configurable"]["thread_id"].
        # This just makes runs for this chapter easy to find/filter in the
        # LangSmith UI instead of one undifferentiated trace per thread.
        run_config = {
            **config,
            "run_name": f"Chapter {active_chapter}",
            "tags": ["novel-gen-pipeline", f"chapter-{active_chapter}"]
        }
        for output in app.stream(stream_input, run_config):
            for key, value in output.items():
                print(f"--> Executed Node: {key}")

                if key == "writer" and "current_draft" in value:
                    latest_draft = value["current_draft"]
                    print(f"\n--- Draft Snippet ---\n{latest_draft[:200]}...\n")

                if key == "critic":
                    latest_passed_critic = value.get("passed_critic", False)

                if key == "canon_guard":
                    latest_passed_canon = value.get("passed_canon", False)

                if key == "manager":
                    auto_passed = latest_passed_critic and latest_passed_canon
                    should_save = bool(latest_draft) and (auto_passed or pending_human_override)

                    if should_save:
                        with open(output_filename, "a", encoding="utf-8") as f:
                            f.write(latest_draft + "\n\n---\n\n")
                        tag = " [HUMAN OVERRIDE]" if pending_human_override and not auto_passed else ""
                        print(f"--> [SAVED] Approved scene written to '{output_filename}'{tag}\n")
                    elif latest_draft:
                        print(f"--> [SKIPPED WRITE] Scene did not pass checks — not saved "
                              f"(see flagged_scenes in state for details).\n")

                    # Reset per-scene tracking for the next cycle
                    latest_draft = ""
                    latest_passed_critic = False
                    latest_passed_canon = False
                    pending_human_override = False

                    new_ch = value.get("current_chapter", active_chapter)
                    if new_ch > active_chapter and not value.get("is_complete"):
                        print(f"\n==========================================")
                        print(f"🎉 CHAPTER {active_chapter} COMPLETE!")
                        print(f"==========================================")
                        active_chapter = new_ch

        # Graph either finished, or paused at the human checkpoint interrupt.
        should_continue, override = _handle_checkpoint(app, config)
        pending_human_override = override
        if not should_continue:
            break
        stream_input = None  # resume from the checkpoint rather than restarting

    final_state = app.get_state(config).values
    flagged = final_state.get("flagged_scenes", [])
    if flagged:
        print(f"\n⚠️  {len(flagged)} scene(s) needed a human override or were force-advanced:")
        for f in flagged:
            print(f"   - Ch {f['chapter']} Sc {f['scene']}: "
                  f"critic={f['passed_critic']} canon={f['passed_canon']}")

    print(f"\n🎉 Novel Generation Complete! Full manuscript saved to '{output_filename}'.")


if __name__ == "__main__":
    init_app()