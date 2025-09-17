from dotenv import load_dotenv
import os, asyncio
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation
from livekit.plugins.google.beta.realtime import RealtimeModel
from prompt import AGENT_CHARACTER, AGENT_RESPONSE_STYLE, STOP_PHRASES


load_dotenv()

# Assistance code
# Livekit does audio pipelining, VAD, STT, TTS
class Assistant(Agent):
    def __init__(self, stop_event) -> None:
        super().__init__(instructions=AGENT_CHARACTER)
        self.stop_event = stop_event

    
    async def on_transcript(self, text: str, final: bool, participant=None):
        if final and any(p in text.lower() for p in STOP_PHRASES):
            self.stop_event.set()

async def entrypoint(ctx: agents.JobContext):
    # Event the task is been grasped into stop_event
    stop_event = asyncio.Event()
    gemini_model = RealtimeModel(
        model="gemini-2.0-flash-exp",
        voice="Puck",
        api_key=os.getenv("GOOGLE_API_KEY"),
    )
    # Google llm does the TTS
    # Voice Activity Detection Hook used by Livekit
    session = AgentSession(llm=gemini_model)
    
    
    # Connects to LiveKit web socket
    await ctx.connect()
    
    # Joins the LiveKit room
    await session.start(
        room=ctx.room,
        # Assistant is called
        agent=Assistant(stop_event),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )
    # Triggers the speech-to-speech flow (Gemini LLM → STT -> TTS → publish reply).
    await session.generate_reply(instructions=AGENT_RESPONSE_STYLE)
    # Use to stop the current output
    await stop_event.wait()
    # Livekit session is been halted
    await session.stop()        
    
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    