from dotenv import load_dotenv
import os, asyncio
import logging
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation
from livekit.plugins.google.beta.realtime import RealtimeModel
from prompt import AGENT_CHARACTER, AGENT_RESPONSE_STYLE, STOP_PHRASES
from tools import get_weather, get_datetime

load_dotenv()

# describing the agent's purpose
class Assistant(Agent):
    """
    Agent subclass holding the stop event and transcript handler.
    """

    def __init__(self, stop_event: asyncio.Event) -> None:
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
        )
        self.stop_event = stop_event


# event handling using transcript functionality
async def on_transcript(self, text: str, final: bool, participant=None):
    """Set stop_event when a stop phrase appears in the final transcript."""
    if final and any(p in text.lower() for p in STOP_PHRASES):
        logging.info("Stop phrase detected. Triggering stop_event.")
        self.stop_event.set()

async def entrypoint(ctx: agents.JobContext):
    # actual asynchronous process
    stop_event = asyncio.Event()

    # declaring livekit session
    session = AgentSession()
    # connecting to livekit session
    await ctx.connect()

    # defining the the agent's way of answering
    instructions = AGENT_RESPONSE_STYLE

    # session start in my live kit room
    await session.start(
        room=ctx.room,
        agent=Assistant(stop_event),
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )
    
    # pass the enriched instruction to generate_reply
    await session.generate_reply(instructions=instructions)

    # wait for stop trigger (your current flow)
    await stop_event.wait()
    # session stopped and wait for your command to continue
    await session.stop()
    
    # initial function call
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
