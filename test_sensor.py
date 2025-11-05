import serial
import serial.tools.list_ports
import time
import sys
import os

def find_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("No serial ports found!")
        return None
    
    print("\nAvailable ports:")
    for port in ports:
        print(f"Port: {port.device}")
        print(f"Description: {port.description}")
        print(f"Hardware ID: {port.hwid}")
        print("-" * 50)
    
    # Look for Arduino or CH340
    for port in ports:
        if any(id in port.description.lower() for id in ["ch340", "arduino", "usb serial"]):
            print(f"\nFound likely Arduino port: {port.device}")
            return port.device
    
    print(f"\nNo Arduino-specific port found, using first available: {ports[0].device}")
    return ports[0].device

def test_fingerprint_sensor():
    # Find port
    port = find_arduino_port()
    if not port:
        print("No ports available!")
        return
        
    print(f"Testing port {port}...")
    
    try:
        # Open serial connection
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        
        print("Port opened successfully")
        print(f"Port settings: {ser}")
        
        if not ser.is_open:
            ser.open()
        
        # Send verify command
        print("\nSending verify command (V)...")
        ser.write(b'V')
        
        # Read response with timeout
        timeout = 10
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if ser.in_waiting:
                response = ser.readline().decode('utf-8').strip()
                print(f"Received: {response}")
                if "Found ID" in response or "Did not find a match" in response:
                    break
            time.sleep(0.1)
            
        print("\nTest completed")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        try:
            ser.close()
            print("Port closed")
        except:
            pass

if __name__ == "__main__":
    test_fingerprint_sensor()