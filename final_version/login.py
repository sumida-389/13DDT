import sqlite3
import tkinter as tk
from tkinter import messagebox
 
from constants import DARK_RED, RED_HOVER_COLOR,LIGHT_GREY
from databasesetup import hash_password
from helpers import clear_screen, make_hover_background

def login_screen(self):
    """Creates the login screen with username and password fields, a login button, and a link to the registration screen."""
    clear_screen(self.root)

    self.left_panel(
        head="Focalize",
        subtext="Knowledge at your fingertips."
    )

    # Right white frame where login goes
    right_panel = tk.Frame(self.root, bg="white")
    right_panel.pack(side="right", fill="both", expand=True)

    form = tk.Frame(right_panel, bg="white")
    form.place(relx=0.5, rely=0.5, anchor="center")

    # Heading
    tk.Label(form, text="Welcome Back!", bg="white", fg="black",
                font=("Helvetica", 22, "bold")).pack(anchor="w")

    # Link to register
    sub_text = tk.Frame(form, bg="white")
    sub_text.pack(anchor="w", pady=(6, 24))
    tk.Label(sub_text, text="No account? ", bg="white", fg=LIGHT_GREY,
                font=("Helvetica", 11)).pack(side="left")
    tk.Label(sub_text, text="Register here", bg="white", fg=DARK_RED,
                font=("Helvetica", 11, "underline")).pack(side="left")
    sub_text.winfo_children()[1].bind("<Button-1>", lambda e: self.register_screen())
    
    
    
    # read values when buttons clicked
    username_entry = self.text_input(form, "Username")
    password_entry = self.text_input(form, "Password", is_password=True)

    status = tk.Label(form, text="", fg=DARK_RED,
                        font=("Helvetica", 11))
    status.pack(anchor="w", pady=(0, 8))

    # What happens when Login is clicked
    def attempt_login():
        """Checks the database for the given username and password."""
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
        # returns (id, username) or None
        user = cursor.fetchone()  

        if user:
            self.current_user_id = user[0]
            self.current_username = user[1]
            # Update how many days in a row they've logged in
            self.current_streak = self.db.update_streak(user[0])
            # go to home screen
            self.home_screen()    
        else:
            status.config(text="Incorrect username or password.")

    # Login button
    login_btn=tk.Label(form, text="Login", bg=DARK_RED, fg="white",
                font=("Helvetica", 13, "bold"), relief="flat", bd=0,
                width=30, height=2)
    login_btn.pack(pady=(4, 0))
    make_hover_background(login_btn,DARK_RED,RED_HOVER_COLOR,attempt_login)
    
def register_screen(self):
    """Makes the registration screen with username and password fields, a register button, and a link to the login screen."""
    clear_screen(self.root)
    self.left_panel(
        head="Create Account",
        subtext=" "
    )
    right_frame = tk.Frame(self.root, bg="white")
    right_frame.pack(side="right", fill="both", expand=True)

    form = tk.Frame(right_frame, bg="white")
    form.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(form, text="Welcome to Focalize", bg="white", fg="black",
                font=("Helvetica", 22, "bold")).pack(anchor="w")
    
    sub = tk.Frame(form, bg="white")
    sub.pack(anchor="w", pady=(6, 24))
    tk.Label(sub, text="Already registered?", bg="white", fg=LIGHT_GREY,
                font=("Helvetica", 11)).pack(side="left")
    tk.Label(sub, text="Login here", bg="white", fg=DARK_RED,
                font=("Helvetica", 11, "underline")).pack(side="left")
    sub.winfo_children()[1].bind("<Button-1>", lambda e: self.login_screen()) # Go back to login screen

    # Input fields
    username_entry  = self.text_input(form, "Username")
    password_entry  = self.text_input(form, "Password",        is_password=True)
    confirm_entry   = self.text_input(form, "Confirm Password", is_password=True)

    # Status message
    status = tk.Label(form, text="", bg="white", fg=DARK_RED,
                        font=("Helvetica", 11))
    status.pack(anchor="w", pady=(0, 8))
    
    def attempt_register():
        """Tries to register new user with the username and password."""
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
        
        try:
            cursor = self.db.get_cursor()
            hashed = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed)
            )
            # save to database
            self.db.commit() 
            messagebox.showinfo("Success", f"Account created! Welcome, {username}.")
            self.login_screen()
        except sqlite3.IntegrityError:
            status.config(text="Username already exists.")
    
    # Register button in label form so that I can change the color on hover
    regis_btn=tk.Label(form, text="Register",bg=DARK_RED, fg="white",
            font=("Helvetica", 13, "bold"),relief="flat", bd=0, width=30, height=2)
    regis_btn.pack(pady=(4, 0))
    regis_btn.bind("<Button-1>", lambda e: attempt_register())