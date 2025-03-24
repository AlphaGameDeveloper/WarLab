import json
import random
import logging

logger = logging.getLogger(__name__)

class Game:
    def __init__(self, config_file='config.json', is_server=False, server_config=None):
        logger.info(f"Initializing game as {'server' if is_server else 'client'}")
        self.is_server = is_server
        
        if is_server:
            # Server loads config from file
            logger.info(f"Loading config from file: {config_file}")
            self.load_config(config_file)
        elif server_config:
            # Client uses config received from server
            logger.info("Using configuration received from server")
            self.load_config_from_dict(server_config)
        else:
            logger.error("Client game initialized without server configuration")
            raise ValueError("Client game requires server configuration")
            
        self.my_health = self.initial_health
        self.opponent_health = self.initial_health
        self.is_defending = False
        logger.info(f"Game initialized with initial health: {self.initial_health}")
        logger.debug(f"Attack success rate: {self.attack_success}, Defend success rate: {self.defend_success}, Heal success rate: {self.heal_success}")
        
    def load_config(self, config_file):
        logger.debug(f"Loading configuration from {config_file}")
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            self.load_config_from_dict(config)
        except FileNotFoundError:
            logger.critical(f"Config file not found: {config_file}")
            raise
        except json.JSONDecodeError as e:
            logger.critical(f"Error parsing config file: {e}")
            raise
        except Exception as e:
            logger.critical(f"Unexpected error loading config: {e}")
            raise
    
    def load_config_from_dict(self, config):
        logger.debug(f"Loading configuration from dictionary")
        try:
            self.attack_success = config['attack']['success_chance']
            self.attack_damage = config['attack']['damage_range']
            self.defend_success = config['defend']['success_chance']
            self.defend_reduction = config['defend']['damage_reduction']
            self.heal_success = config['heal']['success_chance']
            self.heal_amount = config['heal']['heal_range']
            self.initial_health = config['initial_health']
            
            logger.debug(f"Configuration loaded successfully: {config}")
        except KeyError as e:
            logger.critical(f"Missing key in config: {e}")
            raise
        
    def perform_server_action(self, action):
        """Server-side action processing with secure rolls"""
        logger.info(f"Server performing action: {action}")
        result = {'action': action, 'success': False, 'value': 0, 'message': ''}
        
        if action == 'attack':
            success_roll = random.random()
            success = success_roll < self.attack_success
            logger.debug(f"Attack roll: {success_roll} (success threshold: {self.attack_success})")
            result['success'] = success
            if success:
                damage = random.randint(self.attack_damage[0], self.attack_damage[1])
                logger.debug(f"Attack damage roll: {damage}")
                result['value'] = damage
                result['message'] = f"Attack successful! Dealt {damage} damage."
            else:
                logger.info("Attack missed!")
                result['message'] = "Attack missed!"
        
        elif action == 'defend':
            success_roll = random.random()
            success = success_roll < self.defend_success
            logger.debug(f"Defend roll: {success_roll} (success threshold: {self.defend_success})")
            result['success'] = success
            if success:
                result['message'] = "Successfully entered defensive stance."
            else:
                logger.info("Failed to defend!")
                result['message'] = "Failed to defend!"
        
        elif action == 'heal':
            success_roll = random.random()
            success = success_roll < self.heal_success
            logger.debug(f"Heal roll: {success_roll} (success threshold: {self.heal_success})")
            result['success'] = success
            if success:
                heal = random.randint(self.heal_amount[0], self.heal_amount[1])
                logger.debug(f"Heal amount roll: {heal}")
                result['value'] = heal
                result['message'] = f"Healed for {heal} points."
            else:
                logger.info("Healing failed!")
                result['message'] = "Healing failed!"
        else:
            logger.warning(f"Unknown action attempted: {action}")
        
        logger.debug(f"Action result: {result}")
        return result
        
    def perform_action(self, action):
        """Client-side method that forwards to server or applies local changes based on results"""
        if self.is_server:
            # Server performs the action itself
            logger.info(f"Server performing action: {action}")
            result = self.perform_server_action(action)
            
            # Update server game state based on the action
            if action == 'attack' and result['success']:
                self.opponent_health -= result['value']
                logger.info(f"Attack successful! Dealt {result['value']} damage. Opponent health now: {self.opponent_health}")
            
            elif action == 'defend' and result['success']:
                self.is_defending = True
                logger.info("Successfully entered defensive stance")
            
            elif action == 'heal' and result['success']:
                old_health = self.my_health
                self.my_health = min(self.initial_health, self.my_health + result['value'])
                actual_heal = self.my_health - old_health
                logger.info(f"Healed for {actual_heal} points. Health now: {self.my_health}")
            
            # Add game over status to result if applicable
            if self.is_game_over():
                result['game_over'] = True
                result['winner'] = self.get_winner()
                
            return result
        else:
            # Client should not be generating random rolls
            logger.error("Client attempted to perform action locally (should be server-side only)")
            return {'action': action, 'error': 'Client cannot perform actions locally'}
    
    def apply_action_result(self, result, is_my_action=True):
        """Apply action result received from server to local game state"""
        logger.info(f"Applying action result: {result} (my action: {is_my_action})")
        
        action = result['action']
        success = result['success']
        value = result.get('value', 0)
        
        if is_my_action:
            # This was my action
            if action == 'attack' and success:
                self.opponent_health -= value
                logger.info(f"My attack successful! Dealt {value} damage. Opponent health now: {self.opponent_health}")
            
            elif action == 'defend' and success:
                self.is_defending = True
                logger.info("Successfully entered defensive stance")
            
            elif action == 'heal' and success:
                old_health = self.my_health
                self.my_health = min(self.initial_health, self.my_health + value)
                actual_heal = self.my_health - old_health
                logger.info(f"Healed for {actual_heal} points. Health now: {self.my_health}")
            
            return result['message']
        
        else:
            # This was opponent's action
            message = self.receive_action_result(result)
            return message
    
    def receive_action_result(self, result):
        """Process opponent action result (unchanged from original)"""
        logger.info(f"Processing opponent action result: {result}")
        action = result['action']
        success = result['success']
        value = result.get('value', 0)
        
        if action == 'attack' and success:
            logger.debug(f"Opponent's attack was successful with value: {value}")
            if self.is_defending:
                reduced_damage = int(value * (1 - self.defend_reduction))
                logger.debug(f"Defending! Damage reduced from {value} to {reduced_damage}")
                self.my_health -= reduced_damage
                self.is_defending = False
                logger.info(f"Took reduced damage of {reduced_damage}. Health now: {self.my_health}")
                return f"Opponent's attack reduced to {reduced_damage} damage due to your defense."
            else:
                self.my_health -= value
                logger.info(f"Took full damage of {value}. Health now: {self.my_health}")
                return f"Opponent attacked successfully for {value} damage."
        
        elif action == 'defend' and success:
            logger.info("Opponent is now in defensive stance")
            return "Opponent is now in a defensive stance."
        
        elif action == 'heal' and success:
            logger.info(f"Opponent healed for {value} health points")
            return f"Opponent healed for {value} health points."
        
        logger.info(f"Opponent's {action} failed")
        return f"Opponent's {action} failed."
    
    def is_game_over(self):
        if self.my_health <= 0 or self.opponent_health <= 0:
            logger.info(f"Game over detected. My health: {self.my_health}, Opponent health: {self.opponent_health}")
            return True
        return False
    
    def get_winner(self):
        if self.my_health <= 0:
            logger.info("Game over - Opponent wins")
            return "opponent"
        elif self.opponent_health <= 0:
            logger.info("Game over - I win")
            return "me"
        logger.debug("get_winner called but game is not over")
        return None
