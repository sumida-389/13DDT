import tkinter as tk
from tkinter import messagebox
 
from constants import DARK_RED, NAVY_BLUE, GREY_BG, BLUE_HOVER_COLOR, LIGHT_GREY
from helpers import clear_screen, make_hover_background

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
    
    status_quiz=tk.Label(top, text="", bg=GREY_BG, fg=DARK_RED)
    status_quiz.pack(side="left", padx=5,pady=5)
    
    def create_quiz():
        """ Creates a new quiz in the database."""
        name = quiz_name_entry.get().strip()
        # If the name is empty dont let user create quiz
        if not name: 
            status_quiz.config(text="Enter a quiz name")
            return
        cursor.execute("INSERT INTO quizzes (user_id, title) VALUES (?, ?)",
                        (self.current_user_id, name))
        self.db.commit()
        quiz_name_entry.delete(0, "end")
        refresh_quiz_list()

    create_quiz_lbl=tk.Label(top, text="Create Quiz",bg=NAVY_BLUE,fg="white",padx=14,pady=6,relief="flat",font=("Helvetica", 11))
    create_quiz_lbl.pack(side="left", padx=5, pady=11)
    
    make_hover_background(create_quiz_lbl,NAVY_BLUE,BLUE_HOVER_COLOR,create_quiz)
    
    # Create a footer frame to for the back button
    footer=tk.Frame(self.root,bg=GREY_BG) 
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
                        bg="white", fg=LIGHT_GREY).pack(pady=20)
            return
        # Create a row for each quiz with buttons to edit, take, or delete the quiz
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
    # Create a dropdown menu for selecting the correct answer
    tk.OptionMenu(form, correct_var, "A", "B", "C", "D").grid(row=5, column=1, sticky="w", padx=5) 

    status = tk.Label(self.root, text="", bg=GREY_BG, fg=DARK_RED)
    status.pack()

    def add_question():
        """ Adds a new question to the quiz in the database."""
        ques  = fields["Question"].get().strip()
        a_opt  = fields["Option A"].get().strip()
        b_opt  = fields["Option B"].get().strip()
        c_opt  = fields["Option C"].get().strip()
        d_opt  = fields["Option D"].get().strip()
        # Get the selected correct answer from the dropdown menu
        ans = correct_var.get().upper() 
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
            # Clear the input fields after adding the question
            e.delete(0, "end") 
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
        # Get all the questions for the current quiz
        rows = cursor.fetchall()
        # If there are no questions in the quiz, display a message
        if not rows: 
            tk.Label(q_frame, text="No questions yet!", bg="white", fg=LIGHT_GREY).pack()
            return
        # Create a row for each question with the question text and the correct answer displayed
        for qid, qtxt, qans in rows: 
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

    # dictionary to keep track of the current question index, the score, and the total number of questions
    state = {"idx": 0, "score": 0, "total": len(questions)} 

    def show_question():
        """ Displays the current question and its options."""
        for widgets in win.winfo_children():
            widgets.destroy()
        idx = state["idx"]
        if idx >= state["total"]:
            show_result()
            return
        _, qtxt, a, b, c, d, correct = questions[idx]

        tk.Label(win, text=qtxt, bg="white", fg="black",
                font=("Helvetica", 13, "bold"), wraplength=520,
                justify="left").pack(anchor="w", padx=30, pady=(0, 16))
        # Variable to keep track of the selected answer
        chosen = tk.StringVar() 
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
            # Disable the submit button after submission to prevent multiple submissions
            submit_btn.config(state="disabled") 
            win.after(1200, lambda: [state.update({"idx": state["idx"]+1}), show_question()])

        submit_btn = tk.Label(win, text="Submit Answer", bg=NAVY_BLUE, fg="white",
                            font=("Helvetica", 11, "bold"), relief="flat",
                            padx=20, pady=6)
        submit_btn.pack(pady=4)
        
        make_hover_background(submit_btn,NAVY_BLUE,BLUE_HOVER_COLOR,submit)

    def show_result():
        """ Displays the final score and saves the try to the database."""
        from datetime import datetime
        # Disable the submit button after submission to prevent multiple submissions
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