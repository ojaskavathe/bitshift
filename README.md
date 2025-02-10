# bitshift
a thing to break into stuff

# on fresh image
1. `sudo apt update && sudo apt install git`
2. clone the repo on the pi
3. cd into the bin directory
4. `chmod -R +x ./*`
5. `sudo ./setup-dependencies.sh`
6. `sudo ./setup-uap.sh`
7. restart
8. `sudo ./setup-hostapd.sh`
9. `sudo ./setup-eviltwin.sh`
10. restart

# i2c
`sudo raspi-config` -> enable i2c interface
