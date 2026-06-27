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

// Estado
let isPlaying = false;
let trackPosition = 0;
let trackDuration = 0;
let lastTrack = null;

function formatTime(microseconds) {
    const seconds = Math.floor(microseconds / 1000000);
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2,'0')}`;
}

function generateGradient(text) {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
        hash = text.charCodeAt(i) + ((hash << 5) - hash);
    }
    const h1 = Math.abs(hash % 360);
    const h2 = (h1 + 40) % 360;
    return `linear-gradient(135deg, hsl(${h1},60%,25%), hsl(${h2},60%,15%))`;
}

async function loadStatus() {
    try {
        const res = await fetch("/status");
        const data = await res.json();
        const bt = data.bluetooth;

        document.getElementById("bt-status").innerHTML = bt.connected
            ? `🔵 ${bt.device}` : "⚫ Sem Bluetooth";

        const btDeviceName = document.getElementById("bt-device-name");
        if (btDeviceName) btDeviceName.innerText = bt.device || "--";

        const albumArt = document.getElementById("album-art");

        if (bt.playing && bt.track) {
            document.getElementById("track").innerText = bt.track;
            document.getElementById("artist").innerText = bt.artist || "--";
            document.getElementById("play-btn").innerText = "⏸";
            isPlaying = true;

            if (bt.track !== lastTrack) {
                lastTrack = bt.track;
                trackPosition = 0;
                trackDuration = bt.duration || 0;

                // Gradiente enquanto carrega
                albumArt.style.background = generateGradient(bt.track + bt.artist);
                albumArt.innerHTML = "🎵";

                // Vai buscar capa ao Spotify
                fetch("/music/cover")
                    .then(r => r.json())
                    .then(data => {
                        if (data.cover) {
                            albumArt.innerHTML = `<img src="${data.cover}" style="width:100%;height:100%;object-fit:cover;border-radius:20px;">`;
                        }
                    });
            }
        } else {
            document.getElementById("track").innerText = bt.connected ? "Em pausa" : "--";
            document.getElementById("artist").innerText = bt.connected ? bt.device : "--";
            document.getElementById("play-btn").innerText = "▶";
            albumArt.style.background = "linear-gradient(135deg, #1a1a2e, #16213e)";
            albumArt.innerHTML = "🎵";
            isPlaying = false;
        }
    } catch (e) {
        console.error("Erro ao carregar status:", e);
    }
}

setInterval(loadStatus, 2000);
loadStatus();

// Progresso
setInterval(() => {
    if (isPlaying) {
        trackPosition = Math.min(trackPosition + 1, trackDuration > 0 ? trackDuration / 1000000 : 300);
        const total = trackDuration > 0 ? trackDuration / 1000000 : 0;
        const pct = total > 0 ? (trackPosition / total) * 100 : 0;
        document.getElementById("progress-bar").style.width = pct + "%";
        document.getElementById("time-current").innerText = formatTime(trackPosition * 1000000);
        document.getElementById("time-total").innerText = formatTime(trackDuration);
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