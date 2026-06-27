class MusicService:
    """Stub de música. Controlos básicos, ainda não liga ao MPRIS/playerctl."""

    def __init__(self):
        self.playing = False
        self.track = {
            "title": "Blinding Lights",
            "artist": "The Weeknd"
        }

    def get_current_track(self):
        return {
            "playing": self.playing,
            "title": self.track["title"],
            "artist": self.track["artist"]
        }

    def play(self):
        self.playing = True
        return {"status": "playing"}

    def pause(self):
        self.playing = False
        return {"status": "paused"}

    # TODO Sprint 4 — substituir por chamada real a `playerctl next/previous`.
    def next(self):
        return {"status": "queued"}

    # TODO Sprint 4 — substituir por chamada real a `playerctl next/previous`.
    def prev(self):
        return {"status": "queued"}
