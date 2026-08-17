import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from constants import (
    DARK_RED,
    NAVY_BLUE,
    GREY_BG,
    TYPE_COLORS,
    RED_HOVER_COLOR,
    LIGHT_GREY,
)
from helpers import clear_screen, make_hover_background, make_hover_foreground


def home_screen(self):
    """Creates the home screen with dashboard"""
    from datetime import date

    clear_screen(self.root)
    self.root.configure(bg=GREY_BG)
    cursor = self.db.get_cursor()

    def check_reminders():
        """Checks the database(every 30sec) for any reminders that are due."""
        from datetime import datetime

        # Get current date and time in same format as reminder timestamps stored in database
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute(
            """
            SELECT id, rem_title
            FROM reminders
            WHERE user_id=?
            AND remind_at<=?
            AND fired=0
        """,
            (self.current_user_id, now),
        )

        reminders = cursor.fetchall()

        for reminder_id, title in reminders:
            # Display a pop-up notification for each reminder that is due
            messagebox.showinfo("Reminder", title)

            cursor.execute("UPDATE reminders SET fired=1 WHERE id=?", (reminder_id,))

        self.db.commit()

        # Function to run every 30 seconds so reminders are constantly checked
        self.root.after(30000, check_reminders)

    check_reminders()

    # Header
    header = tk.Frame(self.root, bg=DARK_RED)
    header.pack(fill="x")
    tk.Label(
        header,
        text=f"Welcome, {self.current_username}",
        font=("Helvetica", 20, "bold"),
        fg="white",
        bg=DARK_RED,
    ).pack(side="left", padx=20, pady=16)
    gear_lbl = tk.Label(
        header,
        text="⚙",
        bg=DARK_RED,
        fg="white",
        font=("Helvetica", 30),
        cursor="hand2",
    )
    gear_lbl.pack(side="right", padx=20, pady=16)

    make_hover_foreground(gear_lbl, "white", "#dddddd", self.open_settings_sidebar)

    search_lbl = tk.Label(
        header,
        text="⌕",
        bg=DARK_RED,
        fg="white",
        font=("Helvetica", 40),
        cursor="hand2",
    )
    search_lbl.pack(side="right", padx=(0, 4), pady=16)

    make_hover_foreground(search_lbl, "white", "#dddddd", self.open_search_panel)

    # Dashboard
    board = tk.Frame(self.root, bg=GREY_BG)
    board.pack(fill="both", expand=True, padx=16, pady=14)
    # Dashboard grid changes so each card expands evenly when window is resized
    board.grid_columnconfigure(0, weight=1, uniform="col")
    board.grid_columnconfigure(1, weight=1, uniform="col")
    board.grid_rowconfigure(0, weight=3)
    board.grid_rowconfigure(1, weight=3)
    board.grid_rowconfigure(2, weight=2)

    def make_card(title, row, col, colspan=1, open_cmd=None):
        """Reusable function to create a card with a title and an "Open" button."""
        outer = tk.Frame(board, bg="white", relief="solid", bd=1)
        outer.grid(
            row=row, column=col, columnspan=colspan, sticky="nsew", padx=8, pady=8
        )

        card_head = tk.Frame(outer, bg=DARK_RED)
        card_head.pack(fill="x")
        tk.Label(
            card_head,
            text=title,
            bg=DARK_RED,
            fg="white",
            font=("Helvetica", 13, "bold"),
        ).pack(side="left", padx=12, pady=8)
        if open_cmd:
            open_lbl = tk.Label(
                card_head,
                text="Open",
                bg=DARK_RED,
                fg="white",
                font=("Helvetica", 10),
                cursor="hand2",
            )
            open_lbl.pack(side="right", padx=12)

            make_hover_foreground(open_lbl, "white", NAVY_BLUE, open_cmd)

        body = tk.Frame(outer, bg="white")
        body.pack(fill="both", expand=True, padx=12, pady=10)
        # Return body frame so different dashboard sections can insert their own widgets
        return body

    # Notes section
    notes_body = make_card("Notes", 0, 0, open_cmd=self.notes_screen)

    # Get five most recently created notes for logged-in user
    cursor.execute(
        "SELECT id, title FROM notes WHERE user_id=? ORDER BY id DESC LIMIT 5",
        (self.current_user_id,),
    )
    note_rows = cursor.fetchall()
    if not note_rows:
        tk.Label(
            notes_body,
            text="No notes yet!",
            bg="white",
            fg=LIGHT_GREY,
            font=("Helvetica", 10),
        ).pack(pady=10)
    else:
        for nid, ntitle in note_rows:
            lbl = tk.Label(
                notes_body,
                text=f"{ntitle}",
                bg="white",
                fg="black",
                font=("Helvetica", 11),
                anchor="w",
                cursor="hand2",
            )
            lbl.pack(fill="x", pady=2)
            # Store current deck values so each label opens correct flashcard deck when clicked
            lbl.bind(
                "<Button-1>", lambda e, i=nid, t=ntitle: self.note_edit_screen(i, t)
            )

    # Flashcards section
    fc_body = make_card("Flashcards", 0, 1, open_cmd=self.flashcards_screen)
    cursor.execute(
        "SELECT id, name FROM decks WHERE user_id=? ORDER BY id DESC LIMIT 5",
        (self.current_user_id,),
    )
    deck_rows = cursor.fetchall()
    if not deck_rows:
        tk.Label(
            fc_body,
            text="No flashcard sets yet!",
            bg="white",
            fg=LIGHT_GREY,
            font=("Helvetica", 10),
        ).pack(pady=10)
    else:
        for did, dname in deck_rows:
            cursor.execute("SELECT COUNT(*) FROM flashcards WHERE deck_id=?", (did,))
            ccount = cursor.fetchone()[0]
            row = tk.Frame(fc_body, bg="white")
            row.pack(fill="x", pady=2)
            lbl = tk.Label(
                row,
                text=f"{dname}",
                bg="white",
                fg="black",
                font=("Helvetica", 11),
                anchor="w",
                cursor="hand2",
            )
            lbl.pack(side="left")
            tk.Label(
                row,
                text=f"{ccount} card{'s' if ccount != 1 else ''}",
                bg="white",
                fg=LIGHT_GREY,
                font=("Helvetica", 9),
            ).pack(side="right")
            # Store current deck values so each label opens correct flashcard deck when clicked
            lbl.bind("<Button-1>", lambda e, i=did, t=dname: self.study_deck(i, t))

    # Quiz section
    quiz_body = make_card("Quiz", 1, 0, open_cmd=self.quiz_screen)
    cursor.execute(
        """
        SELECT quiz_attempts.score, quiz_attempts.total,
            quizzes.title, quizzes.id
        FROM quiz_attempts
        JOIN quizzes
            ON quizzes.id = quiz_attempts.quiz_id
        WHERE quiz_attempts.user_id = ?
        ORDER BY quiz_attempts.id DESC
        LIMIT 1
        """,
        (self.current_user_id,),
    )
    last_attempt = cursor.fetchone()
    # If user has not taken a quiz before, show a message saying take one
    if not last_attempt:
        tk.Label(
            quiz_body,
            text="Take a quiz!",
            bg="white",
            fg=LIGHT_GREY,
            font=("Helvetica", 10),
        ).pack(pady=10)
    else:
        score, total, qtitle, qid = last_attempt

        # Makke a left and right side of quiz card, with left side showing
        # quiz title and score, and right side showing a pie chart
        quiz_left = tk.Frame(quiz_body, bg="white")
        quiz_left.pack(side="left", fill="both", expand=True)

        tk.Label(
            quiz_left,
            text=qtitle,
            bg="white",
            fg="black",
            font=("Helvetica", 12, "bold"),
            anchor="w",
        ).pack(anchor="w")
        tk.Label(
            quiz_left,
            text=f"Latest score: {score} / {total}",
            bg="white",
            fg=NAVY_BLUE,
            font=("Helvetica", 14, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(4, 4))
        if total > 0 and score == total:
            note_txt = "Perfect score! Can you get it again?"
        else:
            note_txt = "Can you beat this score?"
        tk.Label(
            quiz_left,
            text=note_txt,
            bg="white",
            fg=DARK_RED,
            font=("Helvetica", 10),
            anchor="w",
            wraplength=180,
            justify="left",
        ).pack(anchor="w")

        # Right side with pie chart
        if total > 0:
            wrong = total - score
            quiz_right = tk.Frame(quiz_body, bg="white")
            quiz_right.pack(side="right", fill="both", expand=True)

            # Figure is object that contains pie chart, and FigureCanvasTkAgg
            # is the object that allows figure to be displayed in a Tkinter window
            fig = Figure(figsize=(2, 2), dpi=100)
            fig.patch.set_facecolor("white")  # Set background color of figure to white
            ax = fig.add_subplot(111)  # Lets you draw 2 pieces of circles

            # Only include slices that have value, so all correct
            # or all wrong answers doesn't draw an empty 0% slice
            slice_values, slice_colors = [], []
            if score > 0:
                slice_values.append(score)
                slice_colors.append("#008631")  # green
            if wrong > 0:
                slice_values.append(wrong)
                slice_colors.append(DARK_RED)  # red

            # Draw pie chart with slices, colors
            ax.pie(
                slice_values,  # Size of slices
                colors=slice_colors,
            )
            ax.set_aspect("equal")  # Equal aspect ratio to ensure circle drawn

            chart_canvas = FigureCanvasTkAgg(
                fig, master=quiz_right
            )  # Canvas for figure(pie chart)
            chart_canvas.draw()
            chart_canvas.get_tk_widget().pack(
                expand=True
            )  # Place canvas into right side of quiz card

    # Calendar section

    cal_body = make_card("Calendar", 1, 1, open_cmd=self.calendar_screen)
    today_str = date.today().strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT title, event_date, event_type FROM calendar_events "
        "WHERE user_id=? AND event_date=? ORDER BY id",
        (self.current_user_id, today_str),
    )
    todays_events = cursor.fetchall()
    if todays_events:
        # event title
        tk.Label(
            cal_body,
            text="Today",
            bg="white",
            fg=LIGHT_GREY,
            font=("Helvetica", 9, "bold"),
        ).pack(anchor="w")
        for ev_title, ev_date, ev_type in todays_events:
            # Use colour coding to make different event types easier for users to identify
            colour = TYPE_COLORS.get(ev_type, "white")
            row = tk.Frame(cal_body, bg=colour)
            row.pack(fill="x", pady=2)
            tk.Label(
                row,
                text=f"●  {ev_title}",
                bg=colour,
                fg="white",
                font=("Helvetica", 11),
                anchor="w",
            ).pack(side="left", padx=6, pady=4)
            tk.Label(
                row,
                text=ev_type,
                bg=colour,
                fg="white",
                font=("Helvetica", 8),
                anchor="e",
            ).pack(side="right", padx=6)
    else:
        cursor.execute(
            "SELECT title, event_date, event_type FROM calendar_events "
            "WHERE user_id=? AND event_date>? ORDER BY event_date ASC LIMIT 5",
            (self.current_user_id, today_str),
        )
        next_event = cursor.fetchone()
        if next_event:
            ev_title, ev_date, ev_type = next_event
            colour = TYPE_COLORS.get(ev_type, "white")
            tk.Label(
                cal_body,
                text="No events today. Next up:",
                bg="white",
                fg=DARK_RED,
                font=("Helvetica", 9),
            ).pack(anchor="w")
            row = tk.Frame(cal_body, bg=colour)
            row.pack(fill="x", pady=4)
            tk.Label(
                row,
                text=f"●  {ev_title}",
                bg=colour,
                fg="black",
                font=("Helvetica", 11, "bold"),
                anchor="w",
            ).pack(side="left", padx=6, pady=4)
            tk.Label(
                row,
                text=ev_date,
                bg=colour,
                fg="black",
                font=("Helvetica", 9),
                anchor="e",
            ).pack(side="right", padx=6)
        else:
            tk.Label(
                cal_body,
                text="No upcoming events.",
                bg="white",
                fg=GREY_BG,
                font=("Helvetica", 10),
            ).pack(pady=10)

    # Reminders section
    rem_body = make_card(
        "Reminders this month", 2, 0, colspan=2, open_cmd=self.reminders_screen
    )
    month_prefix = date.today().strftime("%Y-%m")
    cursor.execute(
        "SELECT rem_title, remind_at, fired FROM reminders "
        "WHERE user_id=? AND remind_at LIKE ? ORDER BY remind_at ASC LIMIT 5",
        (self.current_user_id, f"{month_prefix}-%"),
    )
    rem_rows = cursor.fetchall()
    if not rem_rows:
        tk.Label(
            rem_body,
            text="No reminders set for this month.",
            bg="white",
            fg=LIGHT_GREY,
            font=("Helvetica", 10),
        ).pack(pady=10)
    else:
        for rtitle, rat, fired in rem_rows:
            # Show a different icon depending on whether reminder has already been triggered
            icon = "✔" if fired else "○"
            cell = tk.Frame(rem_body, bg=GREY_BG, relief="solid", bd=1)
            cell.pack(fill="x", pady=2)
            tk.Label(
                cell,
                text=f"{icon}  {rtitle}",
                bg=GREY_BG,
                fg="black",
                font=("Helvetica", 10),
            ).pack(side="left", padx=8, pady=4)
            tk.Label(
                cell, text=rat, bg=GREY_BG, fg=LIGHT_GREY, font=("Helvetica", 9)
            ).pack(side="right", padx=8)


def open_settings_sidebar(self):
    """Shows a panel over the home screen with the user's name and a logout button."""
    panel = tk.Frame(self.root, bg="white", width=270, relief="solid", bd=1)
    # Sits on right side, over home screen no matter window size due to relx
    panel.place(relx=1.0, y=0, anchor="ne", relheight=1.0)
    panel.pack_propagate(False)

    close_lbl = tk.Label(
        panel,
        text="✕ Close",
        bg="white",
        fg=LIGHT_GREY,
        font=("Helvetica", 10),
        cursor="hand2",
    )
    close_lbl.pack(anchor="ne", padx=10, pady=10)
    close_lbl.bind("<Button-1>", lambda e: panel.destroy())

    profile_img = Image.open("images/profile.png")
    profile_img = profile_img.resize((100, 100))
    self.profile_img = ImageTk.PhotoImage(profile_img)

    tk.Label(panel, image=self.profile_img, bg="white", font=("Helvetica", 30)).pack(
        pady=(20, 4)
    )
    # Shows username of logged in user
    tk.Label(
        panel,
        text=self.current_username,
        bg="white",
        fg="black",
        font=("Helvetica", 14, "bold"),
    ).pack(pady=(0, 30))

    # Study streak with fire icon
    cursor = self.db.get_cursor()
    cursor.execute("SELECT streak FROM users WHERE id=?", (self.current_user_id,))
    streak_row = cursor.fetchone()
    streak_count = streak_row[0] if streak_row and streak_row[0] else 0

    fire_img = Image.open("images/fire.png")  # path to my image
    fire_img = fire_img.resize((24, 24))  # resize to fit in panel
    self.fire_icon = ImageTk.PhotoImage(
        fire_img
    )  # make image uasble by changing it to photoimage

    streak_frame = tk.Frame(panel, bg="white")
    streak_frame.pack(pady=(0, 30))
    tk.Label(streak_frame, image=self.fire_icon, bg="white").pack(
        side="left", padx=(0, 6)
    )
    tk.Label(
        streak_frame,
        text=streak_count,
        bg="white",
        fg=DARK_RED,
        font=("Helvetica", 13, "bold"),
    ).pack(side="left")

    def logout():
        """Logs user out and returns to login screen."""
        self.current_user_id = None
        self.current_username = None
        self.login_screen()

    logout_lbl = tk.Label(
        panel,
        text="Log Out",
        bg=DARK_RED,
        fg="white",
        font=("Helvetica", 12, "bold"),
        padx=14,
        pady=8,
        cursor="hand2",
    )
    logout_lbl.pack(pady=10)

    make_hover_background(logout_lbl, DARK_RED, RED_HOVER_COLOR, logout)
