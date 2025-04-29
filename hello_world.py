# hello_world.py
def display_message(msg):
    if msg == "Start":
        print("Hello, World!")
        return "start"
    elif msg == "Stop":
        print("Stop, World!")
    elif msg == "Reset":
        print("Reset, World!")
    elif msg == "Exit":
        print("Exit")
    else:
        pass

# other effects, 
# Force too low! Moving CCW
# Force within desired range. No movement
# Force to high! Moving CW