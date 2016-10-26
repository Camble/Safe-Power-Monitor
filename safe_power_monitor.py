#!/usr/bin/env python2.7
# date: 13/10/16
# author: Camble
# version: 1.0a
# name: Safe-Power-Monitor - A utility to compliment the Safe Shutdown Switch for the Gameboy Zero project
# description: A GPIO monitor with graceful shutdown capability and video warning overlays
# source: https://github.com/Camble/Safe-Power-Monitor

import RPi.GPIO as GPIO
import os
import sys
import time
import datetime
from shutil import copyfile

AdafruitPowerBoost  = True # Set this to False if using a generic power booster/charger module ie. a "BangGood" or "GearBest" Module

powerGPIO           = 27   # GPIO BCM 27 / Physical Pin 13
batteryGPIO         = 17   # GPIO BCM 17 / Physical Pin 11
keepAliveGPIO       = 22   # GPIO BCM 22 / Physical Pin 15

sampleRate          = 0.1  # tenth of a second
batteryTimeout      = 10   # How long in seconds before acting on low battery
powerTimeout        = 1    # How long in seconds before acting on power switch

videoAlpha          = 180  # Alpha transparency for overlaid videos

videoPlayer         = "/usr/bin/omxplayer --no-osd --layer 999999"    # Path to video player and switches for overlay layer
shutdownVideo       = "~/Safe-Power-Monitor/lowbattshutdown.mp4"      # Alphanumeric only. No spaces.
lowalertVideo       = "~/Safe-Power-Monitor/lowbattalert.mp4"         # Alphanumeric only. No spaces.
logFile             = "~/Safe-Power-Monitor/log.txt"                  # Alphanumeric only. No spaces.

# ==================== DO NOT CHANGE ANYTHING BELOW THIS LINE ====================

def log(int code, string message):
  file = open(logFile, "a")
  file.write(datetime.datetime.strftime("%Y-%m-%d %H:%M:%S") + "[" + str(code) + "] " + message + "\n")
  file.close()

class GpioWatcher():
  pin, pull, trigger, edge = None
  def __init__(self, gpio_pin, internal_pull, trigger_state):
    # Configure GPIO pin
    pin = gpio_pin
    pull = internal_pull
    trigger = trigger_state

    # Set edge type for event listener
    if trigger_state is 0:
      edge = GPIO.FALLING
    elif trigger_state is 1:
      edge = GPIO.RISING

    # Create a threaded event listener
    try:
      GPIO.remove_event_detect(pin)
      GPIO.add_event_detect(pin, edge, callback=callbackFunc, bouncetime=300)

    except KeyboardInterrupt:
      GPIO.cleanup()

    # If the pin is already triggered, perform the callback
    if GPIO.input(pin) is trigger:
      callbackFunc()

  def callbackFunc():
    print "GPIO Pin " + pin + " was triggered!"
    log(01, "GPIO Pin " + pin + " was triggered!")

class PowerWatcher(GpioWatcher):
  def callbackFunc():
    for bounceSample in range(1, int(round(powerTimeout / sampleRate))):
      time.sleep(sampleRate)

    if GPIO.input(pin) is trigger:
      break

  if bounceSample is int(round(powerTimeout / sampleRate)) - 1:
    # If the power switch is placed in the off position with no bounce, shutdown
    log(12, "Power switch on pin " + pin + " initiated a shutdown.")
    os.system("sudo shutdown -h now")
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
  def callbackFunc():
    # Checking for LED bounce for the duration of the battery timeout
    for bounceSample in range(1, int(round(batteryTimeout / sampleRate))):
      time.sleep(sampleRate)

      if GPIO.input(pin) is not trigger:
         break

    global playerFlag
    while playerFlag is 1:
      time.sleep(1)

    # If the LED is a solid condition, there will be no bounce. Launch shutdown video and then gracefully shutdown
    if bounceSample is int(round(batteryTimeout / sampleRate)) - 1:

      playerFlag = 1
      log(22, "Low battery on pin " + pin + " initiated a shutdown alert.")
      os.system(videoPlayer + " " + shutdownVideo + " --alpha 180;")
      if GPIO.input(pin) is not trigger
        log(26, "Low battery on pin " + pin + " was cancelled.")
        break
      else:
        log(23, "Low battery on pin " + pin + " initiated a shutdown.")
        os.system("sudo shutdown -h now")
        playerFlag = 0
        sys.exit(0)

    # If the LED is a solid for more than 10% of the timeout, launch the low battery alert
    if bounceSample > int(round(batteryTimeout / sampleRate * 0.1)):
      playerFlag = 1
      log(21, "Low battery on pin " + pin + " initiated a warning.")
      os.system("/usr/bin/omxplayer --no-osd --layer 999999 " + lowalertVideo + " --alpha 160;")
      playerFlag = 0

      # Rebind GPIO event detect after system call (due to a bug with the GPIO library and threaded events)
      GPIO.remove_event_detect(pin)
      GPIO.add_event_detect(pin, edge, callback=callbackFunc, bouncetime=300)

      # If the battery is low, continue to monitor to ensure safe shutdown after the timeout period
      callbackFunc()

def main():
  log(11, "Safe Power Monitor script running.")

  # Check /boot/config.txt for dtoverlay line, and add it if required
  newLine = "dtoverlay=gpio-poweroff,gpiopin=" + str(keepAliveGPIO) + ",active_low=\"y\""
  filepath = "/boot/config.txt"
  file = open(filepath, "r")
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
    log(81, "No dtoverlay line found for keep-alive in /boot/config.txt")
    # Backup config.txt first!
    try:
      copyfile(filepath, filepath + ".bak")
      log(82, "Backup successfully created /boot/config.txt.bak")

      # Write the new line
      try:
        file = open(filepath, "a")
        file.write("\n" + newLine)
        configDone = True
      except:
        log(87, "Could not write to /boot/config.txt. Please amend manually.")
      finally:
        file.close()
        log(83, "Successfully amended /boot/config.txt. Rebooting...")
        os.system("sudo reboot")

    except:
      log(86, "Backup failed. Write aborted. Please amend /boot/config.txt manually.")

  # Configure GPIO mode
  GPIO.setmode(GPIO.BCM)

  # Configure pin settings based on the choice of power supply
  if AdafruitPowerBoost is True:
    log(30, "Adafruit PowerBoost is selected.")
    powerTriggerState       = 0               # 0 = Low, 1 = High
    batteryTriggerState     = 0               # 0 = Low, 1 = High
    powerInternalResistor   = GPIO.PUD_DOWN   # Use GPIO.PUD_UP, GPIO.PUD_DOWN, or None
    batteryInternalResistor = None            # Use GPIO.PUD_UP, GPIO.PUD_DOWN, or None

  elif AdafruitPowerBoost is False:
    log(40, "Generic Power Supply is selected.")
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
while True:
  time.sleep(1)

GPIO.cleanup()
