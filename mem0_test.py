# mem0_test.py — function style
import os, json, warnings, logging,time
from dotenv import load_dotenv
from mem0 import MemoryClient

load_dotenv()
warnings.filterwarnings("ignore", category=DeprecationWarning)

user_name = "Boss"
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

def add_memory():
    messages_formatted = [
        {"role": "user", "content": "I really like Python Language."},
        {"role": "assistant", "content": "That is a good choice to start with programming."},
        {"role": "user", "content": "I think so too, Because several built libraries and simpler syntax."},
        {"role": "assistant", "content": "What is your favorite feature ?"},
    ]
    client.add(messages_formatted, user_id=user_name)

def get_memory_by_query():
    query = f"What are {user_name}'s preferences?"
    results = client.search(query, user_id=user_name)

    memories = [
        {"memory": r.get("memory"), "updated_at": r.get("updated_at")}
        for r in (results or [])
    ]
    memories_str = json.dumps(memories, indent=2, default=str)
    print(f"\nMemories:\n{memories_str}")
    return memories_str

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    add_memory()
    time.sleep(0.5)
    get_memory_by_query()
