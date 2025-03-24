import logging
import tkinter as tk

class StatusBarLogHandler(logging.Handler):
    """Custom logging handler that updates a tkinter StringVar with the latest log message"""
    
    def __init__(self, status_var=None, root=None):
        super().__init__()
        self.status_var = status_var
        self.root = root
        self.last_message = ""
        
    def emit(self, record):
        """Process a log record and update status variable if available"""
        try:
            self.last_message = self.format(record)
            if self.status_var is not None and isinstance(self.status_var, tk.StringVar) and self.root is not None:
                # Use after_idle to ensure thread safety with tkinter
                self.root.after_idle(lambda: self.status_var.set(f"{record.levelname}: {record.getMessage()}"))
        except Exception:
            self.handleError(record)
    
    def set_status_var(self, status_var, root=None):
        """Set or update the status variable after initialization"""
        self.status_var = status_var
        self.root = root
        # Update with last message if we have one
        if self.last_message and isinstance(status_var, tk.StringVar):
            status_var.set(self.last_message)
