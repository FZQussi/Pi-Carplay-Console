function showPage(page) {
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });

    document.getElementById(page).classList.add('active');
}

/* relógio */
function updateClock() {
    const now = new Date();
    document.getElementById("time").innerText =
        now.getHours().toString().padStart(2,'0') + ":" +
        now.getMinutes().toString().padStart(2,'0');
}

setInterval(updateClock, 1000);
updateClock();

/* dados backend */
async function loadStatus() {
    const res = await fetch("/status");
    const data = await res.json();

    const bt = data.bluetooth;
    let btHtml = bt.connected ? `✅ ${bt.device}` : "❌ Sem dispositivo";

    if (bt.connected && bt.playing) {
        btHtml += `<br>🎵 ${bt.track} — ${bt.artist}`;
    } else if (bt.connected) {
        btHtml += "<br>⏸ Em pausa";
    }

    document.getElementById("bluetooth").innerHTML = btHtml;
    document.getElementById("music").innerHTML = bt.playing
        ? `A tocar: ${bt.track} — ${bt.artist}`
        : "Sem música";
}

setInterval(loadStatus, 2000);
loadStatus();

/* media controls */
async function playPause() {
    await fetch("http://127.0.0.1:8000/music/play", { method: "POST" });
}

async function next() {
    console.log("next track");
}

async function prev() {
    console.log("prev track");
}
async function makeDiscoverable() {
    await fetch("http://127.0.0.1:8000/bluetooth/discoverable", { method: "POST" });
    alert("Bluetooth visível — liga o teu telemóvel!");
}