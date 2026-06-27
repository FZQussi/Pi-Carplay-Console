// Navegação
function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
    document.getElementById(id).classList.remove('hidden');
}

// Relógio
function updateClock() {
    const now = new Date();
    document.getElementById("time").innerText =
        now.getHours().toString().padStart(2,'0') + ":" +
        now.getMinutes().toString().padStart(2,'0');
}
setInterval(updateClock, 1000);
updateClock();

// Estado da música
let isPlaying = false;
let trackPosition = 0;
let trackDuration = 0;

function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2,'0')}`;
}

// Atualizar estado do backend
async function loadStatus() {
    try {
        const res = await fetch("/status");
        const data = await res.json();
        const bt = data.bluetooth;

        // Barra de topo
        document.getElementById("bt-status").innerHTML = bt.connected
            ? `🔵 ${bt.device}` : "⚫ Sem Bluetooth";

        // Settings
        if (document.getElementById("bt-device-name")) {
            document.getElementById("bt-device-name").innerText =
                bt.device || "--";
        }

        // Música
        if (bt.playing && bt.track) {
            document.getElementById("track").innerText = bt.track;
            document.getElementById("artist").innerText = bt.artist || "--";
            document.getElementById("play-btn").innerText = "⏸";
            isPlaying = true;
        } else {
            document.getElementById("track").innerText = bt.connected ? "Em pausa" : "--";
            document.getElementById("artist").innerText = bt.connected ? bt.device : "--";
            document.getElementById("play-btn").innerText = "▶";
            isPlaying = false;
        }
    } catch (e) {
        console.error("Erro ao carregar status:", e);
    }
}

setInterval(loadStatus, 2000);
loadStatus();

// Simular progresso da barra (atualiza a cada segundo)
setInterval(() => {
    if (isPlaying) {
        trackPosition = Math.min(trackPosition + 1, trackDuration || 300);
        const pct = trackDuration > 0 ? (trackPosition / trackDuration) * 100 : 0;
        document.getElementById("progress-bar").style.width = pct + "%";
        document.getElementById("time-current").innerText = formatTime(trackPosition);
        document.getElementById("time-total").innerText = formatTime(trackDuration || 0);
    }
}, 1000);

// Controlos
async function togglePlay() {
    if (isPlaying) {
        await fetch("/music/pause", { method: "POST" });
    } else {
        await fetch("/music/play", { method: "POST" });
    }
    loadStatus();
}

async function nextTrack() {
    await fetch("/music/next", { method: "POST" });
    trackPosition = 0;
    loadStatus();
}

async function prevTrack() {
    await fetch("/music/prev", { method: "POST" });
    trackPosition = 0;
    loadStatus();
}

async function makeDiscoverable() {
    await fetch("/bluetooth/discoverable", { method: "POST" });
}