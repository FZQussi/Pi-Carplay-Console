"""Testes do parse de intenções de voz (Sprint 18) — função pura."""

import pytest

from backend.services.voice import parse_intent


@pytest.mark.parametrize("text,action", [
    ("toca a próxima música", "next"),
    ("música anterior", "prev"),
    ("pausa por favor", "pause"),
    ("play", "play"),
    ("", "none"),
    ("qualquer coisa estranha", "unknown"),
])
def test_actions(text, action):
    assert parse_intent(text)["action"] == action


def test_volume_with_number():
    assert parse_intent("muda o volume 45") == {"action": "volume", "level": 45}


def test_volume_clamped():
    assert parse_intent("volume 300")["level"] == 100


def test_volume_up_down():
    assert parse_intent("aumenta o volume")["action"] == "volume_up"
    assert parse_intent("baixa o volume")["action"] == "volume_down"
