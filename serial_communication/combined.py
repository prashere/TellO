import serial
import time
import serial.tools.list_ports

# Auto-detect available serial ports
def find_esp32_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.description or "UART" in port.description:
            return port.device
    return None

# Get the correct port
port = find_esp32_port()
if port is None:
    print("ESP32 not detected. Check connections!")
    exit()

try:
    ser = serial.Serial(port, 115200, timeout=1)
    time.sleep(2)  # Allow time for the connection to establish
    ser.flush()    # Clear any previous data from the buffer
except serial.SerialException:
    print(f"Error: Could not open serial port {port}. Check connection!")
    exit()

# Function to send pan-tilt (servo movement) commands.
# Arduino expects commands in the format: "move:angle1,angle2"
def send_motor_command(angle1, angle2):
    command = f"move:{angle1},{angle2}\n"  # note the prefix "move:" and comma separation
    ser.write(command.encode())  # Send command to ESP32
    time.sleep(0.1)  # Allow time for ESP32 to process
    response = ser.readline().decode().strip()
    return response if response else "No response received"

# Function to send expression commands (e.g., "blink", "happy", "sad", etc.)
def send_expression_command(command):
    ser.write((command + '\n').encode())
    time.sleep(0.5)

# Pan-Tilt Movement Control Mode
def pan_tilt_movement_control():
    movements = {
        "Center": (65, 105),
        "Look Left": (30, 105),
        "Look Right": (140, 105),
        "Look Down": (70, 70),
        "Look Up": (70, 140),
        "Bottom Left": (20, 60),
        "Bottom Right": (140, 60),
        "Top Left": (20, 140),
        "Top Right": (140, 140),
        "Sweep Horizontal": [(0, 90), (90, 90), (180, 90)]  # Multi-step movement example
    }

    print("\nPan-Tilt Movement Control")
    print("Available Movements:")
    for idx, name in enumerate(movements.keys(), start=1):
        print(f"{idx}. {name}")
    print("Type 'back' to return to the main menu.\n")

    while True:
        user_input = input("Select a movement: ").strip()
        if user_input.lower() == "back":
            break

        # Allow selection by number or by name
        if user_input.isdigit():
            choice = int(user_input) - 1
            if 0 <= choice < len(movements):
                movement_name = list(movements.keys())[choice]
            else:
                print("Invalid selection. Try again.")
                continue
        else:
            movement_name = user_input.title()

        if movement_name not in movements:
            print("Invalid movement name. Try again.")
            continue

        movement = movements[movement_name]
        print(f"Executing '{movement_name}'...")

        # Handle multi-step movements (list of tuples) vs. single-step (tuple)
        if isinstance(movement, list):
            for angle1, angle2 in movement:
                response = send_motor_command(angle1, angle2)
                print(f"Sent: {angle1},{angle2}, ESP32 Response: {response}")
                time.sleep(0.5)  # Delay between steps
        else:
            angle1, angle2 = movement
            response = send_motor_command(angle1, angle2)
            print(f"Sent: {angle1},{angle2}, ESP32 Response: {response}")

# Expression Control Mode
def expression_control():
    print("\nPan-Tilt Expression Control")
    print("Available commands: blink, happy, sad, confused, winkleft, winkright")
    print("Type 'back' to return to the main menu.")

    while True:
        user_input = input("Enter expression command: ").strip().lower()
        if user_input == "back":
            break
        if user_input in ["blink", "happy", "sad", "confused", "winkleft", "winkright"]:
            send_expression_command(user_input)
            print(f"Sent command: {user_input}")
        else:
            print("Invalid command. Try again.")

# Main menu to choose between modes
def main():
    while True:
        print("\n=== Main Menu ===")
        print("1. Pan-Tilt Movement Control")
        print("2. Expression Control")
        print("3. Exit")
        mode = input("Select mode (1/2/3): ").strip()
        if mode == "1":
            pan_tilt_movement_control()
        elif mode == "2":
            expression_control()
        elif mode == "3":
            print("Exiting program.")
            break
        else:
            print("Invalid selection. Please try again.")

    print("Closing serial connection.")
    ser.close()

if __name__ == "__main__":
    main()
