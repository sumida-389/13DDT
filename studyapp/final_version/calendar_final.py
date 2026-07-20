import tkinter as tk
from tkinter import messagebox
 
from constants_final import DARK_RED, NAVY_BLUE, GREY_BG, TYPE_COLORS, BLUE_HOVER_COLOR
from helpers_final import clear_screen, make_hover_background

def calendar_screen(self):
    """Creates the calendar screen where users can view and add events."""
    from datetime import datetime, date
    import calendar as cal

    clear_screen(self.root)
    self.root.configure(bg="white")
    cursor = self.db.get_cursor()

    now = datetime.now()
    state = {"year": now.year, "month": now.month} # dictionary to keep track of the current year and month being displayed in the calendar
    header=tk.Frame(self.root,bg=DARK_RED)
    header.pack(fill="x")
    tk.Label(header, text="Calendar", font=("Helvetica", 20, "bold"),fg="white",bg=DARK_RED).pack(pady=10,side="left",padx=20)
    back_cal=tk.Label(header,text="Back",bg=NAVY_BLUE,fg="white",padx=14,pady=6)
    back_cal.pack(pady=5,side="right", padx=20)

    make_hover_background(back_cal,NAVY_BLUE,BLUE_HOVER_COLOR,self.home_screen)

    # Navigation bar to switch months
    nav = tk.Frame(self.root, bg="white")
    nav.pack()
    left_btn=tk.Label(nav, text="◄", bg="white", fg=DARK_RED,width="4", font=("Helvetica", 20), cursor="hand2")
    left_btn.pack(side="left", padx=10, pady=10)
    def prev_month(event=None):
        """ Moves to the previous month in the calendar."""
        if state["month"] == 1:
            state["month"] = 12
            state["year"] -= 1
        else:
            state["month"] -= 1
        actual_calendar() # Refresh the calendar display after changing the month
    left_btn.bind("<Button-1>", prev_month)
    right_btn=tk.Label(nav, text="►", bg="white",width="2",fg=DARK_RED, font=("Helvetica", 20), cursor="hand2")
    right_btn.pack(side="right", padx=10, pady=10)
    def next_month(event=None):
        """ Moves to the next month in the calendar."""
        if state["month"] == 12:
            state["month"] = 1
            state["year"] += 1
        else:
            state["month"] += 1
        actual_calendar()

    right_btn.bind("<Button-1>", next_month)        
    month_lbl = tk.Label(nav, text="", bg="white",fg=DARK_RED,font=("Helvetica", 26, "bold"), width=20)
    month_lbl.pack(side="left")

    # main area
    main = tk.Frame(self.root, bg="white")
    main.pack(fill="both", expand=True, padx=10)

    # left panel calendar
    cal_frame = tk.Frame(main, bg="white")
    cal_frame.pack(side="left", fill="both", expand=True)

    # right panel events + add form
    right_panel = tk.Frame(main, width=260)
    right_panel.pack(side="right", fill="y", padx=(10,0))
    right_panel.pack_propagate(False)

    event_list_frame = tk.Frame(right_panel, bg=GREY_BG)
    event_list_frame.pack(fill="both", expand=True)

    tk.Label(right_panel, text="Events this month", bg="white",
                font=("Helvetica", 11, "bold")).pack(pady=(10,4))
    
    add_form = tk.LabelFrame(right_panel, text="add event", bg=GREY_BG, font=("Helvetica", 9))
    add_form.pack(fill="x", padx=6, pady=6)
    
    tk.Label(add_form, text="title", bg=GREY_BG, font=("Helvetica", 9)).grid(row=0, column=0, sticky="w", padx=4)
    event_name = tk.Entry(add_form, width=18, font=("Helvetica", 9))
    event_name.grid(row=0, column=1, padx=4, pady=2)
    
    tk.Label(add_form, text="Date:", bg=GREY_BG, font=("Helvetica", 9)).grid(row=1, column=0, sticky="w", padx=4)
    event_date = tk.Entry(add_form, width=18, font=("Helvetica", 9))
    event_date.grid(row=1, column=1, padx=4, pady=2)
    
    event_date.insert(0, now.strftime("%Y-%m-%d")) # Pre-fill the date entry with todays date
    tk.Label(add_form, text="Type:", bg=GREY_BG, font=("Helvetica", 9)).grid(row=2, column=0, sticky="w", padx=4)
    type_var = tk.StringVar(value="exam")
    
    tk.OptionMenu(add_form, type_var, "exam", "assignment", "study", "other").grid(row=2, column=1, sticky="w", padx=4)  # Create a dropdown menu for selecting the event type     
    def load_event_list():
        for widgets in event_list_frame.winfo_children():
            widgets.destroy()
        y, m = state["year"], state["month"] # Get the current year and month from the state dictionary
        cursor.execute(
            "SELECT title, event_date, event_type FROM calendar_events "
            "WHERE user_id=? AND event_date LIKE ? ORDER BY event_date",
            (self.current_user_id, f"{y:04d}-{m:02d}-%"))
        rows = cursor.fetchall()
        if not rows:
            tk.Label(event_list_frame, text="No events.", bg=GREY_BG,
                    fg="#888888", font=("Helvetica", 9)).pack(pady=6)
            return
        for ev_title, ev_date, ev_type in rows: # Create a row for each event with the date and title displayed
            rf = tk.Frame(event_list_frame, bg=GREY_BG)
            rf.pack(fill="x", pady=1, padx=4)
            tk.Label(rf, text=f"{ev_date[8:]}  {ev_title}", bg=GREY_BG,
                    font=("Helvetica", 9)).pack(side="left", padx=2)
        
            
    def actual_calendar():
        for widgets in cal_frame.winfo_children():
            widgets.destroy()
        y, m = state["year"], state["month"] # Get the current year and month from the state dictionary
        month_lbl.config(text=datetime(y, m, 1).strftime("%B %Y"))

        cursor.execute(
            "SELECT event_date, event_type FROM calendar_events WHERE user_id=? AND event_date LIKE ?",
            (self.current_user_id, f"{y:04d}-{m:02d}-%"))
        event_map = {}
        for ed, et in cursor.fetchall(): # Create a mapping of days to event types for coloring the calendar cells
            day = int(ed[8:])
            event_map.setdefault(day, []).append(et)

        for col, dn in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]): # Create the header row for the days of the week
            tk.Label(cal_frame, text=dn, bg="white", fg="#888888",
                        font=("Helvetica",11, "bold"), width=7).grid(row=0, column=col, pady=(0,2))

        first_wd = date(y, m, 1).weekday()
        days_in  = cal.monthrange(y, m)[1]
        today    = now.day if (y == now.year and m == now.month) else -1

        r, c = 1, first_wd # Start the row and column for the first day of the month based on the weekday of the first day
        for d in range(1, days_in + 1):
            evts = event_map.get(d, [])
            first_type = evts[0] if evts else None
            bg = "#bbdefb" if d == today else (TYPE_COLORS.get(first_type, "white") if first_type else "white")          
            cell = tk.Frame(cal_frame, bg=bg, width=100, height=100, relief="solid", bd=1)
            cell.grid(row=r, column=c, padx=1, pady=1)
            cell.grid_propagate(False) # Prevent the cell from resizing if the content inside is large
            tk.Label(cell, text=str(d), bg=bg, fg="#0d0d0d",
                        font=("Helvetica", 15, "bold" if d == today else "normal")).pack(anchor="nw", padx=3)
            c += 1# Move to the next column for the next day
            if c == 7: # If the column index reaches 7 (end of the week), reset to the first column and move to the next row
                c, r = 0, r + 1

        load_event_list()    
    
    def add_event():
        name=event_name.get()
        date=event_date.get()
        type=type_var.get()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError: # If the date format is invalid, show a warning message
            messagebox.showwarning("Bad date", "Use Year-Month-Day!")
            return
        
        if not name:
            messagebox.showwarning("No title", "Enter an event title")
            return
        cursor.execute(
            "INSERT INTO calendar_events (user_id, title, event_date, event_type) VALUES (?,?,?,?)",
            (self.current_user_id, name, date, type))
        self.db.commit()
        event_name.delete(0, "end")
        actual_calendar()

    tk.Button(add_form, text="Add Event", command=add_event,
            font=("Helvetica", 9)).grid(row=3, column=0, columnspan=2, pady=4)
    actual_calendar()