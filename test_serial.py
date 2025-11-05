import serial
import time

def test_serial():
    try:
        # Open port with basic settings
        ser = serial.Serial('COM7', 
                          baudrate=9600,
                          bytesize=serial.EIGHTBITS,
                          parity=serial.PARITY_NONE,
                          stopbits=serial.STOPBITS_ONE,
                          timeout=1)
        
        print("Port opened successfully")
        print(f"Port settings: {ser}")
        
        # Test if port is actually open
        if ser.is_open:
            print("Port is confirmed open")
            
            # Send a test command
            print("Sending test command...")
            ser.write(b'V\n')
            
            # Read response
            time.sleep(2)
            while ser.in_waiting:
                response = ser.readline().decode('utf-8').strip()
                print(f"Received: {response}")
                
        ser.close()
        print("Port closed successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_serial()