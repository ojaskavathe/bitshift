#! /bin/bash

echo "Updating package sources"
sudo apt update

# apache2
echo "Installing apache2"
sudo apt install -y apache2
echo "Enabling apache2"
sudo systemctl enable apache2

# macchanger, dnsmasq, php
sudo apt install -y macchanger dnsmasq php
