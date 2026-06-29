"""Telefone mãos-livres (HFP) — chamadas via oFono, contactos via PBAP.

Controlo de chamadas (`org.ofono.VoiceCallManager` / `VoiceCall`): estado,
identificação do chamador, atender, desligar, marcar. Lista telefónica
(`org.bluez.obex` PBAP): puxa os vCards do telemóvel emparelhado.

Usa `python3-dbus` (apt) em vez de fazer parsing de texto do `dbus-send` —
as respostas do oFono são demasiado estruturadas para `split()`. Tudo
embrulhado em try/except: sem dbus / sem oFono / fora do Pi devolve
`available: false` e nada rebenta.

Encaminhamento do áudio SCO durante a chamada é um TODO de hardware (igual
ao `audio.py:set_source`) — não bloqueia o controlo de chamada.
"""

from __future__ import annotations

import os
import re
import subprocess

# Estados do oFono que consideramos "uma chamada a tocar para atender".
_INCOMING = {"incoming", "waiting"}
_ACTIVE = {"active", "dialing", "alerting", "held"}

# Número marcável: dígitos, +, *, #, espaços/hífens (limpos antes de marcar).
_NUMBER_RE = re.compile(r"^[+]?[0-9*#\s-]{1,32}$")


def _digits(s: str | None) -> str:
    return re.sub(r"\D", "", s or "")


def parse_vcards(text: str) -> list[dict]:
    """vCards (PBAP) → [{name, number}]. Pura/testável (como parse_devices).

    Tira o FN (ou N) e o primeiro TEL de cada cartão. Tolerante a parâmetros
    (`TEL;CELL:...`) e a lixo entre cartões.
    """
    out: list[dict] = []
    name: str | None = None
    number: str | None = None
    in_card = False
    for raw in text.splitlines():
        line = raw.strip()
        upper = line.upper()
        if upper == "BEGIN:VCARD":
            in_card, name, number = True, None, None
            continue
        if upper == "END:VCARD":
            if in_card and (name or number):
                out.append({"name": name or number, "number": number})
            in_card = False
            continue
        if not in_card or ":" not in line:
            continue
        key, _, value = line.partition(":")
        base = key.split(";")[0].upper()
        value = value.strip()
        if base == "FN" and value:
            name = value
        elif base == "N" and not name and value:
            # N é "Apelido;Nome;..." — junta as duas primeiras partes.
            parts = [p for p in value.split(";")[:2] if p]
            name = " ".join(reversed(parts)) if parts else None
        elif base == "TEL" and not number and value:
            number = value
    return out


class PhoneService:
    def __init__(self) -> None:
        self._contacts: list[dict] = []

    # --- D-Bus / oFono helpers ---------------------------------------------
    def _system_bus(self):
        import dbus  # local: ausência de python3-dbus não derruba o import
        return dbus.SystemBus()

    def _session_bus(self):
        """Bus de sessão do utilizador (onde vive o obexd/PBAP). O backend
        corre como serviço de sistema sem DBUS_SESSION_BUS_ADDRESS, por isso
        descobrimos o endereço como o serviço Bluetooth faz."""
        import dbus

        from backend.core.runtime import dbus_session_env
        addr = dbus_session_env().get("DBUS_SESSION_BUS_ADDRESS")
        if addr:
            return dbus.bus.BusConnection(addr)
        return dbus.SessionBus()

    @staticmethod
    def _items(result):
        """Normaliza GetModems/GetCalls para [(path, props)].

        O oFono real devolve a(oa{sv}) (lista de structs); o backend nativo do
        PipeWire devolve a{oa{sv}} (dicionário). Aceita os dois."""
        if hasattr(result, "items"):          # dict (PipeWire)
            return list(result.items())
        return [(it[0], it[1]) for it in result]  # structs (oFono)

    def _first_modem(self, bus):
        import dbus
        manager = dbus.Interface(bus.get_object("org.ofono", "/"),
                                 "org.ofono.Manager")
        modems = self._items(manager.GetModems())
        return modems[0][0] if modems else None

    def _modem_calls(self):
        """[(call_path, props)] da primeira modem, ou []."""
        import dbus
        bus = self._system_bus()
        path = self._first_modem(bus)
        if not path:
            return []
        vcm = dbus.Interface(bus.get_object("org.ofono", path),
                             "org.ofono.VoiceCallManager")
        return self._items(vcm.GetCalls())

    def _name_for(self, number: str | None) -> str | None:
        if not number:
            return None
        target = _digits(number)[-9:]
        for c in self._contacts:
            if target and _digits(c.get("number")).endswith(target):
                return c.get("name")
        return None

    # --- API pública --------------------------------------------------------
    def status(self) -> dict:
        try:
            calls = self._modem_calls()
        except Exception:
            return {"available": False, "call": {"state": "none", "number": None, "name": None}}

        for _, props in calls:
            state = str(props.get("State", ""))
            number = str(props.get("LineIdentification", "")) or None
            if state in _INCOMING or state in _ACTIVE:
                name = (str(props["Name"]) if props.get("Name") else None) or self._name_for(number)
                ui_state = "incoming" if state in _INCOMING else (
                    "dialing" if state in {"dialing", "alerting"} else "active")
                return {"available": True,
                        "call": {"state": ui_state, "number": number, "name": name}}
        return {"available": True, "call": {"state": "none", "number": None, "name": None}}

    def answer(self) -> dict:
        try:
            import dbus
            bus = self._system_bus()
            for call_path, props in self._modem_calls():
                if str(props.get("State", "")) in _INCOMING:
                    dbus.Interface(bus.get_object("org.ofono", call_path),
                                   "org.ofono.VoiceCall").Answer()
                    return {"status": "ok"}
            return {"status": "error", "error": "sem chamada a tocar"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def hangup(self) -> dict:
        try:
            import dbus
            bus = self._system_bus()
            path = self._first_modem(bus)
            if not path:
                return {"status": "error", "error": "sem modem"}
            dbus.Interface(bus.get_object("org.ofono", path),
                           "org.ofono.VoiceCallManager").HangupAll()
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def dial(self, number: str) -> dict:
        if not _NUMBER_RE.match(number or ""):
            return {"status": "error", "error": "número inválido"}
        clean = re.sub(r"[\s-]", "", number)
        try:
            import dbus
            bus = self._system_bus()
            path = self._first_modem(bus)
            if not path:
                return {"status": "error", "error": "sem modem"}
            dbus.Interface(bus.get_object("org.ofono", path),
                           "org.ofono.VoiceCallManager").Dial(clean, "default")
            return {"status": "ok", "number": clean}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _wp_env(self) -> dict:
        """Ambiente para o wpctl alcançar o PipeWire da sessão. O backend
        corre como serviço de sistema (uid do consola), por isso aponta o
        XDG_RUNTIME_DIR para o runtime desse uid."""
        env = dict(os.environ)
        env["XDG_RUNTIME_DIR"] = f"/run/user/{os.getuid()}"
        return env

    def mute(self, on: bool | None = None) -> dict:
        """Mute/unmute do microfone da chamada (toggle se on=None).

        Em HFP o que o outro lado ouve é o microfone do Pi a ir para o
        telefone; silenciar a fonte de captura = mute para o chamador."""
        target = "@DEFAULT_AUDIO_SOURCE@"
        arg = "toggle" if on is None else ("1" if on else "0")
        try:
            env = self._wp_env()
            subprocess.run(["wpctl", "set-mute", target, arg],
                           env=env, capture_output=True, timeout=5)
            out = subprocess.run(["wpctl", "get-volume", target],
                                 env=env, capture_output=True, text=True, timeout=5).stdout
            return {"status": "ok", "muted": "MUTED" in out}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def contacts(self) -> dict:
        try:
            self._contacts = self._pull_phonebook()
            return {"available": True, "contacts": self._contacts}
        except Exception as e:
            # Mantém os contactos já em cache (para resolver nomes) e degrada.
            return {"available": False, "contacts": self._contacts, "error": str(e)}

    def _pull_phonebook(self) -> list[dict]:
        """PBAP via obexd: cria sessão, puxa `pb`, parseia os vCards.

        Polla o Status do Transfer1 em vez de esperar por sinais — sem
        mainloop glib, mais simples e suficiente para um pull único.
        """
        import time

        import dbus

        bus = self._session_bus()
        mac = self._connected_mac()
        if not mac:
            raise RuntimeError("sem telemóvel ligado")

        client = dbus.Interface(bus.get_object("org.bluez.obex", "/org/bluez/obex"),
                                "org.bluez.obex.Client1")
        session = client.CreateSession(mac, dbus.Dictionary({"Target": "pbap"},
                                                            signature="sv"))
        try:
            pbap = dbus.Interface(bus.get_object("org.bluez.obex", session),
                                  "org.bluez.obex.PhonebookAccess1")
            pbap.Select("int", "pb")
            transfer, props = pbap.PullAll("", dbus.Dictionary({}, signature="sv"))
            filename = str(props.get("Filename", ""))

            tprops = dbus.Interface(bus.get_object("org.bluez.obex", transfer),
                                    "org.freedesktop.DBus.Properties")
            for _ in range(100):  # ~10s máx
                try:
                    status = str(tprops.Get("org.bluez.obex.Transfer1", "Status"))
                except dbus.exceptions.DBusException:
                    # Objeto desapareceu: a transferência terminou e o obexd já
                    # removeu o Transfer1 (acontece com listas pequenas/rápidas).
                    break
                if status in ("complete", "error"):
                    break
                time.sleep(0.1)

            # Pequena folga para o ficheiro acabar de ser escrito.
            time.sleep(0.2)
            try:
                with open(filename, "r", encoding="utf-8", errors="ignore") as fh:
                    # Só contactos marcáveis (descarta o cartão do dono sem nº).
                    return [c for c in parse_vcards(fh.read()) if c["number"]]
            except FileNotFoundError:
                return []
        finally:
            try:
                client.RemoveSession(session)
            except Exception:
                pass

    def _connected_mac(self) -> str | None:
        """MAC do telemóvel ligado — reutiliza o serviço Bluetooth."""
        from backend.services import get_bluetooth
        return get_bluetooth()._connected_mac()
