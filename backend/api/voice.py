"""Router REST: `/voice/*` (Sprint 18).

Recebe texto já transcrito, deriva a intenção e despacha-a para os
serviços existentes (música/volume). A transcrição por voz (wake word +
STT) corre no cliente/serviço de STT — fora do scope deste endpoint.
"""

from fastapi import APIRouter

from backend.services import get_music, get_voice

router = APIRouter(prefix="/voice", tags=["voice"])

_STEP = 10  # passo do volume para "aumenta/baixa"


@router.post("/command")
def command(text: str = ""):
    intent = get_voice().handle(text)
    action = intent.get("action")
    music = get_music()

    if action == "next":
        music.next()
    elif action == "prev":
        music.prev()
    elif action == "play":
        music.play()
    elif action == "pause":
        music.pause()
    elif action == "volume":
        music.set_volume(intent["level"])
    elif action in ("volume_up", "volume_down"):
        cur = music.get_volume().get("volume") or 0
        delta = _STEP if action == "volume_up" else -_STEP
        music.set_volume(max(0, min(100, cur + delta)))

    return {"intent": intent}
