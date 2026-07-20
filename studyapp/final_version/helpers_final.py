
def make_hover_background(widget, normal_colour, hover_colour, command):
    """Adds hover effects and click effect to a Label."""
    widget.bind("<Enter>",lambda e: widget.config(bg=hover_colour))
    widget.bind("<Leave>",lambda e: widget.config(bg=normal_colour))
    widget.bind("<Button-1>",lambda e: command())

def make_hover_foreground(widget, normal_colour, hover_colour, command):
    """Adds hover effects and click effect to a Label."""
    widget.bind("<Enter>",lambda e: widget.config(fg=hover_colour))
    widget.bind("<Leave>",lambda e: widget.config(fg=normal_colour))
    widget.bind("<Button-1>",lambda e: command())
    
def clear_screen(root):
    """Clears all widgets from the given root window."""
    for widget in root.winfo_children():
        widget.destroy()