from gpioexp import I2c_expander


class PWM_servo:
    def __init__(self, id, pin, expander):
        self._expander = expander
        self.pin = pin
        self.adc_map = None
        self.sensor = None
        self._angle
        return
    
    def write(self, deg):
        inp = float(deg/90)
        self._angle = inp
        pulse = 1000 + inp*1000
        self._expander.analogWrite(self.pin, pulse / 20000)
        return

    def add_sensor(self, pin):
        self.sensor = pin
        return

    @property
    def angle(self):
        if self.sensor is not None:
            return self._angle
        else:
            return self._expander.analogRead(self.sensor)


class PWM_servo_handler:
    def __init__(self, i2c_addr=0X2A):
        self._expanders = { 0: I2c_expander(0, i2c_addr) }
        self._servos = {}
        for exp in self._expanders.values():
            exp.pwmFreq(50)

    def add_servo(self, id, pin, expander_id=None):
        if expander is None:
            expander = self._expanders[0]
        elif expander_id not in self._expanders:
            raise ValueError("No expander with such ID. Please use add_exp(id, addr)")

        self._servos[id] = PWM_servo(pin, expander)
        return

    def add_exp(self, id, addr):
        self._expanders[id] = I2c_expander(addr)
        return

    def add_servo_sensor(self, id, pin):
        self._servos[id].add_sensor(pin)
        return
    
    def servo_write(self, id, deg):
        servo = self._servos[id]
        servo.write(deg)
        return

    def servo_read(self, id):
        return self._servos[id].angle

