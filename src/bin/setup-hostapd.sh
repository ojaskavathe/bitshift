#!/bin/sh -e

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root." 1>&2
   exit 1
fi

echo "Replacing hostapd.conf..."
sudo cp ./conf/hostapd.conf /etc/hostapd/hostapd.conf

echo "Restart for changes to take effect"
