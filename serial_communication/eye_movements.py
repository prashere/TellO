import serial
import time
import serial.tools.list_ports

# Auto-detect available serial ports (adjust if needed)
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
    ser.flush()
except serial.SerialException:
    print(f"Error: Could not open serial port {port}. Check connection!")
    exit()

def send_command(command):
    ser.write((command + '\n').encode())
    # Optionally, wait a little for the ESP32 to process the command
    time.sleep(0.5)

print("Pan-Tilt Expression Control")
print("Available commands: blink, happy, sad, confused, winkLeft, winkRight")
print("Type 'exit' to quit.")

while True:
    user_input = input("Enter expression command: ").strip().lower()
    if user_input == "exit":
        print("Exiting...")
        break
    if user_input in ["blink", "happy", "sad", "confused","winkleft","winkright"]:
        send_command(user_input)
        print(f"Sent command: {user_input}")
    else:
        print("Invalid command. Try again.")

ser.close()
