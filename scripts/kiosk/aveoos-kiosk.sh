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

exec chromium \
    --noerrdialogs \
    --disable-infobars \
    --kiosk "$URL" \
    --disk-cache-dir="$CACHE_DIR" \
    --autoplay-policy=no-user-gesture-required
