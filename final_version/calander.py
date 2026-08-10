import tkinter as tk
from tkinter import messagebox
 
from constants import DARK_RED, NAVY_BLUE, GREY_BG, TYPE_COLORS, BLUE_HOVER_COLOR, LIGHT_GREY
from helpers import clear_screen, make_hover_background

def calendar_screen(self):
    """Creates the calendar screen where users can view and add events."""
    from datetime import datetime, date
    import calendar as cal
    
    # Clear the previous screen before displaying the calendar
    clear_screen(self.root)
    self.root.configure(bg="white")
    cursor = self.db.get_cursor()

    now = datetime.now()
    # dictionary to keep track of the current year
    # and month being displayed in the calendar
    state = {"year": now.year, "month": now.month} 
    header=tk.Frame(self.root,bg=DARK_RED)
    header.pack(fill="x")
    tk.Label(header, text="Calendar", font=("Helvetica", 20, "bold"),fg="white",bg=DARK_RED).pack(pady=10,side="left",padx=20)
    back_cal=tk.Label(header,text="Back",bg=NAVY_BLUE,fg="white",padx=14,pady=6)
    back_cal.pack(pady=5,side="right", padx=20)

    # Return the user to the home screen when back is clicked
    make_hover_background(back_cal,NAVY_BLUE,BLUE_HOVER_COLOR,self.home_screen)
    
    #Button to add events to calendar
    add_btn = tk.Label(header, text="+ Add Event", bg=DARK_RED, fg="white",
                        padx=14, pady=6, cursor="hand2",
                        highlightbackground="white")
    add_btn.pack(pady=5, side="right", padx=8)
    
    
    # Navigation bar to switch months
    nav = tk.Frame(self.root, bg="white")
    nav.pack()
    left_btn=tk.Label(nav, text="◀", bg="white", fg=DARK_RED,width="4", font=("Helvetica", 20), cursor="hand2")
    left_btn.pack(side="left", padx=10, pady=10)
    def prev_month(event=None):
        """ Moves to the previous month in the calendar."""
        # If January is reached, wrap back to December of the previous year
        if state["month"] == 1:
            state["month"] = 12
            state["year"] -= 1
        else:
            state["month"] -= 1
        # Refresh the calendar display after changing the month
        actual_calendar() 
    left_btn.bind("<Button-1>", prev_month)
    right_btn=tk.Label(nav, text="►", bg="white",width="2",fg=DARK_RED, font=("Helvetica", 20), cursor="hand2")
    right_btn.pack(side="right", padx=10, pady=10)
    def next_month(event=None):
        """ Moves to the next month in the calendar."""
        # If December is reached, wrap to January of the next year
        if state["month"] == 12:
            state["month"] = 1
            state["year"] += 1
        else:
            state["month"] += 1
        actual_calendar()

    right_btn.bind("<Button-1>", next_month)     
    # Displays the current month and year   
    month_lbl = tk.Label(nav, text="", bg="white",fg=DARK_RED,font=("Helvetica", 26, "bold"), width=20)
    month_lbl.pack(side="left")
    
    
    
    
    #The main area of the calendar
    main = tk.Frame(self.root, bg=GREY_BG)
    #Footer to show event types
    footer = tk.Frame(self.root, bg="white")

    main.pack(fill="both", expand=True)
    footer.pack(fill="x", pady=(5, 10))

    #Calendar grid/frame
    cal_frame = tk.Frame(main, bg=GREY_BG)
    cal_frame.pack(fill="both", expand=True)

    # make every column/row stretch evenly so the boxes fill the screen
    for col in range(7):
        cal_frame.grid_columnconfigure(col, weight=1, uniform="cal_col")
    for row in range(1, 7):
        cal_frame.grid_rowconfigure(row, weight=1, uniform="cal_row")


    #event=none so function can be called from button
    def open_add_event_popup(event=None):
        """Popup window opens when user clicks add button for an event to be added to the calender"""
        add_event_popup = tk.Toplevel(self.root)
        add_event_popup.title("Add Event")
        add_event_popup.configure(bg=GREY_BG)
        add_event_popup.resizable(False, False)
        #Child window hence will be on top of main window and be resized with it
        add_event_popup.transient(self.root)
        # Makes window modal so that users can't interact with the main window while this is open
        add_event_popup.grab_set()

        form = tk.Frame(add_event_popup, bg=GREY_BG, padx=14, pady=14)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Title", bg=GREY_BG, font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", padx=4, pady=4)
        event_name = tk.Entry(form, width=24, font=("Helvetica", 10))
        event_name.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(form, text="Date (YYYY-MM-DD)", bg=GREY_BG, font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", padx=4, pady=4)
        event_date = tk.Entry(form, width=24, font=("Helvetica", 10))
        event_date.grid(row=1, column=1, padx=4, pady=4)
        event_date.insert(0, f"{state['year']:04d}-{state['month']:02d}-{now.day:02d}")

        tk.Label(form, text="Type", bg=GREY_BG, font=("Helvetica", 10)).grid(row=2, column=0, sticky="w", padx=4, pady=4)
        type_var = tk.StringVar(value="exam")
        tk.OptionMenu(form, type_var, "exam", "assignment", "study", "other").grid(row=2, column=1, sticky="w", padx=4, pady=4)

        def add_event():
            """Add events to the calendar"""
            name = event_name.get()
            ev_date = event_date.get()
            ev_type = type_var.get()
            try:
                #Validate date ensure its in correct format
                datetime.strptime(ev_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Bad date", "Use Year-Month-Day!")
                return

            if not name:
                messagebox.showwarning("No title", "Enter an event title")
                return
            cursor.execute(
                "INSERT INTO calendar_events (user_id, title, event_date, event_type) VALUES (?,?,?,?)",
                (self.current_user_id, name, ev_date, ev_type))
            self.db.commit()
            add_event_popup.destroy()
            actual_calendar()

        tk.Button(form, text="Add Event", command=add_event, font=("Helvetica", 10)).grid(row=3, column=0, columnspan=2, pady=(10, 0))

    add_btn.bind("<Button-1>", open_add_event_popup)

            
    def actual_calendar():
        """Display the calendar with numbers in boxes and days on top"""
        for widgets in cal_frame.winfo_children():
            widgets.destroy()
        # Get the current year and month from the state dictionary
        y, m = state["year"], state["month"] 
        month_lbl.config(text=datetime(y, m, 1).strftime("%B %Y"))

        #Get events for current month from specific user and strore them in dict
        cursor.execute(
            "SELECT title, event_date, event_type FROM calendar_events WHERE user_id=? AND event_date LIKE ?",
            (self.current_user_id, f"{y:04d}-{m:02d}-%"))
        #Map of days-events for month(day is key and value is list of title & type)
        event_map={}
        for ev_title, ed, et in cursor.fetchall():
            day=int(ed[8:])
            event_map.setdefault(day, []).append((ev_title, et))

        for col, dn in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            tk.Label(cal_frame, text=dn, bg="white", fg="black",
                     font=("Helvetica", 11, "bold")).grid(row=0, column=col, sticky="nsew")
        #Get first weekday of month and number of days in month
        first_wd=date(y, m, 1).weekday()
        days_in=cal.monthrange(y, m)[1]
        today=now.day if (y == now.year and m == now.month) else -1

        #look thorugh each day of month and create cell
        r, c = 1, first_wd
        for d in range(1, days_in + 1):
            #Get events for current day
            evts=event_map.get(d, [])
            if evts:
                bg = TYPE_COLORS.get(evts[0][1], "white")
            else:
                bg = "white"

            cell=tk.Frame(cal_frame, bg=bg, relief="solid", bd=1)
            cell.grid(row=r, column=c, sticky="nsew", padx=0, pady=0)
            cell.grid_propagate(False)

            day_lbl=tk.Label(cell, text=str(d), bg=bg, fg=DARK_RED if d == today else "black",
                                font=("Helvetica", 12, "bold" if d == today else "normal"))
            day_lbl.pack(anchor="nw", padx=4, pady=2)

            max_shown =2
            for ev_title, ev_type in evts[:max_shown]:
                #Get colour for event, grey if not used
                swatch_color = TYPE_COLORS.get(ev_type, "#cccccc")
                ev_row = tk.Frame(cell, bg=bg)
                ev_row.pack(fill="x", padx=3, pady=1, anchor="nw")
                tk.Label(ev_row, text="●", bg=bg, fg=swatch_color, font=("Helvetica", 8)).pack(side="left")
                tk.Label(ev_row, text=ev_title, bg=bg, fg="#222222",
                         font=("Helvetica", 8), anchor="w").pack(side="left", padx=(2, 0))
            if len(evts) > max_shown:
                #If more events than can be shown(3), show + with number of evetns.
                tk.Label(cell, text=f"+{len(evts) - max_shown} more", bg=bg, fg=LIGHT_GREY,
                         font=("Helvetica", 8)).pack(anchor="nw", padx=4)
            #Move to next column and if end of week(c=7), move to next row.
            c += 1
            if c == 7:
                c, r = 0, r + 1  
                
    #Create a footer showing events and their colours.
    for event_type, colour in TYPE_COLORS.items():
        item = tk.Frame(footer, bg="white")
        item.pack(side="left", padx=12)

        tk.Label(item,text="●",fg=colour,bg="white",
                    font=("Helvetica", 15)).pack(side="left")

        tk.Label(item,text=event_type.capitalize(),bg="white",fg="#555555",
        font=("Helvetica", 10)).pack(side="left", padx=(2, 0))        
                        
    actual_calendar()