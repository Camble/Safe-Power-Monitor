# GBZ-Power-Monitor V1.0a by Popcorn 🍿
PowerBoost edition (amended by Camble)

UPDATE
------
There are multiple reports that [Camble](http://sudomod.com/forum/memberlist.php?mode=viewprofile&u=76)'s Graceful Shutdown hardware solution works perfectly and with the ability to close the EN pin on the Powerboost. Something that the Pololu solution cannot do which was annoying to some. So, I would strongly consider using [his hardware method](http://sudomod.com/forum/viewtopic.php?f=22&p=10968#p10968) if you have not already purchased a pololu switch. You can still use my monitor also with the low battery warning along with his solution (with a slight modification of one line of code). I will be testing the circuit and revising my instructions once I'm able to replicate everything and it's working well. Thanks!

ORIGINAL POLOLU SOLUTION BELOW:

This is a Power Management utlity which is primarily built for the [Gameboy Zero](http://sudomod.com/hi/) project.  This adds graceful shutdowns from the main power switch and automatic low battery alerts and shutdowns when the battery level is low.  This is meant to be used in concert with the provided list of required hardware and components within a Retropie 3.7+ environment.

This solution will work in any portable battery powered raspberry PI unit that uses a Powerboost 1000C. So not only can this be applied to the Gameboy Zero project, but also to the Adafruit Pi Grrl and Pi Grrl 2 projects as well as a wide variety of portable retro gaming systems or IoT solutions that use the Raspberry Pi and a Powerboost 1000C

Background
----------
Currently in the GBZ, the power switch works like a normal On/Off switch. The only problem is when you cut the power, it's kinda hard on the system. There's no clean dismounting of the drives. It's really just like yanking the power out. And that's been known to cause corrupted files and disks.

My goal is to add an inexpensive and small electronic switch that will take care of the killing the power part, but only after a clean shutdown process. After some research, both the Pololu Mini Pushbutton LV or the Pololu Mini Slider LV will both work and fits our needs. They are basically identical in size and price ($5) with a couple extra features on the pushbutton version.

The main power switch will toggle ON the Pololu switch (but only ON, not off). Then, we need 3 GPIO pins mapped, one as output, and two as input. Once the unit is turned on, we use the built-in UART TX pin and send a signal to the ON pin of the electric switch which overrides it to remain on. (Alternatively, for the Pololu Mini Push Button switch, we use a GPIO pin mapped with the GPIO-Poweroff driver which maps to the OFF pin which tells the switch to shut off when we successfully power off). This ensures the system remains on until we are ready to shut it off. Another GPIO input pin will read the setting of the power switch, so we can tell when the user wants to shutdown. And lastly, the final GPIO input pin will go to the pin attached to the Low Battery LED of the Powerboost, so we can gracefully power down automatically when the battery is very low. A nice little add.

Required Hardware and Components
--------------------------------
- [Raspberry Pi Zero](https://www.raspberrypi.org/products/pi-zero/) (or Model B+, Raspberry Pi 2 and Pi 3)
- [Adafruit Powerboost 1000C](https://learn.adafruit.com/adafruit-powerboost-1000c-load-share-usb-charge-boost/overview)
- [Pololu Mini Slide Switch LV](https://www.pololu.com/product/2810) or [Pololu Mini Push Button LV](https://www.pololu.com/product/2808)
- [2N3904 NPN transistor](https://en.wikipedia.org/wiki/2N3904)
- [47k resistor](http://resisto.rs/#47K)
- A mini SPDT or DPDT latching push and hold switch (for emergency resets and prolonged storage)
- Original DMG (or equivalant) SPDT Slide Power Switch

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

Default password is 'raspberry'.  Next at the command prompt, copy this monitor and the video assets with the following command:

```
cd ~;git clone https://github.com/Camble/GBZ-Power-Monitor_PB.git
```

Now, launch the Monitor manually and test that it's working properly
```
python ~/GBZ-Power-Monitor/gbz_power_monitor.py
```

Once you are satified that the monitor behaves properly, add the monitor to the startup process to complete the installation and then reboot to make it live.

```
echo "@reboot     /usr/bin/nice -n 19 /usr/bin/python ~/GBZ-Power-Monitor/gbz_power_monitor.py" >> mycron; crontab mycron;rm mycron
```

Keeping Up-to-Date
------------------
I'm always tinkering with the script to fix bugs and improve it's stablity.  There's a bunch of changes I'm planning to add including the ability to detect when the power is plugged back in, which would cancel the shutdown process.  Presently, once the shutdown process is activated, it will shutdown even if you had rushed to go plug in the unit.  I also want to add logging and implement proper threaded processes.  Right now, it's a bit uglier than I would want.

So, as I continue to tinker and add these things, you can make sure you have the latest updates by issuing this command

```
cd ~/GBZ-Power-Monitor;git pull origin master
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
