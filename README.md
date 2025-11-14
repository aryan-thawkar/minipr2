# Fingerprint Payment System

A simplified payment system using fingerprint authentication.

## Features

- **Simple Payment Interface**: Users can make payments directly from the home page without logging in
- **Fingerprint Authentication**: Each payment requires fingerprint verification
- **User Registration**: New users can register and enroll their fingerprints
- **Admin Dashboard**: Administrators can view payment transactions and balance history
- **Animated Feedback**: Success and failure animations for payment attempts

## How to Use

### For Users

1. **Make a Payment**:
   - Enter your phone number and payment amount on the home page
   - Click "Place Fingerprint & Pay"
   - Place your registered finger on the scanner
   - Wait for success/failure animation

2. **Register New User**:
   - Click "Register New User" on the home page
   - Fill in your details (name, phone, initial balance)
   - Follow the fingerprint enrollment process
   - After successful registration, you can make payments

### For Administrators

1. **Access Admin Dashboard**:
   - Click "Admin" in the navigation
   - Login with admin credentials
   - View balance and transaction history

## Technical Details

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Database**: JSON file storage
- **Authentication**: Fingerprint sensor integration
- **Charts**: Plotly.js for transaction visualization

## Security Features

- No user login required - reduces attack surface
- Fingerprint verification for each payment
- Admin-only access to transaction history
- No user transaction history displayed to maintain privacy

## File Structure

```
minipr2/
├── app.py                 # Main Flask application
├── bank_data.json         # User and admin data storage
└── templates/
    ├── base.html          # Base template with navigation
    ├── index.html         # Home page with payment form
    ├── register.html      # User registration page
    ├── admin_login.html   # Admin login page
    ├── admin_dashboard.html # Admin dashboard
    └── make_payment.html  # Direct payment page (redirects to home)
```

## Running the Application

1. Install required packages:
   ```
   pip install flask flask-login plotly pandas pyserial
   ```

2. Connect your fingerprint sensor

3. Run the application:
   ```
   python app.py
   ```

4. Access the application at `http://127.0.0.1:5000`

## Changes Made

- Removed user login system
- Simplified payment process to single-step operation
- Added animated success/failure feedback
- Removed user transaction history viewing
- Kept admin functionality for business oversight
- Enhanced user experience with better UI/UX