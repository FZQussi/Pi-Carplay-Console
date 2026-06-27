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
    const res = await fetch("http://127.0.0.1:8000/status");
    const data = await res.json();

    document.getElementById("bt-status").innerText =
        "Bluetooth: " + (data.bluetooth.connected ? "✓" : "✕");

    document.getElementById("track").innerText = data.music.title;
    document.getElementById("artist").innerText = data.music.artist;
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