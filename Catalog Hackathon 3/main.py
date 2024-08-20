import hashlib
import getpass
import re
import os

supply_chain = []
user_credentials = {}
def generate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def log_operation(operation, details, username):
    with open("log.txt", "a") as log_file:
        log_file.write(f"{operation} by {username}: {details}\n")

def validate_input(input_data, data_type):
    if data_type == "name":
        return re.match("^[A-Za-z0-9 ]+$", input_data) is not None
    elif data_type == "date":
        return re.match("^\d{4}-\d{2}-\d{2}$", input_data) is not None
    elif data_type == "status":
        return input_data in ["Manufactured", "Distributed", "Delivered"]
    return False

def register_user():
    username = input("Enter a new username: ")
    if username in user_credentials:
        print("Username already exists. Please choose a different one.")
        return None
    password = getpass.getpass("Enter a new password: ")
    hashed_password = generate_hash(password)
    user_credentials[username] = hashed_password
    with open("cred.txt", "a") as cred_file:
        cred_file.write(f"{username}:{hashed_password}\n")
    print(f"User '{username}' registered successfully!")

def authenticate():
    attempts = 3
    while attempts > 0:
        username = input("Enter Username: ")
        if username in user_credentials:
            password = getpass.getpass("Enter Password: ")
            if generate_hash(password) == user_credentials[username]:
                print("Access Granted.")
                return username
            else:
                attempts -= 1
                print(f"Access Denied. {attempts} attempts left.")
        else:
            print("Username not found.")
            attempts -= 1
    return None

def add_transaction(drug_name, manufacturer, batch_number, expiry_date, status, username):
    if not (validate_input(drug_name, "name") and 
            validate_input(manufacturer, "name") and 
            validate_input(batch_number, "name") and 
            validate_input(expiry_date, "date") and 
            validate_input(status, "status")):
        print("Invalid input detected. Transaction aborted.")
        return

    transaction = {
        'Drug Name': drug_name,
        'Manufacturer': manufacturer,
        'Batch Number': batch_number,
        'Expiry Date': expiry_date,
        'Status': status,
        'Hash': generate_hash(drug_name + manufacturer + batch_number + expiry_date + status)
    }
    supply_chain.append(transaction)
    print(f"\nTransaction added successfully:\n\n")
    log_operation("Add Transaction", f"Drug: {drug_name}, Manufacturer: {manufacturer}, Batch: {batch_number}", username)

def verify_transaction(drug_name, batch_number, username):
    if not (validate_input(drug_name, "name") and validate_input(batch_number, "name")):
        print("Invalid input detected. Verification aborted.")
        return

    for transaction in supply_chain:
        if transaction['Drug Name'] == drug_name and transaction['Batch Number'] == batch_number:
            print(f"\nTransaction verified:\n")
            log_operation("Verify Transaction", f"Drug: {drug_name}, Batch: {batch_number}", username)
            return
    print("\nTransaction not found or has been tampered with.\n")
    log_operation("Verify Transaction Failed", f"Drug: {drug_name}, Batch: {batch_number}", username)

def trace_drug(drug_name):
    if not validate_input(drug_name, "name"):
        print("Invalid input detected. Trace aborted.")
        return

    print(f"\nTracing drug '{drug_name}':\n")
    found = False
    for transaction in supply_chain:
        if transaction['Drug Name'] == drug_name:
            found = True
            print(f"Status: {transaction['Status']}")
            print(f"Expiry Date: {transaction['Expiry Date']}\n")
    if not found:
        print(f"No records found for drug '{drug_name}'.")

def load_credentials():
    if os.path.exists("cred.txt"):
        with open("cred.txt", "r") as cred_file:
            for line in cred_file:
                username, hashed_password = line.strip().split(':')
                user_credentials[username] = hashed_password

def display_menu():
    print("\nPharma Supply Chain System using Smart Contracts")
    print("1. Register User")
    print("2. Login")
    print("3. Exit")

def display_user_menu():
    print("\nPharma Supply Chain System - User Menu")
    print("1. Add Transaction")
    print("2. Verify Transaction")
    print("3. Trace Drug")
    print("4. Logout")

load_credentials()

current_user = None

while True:
    if current_user is None:
        display_menu()
        choice = input("Choose an option: ")

        if choice == '1':
            register_user()

        elif choice == '2':
            current_user = authenticate()

        elif choice == '3':
            print("Exiting the system.")
            break

        else:
            print("Invalid option. Please try again.")
    else:
        display_user_menu()
        user_choice = input("Choose an option: ")

        if user_choice == '1':
            drug_name = input("Enter Drug Name: ")
            manufacturer = input("Enter Manufacturer: ")
            batch_number = input("Enter Batch Number: ")
            expiry_date = input("Enter Expiry Date (YYYY-MM-DD): ")
            status = input("Enter Status (Manufactured/Distributed/Delivered): ")
            add_transaction(drug_name, manufacturer, batch_number, expiry_date, status, current_user)

        elif user_choice == '2':
            drug_name = input("Enter Drug Name to Verify: ")
            batch_number = input("Enter Batch Number to Verify: ")
            verify_transaction(drug_name, batch_number, current_user)

        elif user_choice == '3':
            drug_name = input("Enter Drug Name to Trace: ")
            trace_drug(drug_name)

        elif user_choice == '4':
            print("Logging out...")
            current_user = None

        else:
            print("Invalid option. Please try again.")
