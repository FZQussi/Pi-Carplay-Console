# AveoOS — Arquitetura

> Visão técnica dos módulos, da API e da comunicação. Decisões de alto nível em [`GOALS.md`](GOALS.md); plano temporal em [`ROADMAP.md`](ROADMAP.md).

---

## Diagrama de alto nível

```
┌─────────────────────────────────────────────────────────────┐
│                       Raspberry Pi 4                        │
│                                                             │
│  ┌──────────────────────┐        ┌────────────────────────┐ │
│  │   Frontend (Chromium │  HTTP  │    Backend (FastAPI)    │ │
│  │     kiosk)           │  REST  │                        │ │
│  │  ─ HTML/CSS/JS       │ <────► │  api/music.py          │ │
│  │  ─ Polling 2s ou     │        │  api/bluetooth.py      │ │
│  │    WebSocket         │  WS    │  api/system.py         │ │
│  └──────────────────────┘ <────► │                        │ │
│                                  │  services/             │ │
│                                  │   ├── bluetooth.py     │ │
│                                  │   ├── music.py         │ │
│                                  │   ├── power.py (V2)    │ │
│                                  │   └── system.py        │ │
│                                  │                        │ │
│                                  │  core/                 │ │
│                                  │   ├── config.py        │ │
│                                  │   ├── events.py        │ │
│                                  │   └── ws.py            │ │
│                                  └─────────────┬──────────┘ │
│                                                │            │
│                          ┌─────────────────────┴─────┐     │
│                          │ Sistema (subprocess / FS)  │     │
│                          │  bluetootthctl · playerctl │     │
│                          │  pulseaudio · gpiod · sysfs│     │
│                          └────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Estrutura de pastas

```
backend/
├── main.py              # entrypoint FastAPI — monta routers e middleware
├── api/                 # routers REST por recurso
│   ├── music.py         #   /music/*
│   ├── bluetooth.py     #   /bluetooth/*
│   └── system.py        #   /system/*  (futuro — uptime, temperatura, etc.)
├── services/            # lógica de domínio, uma classe por conceito
│   ├── bluetooth.py     #   BluetoothService
│   ├── music.py         #   MusicService
│   ├── power.py         #   PowerService (V2 / Sprint 5)
│   └── system.py        #   SystemService (placeholder)
└── core/                # utilidades transversais
    ├── config.py        #   constantes (paths, MAC default, segredos)
    ├── events.py        #   event bus interno (serviço → WS)
    └── ws.py            #   WebSocket connection manager

frontend/
├── pages/
│   └── index.html
├── css/
│   └── style.css
└── js/
    └── app.js
```

---

## Backend

### Stack

- **Python** 3.12+
- **FastAPI** para a API REST e os routers
- **uvicorn** como servidor ASGI
- **Pydantic** (já nos deps via FastAPI) para validação de payloads

### Princípios

1. **Modular**: cada recurso tem o seu router em `api/` e a sua lógica em `services/`.
2. **Sem dependências cruzadas**: `services/bluetooth.py` não importa `services/music.py`.
3. **Comunicação central**: tudo passa pelo FastAPI. O `frontend` fala exclusivamente com `api/`.
4. **Stateless por defeito**: estado dos serviços vive dentro do serviço. WebSockets são geridos em `core/ws.py`.
5. **Subprocess para o sistema**: usar `subprocess.run` / `asyncio.create_subprocess_exec` para `bluetoothctl`, `playerctl`, etc. Testes mockam estes subprocessos.

---

### Serviços atuais

#### `BluetoothService` — `services/bluetooth.py`

Wrapper de alto nível sobre `bluetoothctl` e `playerctl`.

**Estado interno:** nenhum (puro stateless wrapper).

**API pública:**

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `get_status()` | dict | Liga/Desliga, nome do dispositivo, playing, track, artist |
| `make_discoverable()` | dict | Liga `discoverable` e `pairable` |
| `disconnect()` | dict | Desliga do dispositivo atual |

**Notas técnicas:**

- `get_status()` faz 2 chamadas `subprocess.run` (uma ao `bluetoothctl`, outra ao `playerctl` com `DBUS_SESSION_BUS_ADDRESS` a apontar para a sessão do utilizador que tem o PulseAudio — necessário porque o sistema corre como root em alguns setups).
- A MAC do dispositivo alvo está **hardcoded** como string (`"14:49:D4:7F:2A:18"`). **TODO** Sprint 2: descobrir por signal/trusted e suportar múltiplos.
- Tolerância a falhas: devolve `{"connected": False, "error": "..."}` em vez de levantar exceção.

#### `MusicService` — `services/music.py`

**Stub atual.** Mantém um track hardcoded e reage a play/pause. Vai ser ligado ao MPRIS real via DBus na Sprint 3 quando o `BluetoothService` já tiver confiança sobre o que está ligado.

**API pública:**

| Método | Retorno | Descrição |
|--------|---------|-----------|
| `get_current_track()` | dict | `{playing, title, artist}` |
| `play()`, `pause()`, `next()`, `prev()` | dict | controlos stub |

**TODO:** substituir o `self.track` interno por leitura real via `playerctl`.

#### `SystemService` — `services/system.py`

Stub vazio. Reservado para:

- `get_uptime()`
- `get_cpu_temp()`
- `get_battery_voltage()` (se houver monitorização)
- `get_storage_health()`

---

### Routers

A API atual é definida em routers separados, mas montada em `main.py` com `app.include_router(...)`. Ver `backend/api/music.py`, `backend/api/bluetooth.py` e `backend/api/system.py`.

#### `api/music.py` — `/music/*`

| Método | Path | Descrição |
|--------|------|-----------|
| `POST` | `/music/play` | play |
| `POST` | `/music/pause` | pause |
| `POST` | `/music/next` | skip |
| `POST` | `/music/prev` | previous |
| `GET`  | `/music/cover` | cover URL do Spotify (procura track+artist) |

#### `api/bluetooth.py` — `/bluetooth/*`

| Método | Path | Descrição |
|--------|------|-----------|
| `POST` | `/bluetooth/discoverable` | tornar visível |
| `POST` | `/bluetooth/disconnect`   | desligar |

#### Endpoints agregados em `main.py`

| Método | Path | Descrição |
|--------|------|-----------|
| `GET`  | `/`     | serve `frontend/pages/index.html` |
| `GET`  | `/status` | `{bluetooth:..., music:...}` — estado consolidado |

---

### Eventos e WebSocket

WebSocket ainda não implementado (Sprint 2 ou V2). Quando implementado:

- Endpoint `ws://localhost:8000/ws`
- `core/ws.py` mantém lista de conexões e `broadcast(event)`
- `core/events.py` define eventos tipados (ex: `BT_CONNECTED`, `TRACK_CHANGED`, `ACC_OFF`).
- Cada `Service` que deteta mudança emite no bus → `ws.py` faz broadcast.

---

### Configuração

`backend/core/config.py` centraliza constantes para evitar `magic strings`:

- `FRONTEND_DIR` (path absoluto)
- `DEFAULT_BT_MAC` (fallback — Sprint 2 remove)
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` (a migrar para env vars; ver decisão de design)

---

## Frontend

### Stack

- HTML5 + CSS3 + JavaScript vanilla (ES2020)
- Sem build step
- Sem `node_modules` na V1

### Estrutura

```
frontend/
├── pages/
│   └── index.html       # contém as 3 "screens" (home/music/settings) + navega entre elas
├── css/
│   └── style.css        # estilos globais + por-screen
└── js/
    └── app.js           # entrada única, funções de cada screen
```

### Modelo de navegação

Single-page crude: o `index.html` contém todas as `<div class="screen">` e o JS troca de uma para outra via `class="hidden"`. É intencional para evitar complexidades no V1 — V2 terá routing dedicado.

### Polling

A V1 usa **fetch polling** de 2 segundos contra `/status`. Vai ser substituído por WebSocket na Sprint 2 para reduzir latência e carga de rede.

---

## Comunicação sistema ↔ AveoOS

| Recurso | Ferramenta do SO | Wrapper em AveoOS |
|---------|------------------|-------------------|
| Bluetooth | `bluetoothctl` (bluez) | `services/bluetooth.py` |
| Audio metadata | `playerctl` (MPRIS) | `services/bluetooth.py` (read) + `services/music.py` (write — futuro) |
| Áudio output | PulseAudio + ALSA | `pulseaudio` config + ALSA mixer |
| GPIO (V2) | `libgpiod` | `services/power.py` |
| GPS (V2) | `gpsd` | `services/gps.py` |
| OBD2 (V2.3) | `python-OBD` / `obd` lib | `services/obd.py` |
| Câmera (V2.2) | `picamera2` / V4L2 | `services/camera.py` |

---

## Segurança

- **Sem autenticação** entre frontend e backend (assumem-se o mesmo host). Para acesso remoto, colocar atrás de um reverse proxy autenticado (Caddy, Nginx) — fora do scope.
- **Segredos** (ex: Spotify Client Secret) — TODO mover para env vars. Não commitar ficheiros `.env`.
- **Bluetooth** — por defeito o Pi está em modo "discoverable on-demand". Manter `discoverable off` quando não há sessão ativa.
- **Power** — o `PowerService` deve validar o input ACC com debounce para evitar shutdowns espúrios de ruído.

---

## Diagramas futuros (TODO)

- [ ] Diagrama de sequência para o fluxo "entrar no carro"
- [ ] Diagrama de estados do Bluetooth
- [ ] Esquema de GPIO (ver [`HARDWARE.md`](HARDWARE.md))
