#!/bin/bash

set -e

# Determine script directory to allow running from any CWD
REMOTELED_SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#Update packages
sudo apt-get update
#Get nodejs package keys to install latest releases of nodejs
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
#Install nodejs on raspberry pi
sudo apt-get install nodejs
#Upgrade all packages of raspberry pi (optional)
sudo apt-get upgrade -y

#Convert dos files to unix
dos2unix "$REMOTELED_SETUP_DIR/install.sh"
dos2unix "$REMOTELED_SETUP_DIR/node/start.sh"
dos2unix "$REMOTELED_SETUP_DIR/python/start.sh"

#Copy code files in /home/pi/ folder (If username is pi)
sudo mkdir -p /usr/local/remoteled/
sudo cp -r "$REMOTELED_SETUP_DIR/python" /usr/local/remoteled/
sudo cp -r "$REMOTELED_SETUP_DIR/node" /usr/local/remoteled/
sudo cp "$REMOTELED_SETUP_DIR/splash.png" /usr/local/remoteled/
sudo cp "$REMOTELED_SETUP_DIR/kiosk.sh" /usr/local/remoteled/

sudo chmod -R 777 /usr/local/remoteled/

#Turn on Bluetooth
sudo hciconfig hci0 up

#Copy splash image on path to replace the raspberry pi logo with splash screen
sudo cp "$REMOTELED_SETUP_DIR/splash.png" /usr/share/plymouth/themes/pix/splash.png

#Install python libraries required for bluetooth and communication with web gui
cd /usr/local/remoteled/python
sudo apt-get install python3-bluez python3-pip python3-dev libbluetooth-dev -y
sudo apt-get install libcairo2-dev libjpeg-dev libgif-dev -y
sudo apt install build-essential libdbus-glib-1-dev libgirepository1.0-dev -y
#In latest python environments, installing libraries is disabled without virtual environment so creating and activating a venv
python3 -m venv bt
source bt/bin/activate
#Installing python packages
pip3 install dbus-python bluezero uuid RPi.GPIO paho-mqtt
pip3 install git+https://github.com/pybluez/pybluez.git#egg=pybluez
deactivate

#Install required nodejs packages/libraries
cd /usr/local/remoteled/node/
npm install

#Install nginx web server to serve web gui
sudo apt-get install nginx -y
#Install mosquitto broker to communicate between python/node and web gui
sudo apt-get install mosquitto -y

cd "$REMOTELED_SETUP_DIR"

#Copy Web GUI files in apache/nginx path at /var/www/html
sudo cp -r web/* /var/www/html/

if [ -z "${DISPLAY}" ]; then
    export DISPLAY=:0
fi

#Change wallpaper with our default image
pcmanfm -w /usr/local/remoteled/splash.png

#Disable boot log display 
sudo sed -i 's/message_sprite = Sprite();//g' /usr/share/plymouth/themes/pix/pix.script
sudo sed -i 's/message_sprite.SetPosition(screen_width * 0.1, screen_height * 0.9, 10000);//g' /usr/share/plymouth/themes/pix/pix.script
sudo sed -i 's/my_image = Image.Text(text, 1, 1, 1);//g' /usr/share/plymouth/themes/pix/pix.script
sudo sed -i 's/message_sprite.SetImage(my_image);//g' /usr/share/plymouth/themes/pix/pix.script

#Rebuild boot file to show latest splash screen and hide unnecessary boot logs
sudo plymouth-set-default-theme --rebuild-initrd pix

#make Autostart files executable
sudo chmod +x /usr/local/remoteled/node/start.sh
sudo chmod +x /usr/local/remoteled/python/start.sh
sudo chmod +x /usr/local/remoteled/kiosk.sh

sudo cp "$REMOTELED_SETUP_DIR/python/remoteled-python.service" /etc/systemd/system/remoteled-python.service
sudo cp "$REMOTELED_SETUP_DIR/node/remoteled-node.service" /etc/systemd/system/remoteled-node.service

CURRENT_USER=$(whoami)
sudo sed -i "s/USERNAME_PLACEHOLDER/${CURRENT_USER}/g" /etc/systemd/system/remoteled-python.service
sudo sed -i "s/USERNAME_PLACEHOLDER/${CURRENT_USER}/g" /etc/systemd/system/remoteled-node.service

sudo chmod 644 /etc/systemd/system/remoteled-python.service
sudo chmod 644 /etc/systemd/system/remoteled-node.service

sudo systemctl daemon-reload

# Configure MQTT broker only if the lines do not already exist
mosquitto_conf="/etc/mosquitto/mosquitto.conf"
if ! grep -q "allow_anonymous true" "$mosquitto_conf"; then
    echo -e "\nallow_anonymous true\n\nlistener 1883\nprotocol mqtt\n\nlistener 8083\nprotocol websockets" | sudo tee -a "$mosquitto_conf"
fi

# Add Chromium autostart configuration if not already present
wayfire_conf="$HOME/.config/wayfire.ini"
if ! grep -q "remoteled/kiosk.sh" "$wayfire_conf"; then
    echo -e "\n\n[autostart]\nchromium = /usr/local/remoteled/kiosk.sh" | sudo tee -a "$wayfire_conf"
fi

# Disable default splash boot info only if not already present
if ! grep -q "disable_splash=1" /boot/config.txt; then
    echo "disable_splash=1" | sudo tee -a /boot/config.txt
fi

# Modify boot command line options if not already present
cmdline_file="/boot/cmdline.txt"
if ! grep -q "logo.nologo" "$cmdline_file"; then
    sudo sed -i 's/console=tty1/console=tty3/g' "$cmdline_file"
    sudo sed -i '1s/$/ logo.nologo vt.global_cursor_default=0/' "$cmdline_file"
fi

# Hide navbar on Raspberry Pi if not already commented out
lxde_autostart="/etc/xdg/lxsession/LXDE-pi/autostart"
if ! grep -q "^# " "$lxde_autostart"; then
    sudo sed -i '1s/^/# /' "$lxde_autostart"
fi

# Disable autostart panel in Wayfire if not already commented out
wayfire_defaults="/etc/wayfire/defaults.ini"
if ! grep -q "^# autostart0 = wfrespawn wf-panel-pi" "$wayfire_defaults"; then
    sudo sed -i '/^autostart0 = wfrespawn wf-panel-pi/s/^/# /' "$wayfire_defaults"
fi

#Reboot pi
echo "Setup Finished. Please reboot"
