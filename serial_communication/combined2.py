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

# Global variables to track current servo positions
current_angle1 = 65  # Default center position
current_angle2 = 105

def send_motor_command_smooth(target_angle1, target_angle2, step_delay=0.02, step_size=2):
    """Moves the servo smoothly by stepping through angles instead of jumping."""
    global current_angle1, current_angle2
    
    while current_angle1 != target_angle1 or current_angle2 != target_angle2:
        if current_angle1 < target_angle1:
            current_angle1 = min(current_angle1 + step_size, target_angle1)
        elif current_angle1 > target_angle1:
            current_angle1 = max(current_angle1 - step_size, target_angle1)

        if current_angle2 < target_angle2:
            current_angle2 = min(current_angle2 + step_size, target_angle2)
        elif current_angle2 > target_angle2:
            current_angle2 = max(current_angle2 - step_size, target_angle2)

        command = f"move:{current_angle1},{current_angle2}\n"
        ser.write(command.encode())
        time.sleep(step_delay)  # Small delay to slow down the motion

    return f"Smoothly moved to {target_angle1}, {target_angle2}"

# Pan-Tilt Movement Control Mode
def pan_tilt_movement_control():
    movements = {
        "Center": (65, 105),
        "Look Left": (30, 105),
        "Look Right": (160, 105),
        "Look Down": (70, 70),
        "Look Up": (70, 140),
        "Bottom Left": (20, 60),
        "Bottom Right": (160, 60),
        "Top Left": (20, 140),
        "Top Right": (160, 140),
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
                response = send_motor_command_smooth(angle1, angle2)
                print(f"Sent: {angle1},{angle2}, ESP32 Response: {response}")
                time.sleep(0.5)
        else:
            angle1, angle2 = movement
            response = send_motor_command_smooth(angle1, angle2)
            print(f"Sent: {angle1},{angle2}, ESP32 Response: {response}")

# Main menu to choose between modes
def main():
    while True:
        print("\n=== Main Menu ===")
        print("1. Pan-Tilt Movement Control")
        print("2. Exit")
        mode = input("Select mode (1/2): ").strip()
        if mode == "1":
            pan_tilt_movement_control()
        elif mode == "2":
            print("Exiting program.")
            break
        else:
            print("Invalid selection. Please try again.")

    print("Closing serial connection.")
    ser.close()

if __name__ == "__main__":
    main()
