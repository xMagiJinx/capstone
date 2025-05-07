import time
import digitalio

class DualStepperMotorControl:
    def __init__(self, direction_pin1, pulse_pin1, direction_pin2, pulse_pin2):
        # Motor 1
        self.direction1 = digitalio.DigitalInOut(direction_pin1)
        self.direction1.direction = digitalio.Direction.OUTPUT
        self.pulse1 = digitalio.DigitalInOut(pulse_pin1)
        self.pulse1.direction = digitalio.Direction.OUTPUT

        # Motor 2
        self.direction2 = digitalio.DigitalInOut(direction_pin2)
        self.direction2.direction = digitalio.Direction.OUTPUT
        self.pulse2 = digitalio.DigitalInOut(pulse_pin2)
        self.pulse2.direction = digitalio.Direction.OUTPUT

        # Direction logic
        self.cw = True
        self.ccw = False

        # Default direction
        self.direction1.value = self.cw
        self.direction2.value = self.ccw

    def set_direction_screw_motors(self, direction1, direction2):
        print(f"Setting directions: Motor1={direction1}, Motor2={direction2}")
        self.direction1.value = direction1
        self.direction2.value = direction2

    def pulse_motor_screw_motors(self, steps, pulse_delay_us1, pulse_delay_us2):
        delay1 = pulse_delay_us1 / 1_000_000
        delay2 = pulse_delay_us2 / 1_000_000
        for _ in range(steps):
            self.pulse1.value = True
            time.sleep(delay1)
            self.pulse1.value = False

            self.pulse2.value = True
            time.sleep(delay2)
            self.pulse2.value = False

    def stop_motors(self):
        self.pulse1.value = False
        self.pulse2.value = False

    def move_both_screw_motors_cw(self, steps, pulse_delay_us1=1000, pulse_delay_us2=1000):
        print('Moving Both Motors CW')
        time.sleep(0.5)
        self.set_direction_screw_motors(self.cw, self.cw)
        self.pulse_motor_screw_motors(steps, pulse_delay_us1, pulse_delay_us2)
        self.stop_motors()

    def move_both_screw_motors_ccw(self, steps, pulse_delay_us1=1000, pulse_delay_us2=1000):
        print('Moving Both Motors CCW')
        time.sleep(0.5)
        self.set_direction_screw_motors(self.ccw, self.ccw)
        self.pulse_motor_screw_motors(steps, pulse_delay_us1, pulse_delay_us2)
        self.stop_motors()
