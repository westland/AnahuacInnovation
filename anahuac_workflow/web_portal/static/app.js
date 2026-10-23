/**
 * Universidad Anáhuac Mayab — Portal de Proyectos y Triage Inteligente
 * Frontend Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initTrackSelector();
  initFileUpload();
  initFormSubmission();
  loadProjectsDropdown();
  loadRankingsTable();
  initSearchAndFilters();
});

// ==========================================================================
// 1. Tab Navigation
// ==========================================================================
function initTabs() {
  const navButtons = document.querySelectorAll(".nav-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      navButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(pane => pane.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      // If switching to rankings, refresh data
      if (targetId === "tab-rankings") {
        loadRankingsTable();
      }
    });
  });

  // Cross-tab button helper
  const openSparringBtn = document.getElementById("btn-open-sparring-from-form");
  if (openSparringBtn) {
    openSparringBtn.addEventListener("click", () => {
      const sparringNavBtn = document.getElementById("nav-btn-sparring");
      if (sparringNavBtn) sparringNavBtn.click();
    });
  }
}

// ==========================================================================
// 2. Track Selector (2nd Sem vs 4th Sem)
// ==========================================================================
function initTrackSelector() {
  const radioSem2 = document.getElementById("radio-sem2");
  const radioSem4 = document.getElementById("radio-sem4");
  const labelSem2 = document.getElementById("track-label-sem2");
  const labelSem4 = document.getElementById("track-label-sem4");
  const fieldsSem2 = document.getElementById("fields-sem2");
  const fieldsSem4 = document.getElementById("fields-sem4");
  const trackTitle = document.getElementById("track-fields-title");

  function updateTrack(semester) {
    if (semester === 2) {
      labelSem2.classList.add("selected");
      labelSem4.classList.remove("selected");
      fieldsSem2.style.display = "block";
      fieldsSem4.style.display = "none";
      if (trackTitle) trackTitle.textContent = "Entregable de 2do Semestre: Feria de Prototipos";
    } else {
      labelSem4.classList.add("selected");
      labelSem2.classList.remove("selected");
      fieldsSem2.style.display = "none";
      fieldsSem4.style.display = "block";
      if (trackTitle) trackTitle.textContent = "Entregable de 4to Semestre: Business Model Canvas";
    }
  }

  if (radioSem2 && radioSem4) {
    radioSem2.addEventListener("change", () => updateTrack(2));
    radioSem4.addEventListener("change", () => updateTrack(4));
  }
}

// ==========================================================================
// 3. File Upload Drag & Drop Handling
// ==========================================================================
let currentSelectedFile = null;

function initFileUpload() {
  const dropzone = document.getElementById("upload-dropzone");
  const fileInput = document.getElementById("file_upload");
  const previewCard = document.getElementById("file-preview-card");
  const previewName = document.getElementById("preview-file-name");
  const previewSize = document.getElementById("preview-file-size");
  const previewIcon = document.getElementById("preview-file-icon");
  const btnRemove = document.getElementById("btn-remove-file");

  if (!dropzone || !fileInput) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  function handleFileSelected(file) {
    const maxBytes = 52428800; // 50 MB
    if (file.size > maxBytes) {
      showToast("El archivo excede el límite máximo de 50 MB.", "error");
      return;
    }

    currentSelectedFile = file;
    if (previewName) previewName.textContent = file.name;
    if (previewSize) previewSize.textContent = formatBytes(file.size);

    // Update icon based on extension
    const ext = file.name.split('.').pop().toLowerCase();
    if (previewIcon) {
      previewIcon.className = "file-icon fa-solid ";
      if (ext === 'pdf') previewIcon.classList.add('fa-file-pdf');
      else if (['ppt', 'pptx'].includes(ext)) previewIcon.classList.add('fa-file-powerpoint');
      else if (['png', 'jpg', 'jpeg'].includes(ext)) previewIcon.classList.add('fa-file-image');
      else if (ext === 'zip') previewIcon.classList.add('fa-file-zipper');
      else previewIcon.classList.add('fa-file');
    }

    if (previewCard) previewCard.style.display = "flex";
    showToast(`Archivo adjuntado: ${file.name}`, "info");
  }

  if (btnRemove) {
    btnRemove.addEventListener("click", () => {
      currentSelectedFile = null;
      fileInput.value = "";
      if (previewCard) previewCard.style.display = "none";
      showToast("Archivo removido.", "info");
    });
  }
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ==========================================================================
// 4. Form Submission to Backend API
// ==========================================================================
function initFormSubmission() {
  const form = document.getElementById("submission-form");
  const submitBtn = document.getElementById("btn-submit-project");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const teamName = document.getElementById("team_name").value.trim();
    const projectTitle = document.getElementById("project_title").value.trim();
    const members = document.getElementById("members").value.trim();
    const videoUrl = document.getElementById("video_pitch_url").value.trim();
    const semester = document.querySelector('input[name="semester"]:checked').value;

    if (!teamName || !projectTitle || !videoUrl) {
      showToast("Por favor completa los campos obligatorios.", "error");
      return;
    }

    // Build FormData
    const formData = new FormData();
    formData.append("team_name", teamName);
    formData.append("team_id", document.getElementById("team_id").value.trim());
    formData.append("project_title", projectTitle);
    formData.append("members", members);
    formData.append("semester", semester);
    formData.append("video_pitch_url", videoUrl);

    if (semester === "2") {
      formData.append("prototype_type", document.getElementById("prototype_type").value);
      formData.append("target_user", document.getElementById("target_user").value.trim());
      formData.append("prototype_description", document.getElementById("prototype_description").value.trim());
    } else {
      formData.append("value_proposition", document.getElementById("value_proposition").value.trim());
      formData.append("customer_segments", document.getElementById("customer_segments").value.trim());
      formData.append("revenue_streams", document.getElementById("revenue_streams").value.trim());
      formData.append("cost_structure", document.getElementById("cost_structure").value.trim());
    }

    if (currentSelectedFile) {
      formData.append("file", currentSelectedFile);
    }

    // Loading UI
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Registrando entrega...';

    try {
      const resp = await fetch("/api/submit-project", {
        method: "POST",
        body: formData
      });

      const data = await resp.json();

      if (resp.ok && data.success) {
        showReceiptModal(data.receipt);
        form.reset();
        currentSelectedFile = null;
        const previewCard = document.getElementById("file-preview-card");
        if (previewCard) previewCard.style.display = "none";
        loadProjectsDropdown();
      } else {
        showToast(data.detail || "Error al procesar entrega.", "error");
      }
    } catch (err) {
      console.error(err);
      showToast("Error de conexión con el servidor Hetzner.", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Registrar y Enviar Proyecto Oficialmente';
    }
  });

  // Pitch preview button
  const previewPitchBtn = document.getElementById("btn-preview-pitch");
  if (previewPitchBtn) {
    previewPitchBtn.addEventListener("click", () => {
      const url = document.getElementById("video_pitch_url").value.trim();
      if (!url) {
        showToast("Ingresa un enlace de video primero.", "error");
        return;
      }
      window.open(url, "_blank");
    });
  }
}

function showReceiptModal(receipt) {
  document.getElementById("receipt-folio").textContent = receipt.folio;
  document.getElementById("receipt-team").textContent = receipt.team_name;
  document.getElementById("receipt-track").textContent = receipt.track;
  document.getElementById("receipt-file").textContent = receipt.file_name || "Sin archivo adjunto";
  document.getElementById("receipt-date").textContent = receipt.timestamp;

  const modal = document.getElementById("submission-modal");
  if (modal) modal.classList.add("active");
}

function closeModal() {
  const modal = document.getElementById("submission-modal");
  if (modal) modal.classList.remove("active");
}

function closeModalAndGoToSparring() {
  closeModal();
  const sparringNavBtn = document.getElementById("nav-btn-sparring");
  if (sparringNavBtn) sparringNavBtn.click();
}

// ==========================================================================
// 5. Avatar Sparring (Dynamic Live Daily.co Rooms & Group Calling)
// ==========================================================================
// ==========================================================================
// 5. Avatar Sparring (Dynamic Live Daily.co Rooms & Interactive Studio)
// ==========================================================================
const activeLiveRooms = {
  mateo: null,
  luna: null
};

let currentAvatarInSession = "mateo";
let studentStream = null;
let pitchTimerInterval = null;
let pitchRemainingSeconds = 180;
let sessionTimerInterval = null;
let sessionSecondsRemaining = 3600;

async function launchSparringSession(avatar = "mateo", isGroupCopyOnly = false, forceNew = true) {
  currentAvatarInSession = avatar;
  const btnSolo = document.getElementById(avatar === "mateo" ? "btn-join-mateo-solo" : "btn-join-luna-solo");
  const origHtml = btnSolo ? btnSolo.innerHTML : "";

  if (btnSolo && !isGroupCopyOnly) {
    btnSolo.disabled = true;
    btnSolo.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Conectando con Avatar...';
  }

  try {
    const res = await fetch("/api/sparring/launch-room", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ avatar: avatar, force_new: forceNew })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      activeLiveRooms[avatar] = data.daily_url || data.conversation_url;

      const hintEl = document.getElementById(avatar === "mateo" ? "room-hint-mateo" : "room-hint-luna");
      if (hintEl && activeLiveRooms[avatar]) {
        hintEl.innerHTML = `<i class="fa-solid fa-circle-check" style="color: #00C853;"></i> <strong>Sala en vivo lista:</strong> <a href="${activeLiveRooms[avatar]}" target="_blank" style="color: var(--anahuac-orange); text-decoration: underline;">${activeLiveRooms[avatar]}</a>`;
      }

      if (isGroupCopyOnly) {
        const linkToCopy = activeLiveRooms[avatar] || window.location.origin + `/?tab=sparring&avatar=${avatar}`;
        await navigator.clipboard.writeText(linkToCopy);
        showToast("¡Enlace de videollamada copiado al portapapeles! Ya puedes compartirlo con tu equipo.", "success");
      } else {
        showToast("¡Cabina activada! Abriendo pantalla de videollamada...", "success");
        // Bring up the video screen directly on page!
        openStudioBooth(data, avatar);
      }
    } else {
      showToast(data.detail || "Error al conectar con el avatar.", "error");
    }
  } catch (err) {
    console.error("Error launching avatar room:", err);
    showToast("Error de conexión al generar la sala del avatar.", "error");
  } finally {
    if (btnSolo && !isGroupCopyOnly) {
      btnSolo.disabled = false;
      btnSolo.innerHTML = origHtml;
    }
  }
}

function restartCurrentAvatarRoom() {
  showToast("Generando sala nueva con voz y parámetros actualizados...", "info");
  launchSparringSession(currentAvatarInSession, false, true);
}

async function copyLiveRoomLink(avatar = "mateo") {
  if (activeLiveRooms[avatar]) {
    try {
      await navigator.clipboard.writeText(activeLiveRooms[avatar]);
      showToast("¡Enlace de la sala en vivo copiado! Compártelo con tu equipo.", "success");
      return;
    } catch (e) {
      prompt("Copia este enlace para tu equipo:", activeLiveRooms[avatar]);
      return;
    }
  }

  // If no room generated yet, request room (reusing active if available) and copy
  await launchSparringSession(avatar, true, false);
}

function openStudioBooth(data, avatar = "mateo") {
  const container = document.getElementById("embedded-room-container");
  const titleEl = document.getElementById("room-active-title");
  const speechNameEl = document.getElementById("speech-avatar-name");
  const speechTextEl = document.getElementById("avatar-speech-text");
  const videoPlayer = document.getElementById("avatar-video-player");
  const dailyFrame = document.getElementById("avatar-daily-frame");
  const linkInput = document.getElementById("external-room-link-input");
  const openTabBtn = document.getElementById("btn-open-external-tab");

  const isMateo = (avatar === "mateo");

  if (titleEl) {
    titleEl.textContent = isMateo 
      ? "Cabina Activa: Mateo (Coach Socrático de Validación y Negocios)" 
      : "Active Studio: Prof. Luna (Global Pitch Judge & VC Mentor)";
  }

  if (speechNameEl) speechNameEl.textContent = isMateo ? "Mateo:" : "Prof. Luna:";
  
  const greeting = data.greeting || (isMateo
    ? "¡Hola! Soy Mateo, tu mentor socrático de Anáhuac Mayab. Comienza tu pitch de 3 minutos cuando estés listo; te escucharé atentamente y te haré preguntas sobre tus supuestos de mercado y validación empírica."
    : "Welcome to your pitch sparring session! I am Professor Luna. Deliver your 3-minute venture presentation, and I will challenge your market assumptions, competitive defensibility, and international scalability. Ready when you are!"
  );

  if (speechTextEl) speechTextEl.textContent = greeting;

  // Set avatar video feed
  if (videoPlayer && data.video_url) {
    videoPlayer.src = data.video_url;
    videoPlayer.poster = data.image_url || "";
    videoPlayer.play().catch(e => console.log("Autoplay policy prevented audio, video will loop silently:", e));
  }

  // Set Daily frame if active Daily room returned
  const roomUrl = data.daily_url || data.conversation_url || (window.location.origin + `/?tab=sparring&avatar=${avatar}`);
  if (dailyFrame && data.daily_url) {
    dailyFrame.src = data.daily_url;
    switchStudioMode('daily');
  } else {
    switchStudioMode('socratic');
  }
  if (linkInput) linkInput.value = roomUrl;
  if (openTabBtn) openTabBtn.href = roomUrl;

  // Show container with animation
  if (container) {
    container.style.display = "block";
    setTimeout(() => {
      container.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 150);
  }

  // Start Session Countdown Timer (1 Hour)
  startSessionTimer();

  // Reset Pitch Timer
  resetPitchTimer();

  // Log in transcript
  addTranscriptMessage("avatar", `<strong>${isMateo ? 'Mateo' : 'Prof. Luna'}:</strong> ${greeting}`);

  // Only speak browser TTS and activate camera if in local socratic booth mode
  if (!data.daily_url) {
    speakText(greeting, data.lang || (isMateo ? "es-MX" : "en-US"));
    activateWebcam();
  } else {
    // In Daily call mode, ensure parent audio is completely silent so Daily.co has exclusive microphone and speaker AEC
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    if (videoPlayer) videoPlayer.muted = true;
  }
}

function switchStudioMode(mode = 'daily') {
  const btnDaily = document.getElementById("btn-tab-daily");
  const btnSocratic = document.getElementById("btn-tab-socratic");
  const viewDaily = document.getElementById("view-daily-call");
  const viewSocratic = document.getElementById("view-socratic-booth");
  const videoPlayer = document.getElementById("avatar-video-player");

  if (mode === 'daily') {
    if (btnDaily) btnDaily.classList.add("active");
    if (btnSocratic) btnSocratic.classList.remove("active");
    if (viewDaily) viewDaily.style.display = "block";
    if (viewSocratic) viewSocratic.style.display = "none";

    // Silence parent window so Daily.co WebRTC stream has 100% exclusive audio & mic
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    if (videoPlayer) videoPlayer.muted = true;
  } else {
    if (btnSocratic) btnSocratic.classList.add("active");
    if (btnDaily) btnDaily.classList.remove("active");
    if (viewDaily) viewDaily.style.display = "none";
    if (viewSocratic) viewSocratic.style.display = "block";

    // Activate camera preview for Socratic booth
    activateWebcam();
  }
}

function startSessionTimer() {
  if (sessionTimerInterval) clearInterval(sessionTimerInterval);
  sessionSecondsRemaining = 3600;
  updateSessionTimerDisplay();

  sessionTimerInterval = setInterval(() => {
    sessionSecondsRemaining--;
    updateSessionTimerDisplay();
    if (sessionSecondsRemaining <= 0) {
      clearInterval(sessionTimerInterval);
      showToast("La sesión de 1 hora ha concluido. Puedes iniciar una nueva en cualquier momento.", "info");
    }
  }, 1000);
}

function updateSessionTimerDisplay() {
  const timerEl = document.getElementById("room-session-timer");
  if (!timerEl) return;
  const mins = Math.floor(sessionSecondsRemaining / 60);
  const secs = sessionSecondsRemaining % 60;
  timerEl.innerHTML = `<i class="fa-regular fa-clock"></i> Sesión: ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

async function triggerSocraticChallenge(category = "prototype") {
  const speechTextEl = document.getElementById("avatar-speech-text");
  const speechNameEl = document.getElementById("speech-avatar-name");
  const isMateo = (currentAvatarInSession === "mateo");

  if (speechTextEl) speechTextEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generando desafío con Qwen 2.5 en clúster Titan...';

  try {
    const sem = document.querySelector('input[name="semester"]:checked')?.value || 2;
    const projectTitle = document.getElementById("project_title")?.value || "Proyecto Estudiantil Anáhuac";

    const resp = await fetch("/api/sparring/socratic-question", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        avatar: currentAvatarInSession,
        semester: parseInt(sem),
        category: category,
        project_title: projectTitle
      })
    });

    const data = await resp.json();
    const question = data.question;

    if (speechNameEl) speechNameEl.textContent = isMateo ? "Mateo:" : "Prof. Luna:";
    if (speechTextEl) speechTextEl.textContent = question;

    addTranscriptMessage("avatar", `<strong>${isMateo ? 'Mateo' : 'Prof. Luna'}:</strong> ${question}`);
    speakText(question, isMateo ? "es-MX" : "en-US");
  } catch (err) {
    console.error("Error generating question:", err);
    const fallbackQ = isMateo 
      ? "¿Cómo validaron este prototipo con usuarios reales y qué falló en la primera prueba?"
      : "What is your defensible technological moat against well-funded incumbents?";
    if (speechTextEl) speechTextEl.textContent = fallbackQ;
    speakText(fallbackQ, isMateo ? "es-MX" : "en-US");
  }
}

function getBestVoiceForLang(langCode) {
  if (!('speechSynthesis' in window)) return null;
  const voices = window.speechSynthesis.getVoices();
  if (!voices || voices.length === 0) return null;
  const prefix = langCode.substring(0, 2).toLowerCase();
  let match = voices.find(v => v.lang && v.lang.toLowerCase() === langCode.toLowerCase());
  if (!match) {
    match = voices.find(v => v.lang && v.lang.toLowerCase().startsWith(prefix));
  }
  if (!match && prefix === 'es') {
    match = voices.find(v => v.name && /spanish|español|mexic|sabina|jorge|paulina|helena|raul/i.test(v.name));
  }
  return match || null;
}

// Pre-warm voices list on supported browsers
if (typeof window !== "undefined" && 'speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
  };
}

function speakText(text, lang = "es-MX") {
  if (!('speechSynthesis' in window)) return;
  try {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    const voice = getBestVoiceForLang(lang);
    if (voice) {
      utterance.voice = voice;
    }
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  } catch (e) {
    console.log("Speech synthesis note:", e);
  }
}

async function activateWebcam() {
  const videoEl = document.getElementById("student-webcam-preview");
  const fallbackEl = document.getElementById("student-cam-fallback");

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    studentStream = stream;
    if (videoEl) {
      videoEl.srcObject = stream;
      videoEl.style.display = "block";
    }
    if (fallbackEl) fallbackEl.style.display = "none";
    showToast("Cámara web del estudiante conectada.", "success");
  } catch (err) {
    console.log("Webcam access optional/declined:", err);
    if (videoEl) videoEl.style.display = "none";
    if (fallbackEl) fallbackEl.style.display = "flex";
  }
}

function toggleCamera() {
  if (studentStream) {
    const vTrack = studentStream.getVideoTracks()[0];
    if (vTrack) {
      vTrack.enabled = !vTrack.enabled;
      const btn = document.getElementById("btn-toggle-cam");
      if (btn) btn.classList.toggle("active", !vTrack.enabled);
      showToast(vTrack.enabled ? "Cámara encendida." : "Cámara apagada.", "info");
    }
  } else {
    activateWebcam();
  }
}

function toggleMic() {
  if (studentStream) {
    const aTrack = studentStream.getAudioTracks()[0];
    if (aTrack) {
      aTrack.enabled = !aTrack.enabled;
      const btn = document.getElementById("btn-toggle-mic");
      if (btn) btn.classList.toggle("active", !aTrack.enabled);
      showToast(aTrack.enabled ? "Micrófono activado." : "Micrófono silenciado.", "info");
    }
  } else {
    showToast("Micrófono no conectado aún.", "info");
  }
}

function startPitchTimer() {
  const startBtn = document.getElementById("btn-pitch-start");
  if (pitchTimerInterval) {
    // Pause
    clearInterval(pitchTimerInterval);
    pitchTimerInterval = null;
    if (startBtn) {
      startBtn.innerHTML = '<i class="fa-solid fa-play"></i> Reanudar Pitch';
      startBtn.classList.remove("running");
    }
    return;
  }

  if (startBtn) {
    startBtn.innerHTML = '<i class="fa-solid fa-pause"></i> Pausar Pitch';
    startBtn.classList.add("running");
  }

  addTranscriptMessage("system", "Temporizador de pitch iniciado (03:00). Comienza tu exposición.");

  pitchTimerInterval = setInterval(() => {
    pitchRemainingSeconds--;
    updatePitchTimerDisplay();
    if (pitchRemainingSeconds <= 0) {
      clearInterval(pitchTimerInterval);
      pitchTimerInterval = null;
      if (startBtn) {
        startBtn.innerHTML = '<i class="fa-solid fa-play"></i> Iniciar Pitch (3 Min)';
        startBtn.classList.remove("running");
      }
      showToast("¡Tiempo cumplido! El avatar formulará una pregunta socrática.", "info");
      triggerSocraticChallenge("prototype");
    }
  }, 1000);
}

function resetPitchTimer() {
  if (pitchTimerInterval) {
    clearInterval(pitchTimerInterval);
    pitchTimerInterval = null;
  }
  pitchRemainingSeconds = 180;
  const startBtn = document.getElementById("btn-pitch-start");
  if (startBtn) {
    startBtn.innerHTML = '<i class="fa-solid fa-play"></i> Iniciar Pitch (3 Min)';
    startBtn.classList.remove("running");
  }
  updatePitchTimerDisplay();
}

function updatePitchTimerDisplay() {
  const display = document.getElementById("pitch-timer-display");
  const fill = document.getElementById("pitch-progress-fill");
  if (!display) return;
  const mins = Math.floor(pitchRemainingSeconds / 60);
  const secs = pitchRemainingSeconds % 60;
  display.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  if (pitchRemainingSeconds <= 30) {
    display.classList.add("warning");
  } else {
    display.classList.remove("warning");
  }
  if (fill) {
    const pct = (pitchRemainingSeconds / 180) * 100;
    fill.style.width = `${pct}%`;
  }
}

function toggleFullscreenStudio() {
  const container = document.getElementById("embedded-room-container");
  if (!document.fullscreenElement) {
    if (container && container.requestFullscreen) {
      container.requestFullscreen().catch(() => {});
    }
  } else {
    if (document.exitFullscreen) document.exitFullscreen();
  }
}

function closeEmbeddedRoom() {
  const container = document.getElementById("embedded-room-container");
  if (container) container.style.display = "none";

  // Completely unhook the Daily iframe so it leaves the WebRTC call immediately
  const dailyFrame = document.getElementById("avatar-daily-frame");
  if (dailyFrame) {
    dailyFrame.src = "about:blank";
  }

  // Notify server to end Tavus room and evict cache
  const closedAvatar = currentAvatarInSession;
  fetch("/api/sparring/end-room", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ avatar: closedAvatar })
  }).catch(e => console.log("End room note:", e));

  activeLiveRooms[closedAvatar] = null;

  if (studentStream) {
    studentStream.getTracks().forEach(t => t.stop());
    studentStream = null;
  }
  const videoEl = document.getElementById("student-webcam-preview");
  if (videoEl) videoEl.style.display = "none";
  const fallbackEl = document.getElementById("student-cam-fallback");
  if (fallbackEl) fallbackEl.style.display = "flex";

  resetPitchTimer();
  if (sessionTimerInterval) clearInterval(sessionTimerInterval);
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
}

function toggleDailyAccordion() {
  const body = document.getElementById("daily-accordion-body");
  const icon = document.getElementById("daily-accordion-icon");
  if (!body) return;
  if (body.style.display === "none") {
    body.style.display = "block";
    if (icon) icon.className = "fa-solid fa-chevron-up accordion-icon";
  } else {
    body.style.display = "none";
    if (icon) icon.className = "fa-solid fa-chevron-down accordion-icon";
  }
}

function copyExternalInputLink() {
  const input = document.getElementById("external-room-link-input");
  if (!input) return;
  navigator.clipboard.writeText(input.value).then(() => {
    showToast("¡Enlace copiado al portapapeles!", "success");
  });
}

function addTranscriptMessage(type, text) {
  const stream = document.getElementById("transcript-stream");
  if (!stream) return;
  const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const div = document.createElement("div");
  div.className = `transcript-msg msg-${type}`;
  div.innerHTML = `<span class="time">[${now}]</span> ${text}`;
  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
}

function clearTranscript() {
  const stream = document.getElementById("transcript-stream");
  if (stream) stream.innerHTML = '<div class="transcript-msg msg-system"><span class="time">[Reinicio]</span> Bitácora limpia.</div>';
}

// ==========================================================================
// 6. Panel de 5 Jueces: Precheck Evaluation
// ==========================================================================
async function loadProjectsDropdown() {
  const select = document.getElementById("select-project-for-eval");
  if (!select) return;

  try {
    const res = await fetch("/api/projects");
    const projects = await res.json();

    select.innerHTML = '<option value="">-- Selecciona un proyecto para simular jurado --</option>';
    projects.forEach(p => {
      const opt = document.createElement("option");
      opt.value = p.team_id;
      opt.textContent = `[${p.team_id}] ${p.team_name} - ${p.project_title.substring(0, 45)}...`;
      select.appendChild(opt);
    });
  } catch (e) {
    console.error("Error loading projects list:", e);
  }
}

const runPrecheckBtn = document.getElementById("btn-run-precheck");
if (runPrecheckBtn) {
  runPrecheckBtn.addEventListener("click", async () => {
    const select = document.getElementById("select-project-for-eval");
    const teamId = select.value;
    if (!teamId) {
      showToast("Selecciona un proyecto de la lista.", "error");
      return;
    }

    runPrecheckBtn.disabled = true;
    runPrecheckBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Evaluando con 5 Jueces Sintéticos...';

    const resultsArea = document.getElementById("precheck-results-area");
    const scoresGrid = document.getElementById("precheck-scores-grid");
    const metaBox = document.getElementById("precheck-meta-verdict");

    try {
      const resp = await fetch(`/api/eval-precheck/${teamId}`);
      const evalData = await resp.json();

      if (resp.ok) {
        scoresGrid.innerHTML = "";
        evalData.individual_judges.forEach(j => {
          const card = document.createElement("div");
          card.className = "score-badge-card";
          card.innerHTML = `
            <div class="score-badge-header">${j.role}</div>
            <div class="score-badge-num">${j.score}/100</div>
            <div class="score-badge-comment">${j.feedback}</div>
          `;
          scoresGrid.appendChild(card);
        });

        metaBox.innerHTML = `
          <h4><i class="fa-solid fa-stamp"></i> Dictamen Colegiado del Comité (Promedio: ${evalData.mean_score}/100)</h4>
          <p>${evalData.meta_verdict}</p>
        `;

        resultsArea.style.display = "block";
        resultsArea.scrollIntoView({ behavior: "smooth" });
        showToast("Evaluación colegiada completada exitosamente.", "success");
      } else {
        showToast("Error al evaluar el proyecto.", "error");
      }
    } catch (err) {
      console.error(err);
      showToast("Error de conexión durante la evaluación.", "error");
    } finally {
      runPrecheckBtn.disabled = false;
      runPrecheckBtn.innerHTML = '<i class="fa-solid fa-play"></i> Ejecutar 5 Jueces Sintéticos';
    }
  });
}

// ==========================================================================
// 8. Tablero de Calificaciones (Top 50 Rankings)
// ==========================================================================
let allRankedTeamsCache = [];

async function loadRankingsTable() {
  const tbody = document.getElementById("rankings-table-body");
  if (!tbody) return;

  try {
    const resp = await fetch("/api/rankings");
    const data = await resp.json();

    allRankedTeamsCache = data.all_ranked_teams || [];

    // Update Metric Cards
    if (data.cohort_stats) {
      document.getElementById("metric-total-teams").textContent = data.cohort_stats.total_teams;
      document.getElementById("metric-mean-score").textContent = data.cohort_stats.total_teams > 0 
        ? data.cohort_stats.raw_mean + "/100" 
        : "--";
      document.getElementById("metric-cutoff-score").textContent = data.cohort_stats.total_teams > 0 
        ? data.cohort_stats.cutoff_score + "/100" 
        : "--";
    }

    renderTableRows(allRankedTeamsCache);
  } catch (err) {
    console.error("Error loading rankings:", err);
    tbody.innerHTML = `<tr><td colspan="9" class="td-loading" style="color: #B71C1C;">Error al cargar las calificaciones.</td></tr>`;
  }
}

function renderTableRows(teams) {
  const tbody = document.getElementById("rankings-table-body");
  if (!tbody) return;

  if (teams.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="td-loading">No se encontraron proyectos para los filtros seleccionados.</td></tr>`;
    return;
  }

  tbody.innerHTML = "";
  teams.forEach(t => {
    const tr = document.createElement("tr");

    let rankClass = "rank-pill";
    if (t.rank === 1) rankClass += " rank-top1";
    else if (t.rank === 2) rankClass += " rank-top2";
    else if (t.rank === 3) rankClass += " rank-top3";

    let statusBadge = t.is_finalist 
      ? '<span class="status-badge-finalist"><i class="fa-solid fa-award"></i> Top 50 Finalista</span>'
      : '<span class="status-badge-standard">Participante</span>';

    if (t.is_borderline) {
      statusBadge = '<span class="status-badge-borderline"><i class="fa-solid fa-triangle-exclamation"></i> Zona Fronteriza</span>';
    }

    const trackLabel = t.semester === 2 ? '2° Sem (Prototipos)' : '4° Sem (BMC)';

    tr.innerHTML = `
      <td><span class="${rankClass}">#${t.rank}</span></td>
      <td><strong>${t.team_id}</strong></td>
      <td>${t.team_name}</td>
      <td><span class="track-badge ${t.semester === 2 ? 'badge-orange' : 'badge-charcoal'}">${trackLabel}</span></td>
      <td>${t.project_title.substring(0, 48)}...</td>
      <td><strong>${t.raw_mean_score.toFixed(1)}</strong></td>
      <td><strong style="color: var(--anahuac-orange);">${t.calibrated_score.toFixed(1)}</strong></td>
      <td>${statusBadge}</td>
      <td>
        <a href="/api/dossier/${t.team_id}" target="_blank" class="btn-view-dossier" title="Ver Ficha Ejecutiva de 1 Página">
          <i class="fa-solid fa-file-invoice"></i> Dossier
        </a>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function initSearchAndFilters() {
  const searchInput = document.getElementById("ranking-search");
  const trackFilter = document.getElementById("ranking-filter-track");

  function applyFilters() {
    const term = (searchInput ? searchInput.value : "").toLowerCase().trim();
    const filter = trackFilter ? trackFilter.value : "all";

    const filtered = allRankedTeamsCache.filter(t => {
      const matchSearch = t.team_name.toLowerCase().includes(term) ||
                          t.project_title.toLowerCase().includes(term) ||
                          t.team_id.toLowerCase().includes(term);

      if (!matchSearch) return false;

      if (filter === "2") return t.semester === 2;
      if (filter === "4") return t.semester === 4;
      if (filter === "finalists") return t.is_finalist;
      return true;
    });

    renderTableRows(filtered);
  }

  if (searchInput) searchInput.addEventListener("input", applyFilters);
  if (trackFilter) trackFilter.addEventListener("change", applyFilters);
}

// ==========================================================================
// 8. Toast Helper
// ==========================================================================
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  
  let icon = "fa-circle-info";
  if (type === "success") icon = "fa-circle-check";
  else if (type === "error") icon = "fa-triangle-exclamation";

  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}
