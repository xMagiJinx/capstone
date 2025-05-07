# This is the main code for the order of how the drop test is integrated with the tightening

# import various classes between the motors and other

import threading  # Import threading module to handle parallel execution
import time  # Import time module to simulate delays
import RPi.GPIO as GPIO

class StepperMotor:
    def __init__(self, motor_id):

        DIR1 = 10    # assign direction
        self.STEP1 = 8    # assign  step value or pulse
        DIR2 = 12    # motor 2 direction
        self.STEP2 = 16   # motor 2 value

        CW = 1      # rotation Clockwise
        CCW = 0    # rotation Counter-Clockwise

        GPIO.setmode(GPIO.BOARD)    # Establish board position and mode
        GPIO.setup(DIR1, GPIO.OUT)   # Establish output of the direction
        GPIO.setup(self.STEP1, GPIO.OUT)  # Establish output of the STEP

        GPIO.setup(DIR2, GPIO.OUT)  # Motor 2
        GPIO.setup(self.STEP2, GPIO.OUT) # Motor 2

        GPIO.output(DIR1, CW)   # Turns CW - Motor 1
        GPIO.output(DIR2, CCW)  # Turns CCW - Motor 2

        self.motor_id = motor_id  # Assign unique ID for each motor
        self.tightening = False  # Initialize tightening state (False initially)

        self.thread_targets = [self.motor1_control, self.motor2_control]    # chose both motors to move at the same time or scan at the same time
        self.threads = [threading.Thread(target = t) for t in self.thread_targets]

        # check and exit, like a flag
        self.stop_event = threading.Event()

    def motor1_control(self):
        """This will move motor 1 clockwise for now"""
        motor1 = GPIO.output()
        for x in range(100):
            motor1(self.STEP1, GPIO.HIGH)

    def motor2_control(self):
        """This will move motor 2 CCW for now"""
        motor2 = GPIO.output()
        for x in range(100):
            motor2(self.STEP2, GPIO.HIGH)

    def tighten(self):
        print(f"Motor {self.motor_id} tightening screws.")  # Log that the motor is tightening
        self.tightening = True  # Set motor state to tightening
        time.sleep(2)  # Simulate tightening process (pause for 2 seconds)
        print(f"Motor {self.motor_id} finished tightening.")  # Log after tightening is finished
    
    def stop(self):
        print(f"Motor {self.motor_id} stopped.")  # Log that motor has stopped
        self.tightening = False  # Set motor state to stopped

    def start_threads(self):
        """This method starts the threads in the main init"""
        print(f"starting {len(self.threads)} threads!")
        [t.start() for t in self.threads]

    def end_threads(self):
        """This ends / joins all of our threads"""
        self.stop_event()
        print('Joining all threads!')
        [t.join() for t in self.threads]

        GPIO.cleanup() # clear any remaining commands within the GPIO

    def run_threads(self):
        """A function to run the threads and make both motors move at the same time"""
        self.start_threads()

        time.sleep(12.5)

        self.end_threads()  # ends after the task is done


if __name__ == "__main__":
    calib = StepperMotor()
    calib.run_threads()
    GPIO.cleanup()