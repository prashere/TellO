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
    ser.flush()  # Clear any previous data from the buffer
except serial.SerialException:
    print(f"Error: Could not open serial port {port}. Check connection!")
    exit()

# Function to send motor commands
def send_motor_command(angle1, angle2):
    command = f"{angle1} {angle2}\n"
    ser.write(command.encode())  # Send command
    time.sleep(0.1)  # Allow time for ESP32 to process

    response = ser.readline().decode().strip()
    return response if response else "No response received"

# Define named movements with pan and tilt angles
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
    "Sweep Horizontal": [(0, 90), (90, 90), (180, 90)],  # Example of multi-step movement
}

# Main interaction loop
print("\nPan-Tilt Mechanism Control")
print("Available Movements:")
for idx, name in enumerate(movements.keys(), start=1):
    print(f"{idx}. {name}")
print("Type 'exit' or 'no' to quit.\n")

while True:
    user_input = input("Select a movement: ").strip()

    if user_input.lower() in ["exit", "no"]:
        print("Exiting control.")
        break

    # Check if user selected by name or number
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

    # Handle multi-step movements
    if isinstance(movement, list):
        for angle1, angle2 in movement:
            response = send_motor_command(angle1, angle2)
            print(f"Sent: {angle1} {angle2}, ESP32 Response: {response}")
            time.sleep(0.5)  # Delay between steps
    else:
        angle1, angle2 = movement
        response = send_motor_command(angle1, angle2)
        print(f"Sent: {angle1} {angle2}, ESP32 Response: {response}")

print("Closing serial connection.")
ser.close()
