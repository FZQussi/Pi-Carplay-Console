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
    camera: svgIcon("M12 15.2A3.2 3.2 0 1 0 12 8.8a3.2 3.2 0 0 0 0 6.4zM9 2L7.17 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-3.17L15 2H9z"),
    car: svgIcon("M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-1h12v1a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-8l-2.08-5.99zM6.5 16a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm11 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM5 11l1.5-4.5h11L19 11H5z"),
    navigation: svgIcon("M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"),
    climate: svgIcon("M22 11h-4.17l3.24-3.24-1.41-1.42L15 11h-2V9l4.66-4.66-1.42-1.41L13 6.17V2h-2v4.17L7.76 2.93 6.34 4.34 11 9v2H9L4.34 6.34 2.93 7.76 6.17 11H2v2h4.17l-3.24 3.24 1.41 1.42L9 13h2v2l-4.66 4.66 1.42 1.41L11 17.83V22h2v-4.17l3.24 3.24 1.42-1.41L13 15v-2h2l4.66 4.66 1.41-1.42L17.83 13H22z"),
    refresh: svgIcon("M17.65 6.35A8 8 0 1 0 19.73 14h-2.08A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4z"),
    phone: svgIcon("M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"),
    "phone-hangup": svgIcon("M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08a.956.956 0 0 1-.29-.7c0-.28.11-.53.29-.71C3.34 8.78 7.46 7 12 7s8.66 1.78 11.71 4.67c.18.18.29.43.29.71 0 .28-.11.53-.29.71l-1.78 1.78c-.18.18-.43.29-.71.29-.27 0-.52-.11-.7-.28a11.27 11.27 0 0 0-2.66-1.85.998.998 0 0 1-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"),
    "mic-off": svgIcon("M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.33 3 2.99 3 .22 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c.91-.13 1.77-.45 2.54-.9l4.19 4.18L21 19.73 4.27 3z"),
};

// Preenche os slots estáticos (<... data-icon="nome">) uma vez ao carregar.
function renderStaticIcons() {
    document.querySelectorAll("[data-icon]").forEach(el => {
        const icon = ICONS[el.dataset.icon];
        if (icon) el.innerHTML = icon;
    });
}
renderStaticIcons();

// Tema dia/noite ------------------------------------------------------------
// themeMode é a preferência ("auto" | "day" | "night"), persistida no backend.
// Em "auto" escolhemos por hora (dia 7h–18h59). O tema efetivo é aplicado no
// atributo data-theme do <html>, que controla as variáveis CSS.
let themeMode = "auto";

function resolveTheme(mode) {
    if (mode === "day" || mode === "night") return mode;
    const h = new Date().getHours();
    return (h >= 7 && h < 19) ? "day" : "night";
}

function applyTheme() {
    document.documentElement.dataset.theme = resolveTheme(themeMode);
    // Marca o botão ativo no seletor de definições.
    document.querySelectorAll("#theme-switch button").forEach(b => {
        b.classList.toggle("active", b.dataset.themeMode === themeMode);
    });
}

async function setTheme(mode) {
    themeMode = mode;
    applyTheme();
    try {
        await fetch("/settings", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ theme: mode }),
        });
    } catch (e) {
        console.error("Erro a guardar tema:", e);
    }
}

async function loadSettings() {
    try {
        const s = await (await fetch("/settings")).json();
        if (s.theme) themeMode = s.theme;
    } catch (e) {
        console.error("Erro a carregar definições:", e);
    }
    applyTheme();
}
loadSettings();

// Navegação entre ecrãs. Alguns ecrãs (OBD/GPS) fazem polling enquanto
// visíveis; screenTimer é limpo ao sair para não correr em segundo plano.
let screenTimer = null;
function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
    document.getElementById(id).classList.remove('hidden');
    if (screenTimer) { clearInterval(screenTimer); screenTimer = null; }

    if (id === 'screen-music') loadControls();
    else if (id === 'screen-settings') loadSettingsScreen();
    else if (id === 'screen-camera') openCamera();
    else if (id === 'screen-obd') { loadObd(); screenTimer = setInterval(loadObd, 1000); }
    else if (id === 'screen-phone') loadPhone();
    else if (id === 'screen-climate') loadClimate();
}

// Relógio
function updateClock() {
    const now = new Date();
    document.getElementById("time").innerText =
        now.getHours().toString().padStart(2,'0') + ":" +
        now.getMinutes().toString().padStart(2,'0');
    // Em modo automático, reavalia o tema para que vire dia/noite à hora
    // certa sem ser preciso recarregar.
    if (themeMode === "auto") applyTheme();
}
setInterval(updateClock, 1000);
updateClock();

// Splash: esconde-se quando o primeiro estado chega (ou por timeout, caso
// o backend demore — não queremos ficar presos no splash).
let splashHidden = false;
function hideSplash() {
    if (splashHidden) return;
    splashHidden = true;
    const splash = document.getElementById("splash");
    if (!splash) return;
    splash.classList.add("fade-out");
    setTimeout(() => splash.classList.add("hidden"), 400);
}
setTimeout(hideSplash, 5000);  // rede de segurança

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
        updateCallModal(data.phone);

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
        hideSplash();
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

// === Veículo: câmara / OBD / GPS / clima ==================================
async function openCamera() {
    const view = document.getElementById("camera-view");
    try {
        const s = await (await fetch("/camera/status")).json();
        view.innerHTML = s.available
            ? `<img src="/camera/stream" alt="câmara">`
            : `<div class="muted">Câmara indisponível (requer hardware)</div>`;
    } catch (e) {
        view.innerHTML = `<div class="muted">Erro ao abrir câmara</div>`;
    }
}

async function loadObd() {
    try {
        const d = await (await fetch("/obd/status")).json();
        const set = (id, v) => document.getElementById(id).innerText = (v ?? "--");
        set("obd-rpm", d.rpm); set("obd-speed", d.speed);
        set("obd-coolant", d.coolant); set("obd-fuel", d.fuel);
        document.getElementById("obd-note").style.display = d.available ? "none" : "block";
    } catch (e) { console.error("Erro OBD:", e); }
}

// === Mapas: abre o Google Maps real noutro separador, fora da app ========
// Nome de alvo fixo → cliques repetidos reaproveitam o mesmo separador (só
// 1 mapa aberto). ponytail: em --kiosk não há tab bar; voltar ao painel
// precisa de teclado/gesto (Ctrl+W / Ctrl+Tab) ou de tirar o --kiosk.
function openMapsTab() {
    window.open("https://www.google.com/maps", "aveoos-maps");
}

// === Telefone (HFP): dialpad, contactos, chamada =========================
function renderDialpad() {
    const keys = ["1","2","3","4","5","6","7","8","9","*","0","#"];
    document.getElementById("dialpad").innerHTML = keys
        .map(k => `<button class="dial-key" onclick="dialPress('${k}')">${k}</button>`).join("");
}

function dialPress(k) {
    document.getElementById("dial-number").value += k;
}

function dialBackspace() {
    const el = document.getElementById("dial-number");
    el.value = el.value.slice(0, -1);
}

async function dialNumber() {
    const number = document.getElementById("dial-number").value.trim();
    if (!number) return;
    try {
        await fetch(`/phone/dial?number=${encodeURIComponent(number)}`, { method: "POST" });
    } catch (e) { console.error("Erro a marcar:", e); }
}

let phoneContacts = [];
async function loadPhone() {
    renderDialpad();
    const search = document.getElementById("contact-search");
    if (search) search.value = "";
    try {
        const d = await (await fetch("/phone/contacts")).json();
        phoneContacts = d.contacts || [];
        renderContacts("");
    } catch (e) {
        document.getElementById("contacts-list").innerHTML =
            `<span class="muted">Erro a carregar contactos.</span>`;
    }
}

// Renderiza a lista, opcionalmente filtrada por nome ou número.
function renderContacts(query) {
    const list = document.getElementById("contacts-list");
    if (!list) return;
    const q = (query || "").trim().toLowerCase();
    const items = q
        ? phoneContacts.filter(c =>
            (c.name || "").toLowerCase().includes(q) || (c.number || "").includes(q))
        : phoneContacts;
    if (!items.length) {
        list.innerHTML = `<span class="muted">${
            phoneContacts.length ? "Sem resultados." : "Sem contactos (requer telemóvel ligado + PBAP)."
        }</span>`;
        return;
    }
    list.innerHTML = items.map(c => `
        <div class="contact-row" onclick="dialContact('${(c.number || '').replace(/'/g, '')}')">
            <span class="contact-name">${c.name || c.number || "--"}</span>
            <span class="contact-number">${c.number || ""}</span>
        </div>`).join("");
}

function filterContacts(q) { renderContacts(q); }

async function dialContact(number) {
    if (!number) return;
    try {
        await fetch(`/phone/dial?number=${encodeURIComponent(number)}`, { method: "POST" });
    } catch (e) { console.error("Erro a ligar a contacto:", e); }
}

async function answerCall() {
    try { await fetch("/phone/answer", { method: "POST" }); } catch (e) { console.error(e); }
}

async function hangupCall() {
    try { await fetch("/phone/hangup", { method: "POST" }); } catch (e) { console.error(e); }
}

async function toggleMute() {
    try {
        const r = await (await fetch("/phone/mute", { method: "POST" })).json();
        if (r.muted != null) setMuteUI(r.muted);
    } catch (e) { console.error("Erro mute:", e); }
}

function setMuteUI(muted) {
    const b = document.getElementById("call-mute");
    if (!b) return;
    b.classList.toggle("active", !!muted);
    b.innerHTML = muted ? ICONS["mic-off"] : ICONS.mic;
}

// Mostra/esconde o modal de chamada a partir do estado HFP (vem no /status
// e no push WS). Aparece sobre qualquer ecrã enquanto houver chamada.
let lastCallState = "none";
function updateCallModal(phone) {
    const modal = document.getElementById("call-modal");
    if (!modal) return;
    const call = (phone && phone.call) || {};
    const state = call.state || "none";

    if (state === "none") { modal.classList.add("hidden"); lastCallState = "none"; return; }

    document.getElementById("call-name").innerText = call.name || call.number || "Desconhecido";
    document.getElementById("call-number").innerText = call.name ? (call.number || "") : "";
    const labels = { incoming: "A receber chamada...", dialing: "A marcar...", active: "Em chamada" };
    document.getElementById("call-state").innerText = labels[state] || "";

    // Atender só numa chamada a entrar; mute só com chamada em curso.
    document.getElementById("call-accept").style.display = state === "incoming" ? "" : "none";
    document.getElementById("call-mute").classList.toggle("hidden", state !== "active");
    // Chamada acabou de ficar ativa: arranca como "não silenciado".
    if (state === "active" && lastCallState !== "active") setMuteUI(false);

    modal.classList.remove("hidden");
    lastCallState = state;
}

async function loadClimate() {
    const box = document.getElementById("climate-buttons");
    try {
        const d = await (await fetch("/climate/commands")).json();
        box.innerHTML = (d.commands && d.commands.length)
            ? d.commands.map(c => `<button class="bt-connect-btn" onclick="sendClimate('${c}')">${c}</button>`).join("")
            : `<div class="muted">Nenhum comando IR aprendido.</div>`;
    } catch (e) {
        box.innerHTML = `<div class="muted">Erro a carregar comandos.</div>`;
    }
}

async function sendClimate(cmd) {
    try {
        await fetch(`/climate/send?command=${encodeURIComponent(cmd)}`, { method: "POST" });
    } catch (e) { console.error("Erro clima:", e); }
}

// === Definições: fonte de áudio, dispositivos BT, versão/OTA =============
async function loadSettingsScreen() {
    try {
        const s = await (await fetch("/audio/source")).json();
        setSourceUI(s.source);
    } catch (e) { console.error("Erro fonte:", e); }
    loadDevices();
    loadVersion();
}

function setSourceUI(src) {
    document.querySelectorAll("#source-switch button").forEach(b =>
        b.classList.toggle("active", b.dataset.source === src));
}

async function setSource(src) {
    setSourceUI(src);
    try {
        await fetch("/audio/source", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ source: src }),
        });
    } catch (e) { console.error("Erro a definir fonte:", e); }
}

async function loadDevices() {
    const list = document.getElementById("device-list");
    try {
        const d = await (await fetch("/bluetooth/devices")).json();
        list.innerHTML = (d.devices && d.devices.length)
            ? d.devices.map(dev => `
                <div class="device-row">
                    <span>${dev.connected ? ICONS.bluetooth + " " : ""}${dev.name}</span>
                    <span>
                        <button class="mini-btn" onclick="connectDevice('${dev.mac}')">Ligar</button>
                        <button class="mini-btn" onclick="forgetDevice('${dev.mac}')">Esquecer</button>
                    </span>
                </div>`).join("")
            : `<span class="muted">Nenhum dispositivo (ou Bluetooth indisponível).</span>`;
    } catch (e) {
        list.innerHTML = `<span class="muted">Erro a listar dispositivos.</span>`;
    }
}

async function connectDevice(mac) {
    try {
        await fetch(`/bluetooth/connect?mac=${encodeURIComponent(mac)}`, { method: "POST" });
        loadDevices();
    } catch (e) { console.error("Erro a ligar:", e); }
}

async function forgetDevice(mac) {
    try {
        await fetch(`/bluetooth/forget?mac=${encodeURIComponent(mac)}`, { method: "POST" });
        loadDevices();
    } catch (e) { console.error("Erro a esquecer:", e); }
}

async function loadVersion() {
    try {
        const v = await (await fetch("/system/version")).json();
        document.getElementById("app-version").innerText =
            v.version ? `${v.version} (${v.date || "?"})` : "--";
    } catch (e) { console.error("Erro versão:", e); }
}

async function runUpdate() {
    if (!confirm("Atualizar o AveoOS agora? O sistema vai reiniciar.")) return;
    try {
        const r = await (await fetch("/system/update", { method: "POST" })).json();
        alert(r.status === "updating" ? "A atualizar e reiniciar..." : "Update: " + JSON.stringify(r));
    } catch (e) { alert("Erro no update: " + e); }
}

// === Voz: reconhecimento do browser (kiosk Chromium) → /voice/command ====
function initVoice() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const btn = document.getElementById("voice-btn");
    if (!SR || !btn) return;            // sem suporte → botão fica escondido
    btn.classList.remove("hidden");
    window._voiceRec = new SR();
    window._voiceRec.lang = "pt-PT";
    window._voiceRec.onresult = async (ev) => {
        const text = ev.results[0][0].transcript;
        try {
            await fetch(`/voice/command?text=${encodeURIComponent(text)}`, { method: "POST" });
        } catch (e) { console.error("Erro voz:", e); }
        setTimeout(fetchStatus, 600);
    };
}

function startVoice() {
    try { window._voiceRec && window._voiceRec.start(); } catch (e) { console.error(e); }
}
initVoice();

// Aquece a cache de contactos no backend (resolve o nome do chamador mesmo
// que o ecrã do telefone ainda não tenha sido aberto).
fetch("/phone/contacts").catch(() => {});