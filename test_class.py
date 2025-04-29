# Import the necessary libraries
from time import sleep
import RPi.GPIO as gpio
from dual_stepper_motor_control import DualStepperMotorControl  # Assuming the class is in this file

# Define GPIO pin numbers for motors
# Motor 1 Pins
direction_pin1 = 7
pulse_pin1 = 8

# Motor 2 Pins
direction_pin2 = 11
pulse_pin2 = 12

# Motor 3 Pins
direction_pin3 = 15
pulse_pin3 = 16

# Motor 4 Pins
direction_pin4 = 37
pulse_pin4 = 38

# Create an instance of DualStepperMotorControl
# Create an instance of the stepper motor control class
motor_control = DualStepperMotorControl(direction_pin1, pulse_pin1, 
                                        direction_pin2, pulse_pin2,
                                        direction_pin3, pulse_pin3,
                                        direction_pin4, pulse_pin4)
                                                                                                                  
                                                                            
try:
    motor_control.move_both_cart_motors_ccw(steps=3500)
    sleep(7)
    motor_control.move_both_cart_motors_ccw(steps= 110)
    motor_control.move_both_screw_motors_ccw(steps=300)
    sleep(2)
    motor_control.move_both_screw_motors_cw(steps=300)
    motor_control.move_both_cart_motors_cw(steps=1110)
   
except KeyboardInterrupt:
    print("\nProcess interrupted by user.")
finally:
    print("Cleaning up GPIO...")
    motor_control.cleanup()
