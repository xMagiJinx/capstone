import time
import usb_cdc
import board
from pico_screw_motors_class import DualStepperMotorControl

# === Motor pin definitions ===
direction_pin1 = board.GP14
pulse_pin1 = board.GP15
direction_pin2 = board.GP17
pulse_pin2 = board.GP16

# === Force thresholds (in Newtons) ===
maximum_force = 2.8593
minimum_force = 1.9765

# === Step size limits ===
MIN_STEPS = 100 # 1 turn
MAX_STEPS = 300 # 3 turns

# === Initialize motor controller ===
motor_control = DualStepperMotorControl(direction_pin1, pulse_pin1, direction_pin2, pulse_pin2)

# === Use USB CDC for serial communication ===
usb_serial = usb_cdc.data
usb_serial.timeout = 0  # Non-blocking

print("Pico is ready to receive ORCA force and position data...")

def calculate_step_count(force, min_force, max_force, min_steps=MIN_STEPS, max_steps=MAX_STEPS):
    if force < min_force:
        error = min_force - force
    elif force > max_force:
        error = force - max_force
    else:
        return 0  # No movement needed

    scale = min(1.0, error / 2.0)  # Cap at 2N deviation
    steps = int(min_steps + scale * (max_steps - min_steps))
    return steps

try:
    while True:
        if usb_serial.in_waiting > 0:
            raw = usb_serial.read(usb_serial.in_waiting)
            if raw:
                try:
                    cmd = raw.decode('utf-8').strip()
                    print("Received:", cmd)

                    if cmd.upper().startswith("ORCA"):
                        _, force_str, pos_str = cmd.split() # Separate from matlab the force and position data and write them as a string 
                        force_val = int(force_str) # May have to be a float
                        position_val = int(pos_str)
                        time.sleep(1)

                        steps = calculate_step_count(force_val, minimum_force, maximum_force)

                        if steps == 0:
                            motor_control.stop_motors()
                            action = "Stopped"
                        elif force_val < minimum_force:
                            motor_control.move_both_screw_motors_cw(steps) # Tightens the screws
                            action = f"Moved CW {steps} steps"
                        elif force_val > maximum_force:
                            motor_control.move_both_screw_motors_ccw(steps) # Loosens the screws
                            action = f"Moved CCW {steps} steps"

                        response = f"Response: Force={force_val:.2f} N, Pos={position_val} um, Action={action}\n"
                        usb_serial.write(response.encode()) # sends to matlab

                    else:
                        usb_serial.write(b"Unknown command\n")

                except Exception as e:
                    usb_serial.write(b"Error: Invalid ORCA format\n")

        time.sleep(0.1)

except Exception as e:
    print("Error:", e)
finally:
    print("Shutting down")
