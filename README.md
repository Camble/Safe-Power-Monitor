# GBZ-Power-Monitor V1.0 by Popcorn

This is a Power Management utlity for the Gameboy Zero project.  This adds graceful shutdowns and automatic low battery alerts and shutdowns when the battery level is low.  

Dependancies
-----------
- Retropie 3.7
- Python Module RPi.GPIO (comes installed with Retropie 3.7)
- omxplayer (comes installed with Retropie 3.7)
- Must be run as a sudoer user (the default Pi user on Retropie 3.7 is a sudoer)

Required Hardware
-----------------
- Raspberry Pi Zero
- Adafruit Powerboost 1000C
- Pololu Mini Slide Switch LV
- 2N3904 NPN transistor
- 47k resistor

Wiring Diagram
-------------
![alt tag](http://i.imgur.com/FpPDcmK.png)

Installation
-----------

From the command prompt as the Pi user:

```
cd ~;git clone https://github.com/NullCorn/GBZ-Power-Monitor.git
```

To add the monitor to the startup process

```
echo "@reboot     /usr/bin/python ~/GBZ-Power-Monitor/gbz_power_monitor.py" >> mycron; crontab mycron;rm mycron
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
