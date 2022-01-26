from gpioexp import gpioexp


class Pwm_servo_handler:
    def __init__(self, i2c_addr=0X2A):
        self._expanders = { 0: gpioexp(i2c_addr) }
        self._servos = {}
        for exp in self._expanders.values():
            exp.pwmFreq(50)

    def add_servo(self, id, pin, expander=None):
        if expander is None:
            expander = self._expanders[0]
        self._servos[id] = { "pin": pin, "exp": expander }
        return

    def servo_write(self, id, deg):
        servo = self._servos[id]
        inp = float(deg/90)
        pulse = 1000 + inp*1000
        servo["exp"].analogWrite(servo["pin"], pulse / 20000)
        return

    def add_exp(self, id, addr):
        self._expanders[id] = gpioexp(addr)
        return


if __name__ == "__main__":
    print("testing servo on pin 7")
    handler = Pwm_servo_handler()
    handler.add_servo(0, 7)
    handler.servo_write(0, 45)
