from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import serial
import serial.tools.list_ports
import time
from datetime import datetime
import plotly.express as px
import plotly.utils
import pandas as pd
import atexit

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Global serial connection
ser = None

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

def initialize_serial():
    global ser
    
    # Find port
    port = find_arduino_port()
    if not port:
        print("No ports available!")
        return False
        
    print(f"Testing port {port}...")
    
    try:
        # Try to clean up any existing connections first
        if ser is not None:
            try:
                ser.close()
            except:
                pass
            ser = None
            
        # Wait a moment
        time.sleep(1)
        
        # Open serial connection with all settings explicit
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            write_timeout=1,
            xonxoff=False,    # disable software flow control
            rtscts=False,     # disable hardware (RTS/CTS) flow control
            dsrdtr=False      # disable hardware (DSR/DTR) flow control
        )
        
        print("Port opened successfully")
        
        if not ser.is_open:
            print("Opening port...")
            ser.open()
            
        # Reset the device
        print("Resetting device...")
        ser.dtr = False
        time.sleep(0.1)
        ser.dtr = True
        time.sleep(2)  # Give the Arduino time to reset
        
        # Clear any pending data
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        return True
        
    except Exception as e:
        print(f"Error initializing serial: {e}")
        if ser is not None:
            try:
                ser.close()
            except:
                pass
            ser = None
        return False

def verify_fingerprint():
    if not initialize_serial():
        return None, 0
    
    try:
        # Send verify command
        print("Sending verify command...")
        ser.write(b'V')
        ser.flush()
        
        # Read response with timeout
        start_time = time.time()
        while time.time() - start_time < 10:  # 10-second timeout
            if ser.in_waiting:
                response = ser.readline().decode('utf-8').strip()
                print(f"Received: {response}")
                
                if "Found ID" in response:
                    fingerprint_id = int(response.split('#')[1].split()[0])
                    confidence = int(response.split('of')[1])
                    return fingerprint_id, confidence
                elif "Did not find a match" in response:
                    return None, 0
                    
            time.sleep(0.1)
        
        print("Verification timed out")
        return None, 0
        
    except Exception as e:
        print(f"Error during verification: {e}")
        return None, 0
        
    finally:
        if ser is not None:
            try:
                ser.close()
            except:
                pass

def enroll_fingerprint(finger_id):
    if not initialize_serial():
        return False
    
    try:
        # Send enrollment command
        command = f'E{finger_id}'.encode()
        print(f"Sending command: {command}")
        ser.write(command)
        ser.flush()
        
        # Read response with timeout
        start_time = time.time()
        while time.time() - start_time < 30:  # 30-second timeout
            if ser.in_waiting:
                response = ser.readline().decode('utf-8').strip()
                print(f"Received: {response}")
                
                if "Stored!" in response:
                    return True
                elif "Failed" in response:
                    return False
                    
            time.sleep(0.1)
        
        print("Enrollment timed out")
        return False
        
    except Exception as e:
        print(f"Error during enrollment: {e}")
        return False
        
    finally:
        if ser is not None:
            try:
                ser.close()
            except:
                pass

class User(UserMixin):
    def __init__(self, user_data, is_admin=False):
        self.id = user_data['phone']
        self.name = user_data['name']
        self.balance = user_data['balance']
        self.transactions = user_data['transactions']
        self.is_admin = is_admin
        if not is_admin:
            self.fingerprint_id = user_data['fingerprint_id']

def load_data():
    with open('bank_data.json', 'r') as file:
        return json.load(file)

def save_data(data):
    with open('bank_data.json', 'w') as file:
        json.dump(data, file, indent=4)

def load_users():
    return load_data()['users']

def load_admin():
    return load_data()['admin']

def save_users(users):
    data = load_data()
    data['users'] = users
    save_data(data)

def save_admin(admin):
    data = load_data()
    data['admin'] = admin
    save_data(data)

@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        admin_data = load_admin()
        return User(admin_data, is_admin=True)
    
    users = load_users()
    user_data = next((user for user in users if user['phone'] == user_id), None)
    if user_data:
        return User(user_data)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form.get('password')  # Optional for admin login
        
        # Check if admin login
        if phone == "admin":
            admin_data = load_admin()
            if password and password == admin_data['password']:
                user = User(admin_data, is_admin=True)
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials!')
            return render_template('login.html', show_password=True)
        
        # Regular user login
        users = load_users()
        user_data = next((user for user in users if user['phone'] == phone), None)
        
        if user_data:
            print("Verifying fingerprint...")
            fingerprint_id, confidence = verify_fingerprint()
            
            if fingerprint_id is not None and fingerprint_id == user_data['fingerprint_id']:
                user = User(user_data)
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Fingerprint verification failed!')
        else:
            flash('User not found!')
            
    # Show password field if admin is attempting to login
    show_password = request.args.get('admin') == 'true'
    return render_template('login.html', show_password=show_password)
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    users = load_users()
    user_data = next((user for user in users if user['phone'] == current_user.id), None)
    
    if user_data and user_data['transactions']:
        df = pd.DataFrame(user_data['transactions'])
        df['date'] = pd.to_datetime(df['date'])
        fig = px.line(df, x='date', y='balance', title='Balance History')
        graph_json = plotly.utils.PlotlyJSONEncoder().encode(fig)
    else:
        graph_json = None
    
    return render_template('dashboard.html', user=user_data, graph_json=graph_json)

@app.route('/make_payment', methods=['GET', 'POST'])
@login_required
def make_payment():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        users = load_users()
        user_idx = next((idx for idx, user in enumerate(users) 
                        if user['phone'] == current_user.id), None)
        
        if user_idx is not None:
            if users[user_idx]['balance'] >= amount:
                fingerprint_id, confidence = verify_fingerprint()
                
                if fingerprint_id is not None and fingerprint_id == users[user_idx]['fingerprint_id']:
                    # Deduct from user's account
                    users[user_idx]['balance'] -= amount
                    transaction = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": amount,
                        "type": "payment",
                        "balance": users[user_idx]['balance']
                    }
                    users[user_idx]['transactions'].append(transaction)
                    save_users(users)
                    
                    # Credit admin's account
                    admin_data = load_admin()
                    admin_data['balance'] += amount
                    transaction = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": amount,
                        "type": "receive",
                        "from": users[user_idx]['name'],
                        "balance": admin_data['balance']
                    }
                    admin_data['transactions'].append(transaction)
                    save_admin(admin_data)
                    
                    flash('Payment successful!')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Fingerprint verification failed!')
            else:
                flash('Insufficient balance!')
        else:
            flash('User not found!')
            
    return render_template('make_payment.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            phone = request.form['phone']
            initial_balance = float(request.form['initial_balance'])
        except ValueError:
            flash('Invalid input values. Please check your entries.')
            return render_template('register.html')

        users = load_users()
        
        if any(user['phone'] == phone for user in users):
            flash('Phone number already registered!')
            return render_template('register.html')

        used_ids = {user['fingerprint_id'] for user in users}
        next_id = 0
        while next_id in used_ids:
            next_id += 1

        print(f"Enrolling fingerprint with ID: {next_id}")
        enrollment_result = enroll_fingerprint(next_id)
        
        if enrollment_result:
            new_user = {
                "phone": phone,
                "name": name,
                "fingerprint_id": next_id,
                "balance": initial_balance,
                "transactions": [{
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "amount": initial_balance,
                    "type": "deposit",
                    "balance": initial_balance
                }]
            }
            
            users.append(new_user)
            save_users(users)
            
            flash('Registration successful! You can now login.')
            return redirect(url_for('login'))
        else:
            flash('Fingerprint enrollment failed! Please try again.')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied!')
        return redirect(url_for('dashboard'))
    
    admin_data = load_admin()
    
    # Create balance history graph
    if admin_data['transactions']:
        df = pd.DataFrame(admin_data['transactions'])
        df['date'] = pd.to_datetime(df['date'])
        fig = px.line(df, x='date', y='balance', title='Admin Balance History')
        graph_json = plotly.utils.PlotlyJSONEncoder().encode(fig)
    else:
        graph_json = None
    
    return render_template('admin_dashboard.html', 
                         admin=admin_data,
                         graph_json=graph_json)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@atexit.register
def cleanup():
    if ser is not None:
        try:
            ser.close()
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True)