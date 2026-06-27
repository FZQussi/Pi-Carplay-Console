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

// Placeholder da capa: varia por música (cor + emoji), em vez de ser
// sempre igual quando não há capa disponível.
const PLACEHOLDER_EMOJIS = ["🎵", "🎶", "🎷", "🎸", "🎹", "🎺", "🥁", "🪕", "🎻", "📻"];

function hashText(text) {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
        hash = text.charCodeAt(i) + ((hash << 5) - hash);
    }
    return hash;
}

function generateGradient(hash) {
    const h1 = Math.abs(hash % 360);
    const h2 = (h1 + 40) % 360;
    return `linear-gradient(135deg, hsl(${h1},60%,25%), hsl(${h2},60%,15%))`;
}

function pickPlaceholderEmoji(hash) {
    const index = Math.abs(hash) % PLACEHOLDER_EMOJIS.length;
    return PLACEHOLDER_EMOJIS[index];
}

// Letras
let lyricsLines = [];   // [{ time: segundos, text: "..." }, ...] (vazio se não sincronizado)
let currentLyricIndex = -1;

function parseLRC(lrc) {
    const lines = [];
    const regex = /\[(\d{2}):(\d{2}(?:\.\d{1,3})?)\]\s*(.*)/;
    lrc.split("\n").forEach(line => {
        const match = line.match(regex);
        if (match) {
            const minutes = parseInt(match[1], 10);
            const seconds = parseFloat(match[2]);
            const text = match[3].trim();
            if (text) lines.push({ time: minutes * 60 + seconds, text });
        }
    });
    return lines;
}

function renderLyricsPlaceholder(msg) {
    const container = document.getElementById("lyrics-container");
    if (container) container.innerHTML = `<div class="lyrics-line">${msg}</div>`;
}

async function loadLyrics(artist, track) {
    lyricsLines = [];
    currentLyricIndex = -1;
    renderLyricsPlaceholder("🎤 A procurar letra...");

    try {
        const url = `/music/lyrics?artist=${encodeURIComponent(artist)}&track=${encodeURIComponent(track)}`;
        const res = await fetch(url);
        if (!res.ok) {
            console.error("Erro HTTP ao obter letra:", res.status, res.statusText);
            renderLyricsPlaceholder("🎤 Letra não disponível");
            return;
        }

        const data = await res.json();
        if (data.error) console.error("Erro do servidor ao obter letra:", data.error);

        const container = document.getElementById("lyrics-container");
        if (!container) return;

        if (data.synced) {
            lyricsLines = parseLRC(data.synced);
            container.innerHTML = lyricsLines
                .map((l, i) => `<div class="lyrics-line" data-index="${i}">${l.text}</div>`)
                .join("");
        } else if (data.plain) {
            container.innerHTML = data.plain
                .split("\n")
                .map(line => `<div class="lyrics-line">${line}</div>`)
                .join("");
        } else {
            renderLyricsPlaceholder("🎤 Letra não disponível");
        }
    } catch (e) {
        console.error("Erro ao obter letra (fetch/parse):", e);
        renderLyricsPlaceholder("🎤 Letra não disponível");
    }
}

function updateActiveLyric() {
    if (lyricsLines.length === 0) return;

    let newIndex = -1;
    for (let i = 0; i < lyricsLines.length; i++) {
        if (trackPosition >= lyricsLines[i].time) newIndex = i;
        else break;
    }

    if (newIndex !== currentLyricIndex) {
        const container = document.getElementById("lyrics-container");
        if (!container) return;

        const prev = container.querySelector(".lyrics-line.active");
        if (prev) prev.classList.remove("active");

        if (newIndex >= 0) {
            const current = container.querySelector(`.lyrics-line[data-index="${newIndex}"]`);
            if (current) {
                current.classList.add("active");
                current.scrollIntoView({ behavior: "smooth", block: "center" });
            }
        }
        currentLyricIndex = newIndex;
    }
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

        if (bt.playing) {
            document.getElementById("track").innerText = bt.track || "--";
            document.getElementById("artist").innerText = bt.artist || "--";
            document.getElementById("play-btn").innerText = "⏸";
            isPlaying = true;

            if (bt.track && bt.track !== lastTrack) {
                lastTrack = bt.track;
                trackPosition = 0;
                trackDuration = bt.duration || 0;

                // Placeholder enquanto não há capa: cor + emoji variam por música
                const hash = hashText(bt.track + bt.artist);
                albumArt.style.background = generateGradient(hash);
                albumArt.innerHTML = pickPlaceholderEmoji(hash);

                // Vai buscar capa (iTunes Search API)
                fetch(`/music/cover?artist=${encodeURIComponent(bt.artist || "")}&track=${encodeURIComponent(bt.track)}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.cover) {
                            albumArt.innerHTML = `<img src="${data.cover}" style="width:100%;height:100%;object-fit:cover;border-radius:20px;">`;
                        }
                        if (data.error) console.error("Erro ao obter capa:", data.error);
                    })
                    .catch(e => console.error("Erro ao obter capa (fetch):", e));

                // Vai buscar a letra (LRCLIB)
                loadLyrics(bt.artist || "", bt.track);
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

// Progresso (mantido para sincronizar a letra com o tempo da música)
setInterval(() => {
    if (isPlaying) {
        trackPosition = Math.min(trackPosition + 1.2, trackDuration > 0 ? trackDuration / 1000000 : 300);
        updateActiveLyric();
    }
}, 1000);

// Controlos
async function togglePlay() {
    // Atualização otimista: muda já o ícone, em vez de esperar pelo
    // round-trip do Bluetooth (telemóvel demora a confirmar).
    isPlaying = !isPlaying;
    document.getElementById("play-btn").innerText = isPlaying ? "⏸" : "▶";

    if (isPlaying) {
        await fetch("/music/play", { method: "POST" });
    } else {
        await fetch("/music/pause", { method: "POST" });
    }

    // Confirma com o estado real passado algum tempo, para dar
    // espaço à propagação via Bluetooth (e corrigir se algo falhou).
    setTimeout(loadStatus, 800);
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