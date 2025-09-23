# AI Assistant with mem0 Integration

This project is an **AI assistant** built with [LiveKit Agents](https://github.com/livekit/agents) and integrated with **mem0**, a lightweight memory database for persistent context management.  
It provides tools, prompts, and an agent interface that can remember past interactions, handle tickets, and extend functionality with custom utilities.

---

## ⚡ Features

- **Persistent Memory (mem0):** Stores and retrieves contextual memory for the agent.  
- **LiveKit Integration:** Uses `livekit-agents` for real-time multimodal agent capabilities.  
- **Custom Tools:** Provides weather, ticket handling, and datetime tools via `tools.py`.  
- **Prompt Management:** Centralized instructions and welcome messages in `prompt.py`.  
- **Testing:** `mem0_test.py` ensures memory configuration works as expected.  

---

## 🔧 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/ai-assistant-mem0.git
   cd ai-assistant-mem0

    Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

Install dependencies:

pip install -r requirements.txt

Set environment variables in a .env file (API keys, model configs, etc.):

    GOOGLE_API_KEY=your_key_here
    LIVEKIT_API_KEY=your_key_here
    LIVEKIT_API_SECRET=your_secret_here
    MEM0_API_KEY=your_secret_here

🚀 Usage
Run the Agent

python agent.py

This will start the assistant with the configured mem0 memory backend.
Test Memory Functionality

python mem0_test.py

This ensures that mem0 is properly storing and retrieving data.
🛠 Development Notes

    Update tools.py to add new tools or utilities.

    Modify prompt.py for custom system instructions.

    Logs can be enabled by adjusting the logging configuration inside agent.py.
