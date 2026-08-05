import sqlite3
import tkinter as tk
from tkinter import messagebox
import json
from constants_final import DARK_RED, NAVY_BLUE, GREY_BG, BLUE_HOVER_COLOR, LIGHT_GREY
from helpers_final import clear_screen, make_hover_background


# Colours available for the highlight tool
HIGHLIGHT_COLORS = {
    "Yellow": "#fff59d",
    "Green":  "#c8e6c9",
    "Pink":   "#f8bbd0",
    "Blue":   "#bbdefb",
}
#The way the text was formatted(colout,boldness eg.) is stored in constant
FORMAT_TAGS = ["heading", "bold"] + [f"highlight_{name}" for name in HIGHLIGHT_COLORS]

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
    
    make_hover_background(back_notes,NAVY_BLUE,BLUE_HOVER_COLOR,self.home_screen)
    
    def create_section():
        """Creates a new note in the database."""
        
        # Remove leading and trailing spaces so users cannot create titles using only whitespace
        title = new_title_entry.get().strip()
        if title == "":
            status_lbl.config(text="Please enter a title.")
            return
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
                        bg=GREY_BG, fg=LIGHT_GREY,
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
    
    # Formatting toolbar, select text and click button
    toolbar = tk.Frame(self.root, bg="white")
    toolbar.pack(fill="x")

    #Make the bar at the top
    def make_toolbar_btn(widg, text, command):
        btn = tk.Label(widg, text=text, bg="white", fg=NAVY_BLUE,
                       font=("Helvetica", 11, "bold"), cursor="hand2",
                       relief="flat", bd=1, padx=10, pady=5)
        btn.pack(side="left", padx=(10, 0), pady=8)
        make_hover_background(btn, "white", "#e8e8f5", command)
        return btn


    #frame to hold the text widget
    text_frame = tk.Frame(self.root, bg=GREY_BG) 
    text_frame.pack(fill="both", expand=True)

    notes_text = tk.Text(text_frame, wrap="word", font=("Helvetica", 13),
                            relief="flat", bd=0, padx=20, pady=16)
    notes_text.pack(side="left", fill="both", expand=True)

    #Describe how each formatting tag changes the text
    notes_text.tag_configure("heading", font=("Helvetica", 20, "bold"))
    notes_text.tag_configure("bold", font=("Helvetica", 13, "bold"))
    for colour_name, colour_val in HIGHLIGHT_COLORS.items():
        notes_text.tag_configure(f"highlight_{colour_name}", background=colour_val)

    def toggle_tag(tag_name):
        """Adds the tag to the current selection, or removes it if the
        seected text already has it."""
        try:
            # Get the start and position of the selected text
            start, end = notes_text.index("sel.first"), notes_text.index("sel.last")
        # If no text is selected, Tkinter raises a TclError
        except tk.TclError:
            # Show a popup telling the user to select some text first
            messagebox.showinfo("Select text", "Highlight some text first, then click this button.")
            return
        if tag_name in notes_text.tag_names("sel.first"):
            notes_text.tag_remove(tag_name, start, end)
        else:
            notes_text.tag_add(tag_name, start, end)
    
    def add_bullet():
        """Adds a bullet point to the start of the current line/s"""
        try:
            start_line = int(notes_text.index("sel.first").split(".")[0])
            end_line = int(notes_text.index("sel.last").split(".")[0])
        #If no text selected, add dot on that line
        except tk.TclError:
            start_line = end_line = int(notes_text.index("insert").split(".")[0])
        for line in range(start_line, end_line + 1):
            line_start = f"{line}.0"
            line_text = notes_text.get(line_start, f"{line}.end")
            #If the selected text already has a dot at the beggineing, dont add one
            if not line_text.startswith("• "):
                notes_text.insert(line_start, "• ")




    save_bar = tk.Frame(self.root, bg=GREY_BG)
    save_bar.pack(fill="x")
    save_status = tk.Label(save_bar, text="", bg=GREY_BG, fg="green",
                            font=("Helvetica", 10))
    save_status.pack(side="left", padx=14)
    
    
    def apply_highlight(colour_name):
        """Applies (or remove) a highlight colour on the current selection."""
        try:
            start, end = notes_text.index("sel.first"), notes_text.index("sel.last")
        except tk.TclError:
            messagebox.showinfo("Select text", "Select some text first!")
            return
        # Only one highlight colour applies at a time, so clear the others first
        for name in HIGHLIGHT_COLORS:
            notes_text.tag_remove(f"highlight_{name}", start, end)
        if colour_name:
            notes_text.tag_add(f"highlight_{colour_name}", start, end)

    make_toolbar_btn(toolbar, "Heading", lambda: toggle_tag("heading"))
    make_toolbar_btn(toolbar, "Bold", lambda: toggle_tag("bold"))
    make_toolbar_btn(toolbar, "⋮", add_bullet)
    
    
    
    
    
    highlight_btn = tk.Menubutton(toolbar, text="Highlight", bg="white", fg=NAVY_BLUE,
                                    font=("Helvetica", 11, "bold"), relief="solid", bd=1,
                                    padx=10, pady=5, cursor="hand2")
    highlight_menu = tk.Menu(highlight_btn, tearoff=0) ## Create the actual popup menu object that drops down when clicked
    # Link the popup menu to the button
    highlight_btn.configure(menu=highlight_menu)
    highlight_btn.pack(side="left", padx=(10, 0), pady=8)
    # Loop through each color name and its color value in the dictionary
    for colour_name, colour_val in HIGHLIGHT_COLORS.items():
        highlight_menu.add_command(label=colour_name, background=colour_val,
                                    command=lambda c=colour_name: apply_highlight(c))
    # Add a horizontal dividing line across the menu to separate colors from the reset option
    highlight_menu.add_separator()
    highlight_menu.add_command(label="Remove Highlight", command=lambda: apply_highlight(None))
    
    # Load the  note. Note stored as json: {"text": ..., "tags": [...]}
    # so formatting saves and is being saved and reopened. 
    cursor.execute("SELECT body FROM notes WHERE id=?", (note_id,))
    existing = cursor.fetchone()
    # Check if note was found and that its not empty
    if existing and existing[0]:
        raw_body = existing[0]
        try:
            # Convert the JSON string into a Python dictionary
            data = json.loads(raw_body)
            #Put text in text widget
            notes_text.insert("1.0", data.get("text", ""))
             # Loop through each saved formatting tag
            for entry in data.get("tags", []):
                notes_text.tag_add(entry["tag"], entry["start"], entry["end"])
        # If the notes format has an error, handle it silently
        except (json.JSONDecodeError, TypeError):
            #Insert contents without formatting
            notes_text.insert("1.0", raw_body)


    save_bar = tk.Frame(self.root, bg=GREY_BG)
    save_bar.pack(fill="x")
    save_status = tk.Label(save_bar, text="", bg=GREY_BG, fg="green",
                            font=("Helvetica", 10))
    save_status.pack(side="left", padx=14)
    
    
    
    
    def save_note():
        """Saves the current note to the database with formatt."""
        # Read the complete content of the text without including newline character
        text_content = notes_text.get("1.0", "end-1c")
        
        # Record formatted range so it can be reapplied when the note is opened
        #Stores in format {"tag": "bold","start": "1.0","end": "1.7"}
        tag_ranges = []
        for tag in FORMAT_TAGS:
            ranges = notes_text.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                tag_ranges.append({
                    "tag": tag,
                    "start": str(ranges[i]),
                    "end": str(ranges[i + 1]),
                })
        #converts the note and all of its formatting into a JSON string so it can be stored in the database
        new_body = json.dumps({"text": text_content, "tags": tag_ranges})


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