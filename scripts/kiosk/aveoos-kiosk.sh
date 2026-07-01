#!/usr/bin/env bash
# Lança Chromium em kiosk apontando para o backend AveoOS.
# Pensado para correr como sessão do utilizador (auto-login CLI + startx, ou LXDE autostart).

set -e

URL="${AVEOOS_URL:-http://localhost:8000}"

# Esperar que o backend esteja disponível
until curl -sf "$URL/status" >/dev/null 2>&1; do
    echo "A esperar pelo backend em $URL..."
    sleep 2
done

# Desligar cursor, screen blanking, dpms
xset -dpms
xset s off

# Cache em sítio conhecido e limpa a cada arranque. O kiosk reinicia em cada
# update OTA; sem isto o Chromium serve HTML/CSS/JS em cache (já mostrou
# marcadores de merge antigos depois de um update). Limpar garante UI fresca.
CACHE_DIR="/tmp/aveoos-chromium-cache"
rm -rf "$CACHE_DIR"

# Flags afinadas para o Pi 4:
#  - GPU rasterization + ignorar a blocklist → compositing/scroll na GPU
#    (VideoCore VI) em vez do CPU. É o ganho de fluidez maior no kiosk.
#  - process-per-site: um só site (o backend local) → menos processos e RAM.
#  - disable-background-networking/component-update/sync/translate: cortam
#    tráfego e CPU em idle que o Chromium faz por defeito e que aqui não
#    serve para nada (sem login, sem extensões, single-page).
# ponytail: se num Pi/Chromium específico o GPU raster der artefactos,
# tira --enable-gpu-rasterization e --ignore-gpu-blocklist; o resto é seguro.
exec chromium \
    --noerrdialogs \
    --disable-infobars \
    --kiosk "$URL" \
    --disk-cache-dir="$CACHE_DIR" \
    --autoplay-policy=no-user-gesture-required \
    --ignore-gpu-blocklist \
    --enable-gpu-rasterization \
    --process-per-site \
    --no-first-run \
    --disable-translate \
    --disable-sync \
    --disable-component-update \
    --disable-background-networking
