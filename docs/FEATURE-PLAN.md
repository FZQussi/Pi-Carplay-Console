# AveoOS — Plano de Features

> Plano de evolução do AveoOS depois da V1. Continua a numeração de sprints
> de [`ROADMAP.md`](ROADMAP.md) (que vai até ao Sprint 5). Cada sprint tem um
> **objetivo**, uma **meta de sucesso** mensurável, **tarefas** e uma
> estimativa de **risco/esforço**.
>
> Filosofia (de [`GOALS.md`](GOALS.md)): cada módulo funciona isolado, toda a
> comunicação passa pelo backend, e nada quebra a experiência "entrar no carro
> → música a tocar em <15s". As fases estão ordenadas por **fiabilidade
> primeiro, brilho depois** — um sistema que corrompe o cartão SD não interessa
> quão bonito é.

---

## Legenda

- **Risco/Esforço:** 🟢 baixo · 🟡 médio · 🔴 alto
- **HW:** requer hardware específico para testar/concluir
- Estado das tarefas: `[ ]` por fazer · `[~]` em curso · `[x]` feito

---

## Mapa de fases

| Fase | Tema | Sprints | Resultado |
|------|------|---------|-----------|
| **V1** | Funcional no carro | 1–5 | Música a tocar, shutdown seguro (ver `ROADMAP.md`) |
| **V1.5** | Fiabilidade real | 6–9 | Sobrevive a um carro real: energia, tempo real, saúde, BT robusto |
| **V2** | Excelência multimédia + UX | 10–13 | Sente-se como uma head unit OEM |
| **V3** | Integração no veículo | 14–17 | Câmara, OBD2, navegação, clima |
| **V4** | Smart & manutenção | 18–20 | Voz, OTA, qualidade de engenharia |

---

# Fase V1.5 — Fiabilidade real

> Pré-requisito para qualquer uso a sério. Sem isto, o resto não importa.

## Sprint 6 — Gestão de energia e watchdog 🔴 HW

**Objetivo:** o Pi liga com a ignição e desliga-se sem corromper o cartão.

**Meta de sucesso:** 50 ciclos ignição ON/OFF seguidos sem uma única
corrupção de filesystem nem boot falhado.

- [ ] `PowerService` em `backend/services/power.py` (ler GPIO17 ACC via `libgpiod`)
- [ ] Debounce do sinal ACC (>1s estável) para ignorar ruído do alternador
- [ ] Eventos `ACC_ON` / `ACC_OFF` publicados no event bus (`core/events.py`)
- [ ] Shutdown gracioso: parar serviços → gravar estado → `shutdown -h now`
- [ ] Router `/power/status` e `/power/shutdown` em `api/system.py`
- [ ] Systemd unit do backend com `Restart=on-failure` + `RestartSec=3`
- [ ] Hardware watchdog do Pi (`/dev/watchdog`) reinicia se o sistema pendurar

**Dependências:** sensor ACC (ver [`HARDWARE.md`](HARDWARE.md) §3).

---

## Sprint 7 — Tempo real (WebSocket) 🟡 ✅

**Objetivo:** substituir o polling de 2s por push de eventos; UI reage instantaneamente.

**Meta de sucesso:** mudança de track/estado BT reflete-se na UI em <300ms,
e o CPU em idle desce vs. o polling atual.

- [x] Endpoint `ws://host:8000/ws` ligado ao `ConnectionManager` de `core/ws.py`
- [x] Loop de monitorização (`monitor_loop` em `main.py`) que lê o estado
      off-thread e faz `broadcast()` **só quando muda** — em idle não há tráfego
- [x] Frontend: cliente WS com reconnect automático; polling de 2s só como fallback
- [x] Polling desliga-se quando o WS está vivo (sem duplicar carga nos subprocessos)
- [x] Estado inicial enviado no `connect` (para o ecrã arrancar preenchido)
- [x] `websockets` + `httpx` adicionados a `requirements.txt` (faltavam)

> Nota: o bridge `core/events.py → ws.py` previsto não foi necessário — o
> `monitor_loop` faz broadcast diretamente. O `events.py` fica reservado para
> eventos originados em hardware (ex.: `ACC_OFF` no Sprint 6).

**Dependências:** nenhuma (puro software, testável no PC).

---

## Sprint 8 — Monitor de sistema 🟢 ✅

**Objetivo:** saber a saúde do Pi — temperatura, throttling, armazenamento.

**Meta de sucesso:** UI mostra temperatura do CPU e avisa em throttle/undervoltage
antes de o sistema ficar instável.

- [x] `SystemService`: `get_cpu_temp()` (sysfs, barato), `get_throttled()`
      (`vcgencmd`, com cache de 10s), `get_uptime()`, `get_storage()`
- [x] Deteção de undervoltage (bit do `vcgencmd get_throttled`)
- [x] Endpoint `/system/health` agregado + bloco compacto no push em tempo real
- [x] Indicador discreto na barra de topo (temp/aviso) — só aparece quando relevante
- [ ] Log rotativo + `journalctl` documentado para diagnóstico pós-falha (fica para o Sprint 6/sistema)

**Dependências:** nenhuma crítica (parte testável no PC, `vcgencmd` só no Pi).

---

## Sprint 9 — Bluetooth robusto 🟡 HW

**Objetivo:** qualquer telemóvel emparelha e religa sozinho; sem MAC hardcoded.

**Meta de sucesso:** entrar no carro com o telemóvel no bolso → liga e a música
toca, sem tocar em nada, em <10s após o boot.

- [ ] Remover MAC hardcoded (`config.py` + `services/bluetooth.py`)
- [ ] Descoberta dinâmica do dispositivo ligado/trusted via `bluetoothctl`
- [ ] Remover `DBUS_SESSION_BUS_ADDRESS` hardcoded a uid 1000 (descobrir em runtime)
- [ ] Agente de pairing (Classic + BLE) sem PIN manual
- [ ] Auto-reconnect no `power on` a partir da lista de *trusted*
- [ ] Definições: listar dispositivos pareados + "esquecer dispositivo"
- [ ] Estado de ligação via WebSocket (depende do Sprint 7)

**Dependências:** Sprint 7 (eventos BT em tempo real).

---

# Fase V2 — Excelência multimédia + UX

## Sprint 10 — Controlo multimédia total 🟢 ✅

**Objetivo:** controlar tudo a partir do ecrã, como uma head unit a sério.

**Meta de sucesso:** seek, volume, shuffle e repeat funcionais e fiáveis a partir do toque.

- [x] Barra de progresso clicável → seek via `playerctl position` (estava em
      falta na UI apesar do CSS/JS já existirem)
- [x] Controlo de volume via mixer ALSA (`amixer`) com slider
- [x] Shuffle / Repeat (estado lido e comandado via `playerctl`; repeat cicla
      None → Track → Playlist, com ícone `repeat-one` no modo Track)
- [x] `/music/controls` separado do `/status` para não pesar no push de 1s
- [x] Tratar graciosamente players que não suportam seek/position (guard
      `trackDuration<=0`; backend devolve erro em vez de rebentar)
- [ ] Botão mute dedicado — slider a 0 cobre funcionalmente; fica para polish

**Dependências:** nenhuma.

---

## Sprint 11 — Capa, cache e offline 🟢

**Objetivo:** capa instantânea e sistema 100% utilizável sem internet.

**Meta de sucesso:** segunda vez que toca uma música, a capa aparece sem rede;
nenhuma feature core depende de internet.

- [ ] Cache local de capas em disco (`~/.cache/aveoos/covers`), chave artist+track
- [ ] Cache local de letras (LRCLIB) com TTL
- [ ] Fallback gracioso offline (placeholder de gradiente já existe — manter)
- [ ] Limpeza/limite de tamanho da cache (LRU)

**Dependências:** nenhuma.

---

## Sprint 12 — Fontes de áudio e chamadas 🟡 HW

**Objetivo:** mais do que Bluetooth — AUX/USB e chamadas mãos-livres.

**Meta de sucesso:** receber/atender uma chamada pelo ecrã com caller ID;
trocar de fonte de áudio sem reiniciar nada.

- [ ] Abstração de "source" (Bluetooth / AUX-in / USB) com seletor na UI
- [ ] Hands-free (HFP): atender/rejeitar, caller ID, mute
- [ ] Banner de chamada/notificação recebida sobre qualquer ecrã
- [ ] Encaminhamento de áudio correto por source (PulseAudio)

**Dependências:** Sprint 9 (BT robusto).

---

## Sprint 13 — UX OEM (tema, toque, persistência) 🟢

**Objetivo:** que pareça e responda como um sistema de fábrica premium.

**Meta de sucesso:** modo noturno automático ao anoitecer; alvos de toque
confortáveis a conduzir; definições sobrevivem a reboot.

- [ ] Tema dia/noite automático por hora (e por sensor de luz no futuro)
- [ ] Alvos de toque maiores + transições suaves entre ecrãs
- [ ] Grelha de início personalizável (ordem/visibilidade dos ícones)
- [ ] Persistência de definições (JSON ou SQLite em `~/.config/aveoos`)
- [ ] Splash de arranque a condizer com o tema

**Dependências:** nenhuma.

---

# Fase V3 — Integração no veículo

## Sprint 14 — Câmara de marcha-atrás 🔴 HW

**Objetivo:** vídeo da câmara em ecrã cheio ao meter marcha-atrás.

**Meta de sucesso:** ao engatar a marcha-atrás, a câmara aparece em <1s com
linhas de guia, e volta ao ecrã anterior ao sair.

- [ ] `CameraService` (picamera2 / V4L2)
- [ ] Trigger por GPIO do fio de marcha-atrás
- [ ] Overlay de linhas de guia
- [ ] Override de prioridade sobre qualquer ecrã ativo

---

## Sprint 15 — Dashboard OBD2 🔴 HW

**Objetivo:** ler e mostrar dados do motor.

**Meta de sucesso:** RPM, velocidade, temperatura e consumo em tempo real num
ecrã dedicado, estáveis em viagem.

- [ ] `OBDService` via adaptador ELM327 (BT/USB), lib `obd`
- [ ] Endpoint `/obd/*` + eventos de telemetria
- [ ] Ecrã dashboard (mostradores) otimizado para relance
- [ ] Avisos configuráveis (ex.: temperatura alta)

---

## Sprint 16 — Navegação offline 🔴 HW

**Objetivo:** navegar sem depender de dados móveis.

**Meta de sucesso:** traçar e seguir uma rota com mapas offline e GPS real.

- [ ] GPS via `gpsd` + `GPSService`
- [ ] Tiles offline (mbtiles) ou integração OsmAnd
- [ ] Pesquisa de moradas (Nominatim/Photon local)
- [ ] Endpoint `/gps/*`

---

## Sprint 17 — Climatização IR 🔴 HW

**Objetivo:** controlar o A/C a partir do ecrã.

**Meta de sucesso:** ligar/desligar A/C e ajustar temperatura por IR de forma fiável.

- [ ] Emissor IR + `ClimateService`
- [ ] Aprendizagem/replay de códigos IR do painel
- [ ] Controlos na UI

---

# Fase V4 — Smart & manutenção

## Sprint 18 — Assistente de voz 🔴

**Objetivo:** comandos por voz mãos-livres.

**Meta de sucesso:** wake word + comandos locais ("próxima", "volume", "navegar para…")
sem latência incomodativa.

- [ ] Wake word (Picovoice/openWakeWord)
- [ ] STT local (Whisper) para comandos
- [ ] Intenções locais → ações nos serviços existentes
- [ ] (Opcional) LLM via API para perguntas livres

---

## Sprint 19 — OTA & recuperação 🟡

**Objetivo:** atualizar e recuperar o sistema sem ligar um teclado.

**Meta de sucesso:** atualizar a partir do ecrã e recuperar automaticamente de
uma atualização falhada.

- [ ] Update pela UI (`git pull` + reinstalar deps + restart do serviço)
- [ ] Verificação de saúde pós-update com rollback automático
- [ ] Indicador de versão nas Definições

---

## Sprint 20 — Qualidade de engenharia 🟢

**Objetivo:** base de código testável, segura e de confiança.

**Meta de sucesso:** suíte de testes verde em CI; zero segredos no repositório.

- [ ] Testes pytest com `subprocess` mockado (a arquitetura já foi desenhada para isto)
- [ ] Cobertura mínima dos serviços (`bluetooth`, `music`, `power`, `system`)
- [ ] CI (GitHub Actions) a correr lint + testes
- [ ] Remover segredos mortos do Spotify de `config.py`; migrar config para `.env`
- [ ] Validação de payloads com Pydantic nos endpoints que recebem input

---

## Prioridade recomendada

1. **Fechar a V1** (Sprints 1–5 do `ROADMAP.md`).
2. **V1.5 inteira (6–9)** — é o que torna o sistema confiável num carro real.
   Dentro dela, o **Sprint 6 (energia)** é o mais crítico de todos.
3. **V2 (10–13)** para a sensação OEM.
4. **V3/V4** consoante o hardware disponível e a vontade.

> Sprints sem dependência de hardware (7, 8, 10, 11, 13, 19, 20) podem ser
> desenvolvidos e testados inteiramente no PC — bons candidatos para avançar
> enquanto o hardware do carro não está montado.
