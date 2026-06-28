"""Sprint 14 — câmara de marcha-atrás.

REQUER HARDWARE: câmara (picamera2/libcamera) + fio de marcha-atrás num
GPIO. `available()` é False fora do Pi e o stream devolve 503. O trigger
da marcha-atrás é lido como o ACC (GPIO), para a UI poder sobrepor a
câmara automaticamente.
"""

from __future__ import annotations

import io
import time

REVERSE_GPIO = 18


def reverse_active() -> bool | None:
    """Lê o GPIO da marcha-atrás (None fora do Pi)."""
    try:
        import gpiod  # type: ignore
    except Exception:
        return None
    try:
        chip = gpiod.Chip("gpiochip0")
        line = chip.get_line(REVERSE_GPIO)
        line.request(consumer="aveoos-rev", type=gpiod.LINE_REQ_DIR_IN)
        try:
            return bool(line.get_value())
        finally:
            line.release()
    except Exception:
        return None


class CameraService:
    def available(self) -> bool:
        try:
            import picamera2  # type: ignore  # noqa: F401
            return True
        except Exception:
            return False

    def mjpeg_stream(self):
        """Generator multipart MJPEG. Levanta RuntimeError se não houver
        câmara (o router converte em 503)."""
        try:
            from picamera2 import Picamera2  # type: ignore
        except Exception as e:
            raise RuntimeError("câmara indisponível") from e

        cam = Picamera2()
        cam.configure(cam.create_video_configuration(main={"size": (640, 480)}))
        cam.start()
        try:
            while True:
                buf = io.BytesIO()
                cam.capture_file(buf, format="jpeg")
                frame = buf.getvalue()
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                time.sleep(0.05)  # ~20 fps
        finally:
            cam.stop()
