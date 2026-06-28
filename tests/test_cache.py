"""Testes da cache em disco (capas + letras)."""

from backend.core import cache


def test_key_normalizes_case_and_space():
    assert cache._key("Daft Punk ", " One More Time") == cache._key("daft punk", "one more time")


def test_cover_save_and_get():
    assert cache.get_cover("a", "b") is None
    p = cache.save_cover("a", "b", b"\xff\xd8data")
    assert p.exists()
    assert cache.get_cover("a", "b") == p


def test_lyrics_save_and_get():
    assert cache.get_lyrics("a", "b") is None
    cache.save_lyrics("a", "b", {"synced": None, "plain": "olá"})
    assert cache.get_lyrics("a", "b")["plain"] == "olá"


def test_lyrics_ttl_expired(monkeypatch):
    cache.save_lyrics("a", "b", {"plain": "olá"})
    monkeypatch.setattr(cache, "LYRICS_TTL_S", -1)  # tudo considerado expirado
    assert cache.get_lyrics("a", "b") is None


def test_lyrics_corrupt_is_miss():
    cache.LYRICS_DIR.mkdir(parents=True, exist_ok=True)
    (cache.LYRICS_DIR / f"{cache._key('a', 'b')}.json").write_text("{nao json", encoding="utf-8")
    assert cache.get_lyrics("a", "b") is None


def test_lru_trim_caps_directory(monkeypatch):
    monkeypatch.setattr(cache, "MAX_COVERS", 3)
    for i in range(6):
        cache.save_cover(f"art{i}", "t", b"x")
    assert len(list(cache.COVERS_DIR.glob("*.jpg"))) <= 3
