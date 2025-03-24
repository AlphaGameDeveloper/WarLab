import tkinter as tk
from gui import FightingGameGUI
import logging
import os
import datetime
from sys import exit as _exit
from log_handler import StatusBarLogHandler

# Global handler to be accessed by the GUI
status_handler = None

def setup_logging():
    """Configure logging for the application"""
    global status_handler
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a timestamp for the log filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f'warlab_{timestamp}.log')
    
    # Create the status bar handler (without StringVar for now)
    status_handler = StatusBarLogHandler()
    status_handler.setLevel(logging.INFO)
    status_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    
    # Configure the logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
            status_handler  # Add our custom handler
        ]
    )
    
    logging.critical("==== STARTING NEW WARLAB SESSION ====")
    logging.info(f"Logging to file: {log_file}")

def main() -> int:
    setup_logging()
    logging.info("Initializing main application")
    root = tk.Tk()
    logging.debug("Created Tkinter root window")
    app = FightingGameGUI(root, status_handler)
    logging.info("Application GUI initialized, starting mainloop")
    root.mainloop()
    logging.critical("==== APPLICATION TERMINATED ====")
    return 0

if __name__ == "__main__":
    _exit(main())
