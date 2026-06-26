class MusicService:
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