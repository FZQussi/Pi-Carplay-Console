# AveoOS — Instalação no Raspberry Pi

> Procedimento completo de instalação do sistema num Raspberry Pi 4. Para hardware/wiring ver [`HARDWARE.md`](HARDWARE.md). Para setup de desenvolvimento_local ver [`DEVELOPMENT.md`](DEVELOPMENT.md).

---

## Visão geral

Em produção o AveoOS corre num Raspberry Pi 4 com Raspberry Pi OS Lite (headless). O frontend arranca em Chromium kiosk mode e o backend em FastAPI é gerido por systemd.

```
Ignição ON → Pi liga → systemd inicia backend → Chromium kiosk abre UI → tudo pronto
Ignição OFF → ACC OFF → backend grava estado e desliga o Pi (shutdown -h now)
```

---

## 1. Pré-requisitos

**Hardware:**

- Raspberry Pi 4 (2 GB RAM mínimo, 4 GB recomendado)
- Cartão microSD classe A1, 16 GB+ (32 GB recomendado)
- Alimentação 12V → 5V/3A (ver [`HARDWARE.md`](HARDWARE.md))
- Ecrã tátil 7" (DSI oficial **ou** HDMI + USB)
- DAC (sugestão: HiFiBerry DAC+ standard) **OU** áudio pela jack 3.5 mm
- Acesso à rede (Wi-Fi ou Ethernet) para configuração inicial via SSH

**Software (na máquina de preparação):**

- Raspberry Pi Imager (<https://www.raspberrypi.com/software/>)
- `ssh` (cliente)

---

## 2. Flash e first-boot do SO

### 2.1 Gravar RPi OS Lite

1. Instalar o Raspberry Pi Imager
2. Selecionar:
   - **OS:** *Raspberry Pi OS Lite (64-bit)*
   - **Storage:** o cartão SD
3. Clicar no ícone de **engrenagem** (configuração avançada) e configurar:
   - Hostname: `aveo-pi` (ou à escolha)
   - Enable SSH → password authentication
   - Username/password: definir credenciais próprias
   - Locale:Portugal/Portuguese, Timezone: Europe/Lisbon
   - Wi-Fi SSID/password (se aplicável)
4. *Write* e ejectar o cartão quando terminar

### 2.2 Primeiro arranque

Inserir o cartão, ligar o Pi, esperar ~30 segundos, e conectar via SSH:

```bash
ssh <username>@aveo-pi.local
# ou usar o IP se mDNS não funcionar
```

### 2.3 Configurar o sistema operativo

```bash
sudo raspi-config
```

Ajustes importantes:

- **Display Options → DSI/HDMI:** consoante o ecrã
- **Performance Options → GPU Memory:** 64 MB (suficiente para kiosk)
- **Interface Options → SPI / I2C:** ativar se o ecrã tátil precisar
- **Boot Options → Desktop / CLI:** *CLI* (sem auto-login em desktop)
- **Advanced → Expand Filesystem:** confirmar cartão expandido

Seguido de:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

---

## 3. Dependências de sistema

Instalar o stack de Bluetooth, áudio e kiosk:

```bash
sudo apt install -y \
    bluetooth bluez bluez-tools \
    pulseaudio pulseaudio-module-bluetooth \
    alsa-utils \
    playerctl \
    chromium \
    xserver-xorg xinit \
    obexd-client python3-dbus \
    libgpiod-dev gpiod \
    git python3-venv python3-dev build-essential
```

- `obexd-client` + `python3-dbus`: telefone mãos-livres (HFP) — lista telefónica via PBAP
  e controlo de chamadas via D-Bus. O HFP em si vem da *telephony nativa do PipeWire*
  (não precisa do daemon oFono). Setup e detalhes em [`PHONE.md`](PHONE.md) e §10.

### 3.1 Validação

```bash
bluetoothctl --version    # >= 5.x
playerctl --version       # instalado
pulseaudio --version      # >= 14
chromium --version        # instalado
gpiodetect                # lista chips GPIO disponíveis
```

---

## 4. Configurar PulseAudio em modo sistema

Por defeito o PulseAudio corre por-utilizador; para o AveoOS correr como serviço sem login, usar systemd-user ou `pulseaudio --system`. **Nota:** o AveoOS assume **session PulseAudio** porque o kiosk corre num contexto *login* — esta nota é para futuro arranque automático sem login.

Recomendação para a V1: arranque automático com auto-login (`raspi-config` → *Desktop / CLI → Console Autologin*) e PulseAudio na sessão. Assim não é preciso seletar com `--system`.

---

## 5. Permissões Bluetooth

Por defeito, `bluetoothctl` interativo requer root, mas `bluetoothctl info <MAC>` em subprocess.run pode ser chamado pelo utilizador `aveo`. Adicionar o utilizador ao grupo:

```bash
sudo usermod -aG bluetooth <username>
```

Verificar `bluetoothd` a correr em modo *compatibility* (não *experimental*) para evitar problemas com AVRCP/A2DP:

```bash
sudo systemctl status bluetooth
sudo btmgmt info
# Se vir "Current settings: le-ready" (LE-only), passar para compat:
sudo sed -i 's/^ExecStart=.*bluetoothd.*/ExecStart=/usr/libexec/bluetooth/bluetoothd -C/' \
    /lib/systemd/system/bluetooth.service
sudo systemctl daemon-reload
sudo systemctl restart bluetooth
```

---

## 6. Instalar o AveoOS

```bash
# Em /home/<username>
cd ~
git clone <repo-url> AveoOS
cd AveoOS

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Sanity check
uvicorn backend.main:app --host 0.0.0.0 --port 8000
# Abrir browser em http://<pi>.local:8000 — confirmar que aparece a dashboard
# Ctrl+C para parar
```

---

## 7. Auto-start do backend (systemd)

Criar a unit `scripts/systemd/aveoos-backend.service`:

```ini
[Unit]
Description=AveoOS backend (FastAPI)
After=bluetooth.target network-online.target
Wants=bluetooth.target

[Service]
Type=simple
User=<username>
WorkingDirectory=/home/<username>/AveoOS
ExecStart=/home/<username>/AveoOS/.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Ativar:

```bash
sudo cp scripts/systemd/aveoos-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aveoos-backend
sudo systemctl start aveoos-backend
sudo systemctl status aveoos-backend
```

---

## 8. Kiosk mode (Chromium)

O script vive em `scripts/kiosk/aveoos-kiosk.sh` — lança o Chromium em modo kiosk a apontar
para o backend.

```bash
chmod +x scripts/kiosk/aveoos-kiosk.sh
```

Tornar executável e configurar autostart. Para V1 com auto-login CLI, usar
`~/.bash_profile` para chamar `startx` que por sua vez executa o script kiosk. Detalhes
XFCE/LXDE autostart dependem do setup — ver `DEVELOPMENT.md` se necessário.

> **Maps / GPS:** o botão *Navegação* abre o `maps.google.com` real **noutro separador**
> (fora da app), reaproveitando sempre o mesmo separador. Atenção: em `--kiosk` não há barra
> de separadores, por isso voltar ao painel precisa de teclado/gesto (`Ctrl+W` para fechar o
> mapa, `Ctrl+Tab` para alternar) ou de correr o Chromium **sem** `--kiosk`. O módulo USB GPS
> (gpsd) **não** alimenta o ponto azul do Google Maps — a geolocalização do Chromium é
> separada (IP/Google).

---

## 9. Verificações finais

```bash
# Backend
curl -s http://localhost:8000/status | python3 -m json.tool

# Bluetooth: emparelhar e ligar
bluetoothctl scan on
bluetoothctl pair <MAC>
bluetoothctl trust <MAC>
bluetoothctl connect <MAC>

# Música via playerctl
playerctl --all-players status
playerctl metadata

# Verificar kiosk a abrir o UI
# (no ecrã tátil — deve aparecer a dashboard AveoOS)
```

---

## Telefone mãos-livres (HFP + PBAP)

O controlo de chamadas (atender/recusar/desligar/marcar/mute + caller ID) vem da
**telephony nativa do PipeWire**, que expõe a API compatível `org.ofono` no system bus.
A lista telefónica vem do **obexd** (PBAP). **Não** é preciso o daemon oFono.

```bash
bash scripts/phone/setup-hfp.sh     # WirePlumber + política D-Bus + reinício
```

Depois **religar o Bluetooth no telemóvel** e confirmar o modem:

```bash
dbus-send --system --print-reply --dest=org.ofono / org.ofono.Manager.GetModems
```

- **Contactos (PBAP):** no telemóvel, autorizar "partilhar contactos / acesso à lista
  telefónica" para o dispositivo emparelhado (senão falha com OBEX `0x53`).
- **Áudio da chamada (SCO):** encaminhado pelo PipeWire native; o nível/rota podem precisar
  de afinação no hardware (ver TODOs em [`PHONE.md`](PHONE.md)).

Documentação completa da feature, arquitetura e troubleshooting: [`PHONE.md`](PHONE.md).
Off-Pi (sem telemóvel/telephony) os endpoints `/phone/*` devolvem `available: false` sem
rebentar.

---

## 10. Manutenção

### Atualizar o AveoOS

```bash
cd ~/AveoOS
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart aveoos
```

### Logs

```bash
journalctl -u aveoos-backend -f
journalctl -u bluetooth -f
```

Para detalhes de debugging, ver [`DEVELOPMENT.md`](DEVELOPMENT.md).

---

## Troubleshooting

| Sintoma | Causa provável | Resolução |
|---------|----------------|-----------|
| Backend não arranca | venv não criado ou deps em falta | `pip install -r requirements.txt` |
| `bluetoothctl: Permission denied` | utilizador fora do grupo | `sudo usermod -aG bluetooth <user>` |
| Música toca mas UI mostra "Sem Bluetooth" | `playerctl` não vê DBus da sessão | confirmar `DBUS_SESSION_BUS_ADDRESS` no service |
| Chromium abre mas o ecrã pisca | GPU mem insuficiente | raspi-config → GPU mem = 64 MB+ |
| Mapa não carrega (página em branco) | sem rede / Google indisponível | confirmar ligação à internet; o embed precisa de rede |
| Telefone mostra "sem contactos" | PBAP não autorizado no telemóvel | autorizar partilha de contactos; confirmar `obex` user service ativo |
| Chamada sem áudio | encaminhamento SCO não configurado | tuning PulseAudio/PipeWire (TODO hardware, ver Telefone HFP) |
| Reinício do Pi a cada loop | GPIO ACC mal dimensionado (V2) | filtrar hardware, ver HARDWARE.md |
