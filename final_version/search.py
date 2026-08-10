import tkinter as tk

from constants import DARK_RED, NAVY_BLUE, GREY_BG , LIGHT_GREY
from helpers import make_hover_foreground


def open_search_panel(self):
    """A side panel is placed on top with a search bar so that the user
    can search throughout the whole app"""
    cursor = self.db.get_cursor()

    panel = tk.Frame(self.root, bg="white", width=340, height=700,
                        relief="solid", bd=1)
    # Sits on the right side of the dashboard(on top of it)
    panel.place(x=760, y=0)
    panel.pack_propagate(False)
    
    close_lbl = tk.Label(panel, text="✕ Close", bg="white", fg=LIGHT_GREY,
                            font=("Helvetica", 10), cursor="hand2")
    close_lbl.pack(anchor="ne", padx=10, pady=10)
    #Close the panel(destroy the widget) once the close label is pressed
    close_lbl.bind("<Button-1>", lambda e: panel.destroy())
    
    tk.Label(panel, text="Search", bg="white", fg="black",
                font=("Helvetica", 14, "bold")).pack(pady=(0, 10))
    
    search_entry = tk.Entry(panel, font=("Helvetica", 12), relief="solid", bd=1)
    search_entry.pack(fill="x", padx=14, pady=(0, 10), ipady=6)
    #Automatically moves the focus of the cursor to the entry widget so users
    #don't have to press on it
    search_entry.focus_set()
    
    # Scrollable area so results can't overflow the panel
    results_canvas = tk.Canvas(panel, bg="white", highlightthickness=0)
    results_scroll = tk.Scrollbar(panel, orient="vertical", command=results_canvas.yview)
    results_frame = tk.Frame(results_canvas, bg="white")
    # Whenever the size of results_frame changes it will opdate.
    # Update the canvas scrollable area so it includes everything inside results_frame.
    results_frame.bind("<Configure>",lambda e: results_canvas.configure(scrollregion=results_canvas.bbox("all")))
    #Results to the top left corner
    results_canvas.create_window((0, 0), window=results_frame, anchor="nw", width=300)
    results_canvas.configure(yscrollcommand=results_scroll.set)
    
    results_canvas.pack(side="left", fill="both", expand=True, padx=(14, 0))
    results_scroll.pack(side="right", fill="y", padx=(0, 4))
    
    def make_result_row(title_text, type_label, open_cmd):
        """Add a row to the results list with the type of feature it is to the left"""
        row = tk.Frame(results_frame, bg="white")
        row.pack(fill="x", pady=4)
        
        title_lbl = tk.Label(row, text=title_text, bg="white", fg="black",font=("Helvetica", 11),
                             anchor="w", cursor="hand2",wraplength=190, justify="left")
        title_lbl.pack(side="left", padx=(0, 6))

        type_lbl = tk.Label(row, text=type_label, bg="white", fg=LIGHT_GREY,
                                font=("Helvetica", 8), anchor="e")
        type_lbl.pack(side="right")
        
        make_hover_foreground(title_lbl, "black", NAVY_BLUE, open_cmd)
        
    def run_search(event=None):
        """Displays a new list of items with every letter/symbol typed"""
        for widget in results_frame.winfo_children():
            widget.destroy()

        # Check if the search box is empty.
        term = search_entry.get().strip()
        if not term:
            return
        #Add % wildcards before and after the search term so that if the phrase appears
        #in a larger word, it is still shown
        like_term = f"%{term}%"
    
        #Match the title or the body text in notes
        cursor.execute(
            "SELECT id, title FROM notes WHERE user_id=? "
            "AND (title LIKE ? OR body LIKE ?) ORDER BY id DESC",
            (self.current_user_id, like_term, like_term))
        for nid, ntitle in cursor.fetchall():
            make_result_row(
                ntitle, "notes",
                lambda i=nid, t=ntitle: (panel.destroy(), self.note_edit_screen(i, t)))

        # Match the deck name in flashcards
        cursor.execute(
            "SELECT id, name FROM decks WHERE user_id=? AND name LIKE ? ORDER BY id DESC",
            (self.current_user_id, like_term))
        for did, dname in cursor.fetchall():
            make_result_row(
                dname, "flashcards",
                lambda i=did, t=dname: (panel.destroy(), self.study_deck(i, t)))
            
        # Match the front or back text and open deck in study mode when pressed
        cursor.execute(
            "SELECT decks.id, decks.name, flashcards.front FROM flashcards "
            "JOIN decks ON decks.id = flashcards.deck_id "
            "WHERE flashcards.user_id=? AND (flashcards.front LIKE ? OR flashcards.back LIKE ?) "
            "ORDER BY flashcards.id DESC",
            (self.current_user_id, like_term, like_term))
        for did, dname, front in cursor.fetchall():
            make_result_row(
                front, "flashcards",
                lambda i=did, t=dname: (panel.destroy(), self.study_deck(i, t)))

        # Match the quiz title
        cursor.execute(
            "SELECT id, title FROM quizzes WHERE user_id=? AND title LIKE ? ORDER BY id DESC",
            (self.current_user_id, like_term))
        for qid, qtitle in cursor.fetchall():
            make_result_row(
                qtitle, "quiz",
                lambda i=qid, t=qtitle: (panel.destroy(), self.take_quiz(i, t)))

        # Match the event title
        cursor.execute(
            "SELECT title, event_date FROM calendar_events "
            "WHERE user_id=? AND title LIKE ? ORDER BY event_date ASC",
            (self.current_user_id, like_term))
        for ev_title, ev_date in cursor.fetchall():
            make_result_row(
                f"{ev_title} ({ev_date})", "event",
                lambda: (panel.destroy(), self.calendar_screen()))

        # Match the reminder title
        cursor.execute(
            "SELECT rem_title, remind_at FROM reminders "
            "WHERE user_id=? AND rem_title LIKE ? ORDER BY remind_at ASC",
            (self.current_user_id, like_term))
        for rtitle, rat in cursor.fetchall():
            make_result_row(
                f"{rtitle} ({rat})", "reminder",
                lambda: (panel.destroy(), self.reminders_screen()))
        #if not results are found display a message
        if not results_frame.winfo_children():
            tk.Label(results_frame, text="No results found.", bg="white",
                    fg=LIGHT_GREY, font=("Helvetica", 10)).pack(pady=20)

    search_entry.bind("<KeyRelease>", run_search)

