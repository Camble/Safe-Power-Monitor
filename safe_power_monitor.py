#!/usr/bin/env python2.7
# date: 13/10/16
# author: Camble
# version: 1.0a
# name: Safe-Power-Monitor - A utility to compliment the Safe Shutdown Switch for the Gameboy Zero project
# description: A GPIO monitor with graceful shutdown capability and video warning overlays
# source: https://github.com/Camble/Safe-Power-Monitor

import RPi.GPIO as GPIO
import subprocess
import sys
import time
import os
from datetime import timedelta
from datetime import datetime
from shutil import copyfile

AdafruitPowerBoost  = True # Set this to False if using a generic power booster/charger module ie. a "BangGood" or "GearBest" Module

powerGPIO           = 27   # GPIO BCM 27 / Physical Pin 13
batteryGPIO         = 17   # GPIO BCM 17 / Physical Pin 11 (Set to None if not required)
keepAliveGPIO       = 22   # GPIO BCM 22 / Physical Pin 15 (/boot/config.txt will be edited automatically)

sampleRate          = 0.1  # How often to sample a pin before acting
batteryTimeout      = 5    # How long in seconds before acting on low battery
powerTimeout        = 1    # How long in seconds before acting on power switch
numberOfWarnings    = 2    # How many times to warn of low battery before shutting down

videoAlpha          = 180  # Alpha transparency for overlaid videos (0-255)

videoPlayer         = "/usr/bin/omxplayer --no-osd --layer 999999"    # Path to video player and switches for overlay layer
shutdownVideo       = "~/Safe-Power-Monitor/lowbattshutdown.mp4"      # Alphanumeric only. No spaces.
lowalertVideo       = "~/Safe-Power-Monitor/lowbattalert.mp4"         # Alphanumeric only. No spaces.

# ==================== DO NOT CHANGE ANYTHING BELOW THIS LINE ====================

def log(code, message):
  # If the log file doesn't exist, create it
  if os.path.isfile(logFile) is False:
    open(logFile, "w")

  file = open(logFile, "a")
  file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " [" + str(code) + "] " + message + "\n")
  file.close()

class GpioWatcher(object):
  def __init__(self, gpio_pin, internal_pull, trigger_state):
    # Configure GPIO pin
    self.pin = gpio_pin
    self.trigger = trigger_state
    if internal_pull is GPIO.PUD_DOWN:
      self.pull = GPIO.PUD_DOWN
    else:
      self.pull = GPIO.PUD_UP

    # Set edge type for event listener
    if trigger_state is 0:
      self.edge = GPIO.FALLING
    elif trigger_state is 1:
      self.edge = GPIO.RISING

    # Create a threaded event listener
    try:
      GPIO.setup(self.pin, GPIO.IN, pull_up_down=self.pull)
      GPIO.remove_event_detect(self.pin)
      GPIO.add_event_detect(self.pin, self.edge, callback=self.callbackFunc, bouncetime=300)

    except KeyboardInterrupt:
      GPIO.cleanup()

    # If the pin is already triggered, perform the callback
    if GPIO.input(self.pin) is self.trigger:
      self.callbackFunc()

  def callbackFunc(self, channel):
    log(99, "GPIO Pin " + str(self.pin) + " was triggered!")

class PowerWatcher(GpioWatcher):
  def callbackFunc(self, channel):
    for bounceSample in range(1, int(round(powerTimeout / sampleRate))):
      time.sleep(sampleRate)

    if GPIO.input(self.pin) is not self.trigger:
      log(13, "Shutdown was cancelled due to switch bounce on pin " + str(self.pin) + ".")
      return

    if bounceSample is int(round(powerTimeout / sampleRate)) - 1:
      # If the power switch is placed in the off position with no bounce, shutdown
      log(12, "Power switch on pin " + str(self.pin) + " initiated a shutdown.")
      subprocess.call(['sudo shutdown -h now'], shell=True)
      subprocess.call(['poweroff'], shell=True)
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
  def __init__(self, gpio_pin, internal_pull, trigger_state):
    GpioWatcher.__init__(self, gpio_pin, internal_pull, trigger_state)
    self.warnCount = 0
    self.playerFlag = 0
    self.previousWarn = None
    self.callbackTriggered = 0

  def warn(self):
    # If the maximum warning count has been reached, skip it and shutdown
    if self.warnCount >= numberOfWarnings:
      shutdown()
    else:
      self.warnCount += 1
      self.playerFlag = 1
      self.previousWarn = time.time()
      log(23, "Low battery warning number " + warnCount + " was displayed.")
      os.system(videoPlayer + " " + lowalertVideo + " --alpha " + videoAlpha + ";")
      playerFlag = 0

      # Rebind GPIO event detect after system call (due to a bug with the GPIO library and threaded events)
      GPIO.remove_event_detect(self.pin)
      GPIO.add_event_detect(self.pin, self.edge, callback=self.callbackFunc, bouncetime=300)

  def shutdown(self):
    playerFlag = 1
    os.system(videoPlayer + " " + shutdownVideo + " --alpha " + videoAlpha + ";");
    playerFlag = 0
    # Last chance to plug the charger in!
    if GPIO.input(self.pin) is not trigger:
      log(26, "Low battery on pin " + str(self.pin) + " was cancelled.")
      return
    else:
      log(25, "Low battery on pin " + str(self.pin) + " initiated a shutdown.")
      subprocess.call(['sudo shutdown -h now'], shell=True)
      subprocess.call(['poweroff --poweroff'], shell=True)
      sys.exit(0)

  def monitor(self):
    if self.callbackTriggered is 0 or self.playerFlag is 1:
      return
    if self.previousWarn is None:
      self.warn()
    else:
      elapsed = time.time() - self.previousWarn
      if elapsed >= 300:
        self.warnCount = 0
        self.playerFlag = 0
        self.previousWarn = None
        self.callbackTriggered = 0
      elif elapsed >= 60:
        self.warn()

  def callbackFunc(self, channel):
    if GPIO.input(self.pin) is not self.trigger:
      self.callbackTriggered = 0
      return

    else:
      self.callbackTriggered = 1
      self.monitor()

class BatteryWatcher_PB(BatteryWatcher):
  def callbackFunc(self, channel):
    # Checking for LED bounce for the duration of the battery timeout
    for bounceSample in range(1, int(round(batteryTimeout / sampleRate))):
      time.sleep(sampleRate)
      if GPIO.input(self.pin) is not self.trigger:
         break

    while self.playerFlag is 1:
      time.sleep(1)

    # If the LED is a solid condition, there will be no bounce. Launch shutdown video and then gracefully shutdown
    if bounceSample is int(round(batteryTimeout / sampleRate)) - 1:
      self.shutdown()

    # If the LED is a solid for more than 10% of the timeout, launch the low battery alert
    if bounceSample > int(round(batteryTimeout / sampleRate * 0.1)):
      self.monitor()

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

      # Write the new line
      try:
        with open("/boot/config.txt", "r") as f:
          s = f.read() + "\n" + newLine
          with open("/tmp/config.txt", "w") as outf:
            outf.write(s)

        subprocess.call(['sudo cp /tmp/config.txt /boot/config.txt'], shell=True)
        subprocess.call(['sudo rm /tmp/config.txt'], shell=True)
        log(83, "Successfully amended /boot/config.txt. Rebooting...")
        print("Successfully amended /boot/config.txt. Rebooting...")
        subprocess.call(['sudo reboot'], shell=True)
        time.sleep(5)

      except:
        log(87, "Could not write to /boot/config.txt. Please amend manually.")

      finally:
        file.close()

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
  if (batteryGPIO is not None):
    playCount = 0
    if (AdafruitPowerBoost is True):
      batteryWatcher = BatteryWatcher_PB(batteryGPIO, batteryInternalResistor, batteryTriggerState)
    else:
      batteryWatcher = BatteryWatcher(batteryGPIO, batteryInternalResistor, batteryTriggerState)

# Run the program
main()

# Wait for GPIO events
while True:
  #batteryWatcher.monitor()
  time.sleep(1)

GPIO.cleanup()
