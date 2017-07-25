from GpioWatcher import GpioWatcher

class PowerWatcher(GpioWatcher):
  def callbackFunc(self, channel):
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