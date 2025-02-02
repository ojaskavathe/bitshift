#!/bin/sh -e

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root." 1>&2
   exit 1
fi

echo "Setting up RougeAP..."
echo "This will trigger a restart after installation"
sudo ./extern/setup-network.sh --install --ap-ssid="plsconnect" --ap-password="lolberry" --ap-country-code="IN" --ap-ip-address="10.1.1.1" --wifi-interface="wlan0"
