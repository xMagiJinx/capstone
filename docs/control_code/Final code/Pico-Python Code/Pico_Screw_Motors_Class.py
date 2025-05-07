from machine import Pin
from time import sleep_us, sleep

class DualStepperMotorControl:
    def __init__(self, direction_pin1, pulse_pin1, direction_pin2, pulse_pin2):
        # Motor 1 Pins
        self.direction1 = Pin(direction_pin1, Pin.OUT)
        self.pulse1 = Pin(pulse_pin1, Pin.OUT)
        
        # Motor 2 Pins
        self.direction2 = Pin(direction_pin2, Pin.OUT)
        self.pulse2 = Pin(pulse_pin2, Pin.OUT)

        # Direction definitions
        self.cw = 0
        self.ccw = 1

        # Default direction
        self.direction1.value(self.cw)
        self.direction2.value(self.ccw)

    def set_direction_screw_motors(self, direction1, direction2):
        self.direction1.value(direction1)
        self.direction2.value(direction2)

    def pulse_motor_screw_motors(self, steps, pulse_delay_us1, pulse_delay_us2):
        for _ in range(steps):
            # Motor 1
            self.pulse1.value(1)
            sleep_us(pulse_delay_us1)
            self.pulse1.value(0)
            
            # Motor 2
            self.pulse2.value(1)
            sleep_us(pulse_delay_us2)
            self.pulse2.value(0)

    def stop_motors(self):
        self.pulse1.value(0)
        self.pulse2.value(0)

    def move_both_screw_motors_cw(self, steps, pulse_delay_us1=1000, pulse_delay_us2=1000):
        print('Direction CW')
        sleep(0.5)
        self.set_direction_screw_motors(self.cw, self.cw)
        self.pulse_motor_screw_motors(steps, pulse_delay_us1, pulse_delay_us2)
        self.stop_motors()

    def move_both_screw_motors_ccw(self, steps, pulse_delay_us1=1000, pulse_delay_us2=1000):
        print('Direction CCW')
        sleep(0.5)
        self.set_direction_screw_motors(self.ccw, self.ccw)
        self.pulse_motor_screw_motors(steps, pulse_delay_us1, pulse_delay_us2)
        self.stop_motors()
