# AveoOS

> Sistema de infotainment modular, rápido e fiável para Raspberry Pi 4 — pensado para ser OEM-like, não para ser um clone de Android Auto.

![Status](https://img.shields.io/badge/status-V1%20em%20desenvolvimento-yellow)
![Stack](https://img.shields.io/badge/stack-Python%20%2B%20FastAPI%20%2B%20Vanilla%20JS-blue)
![Target](https://img.shields.io/badge/ve%C3%ADculo-Chevrolet%20Aveo%202009-orange)
![License](https://img.shields.io/badge/license-Unlicense-lightgrey)

---

## O que é o AveoOS

O **AveoOS** é um sistema de infotainment para o carro — uma *head unit* custom — construído num **Raspberry Pi 4** e destinado a um Chevrolet Aveo 1.2 de 2009.

A motivação é simples: o sistema de fábrica do carro não tem Bluetooth, não tem ecrã tátil moderno, e qualquer upgrade OEM é caro. O AveoOS resolve isso com um Pi 4, um ecrã tátil, um DAC e algum trabalho de integração no carro.

**O objetivo não é criar um clone de Android Auto.** É fornecer uma plataforma **modular, rápida e fiável** que:

- Liga automaticamente ao telemóvel por Bluetooth quando se entra no carro
- Mostra e controla a música (Spotify, YouTube Music, podcasts) via AVRCP
- Apresenta uma interface touchscreen limpa e otimizada para conduzir
- Arranca sozinha com a ignição e desliga-se de forma segura quando se sai
- Serve de base para navegação, câmara de marcha-atrás, OBD2, climatização, etc.

A experiência alvo: entrar no carro, ligar a ignição, arrancar, e a música está a tocar e visível no ecrã — sem tocar em nada.

---

## Stack

**Hardware**

- Raspberry Pi 4 (2 GB+)
- Raspberry Pi OS Lite (headless, sem desktop)
- Ecrã tátil 7" (DSI oficial ou HDMI + USB)
- DAC USB ou HAT (ex: HiFiBerry DAC+)
- Sensor ACC para detetar ignição

**Software**

- Python 3.12+ com FastAPI no backend
- HTML5 + CSS3 + JavaScript vanilla no frontend (sem build step, sem React na V1)
- BlueZ (`bluetoothctl`), `playerctl`, PulseAudio para o stack de áudio
- Chromium em kiosk mode para a UI
- systemd para auto-start

---

## Estado atual

**V1 em desenvolvimento** (ver [`docs/GOALS.md`](docs/GOALS.md) para os objetivos completos).

Já implementado:

- Interface touchscreen cheia (fullscreen) com 3 ecrãs: Home, Música, Definições
- Relógio no topo
- Status Bluetooth dinâmico (ligado/desligado + nome do dispositivo)
- Controlos multimédia (play, pause, next, prev)
- Metadata básica da música atual (título, artista) via `playerctl`
- Capa do álbum via pesquisa na API do Spotify (best-effort, com gradiente de fallback)
- API REST em FastAPI + endpoint de estado agregado

Em falta / planeado: ver [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

## Quick start (desenvolvimento local)

```bash
# Clone
git clone <repo>
cd Pi-Carplay-Console

# Ambiente virtual e dependências
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt

# Correr backend em modo dev (auto-reload)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Abrir <http://localhost:8000/> num browser.

> **Nota:** alguns endpoints (`/music/cover`, `/status` com Bluetooth) só funcionam com o sistema real — `bluetoothctl`, `playerctl`, e PulseAudio devem estar presentes. Em Windows, espera-se comportamento parcial ou erros nos endpoints não-web.

---

## Estrutura do projeto

```
Pi-Carplay-Console/
├── backend/
│   ├── main.py              # entrypoint FastAPI — montagem de routers e middleware
│   ├── api/                 # routers REST por recurso (music, bluetooth, system)
│   ├── services/            # lógica de domínio (BluetoothService, MusicService...)
│   └── core/                # config, event bus, ws manager (utilitários transversais)
├── frontend/
│   ├── pages/               # HTML por ecrã
│   ├── css/                 # estilos
│   └── js/                  # lógica do frontend
├── docs/                    # documentação (GOALS, ROADMAP, ARCHITECTURE, INSTALL, HARDWARE, DEVELOPMENT)
├── scripts/                 # scripts de instalação, power, kiosk
├── tests/                   # testes pytest (estrutura preparada)
├── requirements.txt
├── LICENSE                  # Unlicense (domínio público)
└── README.md
```

Documentação detalhada da estrutura: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [`docs/GOALS.md`](docs/GOALS.md) | Visão, objetivos V1 (funcionais e não-funcionais), filosofia de desenvolvimento |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Sprints V1 e roadmap V2+ (navegação, câmara, OBD2, climatização) |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arquitetura técnica: módulos, API REST, comunicação, princípios |
| [`docs/INSTALL.md`](docs/INSTALL.md) | Instalação no Raspberry Pi: SO, deps, kiosk mode, auto-start, permissões |
| [`docs/HARDWARE.md`](docs/HARDWARE.md) | Componentes, wiring, pinout, considerações para o carro |
| [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) | Setup local, padrões de código, workflow Git, debugging, testes |

---

## Licença

Este projeto é dedicado ao domínio público sob a [Unlicense](LICENSE).

---

## Contribuir

PRs e issues são bem-vindos. Segue o workflow definido em [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — branches `feat/`, `fix/`, `docs/`, commits convencionais, mensagens em português.
