import json
from graph import build_graph
from db import CanonDatabase

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

def _handle_bible_checkpoint(app, config, snapshot) -> bool:
    print("\n=== STORY BIBLE REVIEW ===")
    bible_data = snapshot.values.get("bible", {})
    print(json.dumps(bible_data, indent=2))
    
    choice = input("\nApprove this Story Bible? [y]es / [r]evise with notes: ").strip().lower()
    if choice == 'y':
        app.update_state(config, {"bible_approved": True, "bible_revision_notes": None})
    else:
        notes = input("Revision notes for the architect: ").strip()
        app.update_state(config, {"bible_approved": False, "bible_revision_notes": notes})
    return True

def _handle_chapter_checkpoint(app, config, snapshot) -> bool:
    print("\n=== CHAPTER OUTLINE REVIEW ===")
    drafted = snapshot.values.get("drafted_chapters", {})
    for ch_num, ch_data in sorted(drafted.items(), key=lambda x: int(x[0])):
        print(f"\nChapter {ch_num}: {ch_data.get('title')}")
        for sc_num, sc_data in ch_data.get('scenes', {}).items():
            print(f"  - Scene {sc_num}: {sc_data.get('brief')}")
            
    choice = input("\nApprove this outline? [y]es / [r]evise with notes: ").strip().lower()
    if choice == 'y':
        # Merge the bible and chapters into the master_outline
        bible = snapshot.values.get("bible", {})
        master_outline = dict(bible)
        master_outline["chapters"] = drafted

        # --- NEW: Save a copy to disk for your records ---
        with open("generated_outline.json", "w", encoding="utf-8") as f:
            json.dump(master_outline, f, indent=2)
        
        # Seed the character DB directly from the approved bible
        db = CanonDatabase()
        for char_name, char_details in bible.get("characters", {}).items():
            db.upsert_entity(char_name, "Character", [f"{k}: {v}" for k, v in char_details.items() if v])
            
        app.update_state(config, {
            "chapters_approved": True, 
            "chapters_revision_notes": None,
            "master_outline": master_outline,
            "current_chapter": 1,
            "current_scene": 1
        })
    else:
        notes = input("Revision notes for the outliner: ").strip()
        app.update_state(config, {
            "chapters_approved": False, 
            "chapters_revision_notes": notes,
            "current_planning_act": 1,  # Reset to rewrite from Act 1
            "drafted_chapters": {}
        })
    return True

def _handle_human_checkpoint(app, config, snapshot):
    _print_draft_for_review(snapshot.values)
    choice = input("Approve this scene? [y]es / [n]o / [r]evise with notes: ").strip().lower()
    
    was_auto_passed = bool(snapshot.values.get("passed_critic")) and bool(snapshot.values.get("passed_canon"))
    
    if choice == "y":
        app.update_state(config, {"human_approved": True, "human_revision_notes": None})
        return True, not was_auto_passed
    elif choice == "r":
        notes = input("Revision notes for the writer: ").strip()
        app.update_state(config, {
            "human_approved": False,
            "human_revision_notes": notes,
            "retry_count": 0
        })
    else:
        app.update_state(config, {
            "human_approved": False,
            "human_revision_notes": "Rejected. Rewrite with stronger adherence to canon and quality standards.",
            "retry_count": 0
        })
    return True, False

def init_app():
    app = build_graph()
    config = {"configurable": {"thread_id": "novel_gen_thread_1"}}
    output_filename = "generated_novel.md"
    current_saved_state = app.get_state(config)
    
    latest_draft = ""
    latest_passed_critic = False
    latest_passed_canon = False
    pending_human_override = False
    
    if current_saved_state.values:
        print("\n  Existing checkpoint found in 'state_checkpoint.db'! Resuming...")
        stream_input = None
        active_chapter = current_saved_state.values.get("current_chapter", 1)
        latest_draft = current_saved_state.values.get("current_draft", "")
        latest_passed_critic = current_saved_state.values.get("passed_critic", False)
        latest_passed_canon = current_saved_state.values.get("passed_canon", False)
    else:
        print("\n  Starting fresh novel generation pipeline...\n")
        story_idea = input("Enter your raw story idea to generate the Bible: ").strip()
        
        stream_input = {
            "story_idea": story_idea,
            "current_planning_act": 1,
            "drafted_chapters": {},
            "rolling_context": [],
            "recent_scene_texts": [],
            "flagged_scenes": [],
            "retry_count": 0,
            "is_complete": False
        }
        active_chapter = 1

    while True:
        run_config = {**config, "run_name": f"Chapter {active_chapter}"}
        
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
                        # Fetch the title safely; default to 'Generated Novel'
                        title = value.get("master_outline", {}).get("title", "Generated Novel")
                        # Write title header if this is the very first scene of the book
                        if active_chapter == 1 and value.get("current_scene", 2) == 2:
                            with open(output_filename, "w", encoding="utf-8") as f:
                                f.write(f"# {title}\n\n")
                                
                        with open(output_filename, "a", encoding="utf-8") as f:
                            f.write(latest_draft + "\n\n---\n\n")
                        tag = " [HUMAN OVERRIDE]" if pending_human_override and not auto_passed else ""
                        print(f"--> [SAVED] Approved scene written to '{output_filename}'{tag}\n")
                    elif latest_draft:
                        print(f"--> [SKIPPED WRITE] Scene did not pass checks — not saved.\n")
                    
                    latest_draft = ""
                    latest_passed_critic = False
                    latest_passed_canon = False
                    pending_human_override = False
                    
                    new_ch = value.get("current_chapter", active_chapter)
                    if new_ch > active_chapter and not value.get("is_complete"):
                        print(f"\n==========================================\n  CHAPTER {active_chapter} COMPLETE!\n==========================================")
                        active_chapter = new_ch

        # Handle Interrupts
        snapshot = app.get_state(config)
        if not snapshot.next:
            break
            
        paused_node = snapshot.next[0]
        
        if paused_node == "bible_checkpoint":
            should_continue = _handle_bible_checkpoint(app, config, snapshot)
            override = False
        elif paused_node == "chapter_checkpoint":
            should_continue = _handle_chapter_checkpoint(app, config, snapshot)
            override = False
        elif paused_node == "human_checkpoint":
            should_continue, override = _handle_human_checkpoint(app, config, snapshot)
        else:
            should_continue, override = True, False

        pending_human_override = override
        if not should_continue:
            break
            
        stream_input = None

    print(f"\n  Pipeline Complete! Full manuscript saved to '{output_filename}'.")

if __name__ == "__main__":
    init_app()