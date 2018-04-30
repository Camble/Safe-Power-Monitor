class Controller(object):
    def __init__(self, power_gpio, keep_alive_gpio):
        self.power_gpio = power_gpio
        self.keep_alive_gpio = keep_alive_gpio