#!/bin/sh -e

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root." 1>&2
   exit 1
fi

echo "Setting up HTML Files..."
cp -Rf ./html /var/www/
chown -R www-data:www-data /var/www/html
chown root:www-data /var/www/html/.htaccess
echo "Setting up Apache Config..."
cp -f ./conf/override.conf /etc/apache2/conf-available/
cd /etc/apache2/conf-enabled
ln -s ../conf-available/override.conf override.conf
cd /etc/apache2/mods-enabled
ln -s ../mods-available/rewrite.load rewrite.load

echo "Setting up IP tables..."
sudo sysctl net.ipv4.ip_forward=1
sudo iptables --flush
sudo iptables -t nat --flush
sudo iptables -t nat -A PREROUTING -i uap0 -p udp -m udp --dport 53 -j DNAT --to-destination 10.1.1.1:53
sudo iptables -t nat -A PREROUTING -i uap0 -p tcp -m tcp --dport 80 -j DNAT --to-destination 10.1.1.1:80
sudo iptables -t nat -A PREROUTING -i uap0 -p tcp -m tcp --dport 443 -j DNAT --to-destination 10.1.1.1:80
sudo iptables -t nat -A POSTROUTING -j MASQUERADE

echo "Setting up dnsmasq..."
sudo cp /home/pi/bitshift/bin/conf/dnsmasq.conf /etc/dnsmasq.conf
