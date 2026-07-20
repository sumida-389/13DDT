import sqlite3
import tkinter as tk
from tkinter import messagebox
 
from constants_final import DARK_RED, NAVY_BLUE, GREY_BG, BLUE_HOVER_COLOR
from helpers_final import clear_screen, make_hover_background

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