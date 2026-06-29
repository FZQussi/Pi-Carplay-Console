#!/usr/bin/env bash
# Lança o AveoOS em kiosk: um window manager mínimo (openbox) + o Chromium
# do dashboard. O WM é necessário para o Maps (janela Chromium própria do
# Google Maps) poder coexistir e ser levantado/baixado pelo backend via
# wmctrl. Sem WM havia só uma janela fullscreen e não dava para alternar.
#
# Pensado para correr como sessão do utilizador (auto-login CLI + startx, ou
# LXDE autostart).

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

# WM mínimo para stacking/levantar janelas (dashboard vs Maps).
# ponytail: openbox é o WM mais leve que dá stacking; matchbox se a RAM apertar.
openbox &
sleep 1

# Dashboard. --class fixa o WM_CLASS para o wmctrl o distinguir do Maps
# (ver backend/services/maps.py: DASH_CLASS = "aveoos-dash").
exec chromium \
    --noerrdialogs \
    --disable-infobars \
    --class=aveoos-dash \
    --kiosk "$URL" \
    --autoplay-policy=no-user-gesture-required
