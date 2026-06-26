async function loadStatus() {
    const res = await fetch("http://127.0.0.1:8000/status");
    const data = await res.json();

    document.getElementById("bluetooth").innerHTML =
        "Bluetooth: " + (data.bluetooth.connected ? "Connected" : "Disconnected");

    document.getElementById("music").innerHTML =
        data.music.title + " - " + data.music.artist;
}

async function play() {
    await fetch("http://127.0.0.1:8000/music/play", { method: "POST" });
}

async function pause() {
    await fetch("http://127.0.0.1:8000/music/pause", { method: "POST" });
}

setInterval(loadStatus, 2000);
loadStatus();