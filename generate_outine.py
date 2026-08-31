import json
from graph import build_outline_graph

def _handle_bible_checkpoint(app, config, snapshot) -> bool:
    print("\n=== STORY BIBLE REVIEW ===")
    print(json.dumps(snapshot.values.get("bible", {}), indent=2))
    choice = input("\nApprove this Story Bible? [y]es / [r]evise: ").strip().lower()
    
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
            
    choice = input("\nApprove this outline? [y]es / [r]evise: ").strip().lower()
    if choice == 'y':
        app.update_state(config, {"chapters_approved": True, "chapters_revision_notes": None})
    else:
        notes = input("Revision notes for the outliner: ").strip()
        app.update_state(config, {
            "chapters_approved": False, 
            "chapters_revision_notes": notes,
            "current_planning_act": 1,
            "drafted_chapters": {}
        })
    return True

def main():
    app = build_outline_graph()
    config = {"configurable": {"thread_id": "outline_thread_1"}}
    
    current_state = app.get_state(config)
    stream_input = None
    
    if current_state.values:
        print("\nResuming existing outline generation...")
    else:
        idea = input("Enter your raw story idea: ").strip()
        stream_input = {
            "story_idea": idea,
            "current_planning_act": 1,
            "drafted_chapters": {}
        }

    while True:
        for output in app.stream(stream_input, config):
            for key in output:
                print(f"--> Executed Node: {key}")

        snapshot = app.get_state(config)
        if not snapshot.next:
            break
            
        paused_node = snapshot.next[0]
        if paused_node == "bible_checkpoint":
            _handle_bible_checkpoint(app, config, snapshot)
        elif paused_node == "chapter_checkpoint":
            _handle_chapter_checkpoint(app, config, snapshot)
            
        stream_input = None

    # Graph finished. Compile and save outline.json.
    final_state = app.get_state(config).values
    if final_state.get("chapters_approved"):
        master_outline = dict(final_state.get("bible", {}))
        master_outline["chapters"] = final_state.get("drafted_chapters", {})
        
        with open("outline.json", "w", encoding="utf-8") as f:
            json.dump(master_outline, f, indent=2)
        print("\nSuccess! Outline generated and saved to 'outline.json'.")
        print("You can now hand-edit the JSON, then run 'python step2_draft_novel.py'.")

if __name__ == "__main__":
    main()