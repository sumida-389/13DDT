import tkinter as tk
from tkinter import messagebox

from constants import DARK_RED, NAVY_BLUE, BLUE_HOVER_COLOR, LIGHT_GREY
from helpers import clear_screen, make_hover_background


def reminders_screen(self):
    from datetime import datetime

    # Clear the previous screen before displaying the reminders
    clear_screen(self.root)
    self.root.configure(bg="white")

    # Create a database cursor to read and update reminder records
    cursor = self.db.get_cursor()

    header = tk.Frame(self.root, bg=DARK_RED)
    header.pack(fill="x")
    tk.Label(
        header,
        text="Reminders",
        font=("Helvetica", 20, "bold"),
        fg="white",
        bg=DARK_RED,
    ).pack(pady=10, side="left", padx=20)

    # Group all reminder input fields together to create an organised form
    form = tk.Frame(self.root, bg="white")
    form.pack(fill="x", padx=20, pady=5)

    # Entry to enter the reminders title
    tk.Label(form, text="Title:", bg="white").grid(row=0, column=0, sticky="w", pady=4)
    re_title = tk.Entry(form, width=40)
    re_title.grid(row=0, column=1, padx=5, sticky="w")
    # Entry to enter the reminders date
    tk.Label(form, text="Date:", bg="white").grid(row=1, column=0, sticky="w", pady=4)
    tk.Label(
        form, text="(YYYY-MM-DD)", bg="white", fg=LIGHT_GREY, font=("Helvetica", 8)
    ).grid(row=2, column=0, sticky="w")
    re_date = tk.Entry(form, width=20)
    re_date.grid(row=1, column=1, padx=5, sticky="w")
    # Entry to enter the reminders time
    tk.Label(form, text="Time:", bg="white").grid(row=3, column=0, sticky="w", pady=4)
    tk.Label(
        form, text="(24hr HH:MM)", bg="white", fg=LIGHT_GREY, font=("Helvetica", 8)
    ).grid(row=4, column=0, sticky="w")
    re_time = tk.Entry(form, width=20)
    re_time.grid(row=3, column=1, padx=5, sticky="w")

    # Display validation messages
    status = tk.Label(
        self.root, text="", bg="white", fg=DARK_RED, font=("Helvetica", 10)
    )
    status.pack()

    footer = tk.Frame(self.root, bg="white")
    footer.pack(side="bottom", fill="x")
    back_rem = tk.Label(
        footer,
        text="Back",
        fg="white",
        bg=NAVY_BLUE,
        relief="flat",
        font=("Helvetica", 11),
        padx=14,
        pady=6,
    )
    back_rem.pack(pady=5, padx=10, side="right")

    # Apply hover effects and return the user to the home screen when clicked
    make_hover_background(back_rem, NAVY_BLUE, BLUE_HOVER_COLOR, self.home_screen)

    def add_reminder():
        """Add a reminder function and save it to the database"""
        # Remove extra spaces to prevent invalid reminder titles from being stored
        rem_title = re_title.get().strip()
        rem_date = re_date.get().strip()
        rem_time = re_time.get().strip()

        # If the reminder title is empty, show an error message
        if not rem_title:
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
        # Format the reminder date and time for storage in the database
        rat = remind_dt.strftime("%Y-%m-%d %H:%M")
        cursor.execute(
            "INSERT INTO reminders (user_id, rem_title, remind_at) VALUES (?,?,?)",
            (self.current_user_id, rem_title, rat),
        )
        self.db.commit()
        # Clear the title entry box after reminder is entered
        re_title.delete(0, "end")
        messagebox.showinfo(
            "Reminder Set!",
            f"Reminder set for {rat}.\nThe app must be open to receive notifications.",
        )
        load_reminders()

    set_btn = tk.Label(
        self.root, text="Set Reminder", padx=10, pady=5, bg=NAVY_BLUE, fg="white"
    )
    set_btn.pack(pady=6)

    make_hover_background(set_btn, NAVY_BLUE, BLUE_HOVER_COLOR, add_reminder)

    # make a container to hold both the canvas and the scrollbar
    container = tk.Frame(self.root, bg="white")
    container.pack(fill="both", expand=True, padx=20, pady=5)

    # Make a canvas that will display the scrollable reminder list
    list_canvas = tk.Canvas(container, bg="white", highlightthickness=0)

    # Create a vertical scrollbar and link it to the canvas
    scrollbar = tk.Scrollbar(container, orient="vertical", command=list_canvas.yview)

    # Create a frame inside the canvas to put all reminder cards
    list_frame = tk.Frame(list_canvas, bg="white")

    # store ID so it can be resized
    window = list_canvas.create_window((0, 0), window=list_frame, anchor="nw")

    # Update the scrollable area whenever the reminder list changes size
    list_frame.bind(
        "<Configure>",
        lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")),
    )

    # Make the inner frame always match the width of the canvas
    def resize_frame(event):
        """Resizes the inside of the canvas"""
        list_canvas.itemconfig(window, width=event.width)

    list_canvas.bind("<Configure>", resize_frame)

    # Connect the scrollbar to the canvas
    list_canvas.configure(yscrollcommand=scrollbar.set)

    # Show the canvas and scrollbar
    list_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def load_reminders():
        """Loads the reminders from the database and displays them in the list."""

        # Remove the previous reminder list before rebuilding it with updated information
        for widegts in list_frame.winfo_children():
            widegts.destroy()
        now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute(
            "SELECT id, rem_title, remind_at, fired FROM reminders WHERE user_id=? ORDER BY fired ASC, remind_at ASC",
            (self.current_user_id,),
        )
        rows = cursor.fetchall()
        if not rows:
            tk.Label(
                list_frame, text="No reminders yet!", bg="white", fg=LIGHT_GREY
            ).pack(pady=10)
            return
        for reminder_id, reminder_title, reminder_at, fired in rows:
            # See which reminders are overdue so it can be visually highlighted
            overdue = reminder_at <= now_time and not fired
            bg = "#ffebee" if overdue else ("#eeeeee" if fired else "white")
            row = tk.Frame(list_frame, bg=bg, relief="solid", bd=1)
            row.pack(fill="x", pady=3)
            # Display a different icon to show whether the reminder is completed, overdue, or still pending
            icon = "✔" if fired else ("⚠" if overdue else "○")
            tk.Label(row, text=icon, bg=bg, font=("Helvetica", 13)).pack(
                side="left", padx=8, pady=6
            )
            tk.Label(
                row,
                text=f"{reminder_title}  —  {reminder_at}",
                bg=bg,
                font=("Helvetica", 11),
            ).pack(side="left", padx=4)
            tk.Button(
                row,
                text="Delete",
                fg=DARK_RED,
                bg=bg,
                relief="flat",
                command=lambda i=reminder_id: [
                    cursor.execute("DELETE FROM reminders WHERE id=?", (i,)),
                    self.db.commit(),
                    load_reminders(),
                ],
            ).pack(side="right", padx=8)

    load_reminders()
