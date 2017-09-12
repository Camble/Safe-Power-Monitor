import ptvsd

ptvsd.enable_attach('secret')

#!/usr/bin/env python2.7
# date: 13/10/16
# author: Camble
# version: 1.0a
# name: Safe-Power-Monitor - A utility to compliment the Safe Shutdown Switch for the Gameboy Zero project
# description: A GPIO monitor with graceful shutdown capability and video warning overlays
# source: https://github.com/Camble/Safe-Power-Monitor

AdafruitPowerBoost  = True # Set this to False if using a generic power booster/charger module ie. a "BangGood" or "GearBest" Module
DebugLog            = True # Set this to False to disable writing to the log file

powerGPIO           = 27   # GPIO BCM 27 / Physical Pin 13
batteryGPIO         = 17   # GPIO BCM 17 / Physical Pin 11 (Set to None if not required)
keepAliveGPIO       = 22   # GPIO BCM 22 / Physical Pin 15 (/boot/config.txt will be edited automatically)

sampleRate          = 0.1  # How often to sample the PowerBoost low battery pin
batteryTimeout      = 5    # How long in seconds before acting on low battery
powerTimeout        = 1    # How long in seconds before acting on power switch
numberOfWarnings    = 2    # How many times to warn of low battery before shutting down

videoAlpha          = 180  # Alpha transparency for overlaid videos (0-255)

videoPlayer         = "/usr/bin/omxplayer --no-osd --layer 999999"    # Path to video player and switches for overlay layer
shutdownVideo       = "~/Safe-Power-Monitor/lowbattshutdown.mp4"      # Alphanumeric only. No spaces.
lowalertVideo       = "~/Safe-Power-Monitor/lowbattalert.mp4"         # Alphanumeric only. No spaces.

# ==================== DO NOT CHANGE ANYTHING BELOW THIS LINE ====================

import RPi.GPIO as GPIO
import subprocess
import sys
import time
import os
from PowerWatcher import PowerWatcher
from datetime import timedelta
from datetime import datetime
from shutil import copyfile

if AdafruitPowerBoost is True:
	from AdafruitBatteryWatcher import AdafruitBatteryWatcher
else:
	from BatteryWatcher import BatteryWatcher

def log(code, message):
  if DebugLog is True:
    # If the log file doesn't exist, create it
    if os.path.isfile(logFile) is False:
      open(logFile, "w")

    file = open(logFile, "a")
    file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " [" + str(code) + "] " + message + "\n")
    file.close()

def main():
  global logFile
  logFile = os.getenv('HOME') + "/Safe-Power-Monitor/log.txt"

  log(11, "Safe Power Monitor script running.")

  time_start = datetime.now()
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
  time_end = datetime.now()
  diff = time_end - time_start
  log(80, "Reading /boot/config.txt took " + str(diff.seconds) + "." + str(diff.microseconds) + " seconds.")

  # If newLine does not exist, add it
  if configDone is False:
    log(81, "No dtoverlay line found for keep-alive in /boot/config.txt")
    # Backup config.txt first!
    try:
      subprocess.call(['sudo cp /boot/config.txt /boot/config.bak'], shell=True)
      log(82, "Backup successfully created /boot/config.bak")

    except:
      print("Backup failed. Write aborted. Please amend /boot/config.txt manually.")
      log(86, "Backup failed. Write aborted. Please amend /boot/config.txt manually.")

    else:
      # Write the new line
      try:
        with open("/boot/config.txt", "r") as f:
          s = f.read() + "\n" + newLine
          with open("/tmp/config.txt", "w") as outf:
            outf.write(s)

        subprocess.call(['sudo cp /tmp/config.txt /boot/config.txt'], shell=True)
        subprocess.call(['sudo rm /tmp/config.txt'], shell=True)
        print("Successfully amended /boot/config.txt. Rebooting...")
        log(83, "Successfully amended /boot/config.txt. Rebooting...")
        subprocess.call(['sudo reboot'], shell=True)
        time.sleep(5)

      except:
        print("Could not write to /boot/config.txt. Please amend manually.")
        log(87, "Could not write to /boot/config.txt. Please amend manually.")

      finally:
        file.close()

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

  if (batteryGPIO is not None):
    playCount = 0
    batteryWatcher = BatteryWatcher(batteryGPIO, batteryInternalResistor, batteryTriggerState)

    #if (AdafruitPowerBoost is True):
    #  batteryWatcher = AdafruitBatteryWatcher(batteryGPIO, batteryInternalResistor, batteryTriggerState)
    #else:
    #  batteryWatcher = BatteryWatcher(batteryGPIO, batteryInternalResistor, batteryTriggerState)

# Run the program
main()

# Wait for GPIO events
while True:
  #batteryWatcher.monitor()
  time.sleep(1)

GPIO.cleanup()
