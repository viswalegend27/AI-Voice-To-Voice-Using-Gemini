# mem0_test.py — function style
import os, json, warnings, logging,time
from dotenv import load_dotenv
from mem0 import MemoryClient

load_dotenv()
warnings.filterwarnings("ignore", category=DeprecationWarning)

user_name = "Boss"
mem0 = MemoryClient()

def add_memory():
    messages_formatted = [
        {"role": "user", "content": "I really like Python Language."},
        {"role": "assistant", "content": "That is a good choice to start with programming."},
        {"role": "user", "content": "I think so too, Because several built libraries and simpler syntax."},
        {"role": "assistant", "content": "What is your favorite feature ?"},
    ]
    mem0.add(messages_formatted, user_id=user_name)

def get_memory_by_query():
    mem0 = MemoryClient()
    query = f"What are {user_name}'s preferences?"
    results = mem0.search(query, user_id=user_name)

    memories = [
        {"memory": r.get("memory"), "updated_at": r.get("updated_at")}
        for r in (results or [])
    ]
    memories_str = json.dumps(memories, indent=2, default=str)
    print(f"\nMemories:\n{memories_str}")
    return memories_str

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    get_memory_by_query()