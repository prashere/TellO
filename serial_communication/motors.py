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
    time.sleep(0.1)  # Allow time for Arduino to process

    response = ser.readline().decode().strip()
    return response if response else "No response received"

# Example: Move motors to different angles
angles = [(0, 0), (90, 90), (180, 180)]
for angle1, angle2 in angles:
    response = send_motor_command(angle1, angle2)
    print(f"Sent: {angle1} {angle2}, Arduino Response: {response}")
    time.sleep(1)

ser.close()  # Close serial connection
