import tkinter as tk
from tkinter import *
import sqlite3
import os
import hashlib
from tkinter import messagebox 


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
        self.root.title("Study App")
        self.root.geometry("900x600")
        self.current_user_id = None # no one logged in yet
        self.current_username = None
        self.left_panel("testing bigtxt", "testing small text")
        self.db = database_setup() # create an object of the database setup class
        self.db.create_tables() # create the tables in the database if they don't exist
        self.login_screen()

        
    def left_panel(self,head,subtext):
        left_frame = tk.Frame(self.root, bg="#780606", width=400, height=400)
        left_frame.pack(side="left", fill="y")
        left_frame.pack_propagate(False)
 
        tk.Label(left_frame, text="✳", bg="#780606", fg="white",
                 font=("Helvetica", 40, "bold")).place(x=44, y=44)
 
        tk.Label(left_frame, text=head, bg="#780606", fg="white",
                 font=("Helvetica", 30, "bold"), justify="left").place(x=44, y=200)
 
        tk.Label(left_frame, text=subtext, bg="#780606", fg="#ccccff",
                 font=("Helvetica", 12), justify="left",
                 wraplength=320).place(x=44, y=330)
    

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
            head="study app",
            subtext="the usbtext thing"
        )
 
        # Right white frame where login goes
        right_panel = tk.Frame(self.root, bg="white")
        right_panel.pack(side="right", fill="both", expand=True)
 
        form = tk.Frame(right_panel, bg="white")
        form.place(relx=0.5, rely=0.5, anchor="center")
 
        # name
        tk.Label(form, text="Study App", bg="white", fg="#111111",
                 font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 30))
 
        # Heading
        tk.Label(form, text="Welcome Back!", bg="white", fg="#0d0d0d",
                 font=("Helvetica", 22, "bold")).pack(anchor="w")
 
        # Link to register
        sub_text = tk.Frame(form, bg="white")
        sub_text.pack(anchor="w", pady=(6, 24))
        tk.Label(sub_text, text="No account? ", bg="white", fg="#888888",
                 font=("Helvetica", 11)).pack(side="left")
        tk.Label(sub_text, text="Register here", bg="white", fg="#2A2AE1",
                 font=("Helvetica", 11, "underline")).pack(side="left")
        sub_text.winfo_children()[1].bind("<Button-1>", lambda e: self.register_screen())
        
        
        
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
                self.home_screen()     # go to home screen
            else:
                status.config(text="Incorrect username or password.")
 
        # Login button
        tk.Button(form, text="Login Now", bg="#0d0d0d", fg="white",
                  font=("Helvetica", 13, "bold"), relief="flat", bd=0,
                  width=30, height=2, activebackground="#2A2AE1",
                  activeforeground="white", command=attempt_login).pack(pady=(4, 0))
        

    def register_screen(self):
        clear_screen(self.root)
        self.left_panel(
            head="create account",
            subtext="subtext for create account screen"
        )
        right_frame = tk.Frame(self.root, bg="white")
        right_frame.pack(side="right", fill="both", expand=True)
 
        form = tk.Frame(right_frame, bg="white")
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
                 font=("Helvetica", 11, "underline")).pack(side="left")
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
                relief="flat", bd=0, width=30, height=2,
                activebackground="#2A2AE1", activeforeground="white",
                command=attempt_register).pack(pady=(4, 0))
    def home_screen(self):
        clear_screen(self.root)
        self.root.configure(bg="white")
        tk.Label(self.root, text=f"Welcome, {self.current_username}",
        font=("Helvetica", 20, "bold")).pack(pady=20)

        tk.Button( self.root,text="Open Notes",command=self.notes_screen).pack(pady=10)
        
        tk.Button(self.root,text="Flashcards",command=self.flashcards_screen).pack(pady=10)
            
        tk.Button(self.root,text="Quizzes",command=self.quiz_screen).pack(pady=10)
        
    def notes_screen(self):
        clear_screen(self.root)
        self.root.configure(bg="white")
        notes_text = tk.Text(self.root, wrap="word", font=("Arial", 14))
        notes_text.pack(fill="both", expand=True)
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT body FROM notes WHERE user_id=?",
            (self.current_user_id,))
        note = cursor.fetchone()
        if note is None:
            cursor.execute(
                "INSERT INTO notes (user_id, title, body) VALUES (?, ?, ?)",
                (self.current_user_id, "My Notes", "")
            )
            self.db.commit()
            note_body = ""
        else:
            note_body = note[0]
        notes_text.insert("1.0", note_body)
        def save_note():
            new_body = notes_text.get("1.0", "end-1c")
            cursor.execute(
                "UPDATE notes SET body=? WHERE user_id=?",
                (new_body, self.current_user_id)
            )
            self.db.commit()
            messagebox.showinfo("Saved", "Your notes have been saved.")
        save_button = tk.Button(self.root, text="Save Notes", command=save_note)
        save_button.pack(pady=10)
        
    def flashcards_screen(self):
        clear_screen(self.root)
        self.root.configure(bg="white")
        cursor=self.db.get_cursor()
        cursor.execute("SELECT id FROM decks WHERE user_id=?",
                        (self.current_user_id,))
        deck = cursor.fetchone()
        if deck is None:
            cursor.execute(
                "INSERT INTO decks (user_id, name) VALUES (?, ?)",
                (self.current_user_id, "My flashcards")
            )
            self.db.commit()
            deck_id= cursor.lastrowid
        else:
            deck_id = deck[0]
        tk.Label(self.root,text="flashcards").pack(pady=20)
        
        flash_frame = tk.Frame(self.root, bg="white")
        flash_frame.pack(pady=10)
        
        question_entry=tk.Entry(flash_frame,width=40)
        question_entry.grid(row=0, column=0, padx=5)
        
        answer_entry=tk.Entry(flash_frame,width=40)
        answer_entry.grid(row=0, column=1, padx=5)
        
        cards_frame=tk.Frame(self.root, bg="white")
        cards_frame.pack(pady=10)
        
        
        
        
        def load_flashcards():
            #clear old cards
            for widget in cards_frame.winfo_children():
                widget.destroy()
                
            cursor.execute("SELECT front, back FROM flashcards WHERE deck_id=?",(deck_id,))
            for question, answer in cursor.fetchall():
                card = tk.Frame(cards_frame,bg="#f0f0f0",width=300,
                height=150,relief="solid",bd=1)
                card.pack(pady=10)
                question_label = tk.Label(card,text=question)
                question_label.pack(pady=10)
                state = {"answer": False}
            
                def flip_card(event,lbl=question_label,q=question,a=answer,s=state):
                    if s["answer"]:
                        lbl.config(text=q)
                    else:
                        lbl.config(text=a)  

                    s["answer"] = not s["answer"]
                card.bind("<Button-1>", flip_card)
                question_label.bind("<Button-1>", flip_card) 
        def add_flashcard():
            question = question_entry.get().strip()
            answer = answer_entry.get().strip()

            if not question or not answer:
                return

            cursor.execute(
                """
                INSERT INTO flashcards
                (deck_id, user_id, front, back)
                VALUES (?, ?, ?, ?)
                """,
                (
                    deck_id,
                    self.current_user_id,
                    question,
                    answer
                )
            )

            self.db.commit()

            question_entry.delete(0, "end")
            answer_entry.delete(0, "end")

            load_flashcards()    
            
        tk.Button(self.root,text="Add Flashcard",
        command=add_flashcard).pack(pady=5)

        tk.Button(self.root,text="Back",
                    command=self.home_screen).pack(pady=5)

        load_flashcards()
        
    def quiz_screen(self):  
        clear_screen(self.root)
        self.root.configure(bg="white")
        cursor = self.db.get_cursor()
 
        tk.Label(self.root, text="Quizzes", font=("Helvetica", 20, "bold")).pack(pady=10)
 
        # top area: list quizzes + create new
        top = tk.Frame(self.root, bg="white")
        top.pack(fill="x", padx=20)
 
        tk.Label(top, text="Quiz name:", bg="white").pack(side="left")
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
 
        tk.Button(top, text="Create Quiz", command=create_quiz).pack(side="left", padx=5)
        tk.Button(top, text="Back", command=self.home_screen).pack(side="right")
 
        # quiz list
        list_frame = tk.Frame(self.root, bg="white")
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        def refresh_quiz_list():
            for w in list_frame.winfo_children():
                w.destroy()
            cursor.execute("SELECT id, title FROM quizzes WHERE user_id=?",
                           (self.current_user_id,))
            quizzes = cursor.fetchall()
            if not quizzes:
                tk.Label(list_frame, text="No quizzes yet. Create one above.",
                         bg="white", fg="#888888").pack(pady=20)
                return
            for qid, qtitle in quizzes:
                row = tk.Frame(list_frame, bg="#f0f0f0", relief="solid", bd=1)
                row.pack(fill="x", pady=4)
                tk.Label(row, text=qtitle, bg="#f0f0f0",
                         font=("Helvetica", 12)).pack(side="left", padx=10, pady=8)
                tk.Button(row, text="Edit / Add Questions",
                          command=lambda i=qid, t=qtitle: self.quiz_edit_screen(i, t)
                          ).pack(side="left", padx=5)
                tk.Button(row, text="Take Quiz",
                          command=lambda i=qid, t=qtitle: self.take_quiz(i, t)
                          ).pack(side="left", padx=5)
                
                def delete_quiz(qid):
                    if messagebox.askyesno("Delete", "Delete this quiz and all its questions?"):
                        cursor.execute("DELETE FROM quizzes WHERE id=?", (qid,))
                        self.db.commit()
                        refresh_quiz_list()
                        
                tk.Button(row, text="Delete", fg="red",
                          command=lambda i=qid: delete_quiz(i)).pack(side="right", padx=10)
                
        refresh_quiz_list()

    def quiz_edit_screen(self, quiz_id, quiz_title):
        clear_screen(self.root)
        self.root.configure(bg="white")
        cursor = self.db.get_cursor()

        tk.Label(self.root, text=f"Edit: {quiz_title}",
                font=("Helvetica", 16, "bold")).pack(pady=10)

        # add question form
        form = tk.Frame(self.root, bg="white")
        form.pack(fill="x", padx=20, pady=5)

        fields = {}
        for i, label in enumerate(["Question", "Option A", "Option B", "Option C", "Option D"]):
            tk.Label(form, text=label+":", bg="white", width=12,
                    anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            e = tk.Entry(form, width=50)
            e.grid(row=i, column=1, padx=5, pady=2, sticky="w")
            fields[label] = e

        tk.Label(form, text="Correct (A-D):", bg="white", width=12,
                anchor="w").grid(row=5, column=0, sticky="w")
        correct_var = tk.StringVar(value="A")
        tk.OptionMenu(form, correct_var, "A", "B", "C", "D").grid(row=5, column=1, sticky="w", padx=5)

        status = tk.Label(self.root, text="", bg="white", fg="red")
        status.pack()

        def add_question():
            q  = fields["Question"].get().strip()
            a  = fields["Option A"].get().strip()
            b  = fields["Option B"].get().strip()
            c  = fields["Option C"].get().strip()
            d  = fields["Option D"].get().strip()
            ans = correct_var.get().upper()
            if not all([q, a, b, c, d]):
                status.config(text="Please fill in all fields.")
                return
            cursor.execute("""
                INSERT INTO quiz_questions
                (quiz_id, question_text, option_a, option_b, option_c, option_d, correct)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (quiz_id, q, a, b, c, d, ans))
            self.db.commit()
            for e in fields.values():
                e.delete(0, "end")
            status.config(text="Question added.", fg="green")
            load_questions()

        tk.Button(self.root, text="Add Question", command=add_question).pack(pady=5)

        # question list
        q_frame = tk.Frame(self.root, bg="white")
        q_frame.pack(fill="both", expand=True, padx=20, pady=5)

        def load_questions():
            for w in q_frame.winfo_children():
                w.destroy()
            cursor.execute(
                "SELECT id, question_text, correct FROM quiz_questions WHERE quiz_id=?",
                (quiz_id,))
            rows = cursor.fetchall()
            if not rows:
                tk.Label(q_frame, text="No questions yet.", bg="white", fg="#888888").pack()
                return
            for qid, qtxt, qans in rows:
                r = tk.Frame(q_frame, bg="#f0f0f0", relief="solid", bd=1)
                r.pack(fill="x", pady=2)
                tk.Label(r, text=f"Q: {qtxt}  [Ans: {qans}]", bg="#f0f0f0",
                        font=("Helvetica", 10), wraplength=500,
                        justify="left").pack(side="left", padx=8, pady=4)
                tk.Button(r, text="Delete", fg="red",
                        command=lambda i=qid: delete_question(i)).pack(side="right", padx=6)

        def delete_question(qid):
            cursor.execute("DELETE FROM quiz_questions WHERE id=?", (qid,))
            self.db.commit()
            load_questions()

        tk.Button(self.root, text="Back to Quizzes",
                command=self.quizzes_screen).pack(pady=5)
        load_questions()

    def take_quiz(self, quiz_id, quiz_title):
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT id, question_text, option_a, option_b, option_c, option_d, correct
            FROM quiz_questions WHERE quiz_id=?
        """, (quiz_id,))
        questions = cursor.fetchall()
        if not questions:
            messagebox.showinfo("Empty Quiz", "This quiz has no questions yet.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Quiz: {quiz_title}")
        win.geometry("600x450")
        win.configure(bg="white")
        win.grab_set()

        state = {"idx": 0, "score": 0, "total": len(questions)}

        def show_question():
            for w in win.winfo_children():
                w.destroy()
            idx = state["idx"]
            if idx >= state["total"]:
                show_result()
                return
            _, qtxt, a, b, c, d, correct = questions[idx]

            tk.Label(win, text=f"Question {idx+1} of {state['total']}",
                    bg="white", fg="#888888", font=("Helvetica", 10)).pack(anchor="w", padx=30, pady=(20, 4))
            tk.Label(win, text=qtxt, bg="white", fg="#0d0d0d",
                    font=("Helvetica", 13, "bold"), wraplength=520,
                    justify="left").pack(anchor="w", padx=30, pady=(0, 16))

            chosen = tk.StringVar()
            for label, text in zip(["A","B","C","D"], [a, b, c, d]):
                tk.Radiobutton(win, text=f"{label}.  {text}", variable=chosen,
                            value=label, bg="white", font=("Helvetica", 11),
                            activebackground="white",
                            selectcolor="white").pack(anchor="w", padx=40, pady=3)

            feedback = tk.Label(win, text="", bg="white", font=("Helvetica", 11, "bold"))
            feedback.pack(pady=8)

            def submit():
                ans = chosen.get()
                if not ans:
                    messagebox.showwarning("No answer", "Please select an option.", parent=win)
                    return
                if ans == correct:
                    state["score"] += 1
                    feedback.config(text="✔  Correct!", fg="green")
                else:
                    feedback.config(text=f"✘  Wrong. Correct answer: {correct}", fg="red")
                submit_btn.config(state="disabled")
                win.after(1200, lambda: [state.update({"idx": state["idx"]+1}), show_question()])

            submit_btn = tk.Button(win, text="Submit Answer", bg="#0d0d0d", fg="white",
                                font=("Helvetica", 11, "bold"), relief="flat",
                                padx=20, pady=6, command=submit)
            submit_btn.pack(pady=4)

        def show_result():
            for w in win.winfo_children():
                w.destroy()
            pct = int(state["score"] / state["total"] * 100)
            tk.Label(win, text="Quiz Complete!", bg="white",
                    font=("Helvetica", 18, "bold")).pack(pady=(40, 10))
            tk.Label(win, text=f"{state['score']} / {state['total']}  ({pct}%)",
                    bg="white", font=("Helvetica", 24, "bold"),
                    fg="green" if pct >= 70 else ("orange" if pct >= 40 else "red")).pack()
            tk.Button(win, text="Try Again",
                    command=lambda: [state.update({"idx":0,"score":0}), show_question()]
                    ).pack(pady=10)
            tk.Button(win, text="Close", command=win.destroy).pack()

        show_question()
        
        
        
            



root=tk.Tk()
app = appface(root) 
root.mainloop()   