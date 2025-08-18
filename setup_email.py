#!/usr/bin/env python3
"""
Script to manually configure email settings.
Use this if the admin panel email config isn't working.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import EmailConfigModel, get_db
from flask import Flask

# Create a minimal Flask app for database context
app = Flask(__name__)
app.config['DATABASE'] = 'blog.db'

def setup_email():
    """Manually configure email settings."""
    
    print("Email Configuration Setup")
    print("=" * 40)
    
    # Get user input
    smtp_server = input("SMTP Server (e.g., smtp.gmail.com): ").strip()
    smtp_port = input("SMTP Port (587 for Gmail): ").strip()
    smtp_username = input("SMTP Username (your email): ").strip()
    smtp_password = input("SMTP Password (App Password for Gmail): ").strip()
    from_email = input("From Email (same as username usually): ").strip()
    to_email = input("To Email (where to send notifications): ").strip()
    use_tls = input("Use TLS? (y/n, default y): ").strip().lower()
    
    # Set defaults
    if not smtp_port:
        smtp_port = "587"
    if not from_email:
        from_email = smtp_username
    if use_tls != 'n':
        use_tls = True
    else:
        use_tls = False
    
    # Validate required fields
    if not all([smtp_server, smtp_username, smtp_password, to_email]):
        print("ERROR: All fields except TLS are required!")
        return False
    
    try:
        smtp_port = int(smtp_port)
    except ValueError:
        print("ERROR: Port must be a number!")
        return False
    
    with app.app_context():
        try:
            print("\nSaving configuration...")
            EmailConfigModel.save_config(
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                smtp_username=smtp_username,
                smtp_password=smtp_password,
                from_email=from_email,
                to_email=to_email,
                use_tls=use_tls
            )
            print("SUCCESS: Email configuration saved!")
            
            # Verify it was saved
            config = EmailConfigModel.get_config()
            if config:
                print("SUCCESS: Configuration verified in database")
                print(f"  Server: {config['smtp_server']}")
                print(f"  Username: {config['smtp_username']}")
                print(f"  From: {config['from_email']}")
                print(f"  To: {config['to_email']}")
                return True
            else:
                print("ERROR: Configuration not found after saving")
                return False
                
        except Exception as e:
            print(f"ERROR: Failed to save configuration: {e}")
            return False

if __name__ == "__main__":
    print("This script will help you configure email settings manually.")
    print("For Gmail, make sure you:")
    print("1. Have 2FA enabled")
    print("2. Generated an App Password (not your regular password)")
    print("3. Use smtp.gmail.com:587 with TLS")
    print()
    
    success = setup_email()
    if success:
        print("\nEmail configuration complete!")
        print("You can now test it by running: python test_email.py")
    else:
        print("\nConfiguration failed. Please try again.")