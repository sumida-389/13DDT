import tkinter as tk
from tkinter import *
import sqlite3
import os
import hashlib
from tkinter import messagebox 
TYPE_COLORS = {
    "exam":       "#FB9EBB",
    "assignment": "#FEDCDB",
    "study":      "#FFE6EE",
    "other":      "#FEDCD2",
}
DARK_RED="#780606"
NAVY_BLUE="#000066"
GREY_BG="#f9f9f9"
RED_HOVER_COLOR="#400000"
BLUE_HOVER_COLOR="#000026"
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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct TEXT NOT NULL,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE)
                """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id    INTEGER NOT NULL,
                user_id    INTEGER NOT NULL,
                score      INTEGER NOT NULL,
                total      INTEGER NOT NULL,
                taken_at   TEXT    NOT NULL,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT    NOT NULL,
            event_date  TEXT    NOT NULL,
            event_type  TEXT    NOT NULL DEFAULT 'other',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)
            """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                rem_title      TEXT    NOT NULL,
                remind_at  TEXT    NOT NULL,
                fired      INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

    def get_cursor(self):
        # returns a cursor so other parts of the app can query the database
        return self.connection.cursor()
 
    def commit(self):
        # saves any changes made to the database
        self.connection.commit()
        

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def clear_screen(root):
    for widget in root.winfo_children():
        widget.destroy()

class appface:
    def __init__(self,root):
        self.root = root
        self.root.title("Focalize")
        self.root.geometry("1000x700")
        self.current_user_id = None # no one logged in yet
        self.current_username = None
        self.left_panel("testing bigtxt", "testing small text")
        self.db = database_setup() # create an object of the database setup class
        self.db.create_tables() # create the tables in the database if they don't exist
        self.login_screen()

        
    def left_panel(self,head,subtext):
        left_frame = tk.Frame(self.root, bg=DARK_RED, width=400, height=400)
        left_frame.pack(side="left", fill="y")
        left_frame.pack_propagate(False)
 
        tk.Label(left_frame, text="✳", bg=DARK_RED, fg="white",
                 font=("Helvetica", 40, "bold")).place(x=44, y=44)
 
        tk.Label(left_frame, text=head, bg=DARK_RED, fg="white",
                 font=("Helvetica", 30, "bold"), justify="left").place(x=44, y=200)
 
        tk.Label(left_frame, text=subtext, bg=DARK_RED, fg="white",
                 font=("Helvetica", 12), justify="left",
                 wraplength=320).place(x=44, y=272)
    

    def text_input(self, parent, placeholder, is_password=False):
        text_frame = tk.Frame(parent, bg="white")
        text_frame.pack(fill="x", pady=(0, 14))
 
        user_pass = tk.Entry(text_frame, font=("Helvetica", 13),
                         bg="white", fg="#aaaaaa",
                         relief="flat", bd=0, width=32)
        user_pass.insert(0, placeholder)
        user_pass.pack(fill="x", ipady=8)
 
        underline = tk.Frame(text_frame, bg="#dddddd", height=1)
        underline.pack(fill="x")

        def on_click_field(event):
            if user_pass.get() == placeholder:
                user_pass.delete(0, "end")
                user_pass.config(fg="#111111")
                if is_password:
                    user_pass.config(show="•")     # hide password with dots
            underline.config(bg="#2A2AE1")
        def unclick_field(event):
            if user_pass.get() == "":
                user_pass.config(fg="#aaaaaa", show="")
                user_pass.insert(0, placeholder)   # put placeholder back
            underline.config(bg="#dddddd") 

        user_pass.bind("<FocusIn>",  on_click_field) # when the user clicks on the field, it will clear the placeholder text and change the text color to black. If it's a password field, it will also hide the input with dots.
        user_pass.bind("<FocusOut>", unclick_field) # when the user clicks away from the field, if it's empty it will put the placeholder text back and change the text color to gray. It will also show the input if it's a password field.
        return user_pass
    
    def login_screen(self):
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
        tk.Label(sub_text, text="No account? ", bg="white", fg="#888888",
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
                self.home_screen()     # go to home screen
            else:
                status.config(text="Incorrect username or password.")
 
        # Login button
        login_btn=tk.Label(form, text="Login", bg=DARK_RED, fg="white",
                  font=("Helvetica", 13, "bold"), relief="flat", bd=0,
                  width=30, height=2)
        login_btn.pack(pady=(4, 0))
        login_btn.bind("<Button-1>", lambda e: attempt_login())
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg=RED_HOVER_COLOR))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg=DARK_RED))


        print(type(login_btn))
    def register_screen(self):
        clear_screen(self.root)
        self.left_panel(
            head="Create Account",
            subtext=" "
        )
        right_frame = tk.Frame(self.root, bg="white")
        right_frame.pack(side="right", fill="both", expand=True)
 
        form = tk.Frame(right_frame, bg="white")
        form.place(relx=0.5, rely=0.5, anchor="center")
  
        tk.Label(form, text="Welcome to Focalize", bg="white", fg="#0d0d0d",
                 font=("Helvetica", 22, "bold")).pack(anchor="w")
        
        sub = tk.Frame(form, bg="white")
        sub.pack(anchor="w", pady=(6, 24))
        tk.Label(sub, text="Already registered?", bg="white", fg="#888888",
                 font=("Helvetica", 11)).pack(side="left")
        tk.Label(sub, text="Login here", bg="white", fg=DARK_RED,
                 font=("Helvetica", 11, "underline")).pack(side="left")
        sub.winfo_children()[1].bind("<Button-1>", lambda e: self.login_screen())
 
        # Input fields
        username_entry  = self.text_input(form, "Username")
        password_entry  = self.text_input(form, "Password",        is_password=True)
        confirm_entry   = self.text_input(form, "Confirm Password", is_password=True)
 
        # Status message
        status = tk.Label(form, text="", bg="white", fg=DARK_RED,
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
            
        regis_btn=tk.Label(form, text="Register",
                bg=DARK_RED, fg="white",
                font=("Helvetica", 13, "bold"),
                relief="flat", bd=0, width=30, height=2)
        regis_btn.pack(pady=(4, 0))
        regis_btn.bind("<Button-1>", lambda e: attempt_register())
        
    def home_screen(self):
        clear_screen(self.root)
        self.root.configure(bg="white")
        tk.Label(self.root, text=f"Welcome, {self.current_username}",
        font=("Helvetica", 20, "bold"),fg="white",bg=DARK_RED).pack(pady=20)

        tk.Button( self.root,text="Open Notes",command=self.notes_screen).pack(pady=10)
        
        tk.Button(self.root,text="Flashcards",command=self.flashcards_screen).pack(pady=10)
            
        tk.Button(self.root,text="Quizzes",command=self.quiz_screen).pack(pady=10)
        
        tk.Button(self.root,text="Calendar",command=self.calendar_screen).pack(pady=10)
        
        tk.Button(self.root,text="Reminders",command=self.reminders_screen).pack(pady=10)
    def notes_screen(self):
        clear_screen(self.root)
        self.root.configure(bg=GREY_BG)
        cursor = self.db.get_cursor()

        header = tk.Frame(self.root, bg=DARK_RED)
        header.pack(fill="x")
        tk.Label(header, text="Notes", bg=DARK_RED, fg="white",
                 font=("Helvetica", 18, "bold")).pack(side="left", padx=20, pady=12)

        new_bar = tk.Frame(self.root, bg=GREY_BG, pady=10)
        new_bar.pack(fill="x", padx=20, pady=(14, 4))
        tk.Label(new_bar, text="Title:", bg=GREY_BG,
                 font=("Helvetica", 11,"bold")).pack(side="left")
        new_title_entry = tk.Entry(new_bar, width=28, font=("Helvetica", 11),
                                   relief="solid", bd=1,bg=GREY_BG)
        new_title_entry.pack(side="left", padx=8, ipady=4)

        status_lbl = tk.Label(self.root, text="", bg=GREY_BG, fg=DARK_RED,
                              font=("Helvetica", 10))
        status_lbl.pack()
        footer= tk.Frame(self.root, bg=GREY_BG)
        footer.pack(fill="x", side="bottom")
        back_notes=tk.Label(footer, text="Back", bg=NAVY_BLUE, fg="white",padx=14, pady=6,)
        back_notes.pack(side="right", padx=25, pady=15)
        back_notes.bind("<Button-1>", lambda e: self.home_screen())
        back_notes.bind("<Enter>", lambda e: back_notes.config(bg=BLUE_HOVER_COLOR))
        back_notes.bind("<Leave>", lambda e: back_notes.config(bg=NAVY_BLUE))
        def create_section():
            title = new_title_entry.get().strip()
            cursor.execute(
                "INSERT INTO notes (user_id, title, body) VALUES (?, ?, ?)",
                (self.current_user_id, title, "")
            )
            self.db.commit()
            new_title_entry.delete(0, "end")
            status_lbl.config(text="")
            load_sections()
        create_note_lbl=tk.Label(new_bar, text="Create new set", bg=NAVY_BLUE, fg="white",
                                 relief="raised", font=("Helvetica", 11),bd=0, padx=15,pady=6)
        create_note_lbl.pack(side="left")
        create_note_lbl.bind("<Button-1>", lambda e: create_section())
        create_note_lbl.bind("<Enter>", lambda e: create_note_lbl.config(bg=BLUE_HOVER_COLOR))
        create_note_lbl.bind("<Leave>", lambda e: create_note_lbl.config(bg=NAVY_BLUE))
        list_canvas = tk.Canvas(self.root, bg=GREY_BG)
        list_canvas.pack(fill="both", expand=True, padx=20, pady=10)
        inner = tk.Frame(list_canvas, bg=GREY_BG)
        list_canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: list_canvas.configure(
            scrollregion=list_canvas.bbox("all")))

        def load_sections():
            for widgets in inner.winfo_children():
                widgets.destroy()
            cursor.execute(
                "SELECT id, title, body FROM notes WHERE user_id=? ORDER BY id",
                (self.current_user_id,)
            )
            rows = cursor.fetchall()
            if not rows:
                tk.Label(inner, text="No notes yet!",
                         bg=GREY_BG, fg="#888888",
                         font=("Helvetica", 12)).pack(pady=30)
                return
            for note_id, note_title, note_body in rows:
                note_card = tk.Frame(inner, bg=GREY_BG, relief="solid", bd=1)
                note_card.pack(fill="x", pady=6)

                left = tk.Frame(note_card, bg=GREY_BG)
                left.pack(side="left", fill="both", expand=True, padx=14, pady=10)
                tk.Label(left, text=note_title, bg=GREY_BG, fg="black",
                         font=("Helvetica", 13, "bold"), anchor="w").pack(anchor="w")
                def open_section(nid=note_id, ntitle=note_title):
                    self.note_edit_screen(nid, ntitle)

                def delete_section(nid=note_id, ntitle=note_title):
                    if messagebox.askyesno("Delete", f'Delete "{ntitle}"?'):
                        cursor.execute("DELETE FROM notes WHERE id=?", (nid,))
                        self.db.commit()
                        load_sections()

                note_card.bind("<Button-1>", lambda e, f=open_section: f())
                left.bind("<Button-1>", lambda e, f=open_section: f())

                btn_frame = tk.Frame(note_card, bg="white")
                btn_frame.pack(side="right", padx=10)
                tk.Button(btn_frame, text="Open", fg=DARK_RED,relief="flat", font=("Helvetica", 10),
                          padx=8, command=open_section).pack(pady=2)
                tk.Button(btn_frame, text="Delete", fg=DARK_RED,
                          relief="flat", font=("Helvetica", 10),
                          command=delete_section).pack(pady=2)

        load_sections()

    def note_edit_screen(self, note_id, note_title):
        clear_screen(self.root)
        self.root.configure(bg=GREY_BG)
        cursor = self.db.get_cursor()

        header = tk.Frame(self.root, bg=DARK_RED)
        header.pack(fill="x")

        back_lbl = tk.Label(header, text="◄", bg=DARK_RED, fg="white",font=("Helvetica",20), cursor="hand2")
        back_lbl.pack(side="left", padx=(15, 8), pady=12)
        back_lbl.bind("<Button-1>", lambda e: self.notes_screen())

        header_lbl = tk.Label(header, text=note_title, bg=DARK_RED, fg="white",
                            font=("Helvetica", 16, "bold"))
        header_lbl.pack(side="left", pady=12)

        text_frame = tk.Frame(self.root, bg=GREY_BG)
        text_frame.pack(fill="both", expand=True)

        notes_text = tk.Text(text_frame, wrap="word", font=("Helvetica", 13),
                             relief="flat", bd=0, padx=20, pady=16)
        notes_text.pack(side="left", fill="both", expand=True)

        cursor.execute("SELECT body FROM notes WHERE id=?", (note_id,))
        existing = cursor.fetchone()
        if existing:
            notes_text.insert("1.0", existing[0])

        save_bar = tk.Frame(self.root, bg="#f5f5f5")
        save_bar.pack(fill="x")
        save_status = tk.Label(save_bar, text="", bg="#f5f5f5", fg="green",
                               font=("Helvetica", 10))
        save_status.pack(side="left", padx=14)
        
        def save_note():
            new_body = notes_text.get("1.0", "end-1c")
            cursor.execute(
                "UPDATE notes SET body=? WHERE id=?",
                (new_body, note_id)
            )
            self.db.commit()
            messagebox.showinfo("Saved", "Your changes have been saved.")

        save_lbl=tk.Label(save_bar, text="Save", bg=NAVY_BLUE, fg="white",
                  relief="flat", font=("Helvetica", 11),padx=14, pady=6)
        save_lbl.pack(side="right", padx=14, pady=8)
        save_lbl.bind("<Button-1>", lambda e: save_note())
    def flashcards_screen(self):
        clear_screen(self.root)
        self.root.configure(bg=GREY_BG)
        cursor = self.db.get_cursor()

        header = tk.Frame(self.root, bg=DARK_RED)
        header.pack(fill="x")
        tk.Label(header, text="Flashcards", bg=DARK_RED, fg="white",
                 font=("Helvetica", 18, "bold")).pack(side="left", padx=20, pady=12)
        footer= tk.Frame(self.root, bg=GREY_BG)
        footer.pack(fill="x", side="bottom")
        back_notes=tk.Label(footer, text="Back", bg=NAVY_BLUE, fg="white",padx=14, pady=6,)
        back_notes.pack(side="right", padx=25, pady=15)
        back_notes.bind("<Enter>", lambda e: back_notes.config(bg=BLUE_HOVER_COLOR))
        back_notes.bind("<Leave>", lambda e: back_notes.config(bg=NAVY_BLUE))
        back_notes.bind("<Button-1>", lambda e: self.home_screen())


        new_bar = tk.Frame(self.root, bg=GREY_BG, pady=10)
        new_bar.pack(fill="x", padx=20, pady=(14, 4))
        tk.Label(new_bar, text="New set name:", bg=GREY_BG,
                 font=("Helvetica", 11)).pack(side="left")
        new_deck_entry = tk.Entry(new_bar, width=28, font=("Helvetica", 11),
                                  relief="solid", bd=1)
        new_deck_entry.pack(side="left", padx=8, ipady=4)

        status_lbl = tk.Label(self.root, text="", bg=GREY_BG, fg=DARK_RED,
                              font=("Helvetica", 10))
        status_lbl.pack()

        def create_deck():
            name = new_deck_entry.get().strip()
            if not name:
                status_lbl.config(text="Enter a set name.")
                return
            cursor.execute(
                "INSERT INTO decks (user_id, name) VALUES (?, ?)",
                (self.current_user_id, name)
            )
            self.db.commit()
            new_deck_entry.delete(0, "end")
            status_lbl.config(text="")
            load_decks()

        create_lbl=tk.Label(new_bar, text="Create Set", bg=NAVY_BLUE, fg="white",
                  relief="flat", font=("Helvetica", 11),padx=10,pady=6)
        create_lbl.pack(side="left")
        create_lbl.bind("<Enter>", lambda e: create_lbl.config(bg=BLUE_HOVER_COLOR))
        create_lbl.bind("<Leave>", lambda e: create_lbl.config(bg=NAVY_BLUE))
        create_lbl.bind("<Button-1>", lambda e: create_deck())
        

        list_frame = tk.Frame(self.root, bg=GREY_BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        def load_decks():
            for widgets in list_frame.winfo_children():
                widgets.destroy()
            cursor.execute(
                "SELECT id, name FROM decks WHERE user_id=? ORDER BY id",
                (self.current_user_id,)
            )
            decks = cursor.fetchall()
            if not decks:
                tk.Label(list_frame, text="No flashcards yet!",
                         bg=GREY_BG, fg="#888888",
                         font=("Helvetica", 12)).pack(pady=30)
                return
            for deck_id, deck_name in decks:
                cursor.execute("SELECT COUNT(*) FROM flashcards WHERE deck_id=?", (deck_id,))
                count = cursor.fetchone()[0]

                deck_card = tk.Frame(list_frame, bg=GREY_BG, relief="solid", bd=1)
                deck_card.pack(fill="x", pady=6)

                left = tk.Frame(deck_card, bg=GREY_BG)
                left.pack(side="left", fill="both", expand=True, padx=14, pady=12)
                tk.Label(left, text=deck_name, bg=GREY_BG, fg="#0d0d0d",
                         font=("Helvetica", 13, "bold"), anchor="w").pack(anchor="w")
                tk.Label(left, text=f"{count} card{'s' if count != 1 else ''}",
                         bg="white", fg="#888888",
                         font=("Helvetica", 10), anchor="w").pack(anchor="w")

                btn_frame = tk.Frame(deck_card, bg=GREY_BG)
                btn_frame.pack(side="right", padx=10, pady=8)

                tk.Button(btn_frame, text="Edit", fg=NAVY_BLUE, relief="flat",
                          font=("Helvetica", 10,"bold"), padx=8,
                          command=lambda did=deck_id, dname=deck_name:
                          self.deck_edit_screen(did, dname)).pack(side="left", padx=4)

                tk.Button(btn_frame, text="Study", fg=NAVY_BLUE, relief="flat",
                          font=("Helvetica", 10, "bold"), padx=8,
                          command=lambda did=deck_id, dname=deck_name:
                          self.study_deck(did, dname)).pack(side="left", padx=4)

                tk.Button(btn_frame, text="Delete",
                          fg=DARK_RED, relief="flat",font=("Helvetica", 10,"bold"),
                          command=lambda did=deck_id, dname=deck_name:
                          delete_deck(did, dname)).pack(side="left", padx=4)

        def delete_deck(deck_id, deck_name):
            if messagebox.askyesno("Delete", f'Delete set "{deck_name}" and all its cards?'):
                cursor.execute("DELETE FROM decks WHERE id=?", (deck_id,))
                self.db.commit()
                load_decks()

        load_decks()

    def deck_edit_screen(self, deck_id, deck_name):
        clear_screen(self.root)
        self.root.configure(bg=GREY_BG)
        cursor = self.db.get_cursor()

        header = tk.Frame(self.root, bg=DARK_RED)
        header.pack(fill="x")
        
        back_sets=tk.Label(header, text="◄", bg=DARK_RED, fg="white",
                  relief="flat",font=("Helvetica", 20) ,padx=14)
        back_sets.pack(side="left", padx=5, pady=10)
        back_sets.bind("<Button-1>", lambda e: self.flashcards_screen())
        tk.Label(header, text=deck_name, bg=DARK_RED, fg="white",
                 font=("Helvetica", 16, "bold")).pack(side="left", pady=12)
        add_frame = tk.Frame(self.root, bg=GREY_BG, relief="flat")
        add_frame.pack(fill="x", pady=14)
        tk.Label(add_frame, text="Add a card", bg=GREY_BG,
                 font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2,
                                                       sticky="w", padx=14, pady=(10, 4))
        tk.Label(add_frame, text="Question", bg=GREY_BG,
                 font=("Helvetica", 11)).grid(row=1, column=0, sticky="w", padx=14, pady=4)
        front_entry = tk.Entry(add_frame, width=40, font=("Helvetica", 11),
                               relief="solid", bd=1)
        front_entry.grid(row=1, column=1, padx=14, pady=4, ipady=4, sticky="w")

        tk.Label(add_frame, text="Answer", bg=GREY_BG,
                 font=("Helvetica", 11)).grid(row=2, column=0, sticky="w", padx=14, pady=4)
        back_entry = tk.Entry(add_frame, width=40, font=("Helvetica", 11),
                              relief="solid", bd=1)
        back_entry.grid(row=2, column=1, padx=14, pady=4, ipady=4, sticky="w")

        add_status = tk.Label(add_frame, text="", bg=GREY_BG, fg=DARK_RED,
                              font=("Helvetica", 10))
        add_status.grid(row=3, column=0, columnspan=2, sticky="w", padx=14)

        def add_card():
            front = front_entry.get().strip()
            back = back_entry.get().strip()
            if not front or not back:
                add_status.config(text="Fill in both sides.", fg=DARK_RED)
                return
            cursor.execute(
                "INSERT INTO flashcards (deck_id, user_id, front, back) VALUES (?, ?, ?, ?)",
                (deck_id, self.current_user_id, front, back)
            )
            self.db.commit()
            front_entry.delete(0, "end")
            back_entry.delete(0, "end")
            add_status.config(text="Card added!")
            self.root.after(1500, lambda: add_status.config(text=""))
            load_cards()

        add_card_lbl=tk.Label(add_frame, text="Add Card", bg=NAVY_BLUE, fg="white",
                  relief="flat", font=("Helvetica", 11, "bold"),padx=12, pady=5)
        add_card_lbl.grid(row=4, column=0, columnspan=2, pady=10)
        add_card_lbl.bind("<Button-1>",lambda e : add_card())

        list_frame = tk.Frame(self.root, bg=GREY_BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)

        def load_cards():
            for widgets in list_frame.winfo_children():
                widgets.destroy()
            cursor.execute(
                "SELECT id, front, back FROM flashcards WHERE deck_id=? ORDER BY id",
                (deck_id,)
            )
            cards = cursor.fetchall()
            if not cards:
                tk.Label(list_frame, text="No cards yet. Add one above!",
                         bg=GREY_BG, fg="#888888",
                         font=("Helvetica", 11)).pack(pady=20)
                return
            for card_id, front, back in cards:
                row = tk.Frame(list_frame, bg=GREY_BG, relief="solid", bd=1)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=f"Q: {front}", bg=GREY_BG,
                         font=("Helvetica", 11, "bold"),
                         anchor="w").pack(side="left", padx=12, pady=6)
                tk.Label(row, text=f"A: {back}", bg=GREY_BG, fg="#555555",
                         font=("Helvetica", 11),
                         anchor="w").pack(side="left", padx=6, pady=6)
                tk.Button(row, text="Delete", fg=DARK_RED, bg=GREY_BG,
                          relief="flat",
                          command=lambda i=card_id: [
                              cursor.execute("DELETE FROM flashcards WHERE id=?", (i,)),
                              self.db.commit(), load_cards()
                          ]).pack(side="right", padx=10)

        load_cards()

    def study_deck(self, deck_id, deck_name):
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT id, front, back FROM flashcards WHERE deck_id=? ORDER BY id",
            (deck_id,)
        )
        all_cards = cursor.fetchall()

        if not all_cards:
            messagebox.showinfo("Empty Set", "This set has no cards yet!")
            return

        win = tk.Toplevel(self.root)
        win.title(deck_name)
        win.geometry("700x520")
        win.configure(bg="#1a1a2e")
        win.grab_set()

        queue = list(all_cards)
        state = {
            "idx": 0,
            "flipped": False,
            "total": len(all_cards),
        }

        card_outer = tk.Frame(win, bg="#1a1a2e")
        card_outer.pack(expand=True, fill="both", padx=40, pady=20)

        card_frame = tk.Frame(card_outer, bg=GREY_BG, relief="flat",
                              width=560, height=240)
        card_frame.pack(expand=True)
        card_frame.pack_propagate(False)

        card_label = tk.Label(card_frame, text="", bg=GREY_BG, fg="#0d0d0d",
                              font=("Helvetica", 17), wraplength=480,
                              justify="center")
        card_label.place(relx=0.5, rely=0.45, anchor="center")


        btn_row = tk.Frame(win, bg="#1a1a2e")
        btn_row.pack(pady=(0, 28))

        def make_circle_btn(circle_frame, label, symbol, colour, command):
            sub = tk.Frame(circle_frame, bg="#1a1a2e")
            sub.pack(side="left", padx=20)
            size = 72
            circle = tk.Canvas(sub, width=size, height=size,highlightthickness=0, bg="#1a1a2e")
            circle.pack()
            circle.create_oval(4, 4, size - 4, size - 4, fill=colour, outline="")
            circle.create_text(size // 2, size // 2, text=symbol,
                               font=("Helvetica", 22), fill="#1a1a2e")
            circle.bind("<Button-1>", lambda e: command())
            tk.Label(sub, text=label, bg="#1a1a2e", fg="#cccccc",
                     font=("Helvetica", 9)).pack(pady=(4, 0))

        def next_card():
            if not queue:
                show_summary()
                return
            current = queue[state["idx"] % len(queue)]
            state["flipped"] = False
            card_frame.config(bg="white")
            card_label.config(text=current[1], bg=GREY_BG, fg="#0d0d0d")

        def flip_card(event=None):
            if not queue:
                return
            current = queue[state["idx"] % len(queue)]
            if not state["flipped"]:
                card_frame.config(bg="#f0f4ff")
                card_label.config(text=current[2], bg="#f0f4ff", fg="#1a1a8e")
                state["flipped"] = True
            else:
                card_frame.config(bg=GREY_BG)
                card_label.config(text=current[1], bg=GREY_BG, fg="#0d0d0d")
                state["flipped"] = False

        card_frame.bind("<Button-1>", flip_card)
        card_label.bind("<Button-1>", flip_card)

        def got_right():
            if not queue:
                return
            queue.pop(state["idx"] % len(queue))
            if queue:
                state["idx"] = state["idx"] % len(queue)
            next_card() if queue else show_summary()

        def dont_know():
            if not queue:
                return
            state["idx"] = (state["idx"] + 1) % len(queue)
            next_card()

        def got_wrong():
            if not queue:
                return
            card = queue.pop(state["idx"] % len(queue))
            queue.append(card)
            state["idx"] = state["idx"] % len(queue)
            next_card()
    

        make_circle_btn(btn_row, "Correct", "✓", "#90E6FC", got_right)
        make_circle_btn(btn_row, "Not Sure",   "?", "#7CD7F7", dont_know)
        make_circle_btn(btn_row, "Incorrent",  "✗", "#A8EEFF", got_wrong)

        def show_summary():
            for widgets in win.winfo_children():
                widgets.destroy()
            win.configure(bg="#1a1a2e")
            tk.Label(win, text="Revision Complete!", bg="#1a1a2e", fg="white",
                     font=("Helvetica", 22, "bold")).pack(pady=(60, 10))
            close_cards=tk.Label(win, text="Close", bg=DARK_RED, fg="white", relief="flat",
                      font=("Helvetica", 11), padx=16, pady=6)
            close_cards.pack()
            close_cards.bind("<Button-1>",lambda e: win.destroy())

        next_card()
        
    def quiz_screen(self):  
        clear_screen(self.root)
        self.root.configure(bg=GREY_BG)
        cursor = self.db.get_cursor()
        header=tk.Frame(self.root,bg=DARK_RED)
        header.pack(fill="x")
        tk.Label(header, text="Quizzes", font=("Helvetica", 20, "bold"),bg=DARK_RED,fg="white").pack(side="left",pady=10)
 
        # top area: list quizzes + create new
        top = tk.Frame(self.root, bg=GREY_BG)
        top.pack(fill="x", padx=20)
 
        tk.Label(top, text="Quiz name:", bg=GREY_BG).pack(side="left")
        quiz_name_entry = tk.Entry(top, width=30)
        quiz_name_entry.pack(side="left", padx=5)
        
        def create_quiz():
            name = quiz_name_entry.get().strip()
            if not name:
                return
            cursor.execute("INSERT INTO quizzes (user_id, title) VALUES (?, ?)",
                           (self.current_user_id, name))
            self.db.commit()
            quiz_name_entry.delete(0, "end")
            refresh_quiz_list()
 
        create_quiz_lbl=tk.Label(top, text="Create Quiz",bg=NAVY_BLUE,fg="white",padx=14,pady=6,relief="flat",font=("Helvetica", 11))
        create_quiz_lbl.pack(side="left", padx=5)
        create_quiz_lbl.bind("<Enter>", lambda e: create_quiz_lbl.config(bg=BLUE_HOVER_COLOR))
        create_quiz_lbl.bind("<Leave>", lambda e: create_quiz_lbl.config(bg=NAVY_BLUE))
        create_quiz_lbl.bind("<Button-1>", lambda e: create_quiz())

        footer=tk.Frame(self.root,bg=GREY_BG)
        footer.pack(side="bottom",fill="x")
        back_quiz=tk.Label(footer, text="Back", bg=NAVY_BLUE, fg="white",padx=14, pady=6,)
        back_quiz.pack(side="right", padx=25, pady=15)
        back_quiz.bind("<Enter>", lambda e: back_quiz.config(bg=BLUE_HOVER_COLOR))
        back_quiz.bind("<Leave>", lambda e: back_quiz.config(bg=NAVY_BLUE))
        back_quiz.bind("<Button-1>", lambda e: self.home_screen())
 
        # quiz list
        list_frame = tk.Frame(self.root, bg=GREY_BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        def refresh_quiz_list():
            for widgets in list_frame.winfo_children():
                widgets.destroy()
            cursor.execute("SELECT id, title FROM quizzes WHERE user_id=?",
                           (self.current_user_id,))
            quizzes = cursor.fetchall()
            if not quizzes:
                tk.Label(list_frame, text="No quizzes yet!",
                         bg="white", fg="#888888").pack(pady=20)
                return
            for qid, qtitle in quizzes:
                row = tk.Frame(list_frame, bg=GREY_BG, relief="solid", bd=1)
                row.pack(fill="x", pady=4)
                tk.Label(row, text=qtitle, bg=GREY_BG,font=("Helvetica", 12)).pack(side="left", padx=10, pady=8)
                tk.Button(row, text="Edit Quiz",command=lambda i=qid, t=qtitle: self.quiz_edit_screen(i, t)
                          ).pack(side="left", padx=5)
                tk.Button(row, text="Take Quiz",command=lambda i=qid, t=qtitle: self.take_quiz(i, t)
                          ).pack(side="left", padx=5)
                
                def delete_quiz(qid):
                    if messagebox.askyesno("Delete", "Delete this quiz and all its questions?"):
                        cursor.execute("DELETE FROM quizzes WHERE id=?", (qid,))
                        self.db.commit()
                        refresh_quiz_list()
                        
                tk.Button(row, text="Delete", fg=DARK_RED,
                          command=lambda i=qid: delete_quiz(i)).pack(side="right", padx=10)
                
        refresh_quiz_list()

    def quiz_edit_screen(self, quiz_id, quiz_title):
        clear_screen(self.root)
        self.root.configure(bg=GREY_BG)
        cursor = self.db.get_cursor()

        quiz_header=tk.Frame(self.root,bg=DARK_RED)
        quiz_header.pack(fill="x")
        tk.Label(quiz_header, text=f"Edit: {quiz_title}",
                font=("Helvetica", 16, "bold"),bg=DARK_RED,fg="white").pack(pady=10)

        # add question form
        form = tk.Frame(self.root, bg=GREY_BG)
        form.pack(fill="x", padx=20, pady=5)

        fields = {}
        for i, label in enumerate(["Question", "Option A", "Option B", "Option C", "Option D"]):
            tk.Label(form, text=label+":", bg=GREY_BG, width=12,
                    anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            e = tk.Entry(form, width=50)
            e.grid(row=i, column=1, padx=5, pady=2, sticky="w")
            fields[label] = e

        tk.Label(form, text="Correct Answer:", bg=GREY_BG, width=12,
                anchor="w").grid(row=5, column=0, sticky="w")
        correct_var = tk.StringVar(value="A")
        tk.OptionMenu(form, correct_var, "A", "B", "C", "D").grid(row=5, column=1, sticky="w", padx=5)

        status = tk.Label(self.root, text="", bg=GREY_BG, fg=DARK_RED)
        status.pack()

        def add_question():
            ques  = fields["Question"].get().strip()
            a_opt  = fields["Option A"].get().strip()
            b_opt  = fields["Option B"].get().strip()
            c_opt  = fields["Option C"].get().strip()
            d_opt  = fields["Option D"].get().strip()
            ans = correct_var.get().upper()
            if not all([ques, a_opt, b_opt, c_opt, d_opt]):
                status.config(text="Please fill in all fields.")
                return
            cursor.execute("""
                INSERT INTO quiz_questions
                (quiz_id, question_text, option_a, option_b, option_c, option_d, correct)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (quiz_id, ques, a_opt, b_opt, c_opt, d_opt, ans))
            self.db.commit()
            for e in fields.values():
                e.delete(0, "end")
            status.config(text="Question added.", fg="green")
            load_questions()

        tk.Button(self.root, text="Add Question", command=add_question).pack(pady=5)

        # question list
        q_frame = tk.Frame(self.root, bg=GREY_BG)
        q_frame.pack(fill="both", expand=True, padx=20, pady=5)

        def load_questions():
            for widgets in q_frame.winfo_children():
                widgets.destroy()
            cursor.execute(
                "SELECT id, question_text, correct FROM quiz_questions WHERE quiz_id=?",
                (quiz_id,))
            rows = cursor.fetchall()
            if not rows:
                tk.Label(q_frame, text="No questions yet!", bg="white", fg="#888888").pack()
                return
            for qid, qtxt, qans in rows:
                r = tk.Frame(q_frame, bg=GREY_BG, relief="solid", bd=1)
                r.pack(fill="x", pady=2)
                tk.Label(r, text=f"Q: {qtxt}  [Ans: {qans}]", bg=GREY_BG,
                        font=("Helvetica", 10), wraplength=500,
                        justify="left",fg="black").pack(side="left", padx=8, pady=4)
                tk.Button(r, text="Delete", fg=DARK_RED,
                        command=lambda i=qid: delete_question(i), bg=DARK_RED).pack(side="right", padx=6)

        def delete_question(qid):
            cursor.execute("DELETE FROM quiz_questions WHERE id=?", (qid,))
            self.db.commit()
            load_questions()

        back_quiz=tk.Label(self.root, text="Back", bg=NAVY_BLUE, fg="white",padx=14, pady=6,)
        back_quiz.pack(side="right", padx=25, pady=15)
        back_quiz.bind("<Enter>", lambda e: back_quiz.config(bg=BLUE_HOVER_COLOR))
        back_quiz.bind("<Leave>", lambda e: back_quiz.config(bg=NAVY_BLUE))
        back_quiz.bind("<Button-1>", lambda e: self.quiz_screen())
        
        
        load_questions()

    def take_quiz(self, quiz_id, quiz_title):
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT id, question_text, option_a, option_b, option_c, option_d, correct
            FROM quiz_questions WHERE quiz_id=?
        """, (quiz_id,))
        questions = cursor.fetchall()
        if not questions:
            messagebox.showinfo("Empty Quiz", "This quiz is empty!")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Quiz: {quiz_title}")
        win.geometry("600x450")
        win.configure(bg="white")
        win.grab_set()

        state = {"idx": 0, "score": 0, "total": len(questions)}

        def show_question():
            for widgets in win.winfo_children():
                widgets.destroy()
            idx = state["idx"]
            if idx >= state["total"]:
                show_result()
                return
            _, qtxt, a, b, c, d, correct = questions[idx]

            tk.Label(win, text=qtxt, bg="white", fg="#0d0d0d",
                    font=("Helvetica", 13, "bold"), wraplength=520,
                    justify="left").pack(anchor="w", padx=30, pady=(0, 16))

            chosen = tk.StringVar()
            for label, text in zip(["A","B","C","D"], [a, b, c, d]):
                tk.Radiobutton(win, text=f"{label}.  {text}", variable=chosen,
                            value=label, bg="white", font=("Helvetica", 11)).pack(anchor="w", padx=40, pady=3)

            feedback = tk.Label(win, text="", bg="white", font=("Helvetica", 11, "bold"))
            feedback.pack(pady=8)

            def submit():
                ans = chosen.get()
                if ans == correct:
                    state["score"] += 1
                    feedback.config(text="✔  Correct!", fg="green")
                else:
                    feedback.config(text=f"✘  Wrong. The correct answer is {correct}", fg=DARK_RED)
                submit_btn.config(state="disabled")
                win.after(1200, lambda: [state.update({"idx": state["idx"]+1}), show_question()])

            submit_btn = tk.Button(win, text="Submit Answer", bg="#0d0d0d", fg="white",
                                font=("Helvetica", 11, "bold"), relief="flat",
                                padx=20, pady=6, command=submit)
            submit_btn.pack(pady=4)

        def show_result():
            from datetime import datetime
            cursor.execute(
                "INSERT INTO quiz_attempts (quiz_id, user_id, score, total, taken_at) VALUES (?,?,?,?,?)",
                (quiz_id, self.current_user_id, state["score"], state["total"],
                 datetime.now().strftime("%Y-%m-%d %H:%M")))
            self.db.commit()
            for widgets in win.winfo_children():
                widgets.destroy()
            win.configure(bg=DARK_RED)
            tk.Label(win, text="Quiz Complete!", fg="white", bg=DARK_RED,
                    font=("Helvetica", 18, "bold")).pack(pady=(40, 10))
            tk.Label(win, text=f"{state['score']} / {state['total']}",fg="white",bg=DARK_RED).pack()
            tk.Button(win, text="Close",bg=DARK_RED,fg="black", command=win.destroy).pack()
        show_question()
        
    def calendar_screen(self):
        from datetime import datetime, date
        import calendar as cal
 
        clear_screen(self.root)
        self.root.configure(bg="white")
        cursor = self.db.get_cursor()
 
        now = datetime.now()
        state = {"year": now.year, "month": now.month}
        header=tk.Frame(self.root,bg=DARK_RED)
        header.pack(fill="x")
        tk.Label(header, text="Calendar", font=("Helvetica", 20, "bold"),fg="white",bg=DARK_RED).pack(pady=10,side="left",padx=20)
        back_cal=tk.Label(header,text="Back",bg=NAVY_BLUE,fg="white",padx=14,pady=6)
        back_cal.pack(pady=5,side="right", padx=20)
        back_cal.bind("<Enter>", lambda e: back_cal.config(bg=BLUE_HOVER_COLOR))
        back_cal.bind("<Leave>", lambda e: back_cal.config(bg=NAVY_BLUE))
        back_cal.bind("<Button-1>", lambda e: self.home_screen())
        
 
        # nav row
        nav = tk.Frame(self.root, bg="white")
        nav.pack()
        left_btn=tk.Label(nav, text="◄", bg="white", fg=DARK_RED,width="4", font=("Helvetica", 20), cursor="hand2")
        left_btn.pack(side="left", padx=10, pady=10)
        left_btn.bind("<Button-1>", lambda e: [state.update({"month": state["month"] - 1}), actual_calender()])
        right_btn=tk.Label(nav, text="►", bg="white",width="2",fg=DARK_RED, font=("Helvetica", 20), cursor="hand2")
        right_btn.pack(side="right", padx=10, pady=10)
        right_btn.bind("<Button-1>", lambda e: [state.update({"month": state    ["month"] + 1}), actual_calender()])
        month_lbl = tk.Label(nav, text="", bg="white",fg=DARK_RED,font=("Helvetica", 26, "bold"), width=20)
        month_lbl.pack(side="left")
 
        # main area
        main = tk.Frame(self.root, bg="white")
        main.pack(fill="both", expand=True, padx=10)
 
        cal_frame = tk.Frame(main, bg="white")
        cal_frame.pack(side="left", fill="both", expand=True)

        # right panel events + add form
        right_panel = tk.Frame(main, width=260)
        right_panel.pack(side="right", fill="y", padx=(10,0))
        right_panel.pack_propagate(False)

        event_list_frame = tk.Frame(right_panel, bg=GREY_BG)
        event_list_frame.pack(fill="both", expand=True)
 
        tk.Label(right_panel, text="Events this month", bg="white",
                 font=("Helvetica", 11, "bold")).pack(pady=(10,4))
        
        add_form = tk.LabelFrame(right_panel, text="add event", bg=GREY_BG, font=("Helvetica", 9))
        add_form.pack(fill="x", padx=6, pady=6)
        
        tk.Label(add_form, text="title", bg=GREY_BG, font=("Helvetica", 9)).grid(row=0, column=0, sticky="w", padx=4)
        event_name = tk.Entry(add_form, width=18, font=("Helvetica", 9))
        event_name.grid(row=0, column=1, padx=4, pady=2)
        
        tk.Label(add_form, text="Date:", bg=GREY_BG, font=("Helvetica", 9)).grid(row=1, column=0, sticky="w", padx=4)
        event_date = tk.Entry(add_form, width=18, font=("Helvetica", 9))
        event_date.grid(row=1, column=1, padx=4, pady=2)
        
        event_date.insert(0, now.strftime("%Y-%m-%d"))
        tk.Label(add_form, text="Type:", bg=GREY_BG, font=("Helvetica", 9)).grid(row=2, column=0, sticky="w", padx=4)
        type_var = tk.StringVar(value="exam")
        
        tk.OptionMenu(add_form, type_var, "exam", "assignment", "study", "other").grid(row=2, column=1, sticky="w", padx=4)        
        def load_event_list():
            for widgets in event_list_frame.winfo_children():
                widgets.destroy()
            y, m = state["year"], state["month"]
            cursor.execute(
                "SELECT title, event_date, event_type FROM calendar_events "
                "WHERE user_id=? AND event_date LIKE ? ORDER BY event_date",
                (self.current_user_id, f"{y:04d}-{m:02d}-%"))
            rows = cursor.fetchall()
            if not rows:
                tk.Label(event_list_frame, text="No events.", bg="#f5f5f5",
                        fg="#888888", font=("Helvetica", 9)).pack(pady=6)
                return
            for ev_title, ev_date, ev_type in rows:
                rf = tk.Frame(event_list_frame, bg="#f5f5f5")
                rf.pack(fill="x", pady=1, padx=4)
                tk.Label(rf, text=f"{ev_date[8:]}  {ev_title}", bg="#f5f5f5",
                        font=("Helvetica", 9)).pack(side="left", padx=2)
            
                
        def actual_calender():
            for widgets in cal_frame.winfo_children():
                widgets.destroy()
            y, m = state["year"], state["month"]
            month_lbl.config(text=datetime(y, m, 1).strftime("%B %Y"))

            cursor.execute(
                "SELECT event_date, event_type FROM calendar_events WHERE user_id=? AND event_date LIKE ?",
                (self.current_user_id, f"{y:04d}-{m:02d}-%"))
            event_map = {}
            for ed, et in cursor.fetchall():
                day = int(ed[8:])
                event_map.setdefault(day, []).append(et)

            for col, dn in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
                tk.Label(cal_frame, text=dn, bg="white", fg="#888888",
                            font=("Helvetica",11, "bold"), width=7).grid(row=0, column=col, pady=(0,2))

            first_wd = date(y, m, 1).weekday()
            days_in  = cal.monthrange(y, m)[1]
            today    = now.day if (y == now.year and m == now.month) else -1

            r, c = 1, first_wd
            for d in range(1, days_in + 1):
                evts = event_map.get(d, [])
                first_type = evts[0] if evts else None
                bg = "#bbdefb" if d == today else (TYPE_COLORS.get(first_type, "white") if first_type else "white")          
                cell = tk.Frame(cal_frame, bg=bg, width=100, height=100, relief="solid", bd=1)
                cell.grid(row=r, column=c, padx=1, pady=1)
                cell.grid_propagate(False)
                tk.Label(cell, text=str(d), bg=bg, fg="#0d0d0d",
                            font=("Helvetica", 15, "bold" if d == today else "normal")).pack(anchor="nw", padx=3)
                c += 1
                if c == 7:
                    c, r = 0, r + 1

            load_event_list()    
        
        def add_event():
            name=event_name.get()
            date=event_date.get()
            type=type_var.get()
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Bad date", "Use Year-Month-Day!")
                return
            
            if not name:
                messagebox.showwarning("No title", "Enter an event title")
                return
            cursor.execute(
                "INSERT INTO calendar_events (user_id, title, event_date, event_type) VALUES (?,?,?,?)",
                (self.current_user_id, name, date, type))
            self.db.commit()
            event_name.delete(0, "end")
            actual_calender()

        tk.Button(add_form, text="Add Event", command=add_event,
                font=("Helvetica", 9)).grid(row=3, column=0, columnspan=2, pady=4)
        actual_calender()
    def reminders_screen(self):
        from datetime import datetime
        clear_screen(self.root)
        self.root.configure(bg="white")
        cursor = self.db.get_cursor()
        
        header=tk.Frame(self.root,bg=DARK_RED)
        header.pack(fill="x")
        tk.Label(header, text="Reminders", font=("Helvetica", 20, "bold"),fg="white",bg=DARK_RED).pack(pady=10,side="left",padx=20)
        
        
        form = tk.Frame(self.root, bg="white")
        form.pack(fill="x", padx=20, pady=5)
        
        tk.Label(form, text="Title:", bg="white").grid(row=0, column=0, sticky="w", pady=4)
        
        re_title = tk.Entry(form, width=40)
        re_title.grid(row=0, column=1, padx=5, sticky="w")
        
        tk.Label(form, text="Date:", bg="white").grid(row=1, column=0, sticky="w", pady=4)
        tk.Label(form, text="(YYYY-MM-DD)", bg="white", fg="#888888", font=("Helvetica", 8)).grid(row=2, column=0, sticky="w")
        re_date = tk.Entry(form, width=20)
        re_date.grid(row=1, column=1, padx=5, sticky="w")

        tk.Label(form, text="Time:", bg="white").grid(row=3, column=0, sticky="w", pady=4)
        tk.Label(form, text="(24hr HH:MM)", bg="white", fg="#888888", font=("Helvetica", 8)).grid(row=4, column=0, sticky="w")
        re_time = tk.Entry(form, width=20)
        re_time.grid(row=3, column=1, padx=5, sticky="w")
        
        status =tk.Label(self.root, text="", bg="white", fg=DARK_RED, font=("Helvetica", 10))
        status.pack()
        
        footer=tk.Frame(self.root,bg="white")
        footer.pack(side="bottom",fill="x")
        back_rem= tk.Label(footer, text="Back",fg="white", bg=NAVY_BLUE, relief="flat", font=("Helvetica", 11), padx=14, pady=6)
        back_rem.bind("<Enter>", lambda e: back_rem.config(bg=BLUE_HOVER_COLOR))
        back_rem.bind("<Leave>", lambda e: back_rem.config(bg=NAVY_BLUE))
        back_rem.bind("<Button-1>", lambda e: self.home_screen())
        back_rem.pack(pady=5,padx=10,side="right")
        
        def add_reminder():
            rem_title = re_title.get().strip()
            rem_date= re_date.get().strip()
            rem_time= re_time.get().strip()
            
            if not rem_title:
                status.config(text="Enter a reminder title.")
                return
            try:
                remind_dt = datetime.strptime(f"{rem_date} {rem_time}", "%Y-%m-%d %H:%M")
            except ValueError:
                status.config(text="Invalid date or time.")
                return
            if remind_dt <= datetime.now():
                status.config(text="Please set a future date/time.")
                return
            status.config(text="")
            rat = remind_dt.strftime("%Y-%m-%d %H:%M")
            cursor.execute(
                "INSERT INTO reminders (user_id, rem_title, remind_at) VALUES (?,?,?)",
                (self.current_user_id,rem_title, rat))
            self.db.commit()
            re_title.delete(0, "end")
            messagebox.showinfo("Reminder Set!", f"Reminder set for {rat}.\nThe app must be open to receive notifications.")
            load_reminders()
 
            
        set_btn=tk.Label(self.root, text="Set Reminder",padx=10, pady=5,bg=NAVY_BLUE,fg="white")
        set_btn.pack(pady=6)
        set_btn.bind("<Enter>", lambda e: set_btn.config(bg=BLUE_HOVER_COLOR))
        set_btn.bind("<Leave>", lambda e: set_btn.config(bg=NAVY_BLUE))
        set_btn.bind("<Button-1>", lambda e: add_reminder())
        list_frame = tk.Frame(self.root, bg="white")
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)
        def load_reminders():
            for widegts in list_frame.winfo_children():
                widegts.destroy()
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute(
                "SELECT id, rem_title, remind_at, fired FROM reminders WHERE user_id=? ORDER BY fired ASC, remind_at ASC",
                (self.current_user_id,))
            rows = cursor.fetchall()
            if not rows:
                tk.Label(list_frame, text="No reminders yet!", bg="white", fg="#888888").pack(pady=10)
                return
            for reminder_id, reminder_title, reminder_at, fired in rows:
                overdue = (reminder_at <= now_time and not fired)
                bg = "#ffebee" if overdue else ("#eeeeee" if fired else "white")
                row = tk.Frame(list_frame, bg=bg, relief="solid", bd=1)
                row.pack(fill="x", pady=3)
                icon = "✔" if fired else ("⚠" if overdue else "○")
                tk.Label(row, text=icon, bg=bg, font=("Helvetica", 13)).pack(side="left", padx=8, pady=6)
                tk.Label(row, text=f"{reminder_title}  —  {reminder_at}", bg=bg,
                         font=("Helvetica", 11)).pack(side="left", padx=4)
                tk.Button(row, text="Delete", fg=DARK_RED, bg=bg, relief="flat",
                          command=lambda i=reminder_id: [cursor.execute("DELETE FROM reminders WHERE id=?", (i,)),
                                                         self.db.commit(), load_reminders()]).pack(side="right", padx=8)
        load_reminders()

root=tk.Tk()
app = appface(root) 
root.mainloop() 