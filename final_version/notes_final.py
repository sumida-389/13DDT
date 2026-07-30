import sqlite3
import tkinter as tk
from tkinter import messagebox
 
from constants_final import DARK_RED, NAVY_BLUE, GREY_BG, BLUE_HOVER_COLOR
from helpers_final import clear_screen, make_hover_background

def notes_screen(self):
    """Creates the notes screen where users can see, create, and delete notes."""
    
    # Remove the previous screen so only the notes interface is displayed
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

    # Display validation messages without opening pop up windows
    status_lbl = tk.Label(self.root, text="", bg=GREY_BG, fg=DARK_RED,
                            font=("Helvetica", 10))
    status_lbl.pack()

    footer= tk.Frame(self.root, bg=GREY_BG)
    footer.pack(fill="x", side="bottom")
    back_notes=tk.Label(footer, text="Back", bg=NAVY_BLUE, fg="white",padx=14, pady=6,)
    back_notes.pack(side="right", padx=25, pady=15)
    
    # Apply hover effects and allow the Back label to return to the home screen
    make_hover_background(back_notes,NAVY_BLUE,BLUE_HOVER_COLOR,self.home_screen)
    
    def create_section():
        """Creates a new note in the database."""
        
        # Remove leading and trailing spaces so users cannot create titles using only whitespace
        title = new_title_entry.get().strip()
        try:
            cursor.execute(
                "INSERT INTO notes (user_id, title, body) VALUES (?, ?, ?)",
                (self.current_user_id, title, "")
            )
            # save to database
            self.db.commit()
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

    container = tk.Frame(self.root, bg=GREY_BG)
    container.pack(fill="both", expand=True, padx=20, pady=10)

    list_canvas = tk.Canvas(container, bg=GREY_BG, highlightthickness=0)
    # Create a vertical scrollbar and link to canvas
    scrollbar = tk.Scrollbar(container, orient="vertical", command=list_canvas.yview)

    inner = tk.Frame(list_canvas, bg=GREY_BG)

    window = list_canvas.create_window((0, 0), window=inner, anchor="nw")

    # Whenever the size of the inner frame changes, chnage the canvas
    # scroll region so the scrollbar knows how far it can scroll
    inner.bind("<Configure>",lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))

    def resize_inner(event):
        """ Resizes the inside of the canvas"""
        list_canvas.itemconfig(window, width=event.width)

    list_canvas.bind("<Configure>", resize_inner)

    list_canvas.configure(yscrollcommand=scrollbar.set)

    list_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    

    def load_sections():
        """Loads the notes from the database and displays them in the list."""
        for widgets in inner.winfo_children():
            widgets.destroy()
            
        # Retrieve every note belonging to the currently logged-in user
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
                    #reload the list after deletion
                    load_sections() 

            # Allow users to open a note by clicking anywhere on the note card
            note_card.bind("<Button-1>", lambda e, f=open_section: f())
            left.bind("<Button-1>", lambda e, f=open_section: f())

            btn_frame = tk.Frame(note_card, bg=GREY_BG)
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
    # get a cursor to the database so we can read and write the note
    cursor = self.db.get_cursor() 

    header = tk.Frame(self.root, bg=DARK_RED)
    header.pack(fill="x")

    back_lbl = tk.Label(header, text="◄", bg=DARK_RED, fg="white",font=("Helvetica",20), cursor="hand2")
    back_lbl.pack(side="left", padx=(15, 8), pady=12)
    back_lbl.bind("<Button-1>", lambda e: self.notes_screen())

    header_lbl = tk.Label(header, text=note_title, bg=DARK_RED, fg="white",
                        font=("Helvetica", 16, "bold"))
    header_lbl.pack(side="left", pady=12)

    #frame to hold the text widget
    text_frame = tk.Frame(self.root, bg=GREY_BG) 
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
        # Read the complete content of the text without including extra newline character
        new_body = notes_text.get("1.0", "end-1c")
        # Update only the edited note while leaving all other notes unchanged
        cursor.execute(
            "UPDATE notes SET body=? WHERE id=?",
            (new_body, note_id)
        )
        self.db.commit()
        #Messagebox to confirm that the note has been saved
        messagebox.showinfo("Saved", "Your changes have been saved.")

    save_lbl=tk.Label(save_bar, text="Save", bg=NAVY_BLUE, fg="white",
                relief="flat", font=("Helvetica", 11),padx=14, pady=6)
    save_lbl.pack(side="right", padx=14, pady=8)
    save_lbl.bind("<Button-1>", lambda e: save_note())
    make_hover_background(save_lbl,NAVY_BLUE,BLUE_HOVER_COLOR,save_note)