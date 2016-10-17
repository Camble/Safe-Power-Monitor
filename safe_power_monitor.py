#!/usr/bin/env python2.7
# date: 13/10/16
# author: Camble
# version: 1.0a
# name: Safe-Power-Monitor - A utility to compliment the Safe Shutdown Switch for the Gameboy Zero project
# description: A GPIO monitor with graceful shutdown capability and video warning overlays
# source: 

import RPi.GPIO as GPIO
import os
import sys
import time

AdafruitPowerBoost  = True # Set this to False if using a generic power booster/charger module ie. a "BangGood" or "GearBest" Module

powerGPIO           = 27   # GPIO BCM 27 / Physical Pin 13
batteryGPIO         = 17   # GPIO BCM 17 / Physical Pin 11
keepAliveGPIO       = 22   # GPIO BCM 22 / Physical Pin 15

checksPerSecond     = 4    # How often to check GPIO pins (higher values *may* impact performance and battery life)
sampleRate          = 0.1  # tenth of a second
batteryTimeout      = 10   # How long in seconds before acting on low battery
powerTimeout        = 1    # How long in seconds before acting on power switch

videoAlpha          = 180  # Alpha transparency for overlaid videos

videoPlayer         = "/usr/bin/omxplayer --no-osd --layer 999999"   # Path to video player and switches for overlay layer
shutdownVideo       = "~/Safe-Power-Monitor/lowbattshutdown.mp4"      # Use no spaces or non-alphanum characters
lowalertVideo       = "~/Safe-Power-Monitor/lowbattalert.mp4"         # Use no spaces or non-alphanum characters

# ==================== DO NOT CHANGE ANYTHING BELOW THIS LINE ==================== 

class GpioWatcher():
  def __init__(self, pin, internal_pull, trigger_state):
    # Configure GPIO pin
    self.pin = pin
    self.pull = internal_pull
    self.trigger = trigger_state

    # Set edge type for event listener
    if trigger_state is 0:
      self.edge = GPIO.FALLING
    elif trigger_state is 1:
      self.edge = GPIO.RISING

    # Create a threaded event listener
    try:
      GPIO.remove_event_detect(self.pin)
      GPIO.add_event_detect(self.pin, self.edge, callback=self.Callback, bouncetime=300)

    except KeyboardInterrupt:
      GPIO.cleanup()

    # If the pin is already triggered, perform the callback
    if GPIO.input(self.pin) is trigger:
      Callback()

  def Callback():
    print "GPIO Pin " + self.pin + " was triggered!"

  pin      = None
  pull     = None
  trigger  = None
  edge     = None

class PowerWatcher(GpioWatcher):
  def Callback():
    for bounceSample in range(1, int(round(powerTimeout / sampleRate))):
      time.sleep(sampleRate)

    if GPIO.input(self.pin) is trigger:
      break

  if bounceSample is int(round(powerTimeout / sampleRate)) - 1:
    # If the power switch is placed in the off position with no bounce, shutdown
    os.system(self.action)
    try:
       sys.stdout.close()
    except:
       pass
    try:
       sys.stderr.close()
    except:
       pass
    sys.exit(0)

class BatteryWatcher(GpioWatcher):
  def Callback(channel):
    # Checking for LED bounce for the duration of the battery timeout
    for bounceSample in range(1, int(round(batteryTimeout / sampleRate))):
      time.sleep(sampleRate)

      if GPIO.input(self.pin) is not self.trigger:
         break
    
    global playerFlag   
    while playerFlag is 1:
      time.sleep(500)
       
    # If the LED is a solid condition, there will be no bounce. Launch shutdown video and then gracefully shutdown
    if bounceSample is int(round(batteryTimeout / sampleRate)) - 1:

      playerFlag = 1
      os.system(videoPlayer + " " + shutdownVideo + " --alpha 180;")
      if GPIO.input(self.pin) is not self.trigger
        break
      else:
        os.system("sudo shutdown -h now")
        playerFlag = 0
        sys.exit(0)

    # If the LED is a solid for more than 10% of the timeout, launch the low battery alert
    if bounceSample > int(round(batteryTimeout / sampleRate * 0.1)):
      playerFlag = 1
      os.system("/usr/bin/omxplayer --no-osd --layer 999999 " + lowalertVideo + " --alpha 160;")
      playerFlag = 0
      
      # Rebind GPIO event detect after system call (due to a bug with the GPIO library and threaded events)
      GPIO.remove_event_detect(self.pin)
      GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=lowBattery, bouncetime=300)
      
      # If the battery is low, continue to monitor to ensure safe shutdown after the timeout period
      self.Callback()

def main():

  # Check /boot/config.txt for dtoverlay line, and add it if required
  newLine = "dtoverlay=gpio-poweroff,gpiopin=" + keepAliveGPIO + ",active_low=\"y\""
  file = open("/boot/config,txt", "r")
  configDone = False

  # Read each line in /boot/config.txt, stop if newLine is found
  line = file.readline()
  while line:
    if line.rstrip("\n") == newLine:
      configDone = True
      break
    else:
      line = file.readline()
  file.close()

  # If newLine does not exist, add it
  if configDone is False:
    file = open(filepath, "a")
    file.write("\n" + newLine)
    configDone = True
    file.close()

  # Configure GPIO mode
  GPIO.setmode(GPIO.BCM)

  # Configure pin settings based on the choice of power supply
  if AdafruitPowerBoost is True:
    powerTriggerState       = 0               # 0 = Low, 1 = High
    batteryTriggerState     = 0               # 0 = Low, 1 = High
    powerInternalResistor   = GPIO.PUD_DOWN   # Use GPIO.PUD_UP, GPIO.PUD_DOWN, or None
    batteryInternalResistor = None            # Use GPIO.PUD_UP, GPIO.PUD_DOWN, or None

  elif AdafruitPowerBoost is False:
    powerTriggerState       = 1               # 0 = Low, 1 = High
    batteryTriggerState     = 0               # 0 = Low, 1 = High
    powerInternalResistor   = GPIO.PUD_DOWN   # Use GPIO.PUD_UP, GPIO.PUD_DOWN, or None
    batteryInternalResistor = None            # Use GPIO.PUD_UP, GPIO.PUD_DOWN, or None

  # Create some GpioWatchers
  powerWatcher = PowerWatcher(powerGPIO, powerInternalResistor, powerTriggerState)
  batteryWatcher = BatteryWatcher(batteryGPIO, batteryInternalResistor, batteryTriggerState)

# Run the program
main()

# Wait for GPIO events
delay = 1000/checksPerSecond
while True:
  time.sleep(delay)

GPIO.cleanup()
