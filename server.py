# server.py
import asyncio, sys, os, subprocess, signal
from pathlib import Path
from typing import AsyncIterator
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, PlainTextResponse, FileResponse

app = FastAPI(title="Agent Controller")

PROJECT_DIR = Path(__file__).parent.resolve()
INDEX_PATH = PROJECT_DIR / "./templates/index.html"
FAVICON_PATH = PROJECT_DIR / "favicon.ico"

AGENT_CMD = [sys.executable, "agent.py", "console"]
_agent_proc = None
_log_queue: asyncio.Queue | None = None


@app.get("/")
async def root():
    return FileResponse(str(INDEX_PATH)) if INDEX_PATH.exists() else PlainTextResponse("index.html not found", 404)


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(str(FAVICON_PATH)) if FAVICON_PATH.exists() else Response(status_code=204)


@app.post("/start")
async def start_agent():
    global _agent_proc, _log_queue
    if _agent_proc and _agent_proc.poll() is None:
        return PlainTextResponse("Agent already running", 400)

    _log_queue = asyncio.Queue()

    # Create a new process group so we can signal/kill the whole group later
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    start_new_session = False if os.name == "nt" else True

    _agent_proc = subprocess.Popen(
        AGENT_CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(PROJECT_DIR),
        bufsize=1,
        universal_newlines=True,
        creationflags=creationflags,
        start_new_session=start_new_session,
    )

    asyncio.get_event_loop().create_task(_read_process_lines(_agent_proc, _log_queue))
    return PlainTextResponse("started", 200)


async def _read_process_lines(proc: subprocess.Popen, queue: asyncio.Queue):
    # Read lines without blocking the event loop
    loop = asyncio.get_event_loop()
    try:
        def reader():
            assert proc.stdout is not None
            for ln in proc.stdout:
                yield ln
        for line in await loop.run_in_executor(None, lambda: list(reader())):
            await queue.put(line.rstrip("\n"))
        await queue.put("[agent] process exited")
    except Exception as e:
        await queue.put(f"[agent-reader] error: {e}")
    finally:
        await queue.put("[agent-reader] finished")


@app.post("/stop")
async def stop_agent():
    global _agent_proc, _log_queue
    if not _agent_proc or _agent_proc.poll() is not None:
        return PlainTextResponse("Agent is not running", 400)

    proc = _agent_proc
    try:
        # Graceful: signal the process group
        if os.name == "nt":
            try:
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            except Exception:
                proc.terminate()
        else:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                proc.terminate()

        # wait for graceful exit, else escalate
        try:
            proc.wait(timeout=6)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                proc.kill()
            else:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                return PlainTextResponse("failed to stop process (timeout)", 500)

        return PlainTextResponse("stopped", 200)

    except Exception as exc:
        return PlainTextResponse(f"error stopping: {exc}", 500)

    finally:
        _agent_proc = None
        if _log_queue is not None:
            # signal clients the agent stopped
            try:
                asyncio.get_event_loop().create_task(_log_queue.put("[server] stop called; agent stopped"))
            except Exception:
                pass


@app.get("/logs")
async def logs():
    global _log_queue

    async def event_generator() -> AsyncIterator[str]:
        if _log_queue is None:
            yield "data: [server] no logs available - start the agent first\n\n"
            return
        while True:
            try:
                line = await _log_queue.get()
            except asyncio.CancelledError:
                break
            if line is None:
                break
            yield f"data: {line}\n\n"
            if line.strip().lower().startswith("[agent] process exited"):
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")
