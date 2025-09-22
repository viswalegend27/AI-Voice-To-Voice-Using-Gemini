from dotenv import load_dotenv
import os, asyncio
import logging
import json
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext
from livekit.plugins import noise_cancellation
from livekit.plugins.google.beta.realtime import RealtimeModel
from prompt import AGENT_CHARACTER, AGENT_RESPONSE_STYLE, STOP_PHRASES
from tools import get_weather, get_datetime
from mem0 import AsyncMemoryClient

load_dotenv()

# describing the agent's purpose
class Assistant(Agent):
    def __init__(self, stop_event: asyncio.Event, chat_ctx=None) -> None:
        super().__init__(
            instructions=AGENT_CHARACTER,
            llm=RealtimeModel(
                model="gemini-2.0-flash-exp",
                voice="Puck",
                api_key=os.getenv("GOOGLE_API_KEY"),
            ),
            tools=[
                get_weather,
                get_datetime,
            ],
            chat_ctx=chat_ctx,
        )
        self.stop_event = stop_event

    # FIXED: Move transcript handler inside the Assistant class
    async def on_transcript(self, text: str, final: bool, participant=None):
        """Set stop_event when a stop phrase appears in the final transcript."""
        if final and any(p in text.lower() for p in STOP_PHRASES):
            logging.info("Stop phrase detected. Triggering stop_event.")
            self.stop_event.set()

async def entrypoint(ctx: agents.JobContext):
    stop_event = asyncio.Event()

    async def shutdown_hook(assistant: Assistant, mem0: AsyncMemoryClient, memory_str: str):
        """Saves the final chat context to mem0 upon shutdown."""
        logging.info("Shutting down, saving chat context to memory...")

        # Get chat context directly from the assistant instance
        chat_ctx = assistant.chat_ctx
        if not chat_ctx or not chat_ctx.items:
            logging.warning("Chat context is empty. Nothing to save.")
            return

        logging.info(f"Chat context messages to process: {chat_ctx.items}")

        messages_formatted = []
        for item in chat_ctx.items:
            content_str = ''.join(item.content) if isinstance(item.content, list) else str(item.content)
            # Skip adding the initial memory context back into memory
            if memory_str and memory_str in content_str:
                continue
            if item.role in ['user', 'assistant']:
                messages_formatted.append({
                    "role": item.role,
                    "content": content_str.strip()
                })

        if not messages_formatted:
            logging.info("No new user/assistant messages to save.")
            return

        logging.info(f"Formatted messages to save: {messages_formatted}")
        try:
            await mem0.add(messages_formatted, user_id="Boss")
            logging.info("✅ Chat context saved to memory.")
        except Exception as e:
            logging.error(f"❌ Failed to save chat context to mem0: {e}", exc_info=True)

    session = AgentSession()
    await ctx.connect()

    mem0 = AsyncMemoryClient(api_key=os.getenv("MEM0_API_KEY"))
    user_name = "Boss"

    try:
        results = await mem0.get_all(user_id=user_name)
    except Exception as e:
        logging.exception("mem0.get_all failed: %s", e)
        results = []

    initial_ctx = ChatContext()
    memory_string = ''
    if results:
        memories = [{"memory": r.get("memory"), "updated_at": r.get("updated_at")} for r in results]
        memory_string = json.dumps(memories)
        logging.info(f"Memories: {memory_string}")
        initial_ctx.add_message(
            role="assistant",
            content=f"The user's name is {user_name}, and this is relvant context about him: {memory_string}."
        )

    instructions = AGENT_RESPONSE_STYLE
    assistant = Assistant(stop_event, chat_ctx=initial_ctx)

    # This ensures it's always set to run when the job ends for any reason.
    # We pass the 'assistant' object directly into the lambda to capture it.
    # Created in order to traceback always to the shutdown
    ctx.add_shutdown_callback(lambda: shutdown_hook(assistant, mem0, memory_string))

    await session.start(
        room=ctx.room,
        agent=assistant,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )
    await session.generate_reply(instructions=instructions)

    # Now, wait for the session to end, either by the stop phrase or by disconnect.
    logging.info("Agent is running. Waiting for stop phrase or disconnect...")
    await stop_event.wait()

    # When stop_event is set, we can gracefully stop the session.
    # If a disconnect happens first, this part is skipped, but the shutdown hook still runs.
    logging.info("Stop event triggered, stopping session.")
    await session.stop()
    # actual asynchronous process
    stop_event = asyncio.Event()

    # FIXED: Changed to accept assistant instance instead of chat_ctx directly
    async def shutdown_hook(assistant_instance: Assistant, mem0: AsyncMemoryClient, memory_str: str):
        logging.info("Shutting down, saving chat context to memory...")

        messages_formatted = []

        # FIXED: Get chat context from the assistant instance
        chat_ctx = assistant_instance.chat_ctx
        logging.info(f"Chat context messages: {chat_ctx.items}")

        for item in chat_ctx.items:
            content_str = ''.join(item.content) if isinstance(item.content, list) else str(item.content)
            if memory_str and memory_str in content_str:
                continue
            if item.role in ['user', 'assistant']:
                messages_formatted.append({
                    "role": item.role,
                    "content": content_str.strip()
                })
        logging.info(f"Formatted messages to add to memory: {messages_formatted}")

        # async add
        try:
            await mem0.add(messages_formatted, user_id="Boss")
            logging.info("Chat context saved to memory.")
        except Exception as e:
            logging.exception("Failed to save chat context to mem0: %s", e)

    # declaring livekit session
    session = AgentSession()

    # connecting to livekit session
    await ctx.connect()

    # initializing our mem0 client (async) and passing api_key explicitly
    mem0 = AsyncMemoryClient(api_key=os.getenv("MEM0_API_KEY"))

    # giving our user a name
    user_name = "Boss"

    # retriving our memories from mem0 (async)
    try:
        results = await mem0.get_all(user_id=user_name)
    except Exception as e:
        logging.exception("mem0.get_all failed: %s", e)
        results = []

    initial_ctx = ChatContext()
    memory_string = ''

    if results:
        memories = [
            {
                # only stack the relevant information from the mem0
                "memory": result.get("memory"),
                "updated_at": result.get("updated_at")
            }
            for result in results
        ]
        # return the array into string
        memory_string = json.dumps(memories)
        logging.info(f"Memories: {memory_string}")
        initial_ctx.add_message(
            role="assistant",
            content=f"The user's name is {user_name}, and this is relvant context about him: {memory_string}."
        )

    # defining the the agent's way of answering
    instructions = AGENT_RESPONSE_STYLE

    # session start in my live kit room
    # create assistant instance so we can reference chat_ctx later
    assistant = Assistant(stop_event, chat_ctx=initial_ctx)

    await session.start(
        room=ctx.room,
        agent=assistant,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    # pass the enriched instruction to generate_reply
    await session.generate_reply(instructions=instructions)

    # wait for stop trigger (your current flow)
    await stop_event.wait()
    # ensure we always call the shutdown hook after stopping the session
    try:
        await session.stop()
    finally:
        # FIXED: Pass assistant instance instead of initial_ctx
        await ctx.add_shutdown_callback(lambda: shutdown_hook(session._agent.chat_ctx, mem0, memory_string))

# initial function call
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))