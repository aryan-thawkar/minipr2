import serial
import time

def enroll_fingerprint():
    try:
        # Initialize connection to Arduino
        # Replace 'COM5' with your Arduino's COM port
        arduino = serial.Serial('COM6', 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset

        # Send enrollment command
        arduino.write(b'E')
        
        # Read and print Arduino's responses
        while True:
            if arduino.in_waiting:
                response = arduino.readline().decode('utf-8').strip()
                print(response)
                
                if response == "Stored!":
                    print("Enrollment successful!")
                    break
                elif "Failed" in response or "error" in response:
                    print("Enrollment failed!")
                    break
                    
        arduino.close()

    except Exception as e:
        print('Error: Could not communicate with Arduino')
        print(f'Exception message: {e}')
        exit(1)

if __name__ == '__main__':
    enroll_fingerprint()