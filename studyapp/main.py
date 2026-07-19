import tkinter as tk
import sqlite3
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
class DatabaseSetup:
    def __init__(self,db_path="study_app.db"):
        """Creates the database connection and sets up the database file."""
        self.db_path = db_path
        self.settings_win = None # Checks if the settings window is open
        self.connection = sqlite3.connect(db_path)#Connect to the database file (creates it if it doesn't exist)
                
    def create_tables(self): 
        """Creates the tables in the database if they don't already exist."""
        cursor = self.connection.cursor() #cursor object to execute SQL commands

        #Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL UNIQUE,
                password    TEXT    NOT NULL
            )
        """)

        #Notes table

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                title      TEXT    NOT NULL,
                body       TEXT    NOT NULL DEFAULT '',
                summary    TEXT    DEFAULT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, title)
            )
        """)

        #Deck table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                name       TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, name)
            )
        """)
        
        #Flashcards table
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
        
        #Quiz + questions tables
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
        """Returns a cursor so other parts of the app can query the database"""
        return self.connection.cursor()
 
    def commit(self):
        """Saves any changes made to the database"""
        self.connection.commit()
        

def hash_password(password):
    """Hashes the password using SHA-256 and returns the hexadecimal digest."""
    return hashlib.sha256(password.encode()).hexdigest()


def clear_screen(root):
    """Clears all widgets from the given root window."""
    for widget in root.winfo_children():
        widget.destroy()


def make_hover_background(widget, normal_colour, hover_colour, command):
    """Adds hover effects and click effect to a Label."""
    widget.bind("<Enter>",lambda e: widget.config(bg=hover_colour))
    widget.bind("<Leave>",lambda e: widget.config(bg=normal_colour))
    widget.bind("<Button-1>",lambda e: command())

def make_hover_foreground(widget, normal_colour, hover_colour, command):
    """Adds hover effects and click effect to a Label."""
    widget.bind("<Enter>",lambda e: widget.config(fg=hover_colour))
    widget.bind("<Leave>",lambda e: widget.config(fg=normal_colour))
    widget.bind("<Button-1>",lambda e: command())
    

    
class AppFace:
    def __init__(self,root):
        """Sets up the database and window"""
        self.root = root
        self.root.title("Focalize")
        self.root.geometry("1100x700")
        self.current_user_id = None # no one logged in yet
        self.current_username = None
        self.left_panel("testing bigtxt", "testing small text")
        self.db = DatabaseSetup() # create an object of the database setup class
        self.db.create_tables() # create the tables in the database if they don't exist
        self.login_screen()

        
    def left_panel(self,head,subtext):
        """`Creates the left panel with a heading and subtext."""
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
        """Creates the entry box for username and password + placeholder text """
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
            """When the user clicks on the field, it will clear the placeholder text and change the text color to black. If it's a password field, it will also hide the input with dots."""
            if user_pass.get() == placeholder:
                user_pass.delete(0, "end")
                user_pass.config(fg="#111111")
                if is_password:
                    user_pass.config(show="•")     # hide password with dots
            underline.config(bg="#2A2AE1")
        def unclick_field(event):
            """When the user clicks away from the field, if it's empty it will put the placeholder text back and change the text color to gray"""
            if user_pass.get() == "":
                user_pass.config(fg="#aaaaaa", show="")
                user_pass.insert(0, placeholder)   # put placeholder back
            underline.config(bg=GREY_BG) 

        user_pass.bind("<FocusIn>",  on_click_field) # when the user clicks on the field, it will clear the placeholder text and change the text color to black. If it's a password field, it will also hide the input with dots.
        user_pass.bind("<FocusOut>", unclick_field) # when the user clicks away from the field, if it's empty it will put the placeholder text back and change the text color to gray. It will also show the input if it's a password field.
        return user_pass
    
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
  
        tk.Label(form, text="Welcome to Focalize", bg="white", fg="#0d0d0d",
                 font=("Helvetica", 22, "bold")).pack(anchor="w")
        
        sub = tk.Frame(form, bg="white")
        sub.pack(anchor="w", pady=(6, 24))
        tk.Label(sub, text="Already registered?", bg="white", fg="#888888",
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
                self.db.commit()   # save to database
                messagebox.showinfo("Success", f"Account created! Welcome, {username}.")
                self.login_screen()
            except sqlite3.IntegrityError:
                status.config(text="Username already exists.")
        
        # Register button in label form so that I can change the color on hover
        regis_btn=tk.Label(form, text="Register",
                bg=DARK_RED, fg="white",
                font=("Helvetica", 13, "bold"),
                relief="flat", bd=0, width=30, height=2)
        regis_btn.pack(pady=(4, 0))
        regis_btn.bind("<Button-1>", lambda e: attempt_register())
        
        
        
        
        
        
        
        
    def home_screen(self):
        """Creates the home screen with dashboard"""
        from datetime import date
        clear_screen(self.root)
        self.root.configure(bg=GREY_BG)
        cursor=self.db.get_cursor()
        def check_reminders():
            """Checks the database(every 30sec) for any reminders that are due."""
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("""
                SELECT id, rem_title
                FROM reminders
                WHERE user_id=?
                AND remind_at<=?
                AND fired=0
            """, (self.current_user_id, now))

            reminders = cursor.fetchall()

            for reminder_id, title in reminders:
                messagebox.showinfo("Reminder", title)

                cursor.execute(
                    "UPDATE reminders SET fired=1 WHERE id=?",
                    (reminder_id,)
                )

            self.db.commit()

            self.root.after(30000, check_reminders)

        check_reminders()
                
        #Header
        header=tk.Frame(self.root,bg=DARK_RED)
        header.pack(fill="x")
        tk.Label(header, text=f"Welcome, {self.current_username}",
                 font=("Helvetica", 20, "bold"), fg="white", bg=DARK_RED
                 ).pack(side="left", padx=20, pady=16)
        gear_lbl = tk.Label(header, text="⚙", bg=DARK_RED, fg="white",
                             font=("Helvetica", 30), cursor="hand2")
        gear_lbl.pack(side="right", padx=20, pady=16)
        
        make_hover_foreground(gear_lbl,"white","#dddddd",self.open_settings_sidebar)
        
        #Dashboard
        board = tk.Frame(self.root, bg=GREY_BG)
        board.pack(fill="both", expand=True, padx=16, pady=14)
        board.grid_columnconfigure(0, weight=1, uniform="col")
        board.grid_columnconfigure(1, weight=1, uniform="col")
        board.grid_rowconfigure(0, weight=3)
        board.grid_rowconfigure(1, weight=3)
        board.grid_rowconfigure(2, weight=2)
        
        def make_card(title, row, col, colspan=1, open_cmd=None):
            """Creates a card with a title and an "Open" button."""
            outer = tk.Frame(board, bg="white", relief="solid", bd=1)
            outer.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=8, pady=8)

            card_head = tk.Frame(outer, bg=DARK_RED)
            card_head.pack(fill="x")
            tk.Label(card_head, text=title, bg=DARK_RED, fg="white",
                     font=("Helvetica", 13, "bold")).pack(side="left", padx=12, pady=8)
            if open_cmd:
                open_lbl = tk.Label(card_head, text="Open", bg=DARK_RED, fg="white",
                                     font=("Helvetica", 10), cursor="hand2")
                open_lbl.pack(side="right", padx=12)
                
                make_hover_foreground(open_lbl,"white",NAVY_BLUE,open_cmd)

            body = tk.Frame(outer, bg="white")
            body.pack(fill="both", expand=True, padx=12, pady=10)
            return body
        
        
        # Notes section
        notes_body = make_card("Notes", 0, 0, open_cmd=self.notes_screen)
        cursor.execute(
            "SELECT id, title FROM notes WHERE user_id=? ORDER BY id DESC LIMIT 5",
            (self.current_user_id,))
        note_rows = cursor.fetchall()
        if not note_rows:
            tk.Label(notes_body, text="No notes yet!",
                     bg="white", fg="#888888", font=("Helvetica", 10)).pack(pady=10)
        else:
            for nid, ntitle in note_rows:
                lbl = tk.Label(notes_body, text=f"{ntitle}", bg="white", fg="#0d0d0d",
                                font=("Helvetica", 11), anchor="w", cursor="hand2")
                lbl.pack(fill="x", pady=2)
                lbl.bind("<Button-1>", lambda e, i=nid, t=ntitle: self.note_edit_screen(i, t))
        
        #Flashcards section
        fc_body = make_card("Flashcards", 0, 1, open_cmd=self.flashcards_screen)
        cursor.execute(
            "SELECT id, name FROM decks WHERE user_id=? ORDER BY id DESC LIMIT 5",
            (self.current_user_id,))
        deck_rows = cursor.fetchall()
        if not deck_rows:
            tk.Label(fc_body, text="No flashcard sets yet!",
                     bg="white", fg="#888888", font=("Helvetica", 10)).pack(pady=10)
        else:
            for did, dname in deck_rows:
                cursor.execute("SELECT COUNT(*) FROM flashcards WHERE deck_id=?", (did,))
                ccount = cursor.fetchone()[0]
                row = tk.Frame(fc_body, bg="white")
                row.pack(fill="x", pady=2)
                lbl = tk.Label(row, text=f"{dname}", bg="white", fg="#0d0d0d",
                                font=("Helvetica", 11), anchor="w", cursor="hand2")
                lbl.pack(side="left")
                tk.Label(row, text=f"{ccount} card{'s' if ccount != 1 else ''}", bg="white",
                         fg="#888888", font=("Helvetica", 9)).pack(side="right")
                lbl.bind("<Button-1>", lambda e, i=did, t=dname: self.study_deck(i, t))
        
        #Quiz section
        quiz_body = make_card("Quiz", 1, 0, open_cmd=self.quiz_screen)
        cursor.execute("""
            SELECT quiz_attempts.score, quiz_attempts.total,
                quizzes.title, quizzes.id
            FROM quiz_attempts
            JOIN quizzes
                ON quizzes.id = quiz_attempts.quiz_id
            WHERE quiz_attempts.user_id = ?
            ORDER BY quiz_attempts.id DESC
            LIMIT 1
            """, (self.current_user_id,))
        last_attempt = cursor.fetchone()
        if not last_attempt:
            tk.Label(quiz_body, text="Take a quiz!",
                     bg="white", fg="#888888", font=("Helvetica", 10)).pack(pady=10) 
        else:
            score, total, qtitle, qid=last_attempt
            tk.Label(quiz_body, text=qtitle, bg="white", fg="#0d0d0d",
                    font=("Helvetica", 12, "bold"), anchor="w").pack(anchor="w")
            tk.Label(quiz_body, text=f"Latest score: {score} / {total}", bg="white",
                    fg=NAVY_BLUE, font=("Helvetica", 14, "bold"), anchor="w"
                    ).pack(anchor="w", pady=(4, 4))
            if total > 0 and score == total:
                note_txt="Perfect score! Can you get it again?"
            else:
                note_txt = "Can you beat this score?"
            tk.Label(quiz_body, text=note_txt, bg="white", fg=DARK_RED,
                     font=("Helvetica", 10), anchor="w",
                     wraplength=260, justify="left").pack(anchor="w")
            
        #Calendar section
        
        cal_body = make_card("Calendar", 1, 1, open_cmd=self.calendar_screen)
        today_str = date.today().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT title, event_date, event_type FROM calendar_events "
            "WHERE user_id=? AND event_date=? ORDER BY id",
            (self.current_user_id, today_str))
        todays_events = cursor.fetchall()
        if todays_events:
            tk.Label(cal_body, text="Today", bg="white", fg="#888888",
                     font=("Helvetica", 9, "bold")).pack(anchor="w") #event title
            for ev_title, ev_date, ev_type in todays_events:
                colour = TYPE_COLORS.get(ev_type, "white")
                row = tk.Frame(cal_body, bg=colour)
                row.pack(fill="x", pady=2)
                tk.Label(row, text=f"●  {ev_title}", bg=colour, fg="white",
                         font=("Helvetica", 11), anchor="w").pack(side="left", padx=6, pady=4)
                tk.Label(row, text=ev_type, bg=colour, fg="white",
                         font=("Helvetica", 8), anchor="e").pack(side="right", padx=6)
        else:
            cursor.execute(
                "SELECT title, event_date, event_type FROM calendar_events "
                "WHERE user_id=? AND event_date>? ORDER BY event_date ASC LIMIT 5",
                (self.current_user_id, today_str))
            next_event = cursor.fetchone()
            if next_event:
                ev_title, ev_date, ev_type = next_event
                colour = TYPE_COLORS.get(ev_type, "white")
                tk.Label(cal_body, text="No events today. Next up:", bg="white",
                         fg=DARK_RED, font=("Helvetica", 9)).pack(anchor="w")
                row = tk.Frame(cal_body, bg=colour)
                row.pack(fill="x", pady=4)
                tk.Label(row, text=f"●  {ev_title}", bg=colour, fg="black",
                         font=("Helvetica", 11, "bold"), anchor="w").pack(side="left", padx=6, pady=4)
                tk.Label(row, text=ev_date, bg=colour, fg="black",
                         font=("Helvetica", 9), anchor="e").pack(side="right", padx=6)
            else:
                tk.Label(cal_body, text="No upcoming events.", bg="white",
                         fg=GREY_BG, font=("Helvetica", 10)).pack(pady=10)
        
        #Reminders section
        rem_body = make_card("Reminders this month", 2, 0, colspan=2, open_cmd=self.reminders_screen)
        month_prefix = date.today().strftime("%Y-%m")
        cursor.execute(
            "SELECT rem_title, remind_at, fired FROM reminders "
            "WHERE user_id=? AND remind_at LIKE ? ORDER BY remind_at ASC LIMIT 5",
            (self.current_user_id, f"{month_prefix}-%"))
        rem_rows = cursor.fetchall()
        if not rem_rows:
            tk.Label(rem_body, text="No reminders set for this month.",
                     bg="white", fg="#888888", font=("Helvetica", 10)).pack(pady=10)
        else:
            for rtitle, rat, fired in rem_rows:
                icon = "✔" if fired else "○"
                cell = tk.Frame(rem_body, bg=GREY_BG, relief="solid", bd=1)
                cell.pack(fill="x", pady=2)
                tk.Label(cell, text=f"{icon}  {rtitle}", bg=GREY_BG, fg="#0d0d0d",
                         font=("Helvetica", 10)).pack(side="left", padx=8, pady=4)
                tk.Label(cell, text=rat, bg=GREY_BG, fg="#888888",
                         font=("Helvetica", 9)).pack(side="right", padx=8)

        
        
    def open_settings_sidebar(self):
        """Shows a panel over the home screen with the user's name and a logout button."""
        panel = tk.Frame(self.root, bg="white", width=220, height=700,
                          relief="solid", bd=1)
        panel.place(x=780, y=0)  # sits on the right side, over the home screen
        panel.pack_propagate(False)

        close_lbl = tk.Label(panel, text="✕ Close", bg="white", fg="#888888",
                              font=("Helvetica", 10), cursor="hand2")
        close_lbl.pack(anchor="ne", padx=10, pady=10)
        close_lbl.bind("<Button-1>", lambda e: panel.destroy())

        tk.Label(panel, text="👤", bg="white", font=("Helvetica", 30)).pack(pady=(20, 4))
        tk.Label(panel, text=self.current_username, bg="white", fg="#0d0d0d",
                 font=("Helvetica", 14, "bold")).pack(pady=(0, 30)) #Shows the username of the logged in user

        def logout():
            """Logs the user out and returns to the login screen."""
            self.current_user_id = None
            self.current_username = None
            self.login_screen()

        logout_lbl = tk.Label(panel, text="Log Out", bg=DARK_RED, fg="white",
                               font=("Helvetica", 12, "bold"), padx=14, pady=8,
                               cursor="hand2")
        logout_lbl.pack(pady=10)

        make_hover_background(logout_lbl,DARK_RED,RED_HOVER_COLOR,logout)
            
    def notes_screen(self):
        """Creates the notes screen where users can see, create, and delete notes."""
        clear_screen(self.root)
        self.root.configure(bg=GREY_BG)
        cursor = self.db.get_cursor()

        header = tk.Frame(self.root, bg=DARK_RED)
        header.pack(fill="x")
        tk.Label(header, text="Notes", bg=DARK_RED, fg="white",
                 font=("Helvetica", 18, "bold")).pack(side="left", padx=20, pady=12)

        new_bar = tk.Frame(self.root, bg=GREY_BG, pady=10)
        new_bar.pack(fill="x", padx=20, pady=(14, 4))
        note_title=tk.Label(new_bar, text="Title:", bg=GREY_BG,
                 font=("Helvetica", 11,"bold"))
        note_title.pack(side="left")
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
        make_hover_background(back_notes,NAVY_BLUE,BLUE_HOVER_COLOR,self.home_screen)
        
        def create_section():
            """Creates a new note in the database."""
            title = new_title_entry.get().strip()
            try:
                cursor.execute(
                    "INSERT INTO notes (user_id, title, body) VALUES (?, ?, ?)",
                    (self.current_user_id, title, "")
                )
                self.db.commit() # save to database
            except sqlite3.IntegrityError:
                status_lbl.config(text="A note with this title already exists.")
                return
            new_title_entry.delete(0, "end")
            status_lbl.config(text="")
            load_sections()
        create_note_lbl=tk.Label(new_bar, text="Create new set", bg=NAVY_BLUE, fg="white",
                                 relief="raised", font=("Helvetica", 11),bd=0, padx=15,pady=6)
        create_note_lbl.pack(side="left")
        make_hover_background(create_note_lbl,NAVY_BLUE,BLUE_HOVER_COLOR,create_section)

        list_canvas = tk.Canvas(self.root, bg=GREY_BG)
        list_canvas.pack(fill="both", expand=True, padx=20, pady=10)
        inner = tk.Frame(list_canvas, bg=GREY_BG) # Make a frame inside the canvas to hold the notes
        list_canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: list_canvas.configure(
            scrollregion=list_canvas.bbox("all")))

        def load_sections():
            """Loads the notes from the database and displays them in the list."""
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
                    """Opens the note editing screen for the selected note."""
                    self.note_edit_screen(nid, ntitle)

                def delete_section(nid=note_id, ntitle=note_title):
                    if messagebox.askyesno("Delete", f'Delete "{ntitle}"?'):
                        cursor.execute("DELETE FROM notes WHERE id=?", (nid,))
                        self.db.commit()
                        load_sections() #reload the list after deletion

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
        """Creates the screen for editing a note."""
        clear_screen(self.root)
        self.root.configure(bg=GREY_BG)
        cursor = self.db.get_cursor() # get a cursor to the database so we can read and write the note

        header = tk.Frame(self.root, bg=DARK_RED)
        header.pack(fill="x")

        back_lbl = tk.Label(header, text="◄", bg=DARK_RED, fg="white",font=("Helvetica",20), cursor="hand2")
        back_lbl.pack(side="left", padx=(15, 8), pady=12)
        back_lbl.bind("<Button-1>", lambda e: self.notes_screen())

        header_lbl = tk.Label(header, text=note_title, bg=DARK_RED, fg="white",
                            font=("Helvetica", 16, "bold"))
        header_lbl.pack(side="left", pady=12)

        text_frame = tk.Frame(self.root, bg=GREY_BG) #frame to hold the text widget
        text_frame.pack(fill="both", expand=True)

        notes_text = tk.Text(text_frame, wrap="word", font=("Helvetica", 13),
                             relief="flat", bd=0, padx=20, pady=16)
        notes_text.pack(side="left", fill="both", expand=True)

        cursor.execute("SELECT body FROM notes WHERE id=?", (note_id,))
        existing = cursor.fetchone()
        if existing:
            notes_text.insert("1.0", existing[0])

        save_bar = tk.Frame(self.root, bg=GREY_BG)
        save_bar.pack(fill="x")
        save_status = tk.Label(save_bar, text="", bg=GREY_BG, fg="green",
                               font=("Helvetica", 10))
        save_status.pack(side="left", padx=14)
        
        def save_note():
            """Saves the current note to the database."""
            new_body = notes_text.get("1.0", "end-1c")
            cursor.execute(
                "UPDATE notes SET body=? WHERE id=?",
                (new_body, note_id)
            )
            self.db.commit()
            messagebox.showinfo("Saved", "Your changes have been saved.")#Messagebox to confirm that the note has been saved

        save_lbl=tk.Label(save_bar, text="Save", bg=NAVY_BLUE, fg="white",
                  relief="flat", font=("Helvetica", 11),padx=14, pady=6)
        save_lbl.pack(side="right", padx=14, pady=8)
        save_lbl.bind("<Button-1>", lambda e: save_note())
        make_hover_background(save_lbl,NAVY_BLUE,BLUE_HOVER_COLOR,save_note)
    def flashcards_screen(self):
        """Creates the flashcards screen where users can see, create, and delete flashcard sets."""
        clear_screen(self.root)
        self.root.configure(bg=GREY_BG)
        cursor = self.db.get_cursor()

        header = tk.Frame(self.root, bg=DARK_RED)
        header.pack(fill="x")
        tk.Label(header, text="Flashcards", bg=DARK_RED, fg="white",
                 font=("Helvetica", 18, "bold")).pack(side="left", padx=20, pady=12)
        footer= tk.Frame(self.root, bg=GREY_BG)
        footer.pack(fill="x", side="bottom")
        back_flashcards=tk.Label(footer, text="Back", bg=NAVY_BLUE, fg="white",padx=14, pady=6,)
        back_flashcards.pack(side="right", padx=25, pady=15)
        make_hover_background(back_flashcards,NAVY_BLUE,BLUE_HOVER_COLOR,self.home_screen)


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
            """Creates a new flashcard set in the database."""
            name = new_deck_entry.get().strip()
            if not name:
                status_lbl.config(text="Enter a set name.")
                return
            try:
                cursor.execute(
                    "INSERT INTO decks (user_id, name) VALUES (?, ?)",
                    (self.current_user_id, name)
                )
                self.db.commit()
            except sqlite3.IntegrityError:
                status_lbl.config(text="A set with this name already exists.") # Error message if the set name already exists
                return
            new_deck_entry.delete(0, "end")
            status_lbl.config(text="")
            load_decks()

        create_lbl=tk.Label(new_bar, text="Create Set", bg=NAVY_BLUE, fg="white",
                  relief="flat", font=("Helvetica", 11),padx=10,pady=6)
        create_lbl.pack(side="left")
        make_hover_background(create_lbl,NAVY_BLUE,BLUE_HOVER_COLOR,create_deck)
        

        list_frame = tk.Frame(self.root, bg=GREY_BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        def load_decks():
            """Loads the flashcard sets from the database and displays them in the list."""
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
                return # If there are no decks, display a message and return
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
            """Deletes a flashcard set"""
            if messagebox.askyesno("Delete", f'Delete set "{deck_name}" and all its cards?'):
                cursor.execute("DELETE FROM decks WHERE id=?", (deck_id,))
                self.db.commit()
                load_decks()

        load_decks() # Load the decks when the screen is first created

    def deck_edit_screen(self, deck_id, deck_name):
        """Creates the screen for editing a flashcard set."""
        clear_screen(self.root) # Clear the screen and set the background color
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
            """Adds a new flashcard to the set."""
            front = front_entry.get().strip()
            back = back_entry.get().strip()
            if not front or not back:
                add_status.config(text="Fill in both sides.", fg=DARK_RED) # Error message if a side is empty
                return
            cursor.execute(
                "INSERT INTO flashcards (deck_id, user_id, front, back) VALUES (?, ?, ?, ?)",
                (deck_id, self.current_user_id, front, back)
            )
            self.db.commit()
            front_entry.delete(0, "end") # Clear the front after adding the card
            back_entry.delete(0, "end") # Clear the back after adding the card
            add_status.config(text="Card added!")
            self.root.after(1500, lambda: add_status.config(text="")) # Clear the status message after 1.5 seconds
            load_cards()

        add_card_lbl=tk.Label(add_frame, text="Add Card", bg=NAVY_BLUE, fg="white",
                  relief="flat", font=("Helvetica", 11, "bold"),padx=12, pady=5)
        add_card_lbl.grid(row=4, column=0, columnspan=2, pady=10)
        make_hover_background(add_card_lbl,NAVY_BLUE,BLUE_HOVER_COLOR,add_card) # Make the "Add Card" label look like a button and call add_card when clicked
        list_frame = tk.Frame(self.root, bg=GREY_BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)

        def load_cards():
            """Loads the flashcards from the database and displays them in the list."""
            for widgets in list_frame.winfo_children():
                widgets.destroy()
            cursor.execute(
                "SELECT id, front, back FROM flashcards WHERE deck_id=? ORDER BY id",
                (deck_id,)
            )# Get all the cards for the current deck
            cards = cursor.fetchall()
            if not cards:
                tk.Label(list_frame, text="No cards yet. Add one above!",
                         bg=GREY_BG, fg="#888888",
                         font=("Helvetica", 11)).pack(pady=20) 
                return
            for card_id, front, back in cards: # Create a row for each card with the question and answer displayed
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
        """Creates the study screen for a flashcard set."""
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT id, front, back FROM flashcards WHERE deck_id=? ORDER BY id",
            (deck_id,)
        )
        all_cards = cursor.fetchall() # Get all the cards for the current deck

        if not all_cards:
            messagebox.showinfo("Empty Set", "This set has no cards yet!")
            return

        win = tk.Toplevel(self.root)
        win.title(deck_name)
        win.geometry("700x520")
        win.configure(bg="#1a1a2e")
        win.grab_set() # Make the study window modal so the user can't interact with the main window until they close it

        queue = list(all_cards)
        state = {
            "idx": 0,
            "flipped": False,
            "total": len(all_cards),
        } # dictionary to keep track of the current card index, whether the card is flipped, and the total number of cards

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
            """Creates a circular button."""
            sub = tk.Frame(circle_frame, bg="#1a1a2e")
            sub.pack(side="left", padx=20)
            size = 72
            circle = tk.Canvas(sub, width=size, height=size,highlightthickness=0, bg="#1a1a2e") # Create a canvas to draw the circle button
            circle.pack()
            circle.create_oval(4, 4, size - 4, size - 4, fill=colour, outline="") # Draw the circle
            circle.create_text(size // 2, size // 2, text=symbol,
                               font=("Helvetica", 22), fill="#1a1a2e") # Draw the symbol in the center of the circle
            circle.bind("<Button-1>", lambda e: command())
            tk.Label(sub, text=label, bg="#1a1a2e", fg="#cccccc",
                     font=("Helvetica", 9)).pack(pady=(4, 0))

        def next_card():
            """ Displays the next card in the queue."""
            if not queue:
                show_summary()
                return
            current = queue[state["idx"] % len(queue)] # Get the current card based on the index in the queue
            state["flipped"] = False # Reset the flipped state when moving to the next card
            card_frame.config(bg="white")
            card_label.config(text=current[1], bg=GREY_BG, fg="#0d0d0d") # Display the questoin and reset the background

        def flip_card(event=None):
            """ Flips the card to reveal answer"""
            if not queue: # If there are no cards in the queue, do nothing
                return
            current = queue[state["idx"] % len(queue)]
            if not state["flipped"]: # If the card is not flipped, flip it to show the answer
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
            """ Removes the current card from the queue and shows the next one"""
            if not queue:
                return
            queue.pop(state["idx"] % len(queue)) # Remove the current card from the queue
            if queue:
                state["idx"] = state["idx"] % len(queue) # If there are still cards left, keep the index within bounds
            next_card() if queue else show_summary() # If there are still cards left, show the next card else show the summary screen

        def dont_know():
            """ Moves to the next card without removing the current one"""
            if not queue:
                return
            state["idx"] = (state["idx"] + 1) % len(queue) 
            next_card()

        def got_wrong():
            """ Moves the current card to the end of the queue and shows the next one"""
            if not queue:
                return
            card = queue.pop(state["idx"] % len(queue))
            queue.append(card)
            state["idx"] = state["idx"] % len(queue)
            next_card()
    

        make_circle_btn(btn_row, "Correct", "✓", "#90E6FC", got_right) # Create the buttons for the user to press if they got the card right, wrong, or don't know
        make_circle_btn(btn_row, "Not Sure",   "?", "#7CD7F7", dont_know)
        make_circle_btn(btn_row, "Incorrect",  "✗", "#A8EEFF", got_wrong)

        def show_summary():
            """ Displays a summary screen when all cards have been reviewed"""
            for widgets in win.winfo_children():
                widgets.destroy()
            win.configure(bg="#1a1a2e") # Set the background color of the summary screen
            tk.Label(win, text="Revision Complete!", bg="#1a1a2e", fg="white",
                     font=("Helvetica", 22, "bold")).pack(pady=(60, 10))
            close_cards=tk.Label(win, text="Close", bg=DARK_RED, fg="white", relief="flat",
                      font=("Helvetica", 11), padx=16, pady=6)
            close_cards.pack()
            make_hover_background(close_cards,DARK_RED,RED_HOVER_COLOR,win.destroy)

        next_card()
        
    def quiz_screen(self):  
        """Creates the quiz management screen where users can see, create, edit, and delete quizzes."""
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
            """ Creates a new quiz in the database."""
            name = quiz_name_entry.get().strip()
            if not name: # If the name is empty dont let user create quiz
                return
            cursor.execute("INSERT INTO quizzes (user_id, title) VALUES (?, ?)",
                           (self.current_user_id, name))
            self.db.commit()
            quiz_name_entry.delete(0, "end")
            refresh_quiz_list()
 
        create_quiz_lbl=tk.Label(top, text="Create Quiz",bg=NAVY_BLUE,fg="white",padx=14,pady=6,relief="flat",font=("Helvetica", 11))
        create_quiz_lbl.pack(side="left", padx=5, pady=11)
        
        make_hover_background(create_quiz_lbl,NAVY_BLUE,BLUE_HOVER_COLOR,create_quiz)
        

        footer=tk.Frame(self.root,bg=GREY_BG) # Create a footer frame to for the back button
        footer.pack(side="bottom",fill="x")
        back_quiz=tk.Label(footer, text="Back", bg=NAVY_BLUE, fg="white",padx=14, pady=6,)
        back_quiz.pack(side="right", padx=25, pady=15)
        
        make_hover_background(back_quiz,NAVY_BLUE,BLUE_HOVER_COLOR,self.home_screen)
 
 
        # quiz list
        list_frame = tk.Frame(self.root, bg=GREY_BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        def refresh_quiz_list():
            """ Refreshes the list of quizzes displayed on the screen."""
            for widgets in list_frame.winfo_children():
                widgets.destroy()
            cursor.execute("SELECT id, title FROM quizzes WHERE user_id=?",
                           (self.current_user_id,))
            quizzes = cursor.fetchall()
            if not quizzes:
                tk.Label(list_frame, text="No quizzes yet!",
                         bg="white", fg="#888888").pack(pady=20)
                return
            for qid, qtitle in quizzes: # Create a row for each quiz with buttons to edit, take, or delete the quiz
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
        """ Creates the screen for editing a quiz, allowing users to add questions and view existing ones."""
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
        tk.OptionMenu(form, correct_var, "A", "B", "C", "D").grid(row=5, column=1, sticky="w", padx=5) # Create a dropdown menu for selecting the correct answer

        status = tk.Label(self.root, text="", bg=GREY_BG, fg=DARK_RED)
        status.pack()

        def add_question():
            """ Adds a new question to the quiz in the database."""
            ques  = fields["Question"].get().strip()
            a_opt  = fields["Option A"].get().strip()
            b_opt  = fields["Option B"].get().strip()
            c_opt  = fields["Option C"].get().strip()
            d_opt  = fields["Option D"].get().strip()
            ans = correct_var.get().upper() # Get the selected correct answer from the dropdown menu
            if not all([ques, a_opt, b_opt, c_opt, d_opt]): # If any of the fields are empty, show an error message
                status.config(text="Please fill in all fields.")
                return
            cursor.execute("""
                INSERT INTO quiz_questions
                (quiz_id, question_text, option_a, option_b, option_c, option_d, correct)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (quiz_id, ques, a_opt, b_opt, c_opt, d_opt, ans))
            self.db.commit()
            for e in fields.values():
                e.delete(0, "end") # Clear the input fields after adding the question
            status.config(text="Question added.", fg="green")
            load_questions()

        tk.Button(self.root, text="Add Question", command=add_question).pack(pady=5)

        # question list
        q_frame = tk.Frame(self.root, bg=GREY_BG)
        q_frame.pack(fill="both", expand=True, padx=20, pady=5)

        def load_questions():
            """ Loads the questions for the quiz and displays them."""
            for widgets in q_frame.winfo_children():
                widgets.destroy()
            cursor.execute(
                "SELECT id, question_text, correct FROM quiz_questions WHERE quiz_id=?",
                (quiz_id,))
            rows = cursor.fetchall()# Get all the questions for the current quiz
            if not rows: # If there are no questions in the quiz, display a message
                tk.Label(q_frame, text="No questions yet!", bg="white", fg="#888888").pack()
                return
            for qid, qtxt, qans in rows: # Create a row for each question with the question text and the correct answer displayed
                r = tk.Frame(q_frame, bg=GREY_BG, relief="solid", bd=1)
                r.pack(fill="x", pady=2)
                tk.Label(r, text=f"Q: {qtxt}  [Ans: {qans}]", bg=GREY_BG,
                        font=("Helvetica", 10), wraplength=500,
                        justify="left",fg="black").pack(side="left", padx=8, pady=4)
                tk.Button(r, text="Delete", fg=DARK_RED,
                        command=lambda i=qid: delete_question(i), bg=DARK_RED).pack(side="right", padx=6)

        def delete_question(qid):
            """ Deletes a question from the quiz."""
            cursor.execute("DELETE FROM quiz_questions WHERE id=?", (qid,))
            self.db.commit()
            load_questions()

        back_quiz=tk.Label(self.root, text="Back", bg=NAVY_BLUE, fg="white",padx=14, pady=6,)
        back_quiz.pack(side="right", padx=25, pady=15)
    
        make_hover_background(back_quiz,NAVY_BLUE,BLUE_HOVER_COLOR,self.quiz_screen)
        
        load_questions()

    def take_quiz(self, quiz_id, quiz_title):
        """ Starts the quiz."""
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

        state = {"idx": 0, "score": 0, "total": len(questions)} # dictionary to keep track of the current question index, the score, and the total number of questions

        def show_question():
            """ Displays the current question and its options."""
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

            chosen = tk.StringVar() # Variable to keep track of the selected answer
            for label, text in zip(["A","B","C","D"], [a, b, c, d]):
                tk.Radiobutton(win, text=f"{label}.  {text}", variable=chosen,
                            value=label, bg="white", font=("Helvetica", 11)).pack(anchor="w", padx=40, pady=3)

            feedback = tk.Label(win, text="", bg="white", font=("Helvetica", 11, "bold"))
            feedback.pack(pady=8)

            def submit():
                ans = chosen.get()
                if ans == "":
                    feedback.config(text="Please select an answer.", fg=DARK_RED)
                    return
                if ans == correct:
                    state["score"] += 1
                    feedback.config(text="✔  Correct!", fg="green")
                else:
                    feedback.config(text=f"✘  Wrong. The correct answer is {correct}", fg=DARK_RED)
                submit_btn.config(state="disabled") # Disable the submit button after submission to prevent multiple submissions
                win.after(1200, lambda: [state.update({"idx": state["idx"]+1}), show_question()])

            submit_btn = tk.Label(win, text="Submit Answer", bg=NAVY_BLUE, fg="white",
                                font=("Helvetica", 11, "bold"), relief="flat",
                                padx=20, pady=6)
            submit_btn.pack(pady=4)
            
            make_hover_background(submit_btn,NAVY_BLUE,BLUE_HOVER_COLOR,submit)

        def show_result():
            """ Displays the final score and saves the try to the database."""
            from datetime import datetime
            cursor.execute(
                "INSERT INTO quiz_attempts (quiz_id, user_id, score, total, taken_at) VALUES (?,?,?,?,?)",
                (quiz_id, self.current_user_id, state["score"], state["total"],
                 datetime.now().strftime("%Y-%m-%d %H:%M"))) # Save the quiz attempt to the database with the current timestamp
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
        """Creates the calendar screen where users can view and add events."""
        from datetime import datetime, date
        import calendar as cal
 
        clear_screen(self.root)
        self.root.configure(bg="white")
        cursor = self.db.get_cursor()
 
        now = datetime.now()
        state = {"year": now.year, "month": now.month} # dictionary to keep track of the current year and month being displayed in the calendar
        header=tk.Frame(self.root,bg=DARK_RED)
        header.pack(fill="x")
        tk.Label(header, text="Calendar", font=("Helvetica", 20, "bold"),fg="white",bg=DARK_RED).pack(pady=10,side="left",padx=20)
        back_cal=tk.Label(header,text="Back",bg=NAVY_BLUE,fg="white",padx=14,pady=6)
        back_cal.pack(pady=5,side="right", padx=20)

        make_hover_background(back_cal,NAVY_BLUE,BLUE_HOVER_COLOR,self.home_screen)
 
        # Navigation bar to switch months
        nav = tk.Frame(self.root, bg="white")
        nav.pack()
        left_btn=tk.Label(nav, text="◄", bg="white", fg=DARK_RED,width="4", font=("Helvetica", 20), cursor="hand2")
        left_btn.pack(side="left", padx=10, pady=10)
        def prev_month(event=None):
            """ Moves to the previous month in the calendar."""
            if state["month"] == 1:
                state["month"] = 12
                state["year"] -= 1
            else:
                state["month"] -= 1
            actual_calendar() # Refresh the calendar display after changing the month
        left_btn.bind("<Button-1>", prev_month)
        right_btn=tk.Label(nav, text="►", bg="white",width="2",fg=DARK_RED, font=("Helvetica", 20), cursor="hand2")
        right_btn.pack(side="right", padx=10, pady=10)
        def next_month(event=None):
            """ Moves to the next month in the calendar."""
            if state["month"] == 12:
                state["month"] = 1
                state["year"] += 1
            else:
                state["month"] += 1
            actual_calendar()

        right_btn.bind("<Button-1>", next_month)        
        month_lbl = tk.Label(nav, text="", bg="white",fg=DARK_RED,font=("Helvetica", 26, "bold"), width=20)
        month_lbl.pack(side="left")
 
        # main area
        main = tk.Frame(self.root, bg="white")
        main.pack(fill="both", expand=True, padx=10)

        # left panel calendar
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
        
        event_date.insert(0, now.strftime("%Y-%m-%d")) # Pre-fill the date entry with todays date
        tk.Label(add_form, text="Type:", bg=GREY_BG, font=("Helvetica", 9)).grid(row=2, column=0, sticky="w", padx=4)
        type_var = tk.StringVar(value="exam")
        
        tk.OptionMenu(add_form, type_var, "exam", "assignment", "study", "other").grid(row=2, column=1, sticky="w", padx=4)  # Create a dropdown menu for selecting the event type     
        def load_event_list():
            for widgets in event_list_frame.winfo_children():
                widgets.destroy()
            y, m = state["year"], state["month"] # Get the current year and month from the state dictionary
            cursor.execute(
                "SELECT title, event_date, event_type FROM calendar_events "
                "WHERE user_id=? AND event_date LIKE ? ORDER BY event_date",
                (self.current_user_id, f"{y:04d}-{m:02d}-%"))
            rows = cursor.fetchall()
            if not rows:
                tk.Label(event_list_frame, text="No events.", bg=GREY_BG,
                        fg="#888888", font=("Helvetica", 9)).pack(pady=6)
                return
            for ev_title, ev_date, ev_type in rows: # Create a row for each event with the date and title displayed
                rf = tk.Frame(event_list_frame, bg=GREY_BG)
                rf.pack(fill="x", pady=1, padx=4)
                tk.Label(rf, text=f"{ev_date[8:]}  {ev_title}", bg=GREY_BG,
                        font=("Helvetica", 9)).pack(side="left", padx=2)
            
                
        def actual_calendar():
            for widgets in cal_frame.winfo_children():
                widgets.destroy()
            y, m = state["year"], state["month"] # Get the current year and month from the state dictionary
            month_lbl.config(text=datetime(y, m, 1).strftime("%B %Y"))

            cursor.execute(
                "SELECT event_date, event_type FROM calendar_events WHERE user_id=? AND event_date LIKE ?",
                (self.current_user_id, f"{y:04d}-{m:02d}-%"))
            event_map = {}
            for ed, et in cursor.fetchall(): # Create a mapping of days to event types for coloring the calendar cells
                day = int(ed[8:])
                event_map.setdefault(day, []).append(et)

            for col, dn in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]): # Create the header row for the days of the week
                tk.Label(cal_frame, text=dn, bg="white", fg="#888888",
                            font=("Helvetica",11, "bold"), width=7).grid(row=0, column=col, pady=(0,2))

            first_wd = date(y, m, 1).weekday()
            days_in  = cal.monthrange(y, m)[1]
            today    = now.day if (y == now.year and m == now.month) else -1

            r, c = 1, first_wd # Start the row and column for the first day of the month based on the weekday of the first day
            for d in range(1, days_in + 1):
                evts = event_map.get(d, [])
                first_type = evts[0] if evts else None
                bg = "#bbdefb" if d == today else (TYPE_COLORS.get(first_type, "white") if first_type else "white")          
                cell = tk.Frame(cal_frame, bg=bg, width=100, height=100, relief="solid", bd=1)
                cell.grid(row=r, column=c, padx=1, pady=1)
                cell.grid_propagate(False) # Prevent the cell from resizing if the content inside is large
                tk.Label(cell, text=str(d), bg=bg, fg="#0d0d0d",
                            font=("Helvetica", 15, "bold" if d == today else "normal")).pack(anchor="nw", padx=3)
                c += 1# Move to the next column for the next day
                if c == 7: # If the column index reaches 7 (end of the week), reset to the first column and move to the next row
                    c, r = 0, r + 1

            load_event_list()    
        
        def add_event():
            name=event_name.get()
            date=event_date.get()
            type=type_var.get()
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError: # If the date format is invalid, show a warning message
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
            actual_calendar()

        tk.Button(add_form, text="Add Event", command=add_event,
                font=("Helvetica", 9)).grid(row=3, column=0, columnspan=2, pady=4)
        actual_calendar()
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
        back_rem.pack(pady=5,padx=10,side="right")
        
        make_hover_background(back_rem,NAVY_BLUE,BLUE_HOVER_COLOR,self.home_screen)
        
        def add_reminder():
            rem_title = re_title.get().strip()
            rem_date= re_date.get().strip()
            rem_time= re_time.get().strip()
            
            if not rem_title: # If the reminder title is empty, show an error message
                status.config(text="Enter a reminder title.")
                return
            try:
                remind_dt = datetime.strptime(f"{rem_date} {rem_time}", "%Y-%m-%d %H:%M")
            except ValueError:
                # If the date or time format is invalid, show an error message
                status.config(text="Invalid date or time.")
                return
            if remind_dt <= datetime.now():
                status.config(text="Please set a future date/time.")
                return
            status.config(text="")
            rat = remind_dt.strftime("%Y-%m-%d %H:%M") # Format the reminder date and time for storage in the database
            cursor.execute(
                "INSERT INTO reminders (user_id, rem_title, remind_at) VALUES (?,?,?)",
                (self.current_user_id,rem_title, rat))
            self.db.commit()
            re_title.delete(0, "end")
            messagebox.showinfo("Reminder Set!", f"Reminder set for {rat}.\nThe app must be open to receive notifications.")
            load_reminders()
 
            
        set_btn=tk.Label(self.root, text="Set Reminder",padx=10, pady=5,bg=NAVY_BLUE,fg="white")
        set_btn.pack(pady=6)
        
        make_hover_background(set_btn,NAVY_BLUE,BLUE_HOVER_COLOR,add_reminder)
        
        list_frame = tk.Frame(self.root, bg="white")
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)
        def load_reminders():
            """ Loads the reminders from the database and displays them in the list."""
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
app = AppFace(root) 
root.mainloop() 