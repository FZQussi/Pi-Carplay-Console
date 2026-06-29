#!/usr/bin/env bash
# Configura o telefone mãos-livres (HFP) no Pi.
#
# O controlo de chamadas vem da *telephony nativa do PipeWire*, que expõe a
# API compatível `org.ofono` no system bus. Não é preciso o daemon oFono — se
# estiver instalado, é desligado para não roubar o nome `org.ofono`.
#
# Idempotente. Correr como o utilizador do kiosk (NÃO root) — usa o teu uid
# para a política D-Bus e para reiniciar o WirePlumber da sessão.
#   bash scripts/phone/setup-hfp.sh
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
USER_NAME="$(id -un)"

echo "==> WirePlumber: backend HFP nativo + provide-ofono"
mkdir -p "$HOME/.config/wireplumber/wireplumber.conf.d"
cp "$HERE/51-bluez-ofono.conf" "$HOME/.config/wireplumber/wireplumber.conf.d/"

echo "==> D-Bus: permitir a $USER_NAME possuir org.ofono no system bus"
sudo tee /etc/dbus-1/system.d/10-wireplumber-telephony.conf >/dev/null <<XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-Bus Bus Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
  <policy user="$USER_NAME">
    <allow own="org.ofono"/>
  </policy>
  <policy context="default">
    <allow send_destination="org.ofono"/>
    <allow receive_sender="org.ofono"/>
  </policy>
</busconfig>
XML

echo "==> Desligar oFono daemon se existir (rouba o nome org.ofono)"
sudo systemctl disable --now ofono dundee 2>/dev/null || true

echo "==> Recarregar D-Bus + reiniciar WirePlumber"
sudo dbus-send --system --type=method_call --dest=org.freedesktop.DBus \
  / org.freedesktop.DBus.ReloadConfig 2>/dev/null || true
systemctl --user restart wireplumber

echo
echo "Feito. Religa o Bluetooth NO TELEMÓVEL para registar o HFP."
echo "Confirmar: dbus-send --system --print-reply --dest=org.ofono / org.ofono.Manager.GetModems"
echo "Contactos (PBAP): autorizar 'partilha de contactos' no telemóvel."
