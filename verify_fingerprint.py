import serial
import time

def verify_fingerprint():
    try:
        # Initialize connection to Arduino
        # Replace 'COM5' with your Arduino's COM port
        arduino = serial.Serial('COM5', 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset

        # Send verification command
        arduino.write(b'V')
        
        # Read and print Arduino's responses
        while True:
            if arduino.in_waiting:
                response = arduino.readline().decode('utf-8').strip()
                print(response)
                
                if "Found ID" in response:
                    print("Match found!")
                    break
                elif "Did not find a match" in response:
                    print("No match found!")
                    break
                elif "error" in response:
                    print("Verification failed!")
                    break
                    
        arduino.close()

    except Exception as e:
        print('Error: Could not communicate with Arduino')
        print(f'Exception message: {e}')
        exit(1)

if __name__ == '__main__':
    verify_fingerprint()