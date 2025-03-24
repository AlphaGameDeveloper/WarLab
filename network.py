import socket
import json
import threading
import logging
import os

logger = logging.getLogger(__name__)

class Server:
    def __init__(self, host='0.0.0.0', port=5555, config_file='config.json'):
        logger.info(f"Initializing Server on {host}:{port}")
        self.host = host
        self.port = port
        self.config_file = config_file
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            logger.debug(f"Server socket created and bound to {host}:{port}")
        except Exception as e:
            logger.critical(f"Failed to create or bind server socket: {e}")
            raise
        self.client = None
        self.addr = None
        self.connected = False
        logger.debug("Server initialized successfully")
        
    def start(self):
        logger.info(f"Starting server on {self.host}:{self.port}")
        try:
            self.server.listen(1)
            logger.info(f"Server listening for connections on {self.host}:{self.port}")
            logger.debug("Waiting for client to connect...")
            self.client, self.addr = self.server.accept()
            self.connected = True
            logger.info(f"Client connected from {self.addr}")
            
            # Send configuration to client after connection
            self.send_config()
        except Exception as e:
            logger.error(f"Error while starting server or accepting connection: {e}")
            raise
    
    def send_config(self):
        """Send server's configuration to the client"""
        logger.info("Sending configuration to client")
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            config_data = {"message_type": "config", "config": config}
            self.send(config_data)
            logger.debug("Configuration sent to client")
            return True
        except Exception as e:
            logger.error(f"Error sending configuration: {e}")
            return False
        
    def send(self, data):
        if not self.client:
            logger.error("Attempted to send data but no client connected")
            return False
            
        try:
            encoded_data = json.dumps(data).encode()
            self.client.send(encoded_data)
            logger.debug(f"Sent data: {data}")
            return True
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            return False
            
    def receive(self):
        if not self.client:
            logger.error("Attempted to receive data but no client connected")
            return None
            
        try:
            logger.debug("Waiting to receive data...")
            data = self.client.recv(2048).decode()
            parsed_data = json.loads(data)
            logger.debug(f"Received data: {parsed_data}")
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error receiving data: {e}")
            return None
    
    def process_action(self, action_request):
        """Process an action request and return the result with server-side rolls"""
        logger.info(f"Processing action request: {action_request}")
        
        if "action_type" not in action_request:
            logger.error("Invalid action request: missing action_type")
            return {"error": "Invalid action request"}
        
        action_result = {"message_type": "action_result", "action": action_request["action_type"]}
        
        # Forward to game logic handler
        if hasattr(self, 'game'):
            result = self.game.perform_server_action(action_request["action_type"])
            action_result.update(result)
        else:
            logger.error("Game object not attached to server")
            action_result = {"error": "Server game not initialized"}
        
        return action_result
            
    def close(self):
        logger.info("Closing server connections")
        if self.client:
            logger.debug("Closing client connection")
            self.client.close()
        logger.debug("Closing server socket")
        self.server.close()
        logger.info("Server shut down successfully")

class Client:
    def __init__(self, host, port=5555):
        logger.info(f"Initializing Client to connect to {host}:{port}")
        self.host = host
        self.port = port
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug("Client socket created")
        except Exception as e:
            logger.critical(f"Failed to create client socket: {e}")
            raise
        self.connected = False
        self.server_config = None
        logger.debug("Client initialized successfully")
        
    def connect(self):
        logger.info(f"Attempting to connect to server at {self.host}:{self.port}")
        try:
            self.client.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Successfully connected to server at {self.host}:{self.port}")
            
            # Wait for server to send configuration
            logger.info("Waiting for server configuration...")
            self.server_config = self.receive_config()
            if not self.server_config:
                logger.error("Failed to receive server configuration")
                self.close()
                return False
                
            logger.info("Received server configuration")
            return True
        except ConnectionRefusedError:
            logger.error(f"Connection refused by server at {self.host}:{self.port}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to server: {e}")
            return False
    
    def receive_config(self):
        """Receive configuration from server"""
        config_data = self.receive()
        if config_data and config_data.get("message_type") == "config":
            return config_data.get("config")
        return None
            
    def send(self, data):
        if not self.connected:
            logger.error("Attempted to send data but not connected to server")
            return False
            
        try:
            encoded_data = json.dumps(data).encode()
            self.client.send(encoded_data)
            logger.debug(f"Sent data: {data}")
            return True
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            return False
    
    def request_action(self, action_type):
        """Send an action request to the server"""
        logger.info(f"Requesting action: {action_type}")
        request = {
            "message_type": "action_request",
            "action_type": action_type
        }
        return self.send(request)
            
    def receive(self):
        if not self.connected:
            logger.error("Attempted to receive data but not connected to server")
            return None
            
        try:
            logger.debug("Waiting to receive data...")
            data = self.client.recv(2048).decode()
            parsed_data = json.loads(data)
            logger.debug(f"Received data: {parsed_data}")
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error receiving data: {e}")
            return None
            
    def close(self):
        logger.info("Closing client connection")
        self.client.close()
        self.connected = False
        logger.debug("Client connection closed")
