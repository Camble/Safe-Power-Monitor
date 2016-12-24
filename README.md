# Safe-Power-Monitor v1.0a by Camble

Background
----------
This power monitor script accompanies the Safe Shutdown PCB by Camble. Compatible with various power supplies, it monitors the power switch and reacts to low battery alerts in the form of video warning(s) and gracefully shutting down to prevent SD card corruption.

Required Hardware and Components
--------------------------------
- [Raspberry Pi Zero](https://www.raspberrypi.org/products/pi-zero/) (or Model B+, Raspberry Pi 2 and Pi 3)
- [Adafruit Powerboost 1000C](https://learn.adafruit.com/adafruit-powerboost-1000c-load-share-usb-charge-boost/overview) or a generic [BangGood/GearBest](http://banggood.com/37V-Liion-Battery-Mini-USB-To-USB-A-Power-Apply-Module-p-928948.html?p=9B1915347037201311DI) power supply module.
- Safe Shutdown PCB (PowerBoost or BangGood Edition)
- A mini DPDT slide switch (SK-22H07 included with Safe Shutdown PCB) or an original DMG slide power switch.

Dependencies
-----------
- [Retropie 3.7+](retropie.org.uk) or latest Raspbian
- Python 2.7 and Python Module RPi.GPIO (comes installed with Retropie 3.7)
- omxplayer (comes installed with Retropie 3.7)
- Must be run as a sudoer user (the default Pi user on Retropie 3.7 is a sudoer)

Installation
-----------

You will need to connect the PI Zero to Wifi and from another computer on the same WiFI network, SSH in (or use Putty on Windows):

```
ssh pi@retropie.local
```

Default password is 'raspberry'.

Copy the Safe Power Monitor script and video assets with the following command:

```
cd ~;git clone https://github.com/Camble/Safe-Power-Monitor.git
```

Now, launch the script and test that it's working properly. At this point, your /boot/config.txt will be amended automatically (if required).
```
python ~/Safe-Power-Monitor/safe_power_monitor.py
```

Once you are satified that the monitor behaves properly, add it to the startup process to complete the installation and then reboot.

```
echo "@reboot     /usr/bin/nice -n 19 /usr/bin/python ~/Safe-Power-Monitor/safe_power_monitor.py" >> mycron; crontab mycron;rm mycron
```
Automatic /boot/config.txt ediing
---------------------------------

Each time the script is run, it checks your /boot/config.txt for the keep-alive line. If it does not exist, it will add it and reboot. Below is an extract from the log file.

```
2016-12-24 13:15:02 [11] Safe Power Monitor script running.
2016-12-24 13:15:02 [80] Reading /boot/config.txt took 0.3671 seconds.
2016-12-24 13:15:02 [81] No dtoverlay line found for keep-alive in /boot/config.txt
2016-12-24 13:15:02 [82] Backup successfully created /boot/config.bak
2016-12-24 13:15:02 [83] Successfully amended /boot/config.txt. Rebooting...
2016-12-24 13:15:16 [11] Safe Power Monitor script running.
2016-12-24 13:15:16 [80] Reading /boot/config.txt took 0.2362 seconds.
2016-12-24 13:15:16 [30] Adafruit PowerBoost is selected.
```

Keeping Up-to-Date
------------------
You can make sure you have the latest updates by issuing this command

```
cd ~/Safe-Power-Monitor;git pull origin master
```


Links
-----
Thread to order Safe Shutdown Switch (PowerBoost edition):
http://sudomod.com/forum/viewtopic.php?f=3&t=1293

Thread to order Safe Shutdown Switch (BangGood edition):
http://sudomod.com/forum/viewtopic.php?f=3&t=1706

Feel free to contact me on the Sudomod forums (www.sudomod.com/forum) or on the Sudomod Discord channel (https://discordapp.com/channels/188359728454303744/188359728454303744)
