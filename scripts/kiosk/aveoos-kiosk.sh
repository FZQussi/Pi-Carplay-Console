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

exec chromium \
    --noerrdialogs \
    --disable-infobars \
    --kiosk "$URL" \
    --autoplay-policy=no-user-gesture-required
