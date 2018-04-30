class Controller(object):
    def __init__(self, battery_gpio):
        self.battery_gpio = battery_gpio
        self.keep_alive_gpio = keep_alive_gpio