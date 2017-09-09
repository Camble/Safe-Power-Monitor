import RPi.GPIO as GPIO
import subprocess
import os
import sys

from GpioWatcher import GpioWatcher

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
