import json
import os
from graph import build_drafting_graph
from db import CanonDatabase

def _print_draft_for_review(values):
    print(f"\n=== HUMAN CHECKPOINT: Ch {values.get('current_chapter')} Sc {values.get('current_scene')} ===")
    print(f"Passed Critic: {values.get('passed_critic')} | Passed Canon: {values.get('passed_canon')}")
    if values.get("canon_violations"): print(f"Canon Violations: {values['canon_violations']}")
    if values.get("critic_feedback"): print(f"Critic Feedback: {values['critic_feedback']}")
    print(f"\n--- Draft ---\n{values.get('current_draft', '')}\n")

def _handle_checkpoint(app, config, snapshot):
    _print_draft_for_review(snapshot.values)
    choice = input("Approve this scene? [y]es / [n]o / [r]evise: ").strip().lower()
    
    was_auto_passed = bool(snapshot.values.get("passed_critic")) and bool(snapshot.values.get("passed_canon"))
    
    if choice == "y":
        app.update_state(config, {"human_approved": True, "human_revision_notes": None})
        return True, not was_auto_passed
    elif choice == "r":
        notes = input("Revision notes for the writer: ").strip()
        app.update_state(config, {"human_approved": False, "human_revision_notes": notes, "retry_count": 0})
    else:
        app.update_state(config, {"human_approved": False, "human_revision_notes": "Rejected. Rewrite.", "retry_count": 0})
    return True, False

def main():
    if not os.path.exists("outline.json"):
        print("Error: 'outline.json' not found. Please run 'step1_generate_outline.py' first.")
        return

    app = build_drafting_graph()
    config = {"configurable": {"thread_id": "drafting_thread_1"}}
    output_filename = "generated_novel.md"
    current_state = app.get_state(config)
    
    latest_draft = ""
    pending_human_override = False
    
    if current_state.values:
        print("\nResuming existing drafting run...")
        stream_input = None
        active_chapter = current_state.values.get("current_chapter", 1)
        latest_draft = current_state.values.get("current_draft", "")
    else:
        print("\nStarting new drafting run from outline.json...")
        with open("outline.json", "r", encoding="utf-8") as f:
            master_outline = json.load(f)
            
        # Seed the DB
        db = CanonDatabase()
        for char_name, char_details in master_outline.get("characters", {}).items():
            db.upsert_entity(char_name, "Character", [f"{k}: {v}" for k, v in char_details.items() if v])
            
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(f"# {master_outline.get('title', 'Untitled Novel')}\n\n")
            
        stream_input = {
            "master_outline": master_outline,
            "current_chapter": 1,
            "current_scene": 1,
            "rolling_context": [],
            "recent_scene_texts": [],
            "flagged_scenes": [],
            "retry_count": 0,
            "is_complete": False
        }
        active_chapter = 1

    while True:
        for output in app.stream(stream_input, config):
            for key, value in output.items():
                print(f"--> Executed Node: {key}")
                if key == "writer" and "current_draft" in value:
                    latest_draft = value["current_draft"]
                if key == "manager":
                    should_save = bool(latest_draft) and (value.get("passed_critic") and value.get("passed_canon") or pending_human_override)
                    if should_save:
                        with open(output_filename, "a", encoding="utf-8") as f:
                            f.write(latest_draft + "\n\n---\n\n")
                        print(f"--> [SAVED] Scene written to '{output_filename}'")
                    
                    latest_draft = ""
                    pending_human_override = False
                    
                    new_ch = value.get("current_chapter", active_chapter)
                    if new_ch > active_chapter and not value.get("is_complete"):
                        print(f"\n=== CHAPTER {active_chapter} COMPLETE ===")
                        active_chapter = new_ch

        snapshot = app.get_state(config)
        if not snapshot.next: break
            
        should_continue, pending_human_override = _handle_checkpoint(app, config, snapshot)
        if not should_continue: break
        stream_input = None

    print(f"\nDrafting Complete! Manuscript saved to '{output_filename}'.")

if __name__ == "__main__":
    main()