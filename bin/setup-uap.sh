#! /bin/bash

echo "Setting up RougeAP"
~/bitshift/bin/extern/setup-network.sh --install --ap-ssid="plsconnect" --ap-password="lolberry" --ap-country-code="IN" --ap-ip-address="10.1.1.1" --wifi-interface="wlan0"
