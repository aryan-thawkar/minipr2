import serial
import time

class FingerprintSensor:
    def __init__(self, port='COM7', baudrate=9600):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        
    def read_response(self):
        while True:
            if self.serial.in_waiting:
                response = self.serial.readline().decode('utf-8').strip()
                print(response)
                if "Stored!" in response or "Failed" in response or "Found ID" in response or "Did not find a match" in response:
                    return response
            time.sleep(0.1)

    def enroll_fingerprint(self):
        print("Starting fingerprint enrollment...")
        self.serial.write(b'E')  # Send enrollment command to Arduino
        return self.read_response()

    def verify_fingerprint(self):
        print("Starting fingerprint verification...")
        self.serial.write(b'V')  # Send verification command to Arduino
        return self.read_response()

    def close(self):
        self.serial.close()

def main():
    try:
        sensor = FingerprintSensor()  # Make sure to use the correct COM port
        
        while True:
            print("\nFingerprint Sensor Menu:")
            print("1. Enroll new fingerprint")
            print("2. Verify fingerprint")
            print("3. Exit")
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == '1':
                result = sensor.enroll_fingerprint()
                if "Stored!" in result:
                    print("Fingerprint enrolled successfully!")
                else:
                    print("Enrollment failed!")
                    
            elif choice == '2':
                result = sensor.verify_fingerprint()
                if "Found ID" in result:
                    print("Fingerprint matched!")
                else:
                    print("No match found!")
                    
            elif choice == '3':
                print("Exiting...")
                sensor.close()
                break
                
            else:
                print("Invalid choice. Please try again.")

    except serial.SerialException as e:
        print(f"Error: Could not open serial port. Make sure Arduino is connected and port is correct.")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()