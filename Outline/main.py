import json
from langgraph.graph import StateGraph, START, END
from state import StoryState

# Import generative nodes
from nodes.concept_node import generate_concept
from nodes.character_node import generate_characters
from nodes.plot_node import generate_plot
from nodes.scene_node import generate_scenes
from nodes.canon_node import generate_canon
from nodes.style_node import generate_style

# Import agentic loop nodes
from nodes.review_node import evaluate_bible
from nodes.refine_node import refine_bible

def router(state: StoryState):
    # Stop condition 1: It's perfect
    if state.get("is_valid") == True:
        print("Editor approved the story bible!")
        return END
    
    # Stop condition 2: Prevent infinite loops (max 2 revisions)
    if state.get("revision_count", 0) >= 2:
        print("Max revisions reached. Exiting loop.")
        return END
        
    # Otherwise, loop back to fix it
    print(f"\n[!] Critic found issues: {state.get('feedback')}\nRouting to Refiner...")
    return "refine"

def build_graph():
    workflow = StateGraph(StoryState)
    
    # Add Nodes
    workflow.add_node("concept", generate_concept)
    workflow.add_node("characters", generate_characters)
    workflow.add_node("plot", generate_plot)
    workflow.add_node("scenes", generate_scenes)
    workflow.add_node("canon", generate_canon)
    workflow.add_node("style", generate_style)
    workflow.add_node("review", evaluate_bible)
    workflow.add_node("refine", refine_bible)
    
    # Linear generation
    workflow.add_edge(START, "concept")
    workflow.add_edge("concept", "characters")
    workflow.add_edge("characters", "plot")
    workflow.add_edge("plot", "scenes")
    workflow.add_edge("scenes", "canon")
    workflow.add_edge("canon", "style")
    workflow.add_edge("style", "review")
    
    # --- Agentic Loop ---
    workflow.add_conditional_edges("review", router)
    workflow.add_edge("refine", "review") # After refining, evaluate it again
    
    return workflow.compile()

if __name__ == "__main__":
    print("Loading input scenes from initial.json...")
    
    # Load the JSON file provided by the user
    try:
        with open("initial.json", "r", encoding="utf-8") as f:
            input_payload = json.load(f)
    except FileNotFoundError:
        print("Error: 'initial.json' not found. Please ensure it exists in the root directory.")
        exit(1)

    # Set up the initial state
    initial_state = {
        "raw_scenes": input_payload.get("chapters", input_payload),
        "revision_count": 0 # Initialize revision counter
    }
    
    print("Compiling agentic workflow...")
    app = build_graph()
    
    print("Executing master story bible generation (this may take a minute)...")
    final_state = app.invoke(initial_state)
    
    # Clean up internal graph state (remove raw input and loop trackers) before saving
    keys_to_remove = ["raw_scenes", "is_valid", "feedback", "revision_count"]
    for key in keys_to_remove:
        final_state.pop(key, None)
    
    # Write the compiled dictionary to a JSON file
    output_filename = "master_outline.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(final_state, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccess! Master story bible saved to {output_filename}")