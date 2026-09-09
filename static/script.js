/* =========================================================================
   GestureSpeak AI — frontend logic
   - Page navigation (single-page app, no reloads)
   - Theme / font-size accessibility controls
   - Webcam capture -> POST /predict -> render result
   - Temporal smoothing so a gesture must hold steady before it is confirmed
   - Text-to-speech via the browser's SpeechSynthesis API
   ========================================================================= */

// Single source of truth for gesture metadata on the frontend. Mirrors
// gesture_classifier.py's GESTURES dict so the "10 Gestures" page and the
// live panel labels stay consistent with what the backend can return.
const GESTURE_LIST = [
  { key: "FOOD", num: "01", emoji: "🖐️", name: "FOOD", message: "I want food.", instruction: "Open palm, five fingers extended" },
  { key: "WATER", num: "02", emoji: "🤟", name: "WATER", message: "I need water.", instruction: "Three fingers extended" },
  { key: "TEA_COFFEE", num: "03", emoji: "✌️", name: "TEA / COFFEE", message: "I want tea or coffee.", instruction: "Index and middle fingers extended" },
  { key: "HELP", num: "04", emoji: "✊", name: "HELP", message: "I need help.", instruction: "Closed fist, all fingers folded" },
  { key: "YES", num: "05", emoji: "👍", name: "YES", message: "Yes.", instruction: "Thumb pointing upward" },
  { key: "NO", num: "06", emoji: "👎", name: "NO", message: "No.", instruction: "Thumb pointing downward" },
  { key: "PLEASE", num: "07", emoji: "🙏", name: "PLEASE", message: "Please.", instruction: "Both hands held close together" },
  { key: "WANT_THAT", num: "08", emoji: "☝️", name: "WANT THAT", message: "I want that.", instruction: "Only the index finger extended" },
  { key: "OKAY", num: "09", emoji: "👌", name: "OKAY", message: "I am okay.", instruction: "Thumb and index finger form an OK sign" },
  { key: "HELLO", num: "10", emoji: "👋", name: "HELLO / ATTENTION", message: "Hello. Please notice me.", instruction: "Open hand, waved side to side" },
];

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------
function goToPage(pageId) {
  document.querySelectorAll(".page").forEach((el) => el.classList.remove("active"));
  document.getElementById("page-" + pageId).classList.add("active");
  document.querySelectorAll(".nav-link").forEach((el) => {
    el.classList.toggle("active", el.dataset.nav === pageId);
  });
  window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
}

document.querySelectorAll("[data-nav]").forEach((el) => {
  el.addEventListener("click", (e) => {
    e.preventDefault();
    goToPage(el.dataset.nav);
  });
});

// ---------------------------------------------------------------------------
// Accessibility controls: theme + font size
// ---------------------------------------------------------------------------
const themeToggle = document.getElementById("theme-toggle");
themeToggle.addEventListener("click", () => {
  const isLight = document.documentElement.classList.toggle("light-mode");
  themeToggle.textContent = isLight ? "☀️" : "🌙";
});

const fontSteps = ["", "font-lg", "font-xl"];
let fontIndex = 0;
document.getElementById("font-toggle").addEventListener("click", () => {
  document.body.classList.remove(...fontSteps.filter(Boolean));
  fontIndex = (fontIndex + 1) % fontSteps.length;
  if (fontSteps[fontIndex]) document.body.classList.add(fontSteps[fontIndex]);
});

// ---------------------------------------------------------------------------
// Build the "10 Gestures" cards from the shared list
// ---------------------------------------------------------------------------
const gestureGrid = document.getElementById("gesture-grid");
gestureGrid.innerHTML = GESTURE_LIST.map(
  (g) => `
  <div class="gesture-card">
    <span class="gnum">${g.num}</span>
    <span class="gi">${g.emoji}</span>
    <h4>${g.name}</h4>
    <div class="gmsg">"${g.message}"</div>
    <p class="ginstr">${g.instruction}</p>
  </div>`
).join("");

// ---------------------------------------------------------------------------
// Webcam + recognition state
// ---------------------------------------------------------------------------
const video = document.getElementById("webcam");
const placeholder = document.getElementById("cam-placeholder");
const statusPill = document.getElementById("status-pill");
const statusText = document.getElementById("status-text");
const btnStart = document.getElementById("btn-start-cam");
const btnStop = document.getElementById("btn-stop-cam");
const camAlert = document.getElementById("cam-alert");
const autospeakToggle = document.getElementById("autospeak-toggle");

const recogEmoji = document.getElementById("recog-emoji");
const recogName = document.getElementById("recog-name");
const recogMessage = document.getElementById("recog-message");
const confidenceValue = document.getElementById("confidence-value");
const confidenceFill = document.getElementById("confidence-fill");
const handTag = document.getElementById("hand-tag");

let stream = null;
let captureTimer = null;
let autoSpeakOn = true;
let inFlight = false;

// Temporal smoothing: a gesture is only "confirmed" (displayed + spoken)
// once the same gesture key has been the top prediction continuously for
// CONFIRM_MS milliseconds, per the 0.8-1.5s stability requirement.
const CONFIRM_MS = 1100;
const CAPTURE_INTERVAL_MS = 220;
let pendingKey = null;
let pendingSince = 0;
let confirmedKey = null;

function showAlert(message) {
  camAlert.textContent = message;
  camAlert.classList.add("show");
}
function clearAlert() {
  camAlert.classList.remove("show");
  camAlert.textContent = "";
}

function setCameraStatus(live, label) {
  statusPill.classList.toggle("live", live);
  statusText.textContent = label;
}

async function checkServer() {
  try {
    const res = await fetch("/health");
    if (!res.ok) throw new Error("offline");
    return true;
  } catch {
    return false;
  }
}

btnStart.addEventListener("click", async () => {
  clearAlert();

  const serverUp = await checkServer();
  if (!serverUp) {
    showAlert("Python AI server is offline. Start app.py and try again.");
    return;
  }

  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 }, audio: false });
  } catch (err) {
    showAlert("Camera permission is required. Please allow camera access in your browser.");
    return;
  }

  video.srcObject = stream;
  placeholder.style.display = "none";
  setCameraStatus(true, "Live");
  btnStart.disabled = true;
  btnStop.disabled = false;

  captureTimer = setInterval(captureAndPredict, CAPTURE_INTERVAL_MS);
});

btnStop.addEventListener("click", stopCamera);

function stopCamera() {
  if (captureTimer) clearInterval(captureTimer);
  captureTimer = null;
  if (stream) {
    stream.getTracks().forEach((t) => t.stop());
    stream = null;
  }
  video.srcObject = null;
  placeholder.style.display = "flex";
  setCameraStatus(false, "Camera off");
  btnStart.disabled = false;
  btnStop.disabled = true;
  pendingKey = null;
  confirmedKey = null;
  renderUnknown(0);
}

autospeakToggle.addEventListener("click", () => {
  autoSpeakOn = !autoSpeakOn;
  autospeakToggle.classList.toggle("on", autoSpeakOn);
  autospeakToggle.setAttribute("aria-checked", String(autoSpeakOn));
});

// ---------------------------------------------------------------------------
// Capture a frame, send it to /predict, apply temporal smoothing
// ---------------------------------------------------------------------------
const captureCanvas = document.createElement("canvas");

async function captureAndPredict() {
  if (inFlight || !stream || video.readyState < 2) return;
  inFlight = true;

  captureCanvas.width = video.videoWidth || 640;
  captureCanvas.height = video.videoHeight || 480;
  const ctx = captureCanvas.getContext("2d");
  ctx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
  const dataUrl = captureCanvas.toDataURL("image/jpeg", 0.7);

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: dataUrl }),
    });
    if (!res.ok) throw new Error("bad response");
    const data = await res.json();
    handleResult(data);
    clearAlert();
  } catch (err) {
    showAlert("Python AI server is offline. Start app.py and try again.");
  } finally {
    inFlight = false;
  }
}

function handleResult(data) {
  handTag.textContent = data.hands === 1 ? "1 hand detected" : data.hands + " hands detected";

  const key = data.gesture;
  const now = performance.now();

  if (key === "UNKNOWN" || !key) {
    pendingKey = null;
    confirmedKey = null;
    renderLive(data, false);
    return;
  }

  if (key !== pendingKey) {
    pendingKey = key;
    pendingSince = now;
  }

  const held = now - pendingSince;
  const isStable = held >= CONFIRM_MS;

  // Always update the live confidence bar and hand count immediately,
  // but only "confirm" (update the big message + speak) once stable.
  renderLive(data, isStable);

  if (isStable && key !== confirmedKey) {
    confirmedKey = key;
    if (autoSpeakOn) speak(data.message);
  }
}

function renderLive(data, confirmed) {
  const meta = GESTURE_LIST.find((g) => g.key === data.gesture);
  recogEmoji.textContent = data.emoji || "🤔";
  recogName.textContent = confirmed && meta ? meta.name : data.gesture === "UNKNOWN" ? "NO GESTURE" : "RECOGNIZING…";
  recogMessage.textContent = data.message;
  const pct = Math.round((data.confidence || 0) * 100);
  confidenceValue.textContent = pct + "%";
  confidenceFill.style.width = pct + "%";
}

function renderUnknown(hands) {
  recogEmoji.textContent = "🤔";
  recogName.textContent = "NO GESTURE";
  recogMessage.textContent = "No gesture detected.";
  confidenceValue.textContent = "0%";
  confidenceFill.style.width = "0%";
  handTag.textContent = hands + " hands detected";
}

// ---------------------------------------------------------------------------
// Text-to-speech + message actions
// ---------------------------------------------------------------------------
function speak(text) {
  if (!("speechSynthesis" in window) || !text) return;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 0.98;
  window.speechSynthesis.speak(utter);
}

document.getElementById("btn-speak").addEventListener("click", () => {
  speak(recogMessage.textContent);
});

document.getElementById("btn-copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(recogMessage.textContent);
  } catch {
    /* clipboard unavailable — silently ignore in this prototype */
  }
});

document.getElementById("btn-clear").addEventListener("click", () => {
  pendingKey = null;
  confirmedKey = null;
  renderUnknown(handTag.textContent.startsWith("0") ? 0 : 1);
});

// Stop the camera cleanly if the user navigates away from the tab/app.
window.addEventListener("beforeunload", () => {
  if (stream) stream.getTracks().forEach((t) => t.stop());
});
