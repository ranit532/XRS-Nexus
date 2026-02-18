import os
import sys
# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.agents import app
from langchain_core.messages import HumanMessage
import uuid

def main():
    print("Welcome to the Multi-Agent Lineage System!")
    print("Type 'exit' to quit.")
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        print("Processing...", end="", flush=True)
        
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        # Run the graph
        for event in app.stream(inputs, config=config):
            for key, value in event.items():
                print(f"\n--- {key} ---")
                # print(value) # Debug full state if needed
        
        # Get final response
        # In this simple implementation, the last message in state is expected to be the answer
        # But since we use stream, the output is printed incrementally or handled above.
        # Let's just print the final message content nicely.
        
        # (This loop prints intermediate steps. A cleaner UI would just show the final answer.)

if __name__ == "__main__":
    main()
