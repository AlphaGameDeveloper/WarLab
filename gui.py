import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import logging

from network import Server, Client
from game import Game

logger = logging.getLogger(__name__)

class FightingGameGUI:
    def __init__(self, root, status_handler=None):
        logger.info("Initializing WarLab GUI")
        self.root = root
        self.root.title("WarLab")
        self.network = None
        self.is_server = False
        
        # Create status bar at the bottom
        self.setup_status_bar(status_handler)
        
        # Initial frame setup (connection screen)
        self.setup_connection_frame()
    
    def setup_status_bar(self, status_handler):
        """Create status bar and connect it to the log handler"""
        # Create status bar frame at the bottom
        self.status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create status variable and label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self.status_frame, 
            textvariable=self.status_var, 
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_label.pack(fill=tk.X)
        
        # Connect to the log handler if provided
        if status_handler:
            status_handler.set_status_var(self.status_var, self.root)
    
    def setup_connection_frame(self):
        # Clear any existing frames except status bar
        for widget in self.root.winfo_children():
            if widget != self.status_frame:
                widget.destroy()
        
        self.conn_frame = ttk.Frame(self.root, padding="20")
        self.conn_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.conn_frame, text="WarLab", font=("Helvetica", 16)).pack(pady=20)
        
        ttk.Button(self.conn_frame, text="Create Server", command=self.create_server_dialog).pack(fill=tk.X, pady=10)
        ttk.Button(self.conn_frame, text="Connect to Server", command=self.connect_dialog).pack(fill=tk.X, pady=10)
        
    def create_server_dialog(self):
        # Clear the connection frame
        for widget in self.conn_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.conn_frame, text="Create Server", font=("Helvetica", 16)).pack(pady=20)
        
        # Server settings
        settings_frame = ttk.Frame(self.conn_frame)
        settings_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(settings_frame, text="Port:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.port_var = tk.StringVar(value="5555")
        port_entry = ttk.Entry(settings_frame, textvariable=self.port_var)
        port_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Start server button
        ttk.Button(self.conn_frame, text="Start Server", command=self.start_server).pack(fill=tk.X, pady=10)
        ttk.Button(self.conn_frame, text="Back", command=self.setup_connection_frame).pack(fill=tk.X, pady=10)
    
    def connect_dialog(self):
        # Clear the connection frame
        for widget in self.conn_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.conn_frame, text="Connect to Server", font=("Helvetica", 16)).pack(pady=20)
        
        # Connection settings
        settings_frame = ttk.Frame(self.conn_frame)
        settings_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(settings_frame, text="IP Address:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ip_var = tk.StringVar(value="127.0.0.1")
        ip_entry = ttk.Entry(settings_frame, textvariable=self.ip_var)
        ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(settings_frame, text="Port:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.port_var = tk.StringVar(value="5555")
        port_entry = ttk.Entry(settings_frame, textvariable=self.port_var)
        port_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Connect button
        ttk.Button(self.conn_frame, text="Connect", command=self.connect_to_server).pack(fill=tk.X, pady=10)
        ttk.Button(self.conn_frame, text="Back", command=self.setup_connection_frame).pack(fill=tk.X, pady=10)
    
    def start_server(self):
        try:
            port = int(self.port_var.get())
            self.is_server = True
            self.show_waiting_screen("Waiting for player to connect...")
            
            # Start server in a separate thread
            threading.Thread(target=self._server_thread, args=(port,), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number")
    
    def _server_thread(self, port):
        try:
            self.network = Server(port=port)
            
            # Initialize the game as server
            self.game = Game(is_server=True)
            
            # Attach game to network for server-side processing
            self.network.game = self.game
            
            # Start server after game initialization
            self.network.start()
            
            # Switch to game screen in the main thread
            self.root.after(0, self.setup_game_screen)
        except Exception as e:
            print(f"Server error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Server Error", str(e)))
            self.root.after(0, self.setup_connection_frame)
    
    def connect_to_server(self):
        try:
            host = self.ip_var.get()
            port = int(self.port_var.get())
            self.is_server = False
            self.show_waiting_screen("Connecting to server...")
            
            # Connect in a separate thread
            threading.Thread(target=self._client_thread, args=(host, port), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number")
    
    def _client_thread(self, host, port):
        try:
            self.network = Client(host, port)
            if self.network.connect():
                # Initialize the game with server config
                self.game = Game(is_server=False, server_config=self.network.server_config)
                
                # Switch to game screen in the main thread
                self.root.after(0, self.setup_game_screen)
            else:
                self.root.after(0, lambda: messagebox.showerror("Connection Error", "Failed to connect to the server"))
                self.root.after(0, self.setup_connection_frame)
        except Exception as e:
            print(f"Client error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
            self.root.after(0, self.setup_connection_frame)
    
    def show_waiting_screen(self, message):
        # Clear any existing frames except status bar
        for widget in self.root.winfo_children():
            if widget != self.status_frame:
                widget.destroy()
        
        self.waiting_frame = ttk.Frame(self.root, padding="20")
        self.waiting_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.waiting_frame, text=message, font=("Helvetica", 12)).pack(pady=20)
        
        # Add an indeterminate progress bar
        self.progress = ttk.Progressbar(self.waiting_frame, mode='indeterminate', length=300)
        self.progress.pack(pady=20)
        self.progress.start()
    
    def setup_game_screen(self):
        # Clear any existing frames except status bar
        for widget in self.root.winfo_children():
            if widget != self.status_frame:
                widget.destroy()
        
        self.game_frame = ttk.Frame(self.root, padding="20")
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        
        # Health displays
        health_frame = ttk.Frame(self.game_frame)
        health_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(health_frame, text="Your Health:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.my_health_var = tk.StringVar(value=str(self.game.my_health))
        ttk.Label(health_frame, textvariable=self.my_health_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(health_frame, text="Opponent Health:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.opponent_health_var = tk.StringVar(value=str(self.game.opponent_health))
        ttk.Label(health_frame, textvariable=self.opponent_health_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Action buttons
        action_frame = ttk.Frame(self.game_frame)
        action_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(action_frame, text="Attack", command=lambda: self.perform_action("attack")).pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Defend", command=lambda: self.perform_action("defend")).pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Heal", command=lambda: self.perform_action("heal")).pack(fill=tk.X, pady=5)
        
        # Status message
        self.status_var = tk.StringVar(value="Choose your action")
        ttk.Label(self.game_frame, textvariable=self.status_var, wraplength=400).pack(pady=10)
        
        # Determine who goes first
        if self.is_server:
            self.my_turn = True
            self.status_var.set("Your turn. Choose an action.")
        else:
            self.my_turn = False
            self.status_var.set("Waiting for opponent's move...")
            self.show_waiting_for_opponent()
            threading.Thread(target=self.receive_opponent_action, daemon=True).start()
    
    def perform_action(self, action):
        if not self.my_turn:
            return
        
        # For server: perform action locally
        # For client: send request to server
        if self.is_server:
            # Server performs action locally and sends result to client
            result = self.game.perform_action(action)
            
            # Update status
            self.status_var.set(result['message'])
            
            # Send action result to client
            self.network.send(result)
            
            # Update health displays
            self.my_health_var.set(str(self.game.my_health))
            self.opponent_health_var.set(str(self.game.opponent_health))
        else:
            # Client sends action request to server
            self.network.request_action(action)
            
            # Wait for server's response with the action result
            result = self.network.receive()
            
            if result:
                # Apply the result to the client's game state
                message = self.game.apply_action_result(result, is_my_action=True)
                
                # Update status
                self.status_var.set(message)
                
                # Update health displays
                self.my_health_var.set(str(self.game.my_health))
                self.opponent_health_var.set(str(self.game.opponent_health))
        
        # Check if game is over
        if result.get('game_over', False) or self.game.is_game_over():
            winner = result.get('winner') or self.game.get_winner()
            if winner == "me":
                messagebox.showinfo("Game Over", "You win!")
            else:
                messagebox.showinfo("Game Over", "You lose!")
            self.setup_connection_frame()
            return
        
        # Wait for opponent's move
        self.my_turn = False
        self.show_waiting_for_opponent()
        threading.Thread(target=self.receive_opponent_action, daemon=True).start()
    
    def show_waiting_for_opponent(self):
        # Disable action buttons
        for widget in self.game_frame.winfo_children():
            if isinstance(widget, ttk.Frame) and widget.winfo_children() and isinstance(widget.winfo_children()[0], ttk.Button):
                for button in widget.winfo_children():
                    button.config(state=tk.DISABLED)
        
        # Show waiting message
        self.status_var.set("Waiting for opponent's move...")
        
        # Show progress bar
        self.wait_frame = ttk.Frame(self.game_frame)
        self.wait_frame.pack(fill=tk.X, pady=10)
        
        self.wait_progress = ttk.Progressbar(self.wait_frame, mode='indeterminate', length=300)
        self.wait_progress.pack(pady=10)
        self.wait_progress.start()
    
    def hide_waiting_for_opponent(self):
        # Enable action buttons
        for widget in self.game_frame.winfo_children():
            if isinstance(widget, ttk.Frame) and widget.winfo_children() and isinstance(widget.winfo_children()[0], ttk.Button):
                for button in widget.winfo_children():
                    button.config(state=tk.NORMAL)
        
        # Remove waiting elements
        if hasattr(self, 'wait_frame'):
            self.wait_frame.destroy()
    
    def receive_opponent_action(self):
        result = self.network.receive()
        if result:
            # Check if it's a game over message
            if result.get('game_over', False):
                # Apply the final action
                message = self.game.apply_action_result(result, is_my_action=False)
                
                # Update health in the main thread
                self.root.after(0, lambda: self.my_health_var.set(str(self.game.my_health)))
                self.root.after(0, lambda: self.opponent_health_var.set(str(self.game.opponent_health)))
                
                # Update status
                self.root.after(0, lambda: self.status_var.set(message))
                
                # Show game over message
                winner = result.get('winner')
                if winner == "me":
                    self.root.after(0, lambda: messagebox.showinfo("Game Over", "You lose!"))
                else:
                    self.root.after(0, lambda: messagebox.showinfo("Game Over", "You win!"))
                
                self.root.after(0, self.setup_connection_frame)
                return
            
            # Normal action processing
            message = ""
            if self.is_server:
                # Server receives client action request and processes it
                if result.get('message_type') == 'action_request':
                    action_type = result.get('action_type')
                    action_result = self.network.process_action(result)
                    
                    # Update opponent health based on result
                    message = self.game.apply_action_result(action_result, is_my_action=False)
                    
                    # Send result back to client
                    self.network.send(action_result)
                else:
                    logger.error(f"Server received unexpected message type: {result}")
                    return
            else:
                # Client receives action result from server
                message = self.game.apply_action_result(result, is_my_action=False)
            
            # Update health in the main thread
            self.root.after(0, lambda: self.my_health_var.set(str(self.game.my_health)))
            self.root.after(0, lambda: self.opponent_health_var.set(str(self.game.opponent_health)))
            
            # Update status in the main thread
            self.root.after(0, lambda: self.status_var.set(message))
            
            # Check if game is over
            if self.game.is_game_over():
                winner = self.game.get_winner()
                if winner == "me":
                    self.root.after(0, lambda: messagebox.showinfo("Game Over", "You win!"))
                else:
                    self.root.after(0, lambda: messagebox.showinfo("Game Over", "You lose!"))
                
                # For server, send game over message to client
                if self.is_server:
                    game_over_msg = {"game_over": True, "winner": "opponent" if winner == "me" else "me"}
                    self.network.send(game_over_msg)
                
                self.root.after(0, self.setup_connection_frame)
                return
            
            # It's now the player's turn
            self.my_turn = True
            
            # Hide waiting elements in the main thread
            self.root.after(0, self.hide_waiting_for_opponent)
            self.root.after(0, lambda: self.status_var.set("Your turn. Choose an action."))
