# robot_comm.py
import serial
import time

# Serial port config
SERIAL_PORT = 'COM5'  # Update as needed
BAUD_RATE = 115200
SERIAL_TIMEOUT = 1  # in seconds

# Predefined social cue combos
SOCIAL_CUES = {
    "intro": [
        {"pan": 65, "tilt": 100, "expression": "happy"},
        {"pan": 65, "tilt": 95, "expression": "blink"}
    ],
    "outro": [
        {"pan": 65, "tilt": 110, "expression": "happy"},
        {"pan": 65, "tilt": 105, "expression": "winkright"}
    ],
    "narration": [
        {"pan": 65, "tilt": 105, "expression": "blink"},
        {"pan": 65, "tilt": 108, "expression": "blink"}
    ],
    "prompt": [
        {"pan": 60, "tilt": 100, "expression": "winkleft"},
        {"pan": 65, "tilt": 100, "expression": "blink"}
    ],
    "listening": [
        {"pan": 65, "tilt": 105, "expression": "blink"},
        {"pan": 65, "tilt": 102, "expression": "confused"}
    ],
    "encouragement": [
        {"pan": 65, "tilt": 95, "expression": "happy"},
        {"pan": 65, "tilt": 90, "expression": "winkright"}
    ],
    "motivation": [
        {"pan": 65, "tilt": 85, "expression": "happy"},
        {"pan": 65, "tilt": 90, "expression": "winkleft"}
    ],
    "agree": [
        {"pan": 65, "tilt": 95, "expression": "happy"},
        {"pan": 65, "tilt": 90, "expression": "blink"}
    ],
    "disagree": [
        {"pan": 60, "tilt": 105, "expression": "confused"},
        {"pan": 65, "tilt": 108, "expression": "sad"}
    ],
    "shutdown": [
        {"pan": 65, "tilt": 105, "expression": "blink"}
    ]
}

def init_serial(port=SERIAL_PORT, baud_rate=BAUD_RATE, timeout=SERIAL_TIMEOUT):
    """
    Initializes and returns a serial connection.
    """
    try:
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        time.sleep(2)  # Allow connection to stabilize
        print("Connected to ESP32.")
        return ser
    except serial.SerialException as e:
        raise Exception(f"Serial error: {e}")

def send_movement(ser, pan, tilt):
    """
    Sends a servo movement command in the format "move:pan,tilt".
    """
    command = f"move:{pan},{tilt}\n"
    print(f"Sending movement: {command.strip()}")
    ser.write(command.encode())
    time.sleep(0.05)

def send_expression(ser, expression):
    """
    Sends a facial expression command.
    """
    command = f"{expression}\n"
    print(f"Sending expression: {expression}")
    ser.write(command.encode())
    time.sleep(0.05)

def execute_combo(ser, combo_name, delay_between_steps=2):
    """
    Executes a social cue combo by name.
    
    :param ser: The serial connection object.
    :param combo_name: The name of the combo (must exist in SOCIAL_CUES).
    :param delay_between_steps: Delay (in seconds) between steps.
    """
    if combo_name not in SOCIAL_CUES:
        print(f"Invalid cue '{combo_name}'.")
        return

    print(f"\n▶ Executing '{combo_name}' combo...")
    for idx, step in enumerate(SOCIAL_CUES[combo_name], start=1):
        print(f"Step {idx}: PAN={step['pan']} | TILT={step['tilt']} | EXPRESSION={step['expression']}")
        send_movement(ser, step['pan'], step['tilt'])
        send_expression(ser, step['expression'])
        time.sleep(delay_between_steps)
    print(f"Finished '{combo_name}' combo.\n")

def shutdown_robot(ser):
    """
    Executes the shutdown sequence and sends final shutdown command.
    """
    print("\nSending shutdown sequence...")
    execute_combo(ser, "shutdown", delay_between_steps=1)
    ser.write(b"shutdown\n")
    print("Shutdown command sent.")

# The module can be imported and these functions can be called from other scripts.
# For demonstration purposes, here is a simple main block:

if __name__ == "__main__":
    try:
        serial_conn = init_serial()
        while True:
            cue = input("Enter social cue name (or 'exit'): ").strip().lower()
            if cue == "exit":
                shutdown_robot(serial_conn)
                break
            if cue not in SOCIAL_CUES:
                print(f"Invalid cue '{cue}'. Try again.")
                continue
            execute_combo(serial_conn, cue)
    except Exception as err:
        print(f"Error: {err}")
    finally:
        if 'serial_conn' in locals() and serial_conn.is_open:
            serial_conn.close()
