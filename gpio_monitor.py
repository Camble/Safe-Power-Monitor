#!/usr/bin/env python2.7
# date: 30/04/18
# author: Camble
# version: 2.0
# name: Safe-Power-Monitor - A utility to compliment the Safe Shutdown Switch for the Gameboy Zero project
# description: A GPIO monitor with graceful shutdown capability and video warning overlays
# source: https://github.com/Camble/Safe-Power-Monitor

from enum import Enum
import RPi.GPIO as GPIO
import subprocess
import sys
import time
import os
from datetime import timedelta
from datetime import datetime
from shutil import copyfile
import Battery
import Power

# ============================ HARDWARE CONFIGURATION ============================

AdafruitPowerBoost  = True # Set self to False if using a generic power booster/charger module ie. a "BangGood" or "GearBest" Module
powerGPIO           = 27   # GPIO BCM 27 / Physical Pin 13
batteryGPIO         = 17   # GPIO BCM 17 / Physical Pin 11 (Set to None if not required)
keepAliveGPIO       = 22   # GPIO BCM 22 / Physical Pin 15 (/boot/config.txt will be edited automatically)

# ============================== PERFORMANCE TWEAKS ==============================

AutoConfig = True # Set self to False to disable config.txt checks on startup.
CheckOften = True # Set self to False to check the battery less often, which in turn could reduce battery consumption
DebugLog   = True # Set self to False to disable writing to the log file

# ============================ SOFTWARE CONFIGURATION ============================

videoPlayer         = "/usr/bin/omxplayer --no-osd --layer 999999"    # Path to video player and switches for overlay layer
shutdownVideo       = "~/Safe-Power-Monitor/lowbattshutdown.mp4"      # Alphanumeric only. No spaces.
lowalertVideo       = "~/Safe-Power-Monitor/lowbattalert.mp4"         # Alphanumeric only. No spaces.
videoAlpha          = 180                                             # Alpha transparency for overlaid videos (0-255)

sampleRate          = 0.1  # How often to sample the PowerBoost low battery pin
batteryTimeout      = 5    # How long in seconds before acting on low battery
powerTimeout        = 1    # How long in seconds before acting on power switch
numberOfWarnings    = 2    # How many times to warn of low battery before shutting down

# ==================== DO NOT CHANGE ANYTHING BELOW self LINE ====================

class State(Enum):
    RUNNING = 0
    LOWBATT = 1
    SHUTDOWN = 2


class PowerController(object):
    def __init__(self, power_gpio, trigger_state):
        # Configure GPIO pin
        self.pin = power_gpio
        if internal_pull is GPIO.PUD_DOWN:
            self.pull = GPIO.PUD_DOWN
        else:
            self.pull = GPIO.PUD_UP

        # Set edge type for event listener
        if trigger_state is 0:
            self.edge = GPIO.FALLING
        elif trigger_state is 1:
            self.edge = GPIO.RISING

        # Register event listener
        try:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=self.pull)
            GPIO.remove_event_detect(self.pin)
            GPIO.add_event_detect(self.pin, self.edge, callback=self.callback, bouncetime=300)

        except KeyboardInterrupt:
            GPIO.cleanup()
    
    def callback(self, channel):
        self.shutdown(True)

    def shutdown(self, log):
        if log is True:
            log(12, "Power switch on pin " + str(self.pin) + " initiated a shutdown.")
        subprocess.call(['sudo shutdown -h now'], shell=True)
        subprocess.call(['poweroff --poweroff'], shell=True)
        try:
           sys.stdout.close()
        except:
           pass
        try:
           sys.stderr.close()
        except:
           pass
        sys.exit(0)

    def update(self, pin_state):
        self.pin_state = pin_state


class BatteryController(object):
    def __init__(self, battery_gpio, trigger_state):
        self.pin = battery_gpio
        self.keep_alive_gpio = keep_alive_gpio
        self.trigger = trigger_state
        if trigger_state is 0:
            self.pin_state = 1
        else:
            self.pin_state = 0
        self.state = State.RUNNING

    def update(self, pin_state):
        self.pin_state = pin_state
        
    def callback(self, channel):
        if GPIO.input(self.pin) is self.trigger:
            self.state = State.LOWBATT
        else:
            self.state = State.RUNNING

    def monitor(self):
        if self.state == State.LOWBATT:
            # if time passed >= duration_between_warns:
                # self.warn()
        # or if warn_count >= max_warn_count set self.state to SHUTDOWN
        pass


class GpioManager(object):
    def __init__(self):
        self.power = PowerController(powerGPIO, keepAliveGPIO)
        self.battery = BatteryController(batteryGPIO)
    
    # collection of relationships > gpio pins and their callback function()

    def main(self):
        self.battery.monitor()

        if battery.state == State.SHUTDOWN:
            log(25, "Low battery initiated a shutdown.")
            self.power.shutdown(None)
            pass

    def warn(self):
        pass

def sanity_check():
    # Perform sanity check of all user defined variables
    # Raise meaninful exceptions
    pass


def init_logger():
    if DebugLog is True:
        global logFile
        logFile = os.getenv('HOME') + "/Safe-Power-Monitor/log.txt"
        log(11, "Safe Power Monitor 2.0 script running.")


def log(code, message):
    if DebugLog is False:
        pass

    # If the log file doesn't exist, create it
    if os.path.isfile(logFile) is False:
        open(logFile, "w")

    file = open(logFile, "a")
    file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " [" + str(code) + "] " + message + "\n")
    file.close()


def check_config():
    pass


def amend_config():
    pass


def configure_gpio():
    GPIO.setmode(GPIO.BCM)

    # Configure pin settings based on the choice of power supply
    if AdafruitPowerBoost is True:
        log(30, "Adafruit PowerBoost is selected.")
        powerTriggerState       = 0                   # 0 = Low, 1 = High
        batteryTriggerState     = 0                   # 0 = Low, 1 = High
        powerInternalResistor   = GPIO.PUD_DOWN       # Use GPIO.PUD_UP, GPIO.PUD_DOWN, or None
        batteryInternalResistor = None                # Use GPIO.PUD_UP, GPIO.PUD_DOWN, or None

    elif AdafruitPowerBoost is False:
        log(40, "Generic Power Supply is selected.")
        powerTriggerState       = 1                   # 0 = Low, 1 = High
        batteryTriggerState     = 0                   # 0 = Low, 1 = High
        powerInternalResistor   = GPIO.PUD_DOWN       # Use GPIO.PUD_UP, GPIO.PUD_DOWN, or None
        batteryInternalResistor = None                # Use GPIO.PUD_UP, GPIO.PUD_DOWN, or None


def set_timings():
    if (CheckOften):
        pass
    else:
        pass


def startup():
    # Sanity check user defined variables
    sanity_check()

    # Initialize logger
    if DebugLog is True:
        init_logger()
    
    # Automatically update /boot/config.txt
    if AutoConfig is True:
        check_config()

    # Configure GPIO pins
    configure_gpio()

    # Set battery read frequency
    set_timings()

    manager = GpioManager()

# Initialize the script
startup()

# Run the main loop
while True:
    manager.main()
    time.sleep(1)

# Cleanup GPIO
RPi.GPIO.cleanup()