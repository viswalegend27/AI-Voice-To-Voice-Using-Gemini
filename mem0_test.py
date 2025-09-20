# mem0_test.py — clean & concise
import os, json
from dotenv import load_dotenv
from mem0 import MemoryClient
import warnings

load_dotenv()
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

user_id = "Boss"
warnings.filterwarnings("ignore", category=DeprecationWarning)

messages = [
    {"role": "user", "content": "Hi, I'm your Boss. I'm a software engineer and I love python."},
    {"role": "assistant", "content": "Hello Boss! I'll remember your expertise and interests."}
]

# Add memory
client.add(messages, user_id=user_id)

# Search memory
query = f"What does {user_id} do for a living?"
search_results = client.search(query, user_id=user_id)
print("Search results:\n", json.dumps(search_results, indent=2, default=str))

# Get all memories
all_mems = client.get_all(user_id=user_id)
print("\nAll memories:\n", json.dumps(all_mems, indent=2, default=str))
