import RPi.GPIO as GPIO
import subprocess

from BatteryWatcher import BatteryWatcher

class AdafruitBatteryWatcher(BatteryWatcher):
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