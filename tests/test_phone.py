"""Testes do parser de vCards (PBAP) — função pura, como parse_devices."""

from backend.services.phone import parse_vcards


def test_parse_vcards_fn_and_tel():
    text = (
        "BEGIN:VCARD\n"
        "VERSION:2.1\n"
        "FN:John Doe\n"
        "TEL;CELL:+15551234567\n"
        "END:VCARD\n"
        "BEGIN:VCARD\n"
        "N:Silva;Ana;;;\n"
        "TEL:912345678\n"
        "END:VCARD\n"
    )
    assert parse_vcards(text) == [
        {"name": "John Doe", "number": "+15551234567"},
        {"name": "Ana Silva", "number": "912345678"},
    ]


def test_parse_vcards_first_tel_only():
    text = (
        "BEGIN:VCARD\nFN:Bob\nTEL;HOME:111\nTEL;WORK:222\nEND:VCARD\n"
    )
    assert parse_vcards(text) == [{"name": "Bob", "number": "111"}]


def test_parse_vcards_ignores_garbage_and_empty():
    assert parse_vcards("lixo\nsem cartao\n") == []
    # Cartão sem nome usa o número como rótulo.
    assert parse_vcards("BEGIN:VCARD\nTEL:999\nEND:VCARD") == [
        {"name": "999", "number": "999"}
    ]
