const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const state = document.getElementById('state');
const log = document.getElementById('log');
let eventSource = null;

function appendLine(s) {
  log.textContent += s + "\n";
  log.scrollTop = log.scrollHeight;
}

async function startAgent(){
  startBtn.disabled = true;
  appendLine("[client] Sending start request...");
  const res = await fetch('/start', { method: 'POST' });
  if (!res.ok) {
    appendLine("[client] Failed to start: " + await res.text());
    startBtn.disabled = false;
    return;
  }
  appendLine("[client] Start request accepted. Opening log stream...");
  state.textContent = "Starting...";
  // open SSE log stream
  if (eventSource) eventSource.close();
  eventSource = new EventSource('/logs');

  eventSource.onmessage = (e) => {
    // regular log line
    appendLine(e.data);
    // try to detect ready/shutdown
    if (e.data.toLowerCase().includes('connected to gemini realtime') || e.data.toLowerCase().includes('connecting to gemini realtime')) {
      state.textContent = "Connected";
      stopBtn.disabled = false;
    }
    if (e.data.toLowerCase().includes('shutting down') || e.data.toLowerCase().includes('session closed') || e.data.toLowerCase().includes('job exiting')) {
      state.textContent = "Stopped";
      startBtn.disabled = false;
      stopBtn.disabled = true;
    }
  };

  eventSource.onerror = (err) => {
    appendLine("[client] Log stream closed / error");
    if (eventSource) eventSource.close();
    eventSource = null;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    state.textContent = "Stopped";
  };

  startBtn.disabled = true;
  stopBtn.disabled = false;
  state.textContent = "Running";
}

async function stopAgent(){
  stopBtn.disabled = true;
  appendLine("[client] Sending stop request...");
  const res = await fetch('/stop', { method: 'POST' });
  if (!res.ok) {
    appendLine("[client] Failed to stop: " + await res.text());
    stopBtn.disabled = false;
    return;
  }
  appendLine("[client] Stop request accepted.");
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  state.textContent = "Stopping";
  startBtn.disabled = false;
}

startBtn.addEventListener('click', startAgent);
stopBtn.addEventListener('click', stopAgent);