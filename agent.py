from dotenv import load_dotenv
import os, asyncio
from datetime import datetime
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation
from livekit.plugins.google.beta.realtime import RealtimeModel
from prompt import AGENT_CHARACTER, PROMPT_INSTRUCTIONS, STOP_PHRASES

load_dotenv()

class Assistant(Agent):
    def __init__(self, stop_event) -> None:
        super().__init__(instructions=AGENT_CHARACTER)
        self.stop_event = stop_event

    async def on_transcript(self, text: str, final: bool, participant=None):
        if final and any(p in text.lower() for p in STOP_PHRASES):
            self.stop_event.set()

async def entrypoint(ctx: agents.JobContext):
    stop_event = asyncio.Event()
    gemini_model = RealtimeModel(
        model="gemini-2.0-flash-exp",
        voice="Puck",
        api_key=os.getenv("GOOGLE_API_KEY"),
    )

    session = AgentSession(llm=gemini_model)
    await ctx.connect()

    instructions = PROMPT_INSTRUCTIONS


    await session.start(
        room=ctx.room,
        agent=Assistant(stop_event),
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    # pass the enriched instruction to generate_reply
    await session.generate_reply(instructions=instructions)

    # wait for stop trigger (your current flow)
    await stop_event.wait()
    await session.stop()

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
