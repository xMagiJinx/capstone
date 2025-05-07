from time import sleep
from Pico_Screw_Motors_Class import DualStepperMotorControl  # Your MicroPython version

# Define GPIO pin numbers (adjust as needed for your board)
# Motor 1 Pins
direction_pin1 = 19
pulse_pin1 = 20

# Motor 2 Pins
direction_pin2 = 11
pulse_pin2 = 12



# Initialize motor controller
motor_control = DualStepperMotorControl(direction_pin1, pulse_pin1,
                                        direction_pin2, pulse_pin2,
                                        )

try:
    motor_control.move_both_screw_motors_ccw(steps=300)
    sleep(2)
    motor_control.move_both_screw_motors_cw(steps=300)

except KeyboardInterrupt:
    print("\nProcess interrupted by user.")
finally:
    print("Done.")
