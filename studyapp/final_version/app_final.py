

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