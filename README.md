# GBZ-Power-Monitor

This is a Power Management utlity for the Gameboy Zero project.  This adds graceful shutdowns and automatic low battery alerts and shutdowns when the battery level is low.  

This is expecting the following hardware:

- Raspberry Pi Zero
- Adafruit Powerboost 1000C
- Pololu Mini Slide Switch LV

                              __________________________________________________
                             |              __________________________________  |(LowBatt)
                             |             |                      (Off Signal)| |                       
               [USB PowerIn] |      [ON/OFF Switch]   [Audio Amp AC]          | | 
                     |       |             | (on only)      ▲                 | |
                     ▼       |             ▼                |                 ▼ ▼
[Battery] ◄-► [Powerboost 1000C] -► [Pololu Switch]  --► [GBZ AC]  ◄---►  [GPIO Ports] 
                     ▲                     ▲ (off only)     |                   | 
                     |                     |                ▼                   |
         [Emergency Reset Button]          |        [Video Screen AC]           |
                                           |____________________________________|
                                           (UART TX killed on clean shutdown)

More detail can be found on this thread:

http://sudomod.com/forum/viewtopic.php?f=8&t=97

