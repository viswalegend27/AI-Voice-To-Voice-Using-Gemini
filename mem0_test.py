# mem0_test.py — fixed version
import os, json, warnings, logging, time
from dotenv import load_dotenv
from mem0 import MemoryClient

load_dotenv()
warnings.filterwarnings("ignore", category=DeprecationWarning)

user_name = "Boss"

def add_memory():
    # Pass API key explicitly
    mem0 = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
    messages_formatted = [
        {"role": "user", "content": "I really like Python Language."},
        {"role": "assistant", "content": "That is a good choice to start with programming."},
        {"role": "user", "content": "My favorite color is blue."},
        {"role": "assistant", "content": "Blue is a nice color choice!"},
    ]
    try:
        result = mem0.add(messages_formatted, user_id=user_name)
        print(f"Memory added successfully: {result}")
    except Exception as e:
        print(f"Error adding memory: {e}")

def get_memory_by_query():
    mem0 = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))  # Pass API key
    try:
        
        queries = [
            f"What are {user_name}'s preferences?",
            "favorite color",
            "What does Boss like?"
        ]
        
        for query in queries:
            print(f"\nSearching: '{query}'")
            results = mem0.search(query, user_id=user_name)
            if results:
                for result in results:
                    print(f"  Found: {result.get('memory')}")
            else:
                print("  No results found")
                
    except Exception as e:
        print(f"Error searching memory: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    add_memory()
    time.sleep(2)  # Wait for processing
    get_memory_by_query()