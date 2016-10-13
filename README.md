# Safe-Power-Monitor v1.0a by Camble
based on Popcorn's original GBZ-Power-Monitor

Background
----------
Currently in the GameBoy Zero, the power switch works like a normal On/Off switch. The only problem is when you cut the power, it's kinda hard on the system. There's no clean dismounting of the drives. It's really just like yanking the power out. And that's been known to cause corrupted files and disks.


Required Hardware and Components
--------------------------------
- [Raspberry Pi Zero](https://www.raspberrypi.org/products/pi-zero/) (or Model B+, Raspberry Pi 2 and Pi 3)
- [Adafruit Powerboost 1000C](https://learn.adafruit.com/adafruit-powerboost-1000c-load-share-usb-charge-boost/overview)
- Safe Shutdown PCB (PowerBoost Edition)
- A mini DPDT slide switch (SK-22H07 included with Safe Shutdown PCB) or an original DMG slide power switch.

Dependencies
-----------
- [Retropie 3.7+](retropie.org.uk) or latest Raspbian
- Python 2.7 and Python Module RPi.GPIO (comes installed with Retropie 3.7)
- omxplayer (comes installed with Retropie 3.7)
- Must be run as a sudoer user (the default Pi user on Retropie 3.7 is a sudoer)

Installation
-----------

You will need to connect the PI Zero to Wifi and from another computer on the same WiFI network, SSH in (or use Putty on PCs):

```
ssh pi@retropie.local
```

Default password is 'raspberry'. At the command prompt, edit the /boot/config.txt file:

Copy the Safe Power Monitor script and video assets with the following command:

```
cd ~;git clone https://github.com/Camble/Safe-Power-Monitor.git
```

Now, launch the script and test that it's working properly
```
python ~/Safe-Power-Monitor/safe_power_monitor.py
```

Once you are satified that the monitor behaves properly, add it to the startup process to complete the installation and then reboot.

```
echo "@reboot     /usr/bin/nice -n 19 /usr/bin/python ~/Safe-Power-Monitor/safe_power_monitor.py" >> mycron; crontab mycron;rm mycron
```

Keeping Up-to-Date
------------------
You can make sure you have the latest updates by issuing this command

```
cd ~/Safe-Power-Monitor;git pull origin master
```

Video Examples
--------------
https://www.youtube.com/watch?v=TRkEfD04unk
Low Battery Warning

https://www.youtube.com/watch?v=nRJ42oSrIg4
Power Switch test

Links
-----
More detail can be found on this thread:

http://sudomod.com/forum/viewtopic.php?f=8&t=97

Contact
-------
Questions, Comments, Kudos, Free Beer to abandonedemails@gmail.com. Please put "sudomod" somewhere in the subject or your message will not be received.
