def clear_screen(root):
    """Clears all widgets from the given root window."""
    for widget in root.winfo_children():
        widget.destroy()
 
 
def make_hover_background(widget, normal_colour, hover_colour, command):
    """Adds hover effects and click effect to a Label."""
    
    # Change the background colour when the cursor enters the widget
    widget.bind("<Enter>",lambda e: widget.config(bg=hover_colour))
    # Restore the original background colour when the cursor leaves
    widget.bind("<Leave>",lambda e: widget.config(bg=normal_colour))
    # Bind the label to a command so it executes when pressed
    widget.bind("<Button-1>",lambda e: command())
 
def make_hover_foreground(widget, normal_colour, hover_colour, command):
    """Adds hover effects and click effect to a Label."""
    
    # Change the foreground colour when the cursor enters the widget
    widget.bind("<Enter>",lambda e: widget.config(fg=hover_colour))
    # Restore the original foreground colour when the cursor leaves
    widget.bind("<Leave>",lambda e: widget.config(fg=normal_colour))
    # Bind the label to a command so it executes when pressed
    widget.bind("<Button-1>",lambda e: command())