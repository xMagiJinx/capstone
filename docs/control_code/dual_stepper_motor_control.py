from time import sleep
import RPi.GPIO as gpio

class DualStepperMotorControl:
    def __init__(self, direction_pin1, pulse_pin1, direction_pin2, pulse_pin2, direction_pin3, pulse_pin3, direction_pin4, pulse_pin4):
        # Motor 1 Pins
        self.direction_pin1 = direction_pin1
        self.pulse_pin1 = pulse_pin1
        
        # Motor 2 Pins
        self.direction_pin2 = direction_pin2
        self.pulse_pin2 = pulse_pin2

        # Motor 3 Pins
        self.direction_pin3 = direction_pin3
        self.pulse_pin3 = pulse_pin3
        
        # Motor 4 Pins
        self.direction_pin4 = direction_pin4
        self.pulse_pin4 = pulse_pin4        
        
        # Direction definitions
        self.cw_direction = 0  # Clockwise
        self.ccw_direction = 1  # Counterclockwise
        
        # Setup GPIO
        gpio.setmode(gpio.BOARD)
        
        gpio.setup(self.direction_pin1, gpio.OUT)
        gpio.setup(self.pulse_pin1, gpio.OUT)
        gpio.setup(self.direction_pin2, gpio.OUT)
        gpio.setup(self.pulse_pin2, gpio.OUT)
        
        gpio.setup(self.direction_pin3, gpio.OUT)
        gpio.setup(self.pulse_pin3, gpio.OUT)
        gpio.setup(self.direction_pin4, gpio.OUT)
        gpio.setup(self.pulse_pin4, gpio.OUT)
        
        # Set initial direction (default CW)
        gpio.output(self.direction_pin1, self.cw_direction)
        gpio.output(self.direction_pin2, self.ccw_direction)
        gpio.output(self.direction_pin3, self.cw_direction)
        gpio.output(self.direction_pin4, self.cw_direction)

    def set_direction_screw_motors(self, direction1, direction2):
        """Set the direction of screw motors."""
        gpio.output(self.direction_pin1, direction1)
        gpio.output(self.direction_pin2, direction2)
        
        
    def set_direction_cart_motors(self, direction3, direction4):
        """Set the direction of screw motors."""
        gpio.output(self.direction_pin3, direction3)
        gpio.output(self.direction_pin4, direction4)
        
        
        
    def pulse_motor_screw_motors(self, steps, pulse_delay1, pulse_delay2):
        """Pulse all motors for a given number of steps and delays."""
        for _ in range(steps):
            # Motor 1 pulse
            gpio.output(self.pulse_pin1, gpio.HIGH)
            sleep(pulse_delay1)
            gpio.output(self.pulse_pin1, gpio.LOW)
            
            # Motor 2 pulse
            gpio.output(self.pulse_pin2, gpio.HIGH)
            sleep(pulse_delay2)
            gpio.output(self.pulse_pin2, gpio.LOW)
            
            
            
    def pulse_motor_cart_motors(self, steps, pulse_delay3, pulse_delay4):
        """Pulse all motors for a given number of steps and delays."""
        for _ in range(steps):
            # Motor 3 pulse
            gpio.output(self.pulse_pin3, gpio.HIGH)
            sleep(pulse_delay3)
            gpio.output(self.pulse_pin3, gpio.LOW)
            
            # Motor 4 pulse
            gpio.output(self.pulse_pin4, gpio.HIGH)
            sleep(pulse_delay4)
            gpio.output(self.pulse_pin4, gpio.LOW)
            
            
            
    def stop_motors(self):
        """Stop all motors by setting pulse pins to LOW."""
        gpio.output(self.pulse_pin1, gpio.LOW)
        gpio.output(self.pulse_pin2, gpio.LOW)
        gpio.output(self.pulse_pin3, gpio.LOW)
        gpio.output(self.pulse_pin4, gpio.LOW)       

    def move_both_screw_motors_cw(self, steps, pulse_delay1=0.001, pulse_delay2=0.001):
        """Move both screw motors in the CW direction."""
        print('Direction CW')
        sleep(0.5)
        self.set_direction_screw_motors(self.cw_direction, self.cw_direction)
        self.pulse_motor_screw_motors(steps, pulse_delay1, pulse_delay2)
        self.stop_motors()

    def move_both_screw_motors_ccw(self, steps, pulse_delay1=0.001, pulse_delay2=0.001):
        """Move both screw motors in the ccw direction."""
        print('Direction CCW')
        sleep(0.5)
        self.set_direction_screw_motors(self.ccw_direction, self.ccw_direction)
        self.pulse_motor_screw_motors(steps, pulse_delay1, pulse_delay2)
        
        
        
        
        
    def move_both_cart_motors_cw(self, steps, pulse_delay3=0.001, pulse_delay4=0.001):
        """Move both cart motors in the cw direction"""
        print('Cart Direction CW')
        sleep(0.5)
        self.set_direction_cart_motors(self.cw_direction, self.cw_direction)
        self.pulse_motor_cart_motors(steps, pulse_delay3, pulse_delay4)

    def move_both_cart_motors_ccw(self, steps, pulse_delay3=0.001, pulse_delay4=0.001):
        """Move both cart motors in the ccw direction"""
        print('Cart Direction CW')
        sleep(0.5)
        self.set_direction_cart_motors(self.ccw_direction, self.ccw_direction)
        self.pulse_motor_cart_motors(steps, pulse_delay3, pulse_delay4)

    def cleanup(self):
        """Clean up GPIO setup."""
        gpio.cleanup()
        
        


































 





