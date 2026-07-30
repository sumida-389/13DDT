import tkinter as tk
 
from constants_final import DARK_RED, GREY_BG
from databasesetup_final import DatabaseSetup

from login_final import login_screen, register_screen
from home_final import home_screen, open_settings_sidebar
from notes_final import notes_screen, note_edit_screen
from flashcards_final import flashcards_screen, deck_edit_screen, study_deck
from quiz_final import quiz_screen, quiz_edit_screen, take_quiz
from calendar_final import calendar_screen
from reminders_final import reminders_screen
from search_final import open_search_panel


class AppFace:
    def __init__(self,root):
        """Sets up the database and window"""
        self.root = root
        self.root.title("Focalize")
        self.root.geometry("1100x700")
        # no one logged in yet
        self.current_user_id = None 
        # Store the username after login so it can be displayed
        self.current_username = None
        self.left_panel("testing bigtxt", "testing small text")
        # create an object of the database setup class
        self.db = DatabaseSetup() 
        # create the tables in the database if they don't exist
        self.db.create_tables() 
        self.login_screen()

        
    def left_panel(self,head,subtext):
        """`Creates the left panel with a heading and subtext."""
        
        # Create a panel to have consistent layout on login/registeration screens
        left_frame = tk.Frame(self.root, bg=DARK_RED, width=400, height=400)
        left_frame.pack(side="left", fill="y")
        # Prevent the frame from shrinking to fit its contents so the layout remains consistent
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
        # Display placeholder text to show users where to enter password
        user_pass.insert(0, placeholder)
        user_pass.pack(fill="x", ipady=8)
 
        underline = tk.Frame(text_frame, bg="#dddddd", height=1)
        underline.pack(fill="x")

        def on_click_field(event):
            """When the user clicks on the field, it will clear the placeholder text and 
            change the text color to black. If it's a password field,
            it will also hide the input with dots."""
            if user_pass.get() == placeholder:
                user_pass.delete(0, "end")
                user_pass.config(fg="#111111")
                if is_password:
                    # hide password with dots
                    user_pass.config(show="•")     
            underline.config(bg="#2A2AE1")
        def unclick_field(event):
            """When the user clicks away from the field, if it's empty it will
            put the placeholder text back and change the text color to gray"""
            if user_pass.get() == "":
                user_pass.config(fg="#aaaaaa", show="")
                # put placeholder back
                user_pass.insert(0, placeholder)   
            underline.config(bg=GREY_BG) 
        # When the user clicks on the field, it will clear the placeholder text and change the text color to black.
        # If it's a password field, it will also hide the input with dots.
        user_pass.bind("<FocusIn>",  on_click_field) 
        # When the user clicks away from the field, if it's
        # empty it will put the placeholder text back and change the text color to gray. 
        # It will also show the input if it's a password field.
        user_pass.bind("<FocusOut>", unclick_field) 
        # Return the completed entry widget so it can be used by other screens
        return user_pass
    
    # Attach screen functions from other modules to the AppFace class, so they can act like class methods
    login_screen = login_screen
    register_screen = register_screen
    home_screen = home_screen
    open_settings_sidebar = open_settings_sidebar
    notes_screen = notes_screen
    note_edit_screen = note_edit_screen
    flashcards_screen = flashcards_screen
    deck_edit_screen = deck_edit_screen
    study_deck = study_deck
    quiz_screen = quiz_screen
    quiz_edit_screen = quiz_edit_screen
    take_quiz = take_quiz
    calendar_screen = calendar_screen
    reminders_screen = reminders_screen 
    open_search_panel = open_search_panel