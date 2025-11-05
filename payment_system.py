import serial
import json
import time
from datetime import datetime

class PaymentSystem:
    def __init__(self, port='COM7', baudrate=9600):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        self.load_database()

    def load_database(self):
        with open('bank_data.json', 'r') as file:
            self.database = json.load(file)

    def save_database(self):
        with open('bank_data.json', 'w') as file:
            json.dump(self.database, file, indent=4)

    def read_arduino_response(self):
        while True:
            if self.serial.in_waiting:
                response = self.serial.readline().decode('utf-8').strip()
                print(response)
                if "Found ID" in response or "Did not find a match" in response:
                    return response
            time.sleep(0.1)

    def verify_fingerprint(self):
        print("\nPlace your finger on the sensor...")
        self.serial.write(b'V')  # Send verification command to Arduino
        response = self.read_arduino_response()
        if "Found ID" in response:
            fingerprint_id = int(response.split('#')[1].split()[0])
            confidence = int(response.split('of')[1])
            return fingerprint_id, confidence
        return None, 0

    def find_user_by_phone(self, phone):
        for user in self.database['users']:
            if user['phone'] == phone:
                return user
        return None

    def find_user_by_fingerprint_id(self, fingerprint_id):
        for user in self.database['users']:
            if user['fingerprint_id'] == fingerprint_id:
                return user
        return None

    def process_payment(self, phone_number, amount):
        # Find user by phone number
        user = self.find_user_by_phone(phone_number)
        if not user:
            print(f"\nNo user found with phone number: {phone_number}")
            return False

        print(f"\nWelcome {user['name']}!")
        print(f"Amount to be paid: ₹{amount:.2f}")
        
        # Verify fingerprint
        print("\nPlease verify your fingerprint...")
        fingerprint_id, confidence = self.verify_fingerprint()
        
        if fingerprint_id is None:
            print("\nFingerprint verification failed!")
            return False

        # Verify if fingerprint matches the user
        if fingerprint_id != user['fingerprint_id']:
            print("\nFingerprint does not match the registered user!")
            return False

        # Check if user has sufficient balance
        if user['balance'] < amount:
            print("\nInsufficient balance!")
            return False

        # Process payment
        user['balance'] -= amount
        transaction = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "type": "payment",
            "balance": user['balance']
        }
        user['transactions'].append(transaction)
        
        # Save updated database
        self.save_database()
        
        print("\nPayment Successful!")
        print(f"Remaining balance: ₹{user['balance']:.2f}")
        return True

    def close(self):
        self.serial.close()

def main():
    try:
        payment_system = PaymentSystem()
        
        while True:
            print("\n=== Kiosk Payment System ===")
            print("1. Make Payment")
            print("2. Check Balance")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == '1':
                phone = input("\nEnter your phone number: ")
                try:
                    amount = float(input("Enter payment amount: ₹"))
                    if amount <= 0:
                        print("Invalid amount!")
                        continue
                except ValueError:
                    print("Invalid amount!")
                    continue
                
                payment_system.process_payment(phone, amount)
                
            elif choice == '2':
                phone = input("\nEnter your phone number: ")
                user = payment_system.find_user_by_phone(phone)
                if user:
                    print(f"\nWelcome {user['name']}!")
                    print(f"Current balance: ₹{user['balance']:.2f}")
                    
                    # Verify fingerprint for security
                    print("\nPlease verify your fingerprint...")
                    fingerprint_id, confidence = payment_system.verify_fingerprint()
                    
                    if fingerprint_id is None or fingerprint_id != user['fingerprint_id']:
                        print("\nFingerprint verification failed!")
                    else:
                        print("\nRecent Transactions:")
                        for transaction in user['transactions'][-5:]:  # Show last 5 transactions
                            print(f"Date: {transaction['date']}")
                            print(f"Amount: ₹{transaction['amount']:.2f}")
                            print(f"Type: {transaction['type']}")
                            print(f"Balance: ₹{transaction['balance']:.2f}")
                            print("-" * 30)
                else:
                    print(f"\nNo user found with phone number: {phone}")
                
            elif choice == '3':
                print("\nThank you for using our service!")
                payment_system.close()
                break
                
            else:
                print("\nInvalid choice. Please try again.")

    except serial.SerialException as e:
        print(f"\nError: Could not connect to fingerprint sensor.")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()