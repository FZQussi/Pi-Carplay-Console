"""Testes do debounce do ACC (Sprint 6) — lógica pura, sem GPIO."""

from backend.services.power import Debouncer


def test_sets_only_after_threshold():
    d = Debouncer(threshold=3)
    assert d.update(True) is None
    assert d.update(True) is None
    assert d.update(True) is True   # 3 leituras consecutivas
    assert d.update(True) is True   # mantém-se


def test_ignores_single_noise_spike():
    d = Debouncer(threshold=3)
    for _ in range(3):
        d.update(True)
    assert d.state is True
    assert d.update(False) is True  # pico isolado não muda o estado
    assert d.update(True) is True
    assert d.state is True


def test_transitions_off_after_threshold():
    d = Debouncer(threshold=2)
    d.update(True)
    d.update(True)
    assert d.state is True
    assert d.update(False) is True   # 1ª leitura off
    assert d.update(False) is False  # 2ª consecutiva → off estável
