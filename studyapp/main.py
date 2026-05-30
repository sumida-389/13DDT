import sqlite3
import hashlib  

def password(user_password):
    return hashlib.sha256(user_password.encode()).hexdigest() # Turns a plaintext password into a secure hash

user_password=input("Enter a password: ")
print(password(user_password))

def create_database():
    connection = sqlite3.connect("studyapp.db") # Create/Connects the database file
    cursor = connection.cursor() # Create a cursor object to interact with the database