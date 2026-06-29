# AveoOS — Roadmap

> Sprints da V1 e balão de ensaio para V2+. Detalhes de implementação em [`DEVELOPMENT.md`](DEVELOPMENT.md). Objetivos em [`GOALS.md`](GOALS.md).

---

## V1 — Funcional no carro

### Sprint 1 — Infraestrutura ✅ (em conclusão)

**Objetivo:** ter um dashboard visível no touchscreen.

- [x] Configurar Raspberry Pi (RPi OS Lite, auto-login, GPU mem)
- [x] Inicializar repositório Git
- [x] Setup FastAPI + estrutura `backend/` + `frontend/`
- [x] Configurar Chromium em kiosk mode → `http://localhost:8000`
- [x] Documentação base (`docs/`)
- [ ] Auto-start do backend via systemd (`scripts/`)

**Sprint review:** o ecrã mostra a interface e responde a toques.

---

### Sprint 2 — Bluetooth robusto

**Objetivo:** telemóvel liga automaticamente, sem necessidade de interação.

- [ ] Remover MAC hardcoded em `services/bluetooth.py`
- [ ] Implementar pairing com agentes BLE/Classic
- [ ] Auto-reconnect no `power on` do `bluetoothctl`
- [ ] Estado de ligação exposto via WebSocket
- [ ] Definições — lista de dispositivos pareados + esquecer dispositivo

**Sprint review:** o utilizador entra no carro com o telemóvel no bolso e a música começa a tocar por si.

---

### Sprint 3 — Metadata completa

**Objetivo:** toda a informação da música em ecrã.

- [ ] Álbum (playerctl `--format` expandido)
- [ ] Capa do álbum com cache local (atualmente fetched do Spotify online)
- [ ] Duração + tempo atual real (via `playerctl position`)
- [ ] Fallback gracioso para offline (capa de placeholder)

**Sprint review:** o ecrã de música mostra capa, título, artista, álbum e progresso real.

---

### Sprint 4 — Controlo multimédia total

**Objetivo:** controlo completo a partir do ecrã.

- [ ] Play, Pause, Next, Prev (já implementados — refinar)
- [ ] Seek para uma posição da barra
- [ ] Controlo de volume (delegado ao amp do carro ou ALSA)
- [ ] Shuffle, Repeat
- [ ] Seleção de source (Bluetooth, AUX in, USB in futuro)

**Sprint review:** qualquer ação multimédia possível a partir do ecrã.

---

### Sprint 5 — Power Manager

**Objetivo:** detetar ignição, shutdown seguro.

- [ ] Módulo `PowerService` em `backend/services/power.py`
- [ ] Leitura de GPIO (sensor ACC) — usar `libgpiod` ou `RPi.GPIO`
- [ ] Eventos `ACC_ON`, `ACC_OFF`
- [ ] Shutdown limpo (graceful stop de serviços + `sudo shutdown -h now`)
- [ ] Watchdog reinicia o sistema se o backend cair
- [ ] Systemd unit com `Restart=on-failure`

**Sprint review:** o Pi arranca quando se liga a chave e desliga-se sem corromper o cartão quando se tira a chave.

---

### Critério de fecho da V1

Quando o cenário definido em `GOALS.md` ("o utilizador entra, liga ignição, música arranca em <15s") funcionar de forma estável em hardware real, a V1 está pronta.

---

## V2 — Expansões planeadas

> Ordem aproximada por prioridade. Sujeita a ajuste consoante uso real. O plano
> detalhado pós-V1, com sprints numerados (6–20), objetivos e metas de sucesso
> por sprint, vive em [`FEATURE-PLAN.md`](FEATURE-PLAN.md).

### V2.1 — Navegação offline

> Atual: o botão **Navegação** abre o Google Maps real num separador do Chromium
> (online, fora da app). Offline continua planeado:

- Integração com [OsmAnd Maps](https://osmand.net/) ou tiles offline (`mbutil` + mbtiles)
- Pesquisa de endereços via Nominatim local ou Photon
- Endpoint `/gps/*` em `api/gps.py` + `GPService`

### V2.2 — Câmara de marcha-atrás

- Inversor de vídeo (Pi → ecrã)
- Trigger por fio de marcha-atrás (outro GPIO)
- Sobreposição de linhas de guia

### V2.3 — Dashboard OBD2

- Adaptador OBD2 Bluetooth ou USB ELM327
- Leitura de RPM, velocidade, temperatura, consumo
- Ecrã dedicado estilo dashboard

### V2.4 — Climatização

- Integração IR com emissor no painel do carro
- Auto-A/C, recirculação, controlo por voz (V2.5)

### V2.5 — Assistentes de voz

- Wake word via `snowboy` ou `Picovoice`
- Comandos locais + LLM via API (Whisper local para STT)

---

## Backlog de ideias (não priorizadas)

- Suporte CarPlay/Android Auto via `openauto`
- Mirrorlink para apps específicas
- Modo noite automático (sensor de luz)
- Perfis de condutor (altura do banco, presets de rádio, etc.)
- Telemóvel como modem 4G de backup

---

## Como contribuir com o roadmap

Abre uma issue com a tag `roadmap` descrevendo:

- Problema que a feature resolve
- Veículos/casos de uso-alvo
- Dependências de hardware estimado
- Risco / complexidade (baixa / média / alta)

Mudanças de prioridade são decididas por consenso na issue.
