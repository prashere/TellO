import serial
import time
import serial.tools.list_ports

# Detect ESP32 port
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
    time.sleep(2)  # Allow ESP32 time to reboot
    ser.flushInput()
    ser.flushOutput()
except serial.SerialException:
    print(f"Error: Could not open serial port {port}. Check connection!")
    exit()

# Safely send pan-tilt commands
def send_motor_command(angle1, angle2):
    # Clamp angle range to protect servos
    angle1 = max(0, min(180, angle1))
    angle2 = max(0, min(180, angle2))

    command = f"move:{angle1},{angle2}\n"
    try:
        ser.flushInput()
        ser.write(command.encode())
        time.sleep(0.2)  # Increased delay to help avoid overflow
        response = ser.readline().decode(errors='ignore').strip()
        if response == '':
            return "No response received"
        return response
    except serial.SerialException as e:
        return f"Serial Error: {str(e)}"

# Send facial expressions
def send_expression_command(command):
    try:
        ser.write((command + '\n').encode())
        time.sleep(0.5)
    except serial.SerialException as e:
        print(f"Serial Error: {str(e)}")

# Movement control menu
def pan_tilt_movement_control():
    movements = {
        "Center": (65, 105),
        "Look Left": (30, 105),
        "Look Right": (110, 105),
        "Look Down": (70, 70),
        "Look Up": (70, 130),  # Reduced from 140 to avoid power draw issues
        "Bottom Left": (20, 60),
        "Bottom Right": (120, 60),
        "Top Left": (20, 130),
        "Top Right": (140, 130),
        "Sweep Horizontal": [(0, 90), (90, 90), (180, 90)]
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

        if isinstance(movement, list):
            for angle1, angle2 in movement:
                response = send_motor_command(angle1, angle2)
                print(f"Sent: {angle1},{angle2}, ESP32 Response: {response}")
                time.sleep(0.5)
        else:
            angle1, angle2 = movement
            response = send_motor_command(angle1, angle2)
            print(f"Sent: {angle1},{angle2}, ESP32 Response: {response}")

# Expression command interface
def expression_control():
    expressions = ["blink", "happy", "sad", "confused", "winkleft", "winkright"]

    print("\nExpression Control Mode")
    print("Available commands:", ', '.join(expressions))
    print("Type 'back' to return to the main menu.")

    while True:
        user_input = input("Enter expression command: ").strip().lower()
        if user_input == "back":
            break
        if user_input in expressions:
            send_expression_command(user_input)
            print(f"Sent command: {user_input}")
        else:
            print("Invalid command. Try again.")

# Main interface
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
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Closing serial port.")
        ser.close()
