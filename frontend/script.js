// ── Session identifier (declared at absolute top) ─────────
const sessionId = (typeof crypto !== "undefined" && crypto.randomUUID)
  ? crypto.randomUUID()
  : "sess-" + Date.now().toString(36) + Math.random().toString(36).substring(2);

// ── DOM refs ──────────────────────────────────────────────
const recordBtn = document.getElementById("recordBtn");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const audioPlayer = document.getElementById("audioPlayer");
const ttsToggle = document.getElementById("ttsToggle");
const conversationArea = document.getElementById("conversationArea");

// Immediately stop audio if toggled off mid-speech
ttsToggle.addEventListener("change", () => {
  if (!ttsToggle.checked && audioPlayer && !audioPlayer.paused) {
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    setStatus("ready", "Ready (Muted)");
  }
});
const emptyState = document.getElementById("emptyState");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const waveform = document.getElementById("waveform");

// Upload zone refs
const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const replaceBtn = document.getElementById("replaceBtn");
const uploadIdle = document.getElementById("uploadIdle");
const uploadTextIdle = document.getElementById("uploadTextIdle");
const uploadProgress = document.getElementById("uploadProgress");
const uploadProgressText = document.getElementById("uploadProgressText");
const uploadLoaded = document.getElementById("uploadLoaded");
const docName = document.getElementById("docName");
const docMeta = document.getElementById("docMeta");
const chunkBadge = document.getElementById("chunkBadge");
const ingestTabs = document.getElementById("ingestTabs");
const textTitle = document.getElementById("textTitle");
const textContent = document.getElementById("textContent");
const indexTextBtn = document.getElementById("indexTextBtn");
const textCharCount = document.getElementById("textCharCount");

const togglePdf = document.getElementById("togglePdf");
const toggleText = document.getElementById("toggleText");
const sourceKnob = document.getElementById("sourceKnob");

let mediaRecorder;
let audioChunks = [];
let docLoaded = false;
let activeTab = "pdf";

// ── Pill toggle helpers ───────────────────────────────────
function positionKnob() {
  const active = activeTab === "pdf" ? togglePdf : toggleText;
  sourceKnob.style.width = active.offsetWidth + "px";
  sourceKnob.style.transform = `translateX(${active.offsetLeft - 3}px)`;
}
// Run once after layout so the knob starts in the right place
requestAnimationFrame(positionKnob);
window.addEventListener("resize", positionKnob);

// ── Upload zone ───────────────────────────────────────────

function setUploadState(state, info = {}) {
  uploadIdle.style.display = "none";
  uploadTextIdle.style.display = "none";
  uploadProgress.style.display = state === "progress" ? "flex" : "none";
  uploadLoaded.style.display = state === "loaded" ? "flex" : "none";
  ingestTabs.style.display = state === "loaded" ? "none" : "flex";

  if (state === "idle") {
    // show correct idle panel based on active tab
    if (activeTab === "pdf") {
      uploadIdle.style.display = "flex";
    } else {
      uploadTextIdle.style.display = "flex";
    }
  }

  uploadZone.classList.toggle("loaded", state === "loaded");

  if (state === "loaded") {
    docName.textContent = info.filename || info.title || "document";
    if (info.pages) {
      docMeta.textContent = `${info.pages} pages · ${info.chunks ?? "?"} chunks indexed`;
    } else {
      docMeta.textContent = `${info.characters ? info.characters.toLocaleString() + " chars · " : ""}${info.chunks ?? "?"} chunks indexed`;
    }
    docLoaded = true;
  } else {
    docLoaded = false;
  }

  // Enable mic only when a doc is loaded
  recordBtn.disabled = !docLoaded;
  chatInput.disabled = !docLoaded;
  sendBtn.disabled = !docLoaded;
  if (docLoaded) {
    chatInput.placeholder = "Ask anything about your study notes or book draft (or tap the mic)...";
  } else {
    chatInput.placeholder = "Upload a PDF or index notes to begin...";
  }
}

async function handleFileUpload(file) {
  if (!file || !file.name.toLowerCase().endsWith(".pdf")) {
    showToast("Please choose a PDF file.");
    return;
  }

  setUploadState("progress");

  const estimatedChunks = Math.max(1, Math.ceil(file.size / 15000));
  chunkBadge.textContent = `~${estimatedChunks} chunks`;

  if (estimatedChunks < 30)
    uploadProgressText.textContent = "Processing… (~5s)";
  else if (estimatedChunks < 50)
    uploadProgressText.textContent = "Processing… (~10s)";
  else if (estimatedChunks < 100)
    uploadProgressText.textContent = "Processing… (~15s)";
  else if (estimatedChunks < 200)
    uploadProgressText.textContent = "Processing… (~20s)";
  else uploadProgressText.textContent = "Processing… (~30s)";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/ingest", {
      method: "POST",
      headers: { "X-Session-ID": sessionId },
      body: formData
    });

    let data;
    try {
      data = await res.json();
    } catch (parseError) {
      throw new Error(`Server error (Status ${res.status}). This is usually a file-size crash or timeout.`);
    }

    if (!res.ok) {
      const errorMsg = data?.error || (typeof data?.detail === "string" ? data.detail : (data?.detail && data.detail[0]?.msg) || "Ingestion failed");
      throw new Error(errorMsg);
    }

    chunkBadge.textContent = `${data.chunks} chunks`;
    setUploadState("loaded", data);
    showToast("✓ Document indexed successfully!", "success");
  } catch (err) {
    setUploadState("idle");
    showToast("Error: " + err.message);
    console.error(err);
  }
}

// Click to pick file
uploadBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  fileInput.click();
});
uploadIdle.addEventListener("click", (e) => {
  if (e.target !== uploadBtn && activeTab === "pdf") {
    fileInput.click();
  }
});
replaceBtn.addEventListener("click", () => {
  setUploadState("idle");
  if (activeTab === "pdf") fileInput.click();
});
fileInput.addEventListener("change", () => {
  if (fileInput.files && fileInput.files[0]) {
    handleFileUpload(fileInput.files[0]);
  }
  fileInput.value = ""; // reset so same file can be re-uploaded
});

// ── Toggle switching ──────────────────────────────────────
function switchTab(tab) {
  activeTab = tab;
  togglePdf.classList.toggle("active", tab === "pdf");
  toggleText.classList.toggle("active", tab === "text");
  positionKnob();
  uploadIdle.style.display = tab === "pdf" ? "flex" : "none";
  uploadTextIdle.style.display = tab === "text" ? "flex" : "none";
}
togglePdf.onclick = () => switchTab("pdf");
toggleText.onclick = () => switchTab("text");

// ── Text char counter ──────────────────────────────────────
textContent.oninput = () => {
  const n = textContent.value.length;
  textCharCount.textContent =
    n.toLocaleString() + " character" + (n !== 1 ? "s" : "");
};

// ── Text ingestion ─────────────────────────────────────────
async function handleTextIngest() {
  const content = textContent.value.trim();
  const title = textTitle.value.trim() || "Pasted Text";

  if (!content) {
    showToast("Please paste some text first.");
    return;
  }
  if (content.length < 50) {
    showToast("Text is too short (minimum 50 characters).");
    return;
  }

  setUploadState("progress");
  const estimatedChunks = Math.max(1, Math.ceil(content.length / 350));
  chunkBadge.textContent = `~${estimatedChunks} chunks`;
  uploadProgressText.textContent =
    estimatedChunks < 50
      ? "Processing… (~30s)"
      : estimatedChunks < 100
        ? "Processing… (~60s)"
        : "Processing… (~90s)";

  try {
    const res = await fetch("/ingest/text", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Session-ID": sessionId
      },
      body: JSON.stringify({ text: content, title }),
    });

    let data;
    try {
      data = await res.json();
    } catch (parseError) {
      throw new Error(`Server error (Status ${res.status}).`);
    }

    if (!res.ok) {
      const errorMsg = data?.error || (typeof data?.detail === "string" ? data.detail : (data?.detail && data.detail[0]?.msg) || "Ingestion failed");
      throw new Error(errorMsg);
    }

    chunkBadge.textContent = `${data.chunks} chunks`;
    setUploadState("loaded", data);
    showToast("✓ Text indexed successfully!", "success");
  } catch (err) {
    setUploadState("idle");
    showToast("Error: " + err.message);
    console.error(err);
  }
}

indexTextBtn.onclick = handleTextIngest;

// ── Suggestion cards (Student & Reader Quick Prompts) ──────
document.querySelectorAll(".suggestion-card").forEach((btn) => {
  btn.addEventListener("click", () => {
    const prompt = btn.dataset.prompt;
    if (!prompt) return;
    if (!docLoaded) {
      showToast("Please upload a PDF or index notes first.");
      return;
    }
    chatInput.value = prompt;
    sendBtn.disabled = false;
    chatForm.dispatchEvent(new Event("submit"));
  });
});

// Drag & drop
uploadZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadZone.classList.add("drag-over");
});
uploadZone.addEventListener("dragleave", () =>
  uploadZone.classList.remove("drag-over"),
);
uploadZone.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) handleFileUpload(file);
});

// ── State helpers ──────────────────────────────────────────
function setStatus(state, text) {
  statusDot.className = "status-dot " + state;
  statusText.textContent = text;

  if (state === "recording") {
    recordBtn.classList.add("recording");
    recordBtn.querySelector(".waveform").classList.add("active");
  } else {
    recordBtn.classList.remove("recording");
    recordBtn.querySelector(".waveform").classList.remove("active");
  }

  if (state !== "idle") {
    const isBusy =
      state === "processing" || state === "speaking" || state === "recording";
    recordBtn.disabled = state === "processing" || state === "speaking";
    chatInput.disabled = isBusy;
    sendBtn.disabled = isBusy || !chatInput.value.trim();
  }
}

function showToast(msg, type = "error") {
  let toast = document.querySelector(".toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.background = type === "success" ? "#2e7d32" : "#c62828";
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3500);
}

function getTime() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ── Markdown Formatter ────────────────────────────────────
function formatMarkdown(rawText) {
  if (!rawText) return "";

  // 1. Normalize dense/inline numbered lists and bullet points into distinct lines
  // e.g. "workflow: 1. **Profile" or "). 2. **Weighted" or "calls to: * Detect"
  let text = rawText
    .replace(/(?<=[^\n])\s+(\d{1,2}\.\s+\*\*)/g, "\n\n$1")
    .replace(/(?<=[^\n])\s+(\d{1,2}\.\s+[A-Z])/g, "\n\n$1")
    .replace(/(?<=[^\n])\s+([*•]\s+)/g, "\n* ");

  // 2. If marked is available, use marked with breaks enabled
  if (typeof marked !== "undefined" && marked.parse) {
    try {
      marked.setOptions({
        breaks: true,
        gfm: true,
      });
      return marked.parse(text);
    } catch (e) {
      console.warn("marked.parse error, using fallback regex parser:", e);
    }
  }

  // 3. Fallback lightweight regex markdown parser
  const escapeHtml = (str) =>
    str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  let out = escapeHtml(text);

  // Bold **text** or __text__
  out = out.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/__(.*?)__/g, "<strong>$1</strong>");

  // Italic *text* or _text_
  out = out.replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, "<em>$1</em>");
  out = out.replace(/(?<!_)_(?!_)(.*?)(?<!_)_(?!_)/g, "<em>$1</em>");

  // Inline code `code`
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Numbered list items
  out = out.replace(/^\s*\d+\.\s+(.*)$/gm, "<li>$1</li>");
  // Bullet items
  out = out.replace(/^\s*[\*\-\•]\s+(.*)$/gm, "<li>$1</li>");

  // Wrap consecutive <li> into <ul>
  out = out.replace(/(<li>[\s\S]*?<\/li>)/g, (match) => {
    return `<ul>${match}</ul>`;
  });
  // Collapse adjacent <ul> tags
  out = out.replace(/<\/ul>\s*<ul>/g, "");

  // Paragraphs
  const paragraphs = out.split(/\n\s*\n/);
  return paragraphs
    .map((p) => {
      p = p.trim();
      if (!p) return "";
      if (p.startsWith("<ul>") || p.startsWith("<ol>") || p.startsWith("<h")) return p;
      return `<p>${p.replace(/\n/g, "<br/>")}</p>`;
    })
    .filter(Boolean)
    .join("");
}

// ── Chat bubble builder ────────────────────────────────────
function addBubble(role, text) {
  if (emptyState) emptyState.style.display = "none";

  const wrap = document.createElement("div");
  wrap.className = "chat-bubble " + role;

  const avatar = document.createElement("div");
  avatar.className = "bubble-avatar";
  avatar.textContent = role === "user" ? "You" : "AI";

  const body = document.createElement("div");
  body.className = "bubble-body";

  const bubble = document.createElement("div");
  bubble.className = "bubble-text";
  if (role === "ai") {
    bubble.innerHTML = formatMarkdown(text);
  } else {
    bubble.textContent = text;
  }

  const time = document.createElement("div");
  time.className = "bubble-time";
  time.textContent = getTime();

  body.appendChild(bubble);
  body.appendChild(time);
  wrap.appendChild(avatar);
  wrap.appendChild(body);
  conversationArea.appendChild(wrap);
  conversationArea.scrollTop = conversationArea.scrollHeight;
  return wrap;
}

function addThinkingBubble() {
  if (emptyState) emptyState.style.display = "none";

  const wrap = document.createElement("div");
  wrap.className = "chat-bubble ai thinking-bubble";

  const avatar = document.createElement("div");
  avatar.className = "bubble-avatar";
  avatar.textContent = "AI";

  const body = document.createElement("div");
  body.className = "bubble-body";

  const bubble = document.createElement("div");
  bubble.className = "bubble-text";
  bubble.innerHTML =
    '<div class="dots"><span></span><span></span><span></span></div>';

  body.appendChild(bubble);
  wrap.appendChild(avatar);
  wrap.appendChild(body);
  conversationArea.appendChild(wrap);
  conversationArea.scrollTop = conversationArea.scrollHeight;
  return wrap;
}

// ── Recording ─────────────────────────────────────────────
recordBtn.onclick = async () => {
  if (!docLoaded) {
    showToast("Upload a PDF first.");
    return;
  }
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    await startRecording();
  } else {
    stopRecording();
  }
};

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });

    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
    mediaRecorder.onstop = sendAudioToBackend;
    mediaRecorder.start();

    setStatus("recording", "Recording…");
  } catch (err) {
    showToast("Microphone access denied.");
    console.error(err);
  }
}

function stopRecording() {
  mediaRecorder.stop();
  mediaRecorder.stream.getTracks().forEach((t) => t.stop());
  setStatus("processing", "Transcribing…");
}

chatInput.addEventListener("input", () => {
  if (
    docLoaded &&
    statusText.textContent !== "Recording…" &&
    statusText.textContent !== "Transcribing…" &&
    statusText.textContent !== "Speaking…"
  ) {
    sendBtn.disabled = !chatInput.value.trim();
  }
});

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!docLoaded) return;

  const msg = chatInput.value.trim();
  if (!msg) return;

  chatInput.value = "";
  sendBtn.disabled = true;

  addBubble("user", msg);
  const thinkingEl = addThinkingBubble();
  setStatus("processing", "Thinking…");

  try {
    const isTtsEnabled = ttsToggle.checked;
    const res = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Session-ID": sessionId
      },
      body: JSON.stringify({ message: msg, tts: isTtsEnabled }),
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Failed to get answer");

    thinkingEl.remove();
    addBubble("ai", data.answer);

    if (isTtsEnabled && data.audio_base64) {
      setStatus("speaking", "Speaking…");
      const mime = data.audio_mime || (data.audio_base64.startsWith("UklGR") ? "audio/wav" : "audio/mpeg");
      const audioBlob = await (
        await fetch(`data:${mime};base64,${data.audio_base64}`)
      ).blob();
      const audioURL = URL.createObjectURL(audioBlob);
      audioPlayer.src = audioURL;
      audioPlayer.onended = () => {
        setStatus("ready", "Ready");
        URL.revokeObjectURL(audioURL);
      };
      audioPlayer.onerror = (e) => {
        console.error("Audio playback error:", e);
        setStatus("ready", "Ready");
        URL.revokeObjectURL(audioURL);
      };
      audioPlayer.play().catch((err) => {
        console.warn("Audio autoplay blocked by browser policy:", err);
        setStatus("ready", "Ready");
      });
    } else {
      setStatus("ready", "Ready");
    }
  } catch (err) {
    thinkingEl.remove();
    showToast("Error: " + err.message);
    setStatus("ready", "Ready");
  }
});

// ── AudioBuffer to 16-bit Mono WAV Converter ────────────────
function audioBufferToWav(buffer) {
  const numChannels = 1;
  const sampleRate = buffer.sampleRate;
  const format = 1; // PCM
  const bitDepth = 16;

  // Downmix to mono if stereo
  let samples;
  if (buffer.numberOfChannels === 1) {
    samples = buffer.getChannelData(0);
  } else {
    const left = buffer.getChannelData(0);
    const right = buffer.getChannelData(1);
    samples = new Float32Array(left.length);
    for (let i = 0; i < left.length; i++) {
      samples[i] = (left[i] + right[i]) / 2;
    }
  }

  const bytesPerSample = bitDepth / 8;
  const blockAlign = numChannels * bytesPerSample;
  const byteRate = sampleRate * blockAlign;
  const dataSize = samples.length * bytesPerSample;
  const bufferSize = 44 + dataSize;

  const arrayBuffer = new ArrayBuffer(bufferSize);
  const view = new DataView(arrayBuffer);

  function writeString(offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  /* RIFF chunk descriptor */
  writeString(0, "RIFF");
  view.setUint32(4, 36 + dataSize, true);
  writeString(8, "WAVE");

  /* fmt sub-chunk */
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, format, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitDepth, true);

  /* data sub-chunk */
  writeString(36, "data");
  view.setUint32(40, dataSize, true);

  // Write PCM 16-bit samples
  let offset = 44;
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }

  return new Blob([view], { type: "audio/wav" });
}

// ── Send to backend ────────────────────────────────────────
async function sendAudioToBackend() {
  if (!audioChunks || !audioChunks.length) {
    setStatus("ready", "Ready");
    return;
  }

  setStatus("processing", "Transcribing…");

  try {
    const rawBlob = new Blob(audioChunks, { type: audioChunks[0]?.type || "audio/webm" });
    const arrayBuffer = await rawBlob.arrayBuffer();

    // Decode audio into PCM via browser AudioContext and encode to WAV
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    const audioCtx = new AudioCtx({ sampleRate: 16000 });
    const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
    const wavBlob = audioBufferToWav(audioBuffer);
    audioCtx.close();

    const formData = new FormData();
    formData.append("audio", wavBlob, "recording.wav");

    const res = await fetch("/voice/text", {
      method: "POST",
      headers: { "X-Session-ID": sessionId },
      body: formData
    });
    if (!res.ok) throw new Error("Transcribe failed: " + res.status);
    const data = await res.json();

    const questionText = (data.question || "").trim();
    if (!questionText) {
      showToast("No speech recognized. Please speak clearly and try again.");
      setStatus("ready", "Ready");
      return;
    }

    // Pipe the transcribed text into the chat flow manually for visual feedback
    chatInput.value = questionText;
    sendBtn.disabled = false;

    // Auto-submit the transcribed text
    chatForm.dispatchEvent(new Event("submit"));
  } catch (err) {
    showToast("Error: " + err.message);
    setStatus("ready", "Ready");
    console.error(err);
  }
}

// ── Init ──────────────────────────────────────────────────
// Always ask the user to choose a data source — never reuse a previous session's index.
(() => {
  setUploadState("idle");
  setStatus("idle", "Choose a data source to begin");
})();
