import tkinter as tk

# Import the main class which contains all screens and program logic
from app_final import AppFace
 
# Create the main Tkinter window that the application will run inside
root=tk.Tk()

# Create an instance of the app and place in window
app = AppFace(root)

#Start tkinter loop
root.mainloop()
 