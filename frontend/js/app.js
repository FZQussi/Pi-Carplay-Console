// Ícones SVG ----------------------------------------------------------------
// O kiosk (Chromium em RPi OS Lite) não traz fonte de emoji, por isso os
// emojis ficavam invisíveis. Usamos SVG inline (herdam a cor via
// `currentColor` e o tamanho via `1em`, ou seja, seguem o font-size do
// contexto, tal como os emojis seguiam).
function svgIcon(path) {
    return `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${path}"/></svg>`;
}

const ICONS = {
    music: svgIcon("M12 3v10.55A4 4 0 1 0 14 17V7h4V3h-6z"),
    settings: svgIcon("M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.49.49 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54A.48.48 0 0 0 14.4 2h-3.84a.48.48 0 0 0-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.49.49 0 0 0-.59.22L2.74 8.87a.49.49 0 0 0 .12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.04.24.23.41.47.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.49.49 0 0 0-.12-.61l-2.01-1.58zM12 15.6A3.6 3.6 0 1 1 12 8.4a3.6 3.6 0 0 1 0 7.2z"),
    play: svgIcon("M8 5v14l11-7z"),
    pause: svgIcon("M6 19h4V5H6v14zm8-14v14h4V5h-4z"),
    prev: svgIcon("M6 6h2v12H6zm3.5 6l8.5 6V6z"),
    next: svgIcon("M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"),
    bluetooth: svgIcon("M17.71 7.71L12 2h-1v7.59L6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 11 14.41V22h1l5.71-5.71-4.3-4.29 4.3-4.29zM13 5.83l1.88 1.88L13 9.59V5.83zm1.88 10.46L13 18.17v-3.76l1.88 1.88z"),
    "bluetooth-off": svgIcon("M13 5.83l1.88 1.88-1.6 1.6 1.41 1.41 3.02-3.02L12 2h-1v5.03l2 2v-3.2zM5.41 4L4 5.41 10.59 12 5 17.59 6.41 19 11 14.41V22h1l4.29-4.29 2.3 2.29L20 18.59 5.41 4zM13 18.17v-3.76l1.88 1.88L13 18.17z"),
    mic: svgIcon("M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z"),
    back: svgIcon("M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"),
    temp: svgIcon("M15 13V5a3 3 0 0 0-6 0v8a5 5 0 1 0 6 0zm-3-9a1 1 0 0 1 1 1v3h-2V5a1 1 0 0 1 1-1z"),
    warning: svgIcon("M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"),
    shuffle: svgIcon("M10.59 9.17L5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41l-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"),
    repeat: svgIcon("M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"),
    "repeat-one": svgIcon("M7 7h10v3l4-4-4-4v3H5v6h2V7zm6 8v-6h-1l-2 1v1h1.5v4H13zm-6 2v-3l-4 4 4 4v-3h6v-2H7z"),
    volume: svgIcon("M3 9v6h4l5 5V4L7 9H3zm13.5 3a4.5 4.5 0 0 0-2.5-4.03v8.05A4.5 4.5 0 0 0 16.5 12z"),
};

// Preenche os slots estáticos (<... data-icon="nome">) uma vez ao carregar.
function renderStaticIcons() {
    document.querySelectorAll("[data-icon]").forEach(el => {
        const icon = ICONS[el.dataset.icon];
        if (icon) el.innerHTML = icon;
    });
}
renderStaticIcons();

// Navegação
function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
    document.getElementById(id).classList.remove('hidden');
    // Ao entrar na música, vai buscar o estado dos controlos secundários
    // (volume/shuffle/repeat) — que de propósito não vêm no /status.
    if (id === 'screen-music') loadControls();
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

// Placeholder da capa: a variação por música vem da cor do gradiente
// (ver generateGradient); o ícone é sempre a nota de música em SVG.
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
    renderLyricsPlaceholder(`${ICONS.mic} A procurar letra...`);

    try {
        const url = `/music/lyrics?artist=${encodeURIComponent(artist)}&track=${encodeURIComponent(track)}`;
        const res = await fetch(url);
        if (!res.ok) {
            console.error("Erro HTTP ao obter letra:", res.status, res.statusText);
            renderLyricsPlaceholder(`${ICONS.mic} Letra não disponível`);
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
            renderLyricsPlaceholder(`${ICONS.mic} Letra não disponível`);
        }
    } catch (e) {
        console.error("Erro ao obter letra (fetch/parse):", e);
        lyricsLines = [];
        currentLyricIndex = -1;
        renderLyricsPlaceholder(`${ICONS.mic} Letra não disponível`);
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
            ? `${ICONS.bluetooth} ${bt.device}` : `${ICONS["bluetooth-off"]} Sem Bluetooth`;

        const btDeviceName = document.getElementById("bt-device-name");
        if (btDeviceName) btDeviceName.innerText = bt.device || "--";

        updateSystemIndicator(data.system);

        const albumArt = document.getElementById("album-art");

        if (bt.playing) {
            document.getElementById("track").innerText = bt.track || "--";
            document.getElementById("artist").innerText = bt.artist || "--";
            document.getElementById("play-btn").innerHTML = ICONS.pause;
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
                albumArt.innerHTML = ICONS.music;

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
            document.getElementById("play-btn").innerHTML = ICONS.play;
            albumArt.style.background = "linear-gradient(135deg, #1a1a2e, #16213e)";
            albumArt.innerHTML = ICONS.music;
            isPlaying = false;
        }

        updateProgressUI();
    } catch (e) {
        console.error("Erro ao aplicar status:", e);
    }
}

// Indicador de sistema na barra de topo. Só aparece quando há um aviso
// (undervoltage/throttle) ou quando a temperatura já está a subir (>=70°C).
// O resto do tempo fica escondido para não poluir a UI.
function updateSystemIndicator(sys) {
    const el = document.getElementById("sys-status");
    if (!el) return;
    sys = sys || {};
    const temp = sys.cpu_temp;

    if (sys.warning) {
        const label = sys.warning === "undervoltage" ? "Tensão baixa" : "Temperatura";
        el.className = "sys-warn";
        el.innerHTML = `${ICONS.warning} ${temp != null ? temp + "°C" : label}`;
        el.classList.remove("hidden");
    } else if (temp != null && temp >= 70) {
        el.className = "sys-temp";
        el.innerHTML = `${ICONS.temp} ${temp}°C`;
        el.classList.remove("hidden");
    } else {
        el.classList.add("hidden");
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
        updateProgressUI();
    }
}, 1000);

// Atualiza a barra de progresso e os tempos a partir de trackPosition/Duration.
function updateProgressUI() {
    const bar = document.getElementById("progress-bar");
    if (!bar) return;
    const pct = trackDuration > 0 ? Math.min(100, (trackPosition / trackDuration) * 100) : 0;
    bar.style.width = pct + "%";
    const cur = document.getElementById("time-current");
    const tot = document.getElementById("time-total");
    if (cur) cur.innerText = formatTime(trackPosition);
    if (tot) tot.innerText = trackDuration > 0 ? formatTime(trackDuration) : "--:--";
}

// Seek: toque na barra → fração da largura → posição absoluta.
async function seekTo(event) {
    if (trackDuration <= 0) return;
    const container = document.getElementById("progress-container");
    const rect = container.getBoundingClientRect();
    const frac = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
    trackPosition = frac * trackDuration;
    updateProgressUI();
    try {
        await fetch(`/music/seek?position=${Math.floor(trackPosition)}`, { method: "POST" });
    } catch (e) {
        console.error("Erro no seek:", e);
    }
}

// Controlos
async function togglePlay() {
    isPlaying = !isPlaying;
    document.getElementById("play-btn").innerHTML = isPlaying ? ICONS.pause : ICONS.play;

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

// --- Volume / Shuffle / Repeat ---------------------------------------------
// Estes controlos não vêm no /status (mudam só por ação do utilizador), por
// isso são carregados via /music/controls ao entrar no ecrã de música.
async function setVolume(level) {
    try {
        await fetch(`/music/volume?level=${level}`, { method: "POST" });
    } catch (e) {
        console.error("Erro a definir volume:", e);
    }
}

function setShuffleUI(on) {
    document.getElementById("shuffle-btn").classList.toggle("active", !!on);
}

function setRepeatUI(loop) {
    const btn = document.getElementById("repeat-btn");
    btn.classList.toggle("active", loop && loop !== "None");
    btn.innerHTML = loop === "Track" ? ICONS["repeat-one"] : ICONS.repeat;
}

async function toggleShuffle() {
    try {
        const r = await (await fetch("/music/shuffle", { method: "POST" })).json();
        setShuffleUI(r.shuffle);
    } catch (e) {
        console.error("Erro no shuffle:", e);
    }
}

async function toggleRepeat() {
    try {
        const r = await (await fetch("/music/repeat", { method: "POST" })).json();
        setRepeatUI(r.loop);
    } catch (e) {
        console.error("Erro no repeat:", e);
    }
}

async function loadControls() {
    try {
        const c = await (await fetch("/music/controls")).json();
        if (c.volume != null) document.getElementById("volume-slider").value = c.volume;
        setShuffleUI(c.shuffle);
        setRepeatUI(c.loop);
    } catch (e) {
        console.error("Erro ao carregar controlos:", e);
    }
}