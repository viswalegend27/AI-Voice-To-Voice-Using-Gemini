from dotenv import load_dotenv
import os
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation
from livekit.plugins.google.beta.realtime import RealtimeModel
from prompt import AGENT_CHARACTER, AGENT_RESPONSE_STYLE


load_dotenv()

# Assistance code
# Livekit does audio pipelining, VAD, STT, TTS
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_CHARACTER)


async def entrypoint(ctx: agents.JobContext):
    
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
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )
    # Triggers the speech-to-speech flow (Gemini LLM → STT -> TTS → publish reply).
    await session.generate_reply(
        instructions=AGENT_RESPONSE_STYLE
    )    
    
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    