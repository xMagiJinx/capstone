from time import sleep
from Pico_Screw_Motors_Class import DualStepperMotorControl
import machine
import usb

usb_cdc = usb.USB()


# Motor pin definitions
direction_pin1 = 14
pulse_pin1 = 15
direction_pin2 = 17
pulse_pin2 = 16

# Force thresholds (in Newtons)
maximum_force = 2.8593
minimum_force = 1.9765

# Step size limits
MIN_STEPS = 10
MAX_STEPS = 300

# Initialize motor controller
motor_control = DualStepperMotorControl(direction_pin1, pulse_pin1, direction_pin2, pulse_pin2)

# Use USB CDC data channel for serial communication
usb_cdc.data.timeout = 0  # Non-blocking read

print("Pico is ready to receive ORCA force and position data...")

def calculate_step_count(force, min_force, max_force, min_steps=MIN_STEPS, max_steps=MAX_STEPS):
    """
    Calculates how many steps to move based on how far force is from target range.
    """
    if force < min_force:
        error = min_force - force
    elif force > max_force:
        error = force - max_force
    else:
        return 0  # No movement needed

    # Cap the scale at a max deviation of 2 N
    scale = min(1.0, error / 2.0)
    steps = int(min_steps + scale * (max_steps - min_steps))
    return steps

try:
    while True:
        if usb_cdc.data.any():
            raw = usb_cdc.data.read(usb_cdc.data.any())
            if raw:
                cmd = raw.decode('utf-8').strip()
                print("Received:", cmd)

                if cmd.upper().startswith("ORCA"):
                    try:
                        _, force_str, pos_str = cmd.split()
                        force_val = float(force_str)
                        position_val = int(pos_str)

                        steps = calculate_step_count(force_val, minimum_force, maximum_force)

                        if steps == 0:
                            motor_control.stop_motors()
                            action = "Stopped"
                        elif force_val < minimum_force:
                            motor_control.move_both_screw_motors_cw(steps)
                            action = f"Moved CW {steps} steps"
                        elif force_val > maximum_force:
                            motor_control.move_both_screw_motors_ccw(steps)
                            action = f"Moved CCW {steps} steps"

                        # Respond to MATLAB
                        response = f"Response: Force={force_val:.2f} N, Pos={position_val} um, Action={action}\n"
                        usb_cdc.data.write(response.encode())

                    except Exception as e:
                        usb_cdc.data.write(b"Error: Invalid ORCA format\n")

                else:
                    usb_cdc.data.write(b"Unknown command\n")

        sleep(0.1)

except KeyboardInterrupt:
    print("Stopped by user")
finally:
    print("Shutting down")
