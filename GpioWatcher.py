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
