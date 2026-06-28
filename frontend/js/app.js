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
let trackPosition = 0;      // segundos (float), actualizado pelo ticker
let trackDuration = 0;      // segundos (float)
let lastTrack = null;

function formatTime(seconds) {
    const s = Math.floor(seconds);
    const m = Math.floor(s / 60);
    return `${m}:${(s % 60).toString().padStart(2,'0')}`;
}

// Placeholder da capa: varia por música (cor + emoji)
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
let lyricsLines = [];
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
    // Não faz reset do lyricsLines/currentLyricIndex aqui para não
    // interromper a letra que já está a correr enquanto o fetch decorre.
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
            currentLyricIndex = -1;   // reset só quando a letra chegou
            container.innerHTML = lyricsLines
                .map((l, i) => `<div class="lyrics-line" data-index="${i}">${l.text}</div>`)
                .join("");
        } else if (data.plain) {
            lyricsLines = [];
            currentLyricIndex = -1;
            container.innerHTML = data.plain
                .split("\n")
                .map(line => `<div class="lyrics-line">${line}</div>`)
                .join("");
        } else {
            lyricsLines = [];
            currentLyricIndex = -1;
            renderLyricsPlaceholder("🎤 Letra não disponível");
        }
    } catch (e) {
        console.error("Erro ao obter letra (fetch/parse):", e);
        lyricsLines = [];
        currentLyricIndex = -1;
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

function applyStatus(data) {
    try {
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

            // Só usa a posição do servidor se for um valor real (>1s).
            // Se o telemóvel não suportar AVRCP position, o servidor devolve
            // 0 — nesse caso NÃO toca em trackPosition para não interromper
            // a contagem local do ticker.
            const serverPos = (bt.position || 0) / 1_000_000;
            if (serverPos > 1) {
                trackPosition = serverPos;
            }
            trackDuration = (bt.duration || 0) / 1_000_000;

            if (bt.track && bt.track !== lastTrack) {
                lastTrack = bt.track;
                // Música nova: começa sempre do início (ou da posição real
                // se o servidor a tiver devolvido acima).
                if (serverPos <= 1) trackPosition = 0;

                // Placeholder enquanto não há capa
                const hash = hashText(bt.track + bt.artist);
                albumArt.style.background = generateGradient(hash);
                albumArt.innerHTML = pickPlaceholderEmoji(hash);

                // Capa
                fetch(`/music/cover?artist=${encodeURIComponent(bt.artist || "")}&track=${encodeURIComponent(bt.track)}`)
                    .then(r => r.json())
                    .then(coverData => {
                        if (coverData.cover) {
                            albumArt.innerHTML = `<img src="${coverData.cover}" style="width:100%;height:100%;object-fit:cover;border-radius:20px;">`;
                        }
                        if (coverData.error) console.error("Erro ao obter capa:", coverData.error);
                    })
                    .catch(e => console.error("Erro ao obter capa (fetch):", e));

                // Letra
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
        console.error("Erro ao aplicar status:", e);
    }
}

// Fetch pontual de /status — usado como fallback e após comandos.
async function fetchStatus() {
    try {
        const res = await fetch("/status");
        applyStatus(await res.json());
    } catch (e) {
        console.error("Erro ao carregar status:", e);
    }
}

// --- Tempo real via WebSocket, com fallback para polling -------------------
// O caminho normal é o WS: o backend faz push do estado sempre que muda.
// Se o WS cair, ligamos um polling de 2s e tentamos reconectar; quando o
// WS volta, o polling desliga-se para não duplicar carga nos subprocessos.
let ws = null;
let pollTimer = null;

function startPolling() {
    if (pollTimer) return;
    fetchStatus();
    pollTimer = setInterval(fetchStatus, 2000);
}

function stopPolling() {
    if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
    }
}

function connectWS() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    ws = new WebSocket(`${proto}://${location.host}/ws`);

    ws.onmessage = (ev) => {
        stopPolling();                 // WS vivo: dispensa o polling
        try {
            applyStatus(JSON.parse(ev.data));
        } catch (e) {
            console.error("Erro a processar mensagem WS:", e);
        }
    };

    ws.onclose = () => {
        startPolling();                // fallback enquanto o WS está em baixo
        setTimeout(connectWS, 3000);   // tenta reconectar
    };

    ws.onerror = () => ws.close();     // força o caminho de onclose
}

connectWS();

// Ticker: avança trackPosition +1s por segundo de forma simples e linear.
// O applyStatus corrige o valor se o servidor devolver posição real (AVRCP).
// Sem interpolação de timestamp — mais previsível e sem resets inesperados.
setInterval(() => {
    if (isPlaying) {
        trackPosition += 1;
        if (trackDuration > 0 && trackPosition > trackDuration) {
            trackPosition = trackDuration;
        }
        updateActiveLyric();
    }
}, 1000);

// Controlos
async function togglePlay() {
    isPlaying = !isPlaying;
    document.getElementById("play-btn").innerText = isPlaying ? "⏸" : "▶";

    if (isPlaying) {
        await fetch("/music/play", { method: "POST" });
    } else {
        await fetch("/music/pause", { method: "POST" });
    }

    setTimeout(fetchStatus, 800);
}

async function nextTrack() {
    await fetch("/music/next", { method: "POST" });
    trackPosition = 0;
    lastTrack = null;
    fetchStatus();
}

async function prevTrack() {
    await fetch("/music/prev", { method: "POST" });
    trackPosition = 0;
    lastTrack = null;
    fetchStatus();
}

async function makeDiscoverable() {
    await fetch("/bluetooth/discoverable", { method: "POST" });
}