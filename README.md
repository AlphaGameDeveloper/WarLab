# WarLab

WarLab is a multiplayer turn-based combat game built with Python and Tkinter, utilizing a client-server architecture for network play.

## Features

- **Network Multiplayer**: Play against friends over a local network or internet connection
- **Turn-Based Combat**: Strategic gameplay with attack, defend, and heal actions
- **Simple GUI**: Easy to understand interface built with Tkinter
- **Configurable Game Logic**: Adjust combat parameters through configuration file

## Requirements

- Python 3.6+
- Tkinter (usually included with Python installation)
- Network connectivity for multiplayer

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/WarLab.git
   cd WarLab
   ```

2. No additional dependencies are required beyond Python with Tkinter

## How to Play

### Starting a Server

1. Run the game: `python main.py`
2. Select "Create Server"
3. Configure server port (default: 5555)
4. Click "Start Server" and wait for a player to connect

### Connecting to a Server

1. Run the game: `python main.py`
2. Select "Connect to Server"
3. Enter server IP address and port
4. Click "Connect"

### Gameplay

- Players take turns choosing one of three actions:
  - **Attack**: Attempt to damage your opponent
  - **Defend**: Reduce incoming damage on your opponent's next turn
  - **Heal**: Restore some of your health

- The game continues until one player's health reaches zero

## Game Mechanics

- **Attack**: Has an 80% chance of success. Deals 10-20 damage when successful.
- **Defend**: Has a 70% chance of success. Reduces incoming damage by 50% when successful.
- **Heal**: Has a 60% chance of success. Restores 5-15 health points when successful.

These values can be adjusted in the `config.json` file.

## Configuration

Game parameters can be adjusted in the `config.json` file:

```json
{
    "attack": {
        "success_chance": 0.8,
        "damage_range": [10, 20]
    },
    "defend": {
        "success_chance": 0.7,
        "damage_reduction": 0.5
    },
    "heal": {
        "success_chance": 0.6,
        "heal_range": [5, 15]
    },
    "initial_health": 100
}
```

## Network Architecture

WarLab uses a client-server model where:
- The server maintains the authoritative game state
- Clients send action requests to the server
- The server processes actions and sends results to clients
- All random number generation happens server-side for fairness

For detailed information about the network protocol, see [networking_documentation.md](networking_documentation.md).

## Logging

WarLab includes a comprehensive logging system that:
- Logs game events to console
- Creates timestamped log files in the `logs` directory
- Displays current status in the GUI status bar

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Developed by Damien Boisvert (AlphaGameDeveloper)
