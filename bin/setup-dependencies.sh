#!/bin/sh -e

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root." 1>&2
   exit 1
fi

echo "Installing Dependencies & enabling apache2..."
sudo apt install -y macchanger dnsmasq apache2 php nmap i2c-tools python3-pip
sudo systemctl enable apache2
