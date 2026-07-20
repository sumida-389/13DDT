import tkinter as tk
from tkinter import *
import sqlite3
import os
import hashlib
from tkinter import messagebox 


root = tk.Tk()

class database_setup:
    def __init__(self,db_path="study_app.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)#connect to the database file (creates it if it doesn't exist)
                
    def create_tables(self): 
        cursor = self.connection.cursor() #cursor object to execute SQL commands

        #users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL UNIQUE,
                password    TEXT    NOT NULL
            )
        """)

        #notes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                title      TEXT    NOT NULL,
                body       TEXT    NOT NULL DEFAULT '',
                summary    TEXT    DEFAULT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        #deck table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                name       TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        #flashcards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id       INTEGER NOT NULL,
                user_id       INTEGER NOT NULL,
                front         TEXT    NOT NULL,
                back          TEXT    NOT NULL,
                FOREIGN KEY (deck_id)  REFERENCES decks(id)  ON DELETE CASCADE,
                FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE
            )
        """)
        
        #quiz + questions tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                title      TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        self.connection.commit()
        
    def get_cursor(self):
        # returns a cursor so other parts of the app can query the database
        return self.connection.cursor()
 
    def commit(self):
        # saves any changes made to the database
        self.connection.commit()
        
db=database_setup()
db.create_tables()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()




def clear_screen(root):
    for widget in root.winfo_children():
        widget.destroy()

class appface:
    def __init__(self,root):
        self.root = root
        self.root.title("Study App")
        self.root.geometry("900x600")
        self.current_user_id = None # no one logged in yet
        self.current_username = None
        self.left_panel("testing bigtxt", "testing small text")
        self.db = database_setup() # create an object of the database setup class
        self.db.create_tables() # create the tables in the database if they don't exist
        self.login_screen()

        
    def left_panel(self,head,subtext):
        left = tk.Frame(self.root, bg="#780606", width=400, height=400)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
 
        tk.Label(left, text="✳", bg="#780606", fg="white",
                 font=("Helvetica", 40, "bold")).place(x=44, y=44)
 
        tk.Label(left, text=head, bg="#780606", fg="white",
                 font=("Helvetica", 30, "bold"), justify="left").place(x=44, y=200)
 
        tk.Label(left, text=subtext, bg="#780606", fg="#ccccff",
                 font=("Helvetica", 12), justify="left",
                 wraplength=320).place(x=44, y=330)
    

    def text_input(self, parent, placeholder, is_password=False):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="x", pady=(0, 14))
 
        entry = tk.Entry(frame, font=("Helvetica", 13),
                         bg="white", fg="#aaaaaa",
                         relief="flat", bd=0, width=32)
        entry.insert(0, placeholder)
        entry.pack(fill="x", ipady=8)
 
        underline = tk.Frame(frame, bg="#dddddd", height=1)
        underline.pack(fill="x")



        return entry
    
    def login_screen(self):
        clear_screen(self.root)
 
        self.left_panel(
            head="study app",
            subtext="the usbtext thing"
        )
 
        # Right white frame where login goes
        right = tk.Frame(self.root, bg="white")
        right.pack(side="right", fill="both", expand=True)
 
        form = tk.Frame(right, bg="white")
        form.place(relx=0.5, rely=0.5, anchor="center")
 
        # name
        tk.Label(form, text="Study App", bg="white", fg="#111111",
                 font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 30))
 
        # Heading
        tk.Label(form, text="Welcome Back!", bg="white", fg="#0d0d0d",
                 font=("Helvetica", 22, "bold")).pack(anchor="w")
 
        # Link to register
        sub = tk.Frame(form, bg="white")
        sub.pack(anchor="w", pady=(6, 24))
        tk.Label(sub, text="No account? ", bg="white", fg="#888888",
                 font=("Helvetica", 11)).pack(side="left")
        tk.Label(sub, text="Register here", bg="white", fg="#2A2AE1",
                 font=("Helvetica", 11, "underline"),
                 cursor="hand2").pack(side="left")
        
        
        
        
        # read values when buttons clicked
        username_entry = self.text_input(form, "Username")
        password_entry = self.text_input(form, "Password", is_password=True)
 
        # Status message (shows errors in red)
        status = tk.Label(form, text="", bg="white", fg="red",
                          font=("Helvetica", 11))
        status.pack(anchor="w", pady=(0, 8))
 
        # What happens when Login is clicked
        def attempt_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
 
            #validation
            if username == "Username" or username == "":
                status.config(text="Please enter your username.")
                return
            if password == "Password" or password == "":
                status.config(text="Please enter your password.")
                return
 
            # Check the database
            cursor = self.db.get_cursor()
            hashed = hash_password(password)
            cursor.execute(
                "SELECT id, username FROM users WHERE username=? AND password=?",
                (username, hashed)
            )
            user = cursor.fetchone()   # returns (id, username) or None
 
            if user:
                self.current_user_id = user[0]
                self.current_username = user[1]
                self.login_screen()     # go to home screen
            else:
                status.config(text="Incorrect username or password.")
 
        # Login button
        tk.Button(form, text="Login Now",
                  bg="#0d0d0d", fg="white",
                  font=("Helvetica", 13, "bold"),
                  relief="flat", bd=0,
                  cursor="hand2", width=30, height=2,
                  activebackground="#2A2AE1", activeforeground="white",
                  command=attempt_login).pack(pady=(4, 0))
        






    def register_screen(self):
        clear_screen(self.root)
        self.left_panel(
            head="create account",
            subtext="subtext for create account screen"
        )
        right = tk.Frame(self.root, bg="white")
        right.pack(side="right", fill="both", expand=True)
 
        form = tk.Frame(right, bg="white")
        form.place(relx=0.5, rely=0.5, anchor="center")
 
        tk.Label(form, text="Study App", bg="white", fg="#111111",
                 font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 30))
 
        tk.Label(form, text="create acc", bg="white", fg="#0d0d0d",
                 font=("Helvetica", 22, "bold")).pack(anchor="w")
        
        sub = tk.Frame(form, bg="white")
        sub.pack(anchor="w", pady=(6, 24))
        tk.Label(sub, text="Already have acc?", bg="white", fg="#888888",
                 font=("Helvetica", 11)).pack(side="left")
        tk.Label(sub, text="Login here", bg="white", fg="#2A2AE1",
                 font=("Helvetica", 11, "underline"),
                 cursor="hand2").pack(side="left")
        sub.winfo_children()[1].bind("<Button-1>", lambda e: self.login_screen())
 
        # Input fields
        username_entry  = self.text_input(form, "Username")
        password_entry  = self.text_input(form, "Password",        is_password=True)
        confirm_entry   = self.text_input(form, "Confirm Password", is_password=True)
 
        # Status message
        status = tk.Label(form, text="", bg="white", fg="red",
                          font=("Helvetica", 11))
        status.pack(anchor="w", pady=(0, 8))
        
        def attempt_register():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            confirm  = confirm_entry.get().strip()

            # Validation checks
            if username in ("Username", ""):
                status.config(text="Please enter a username.")
                return
            if password in ("Password", ""):
                status.config(text="Please enter a password.")
                return
            if confirm in ("Confirm Password", ""):
                status.config(text="Please confirm your password.")
                return
            if password != confirm:
                status.config(text="Passwords do not match.")
                return
            
            cursor = self.db.get_cursor()
            hashed = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed)
            )
            self.db.commit()   # save to database
            messagebox.showinfo("Success", f"Account created! Welcome, {username}.")
            self.login_screen()
            
        tk.Button(form, text="create acc",
                bg="#a6ba42", fg="white",
                font=("Helvetica", 13, "bold"),
                relief="flat", bd=0,
                cursor="hand2", width=30, height=2,
                activebackground="#2A2AE1", activeforeground="white",
                command=attempt_register).pack(pady=(4, 0))
 

            
            
            
            
        
    
    
root=tk.Tk()
app = appface(root) 
root.mainloop()   