# WarLab Network Protocol Documentation

This document outlines the networking architecture and packet structure used in WarLab.

## Overview

WarLab uses a client-server architecture where:
- The server hosts the game, processing game logic and managing the state
- The client connects to the server and sends action requests
- All communication uses JSON-encoded messages sent over TCP sockets

## Network Components

### Server

The server component:
- Binds to a specified host and port (default: 0.0.0.0:5555)
- Accepts a single client connection
- Sends game configuration to client upon connection
- Processes action requests from the client
- Maintains authoritative game state

### Client

The client component:
- Connects to a server at a specified host and port
- Receives configuration from the server
- Sends action requests to the server
- Maintains a local game state synchronized with the server

## Packet Structure

All network messages in WarLab are JSON objects encoded as strings and transmitted over TCP. Each message has a specific structure depending on its type.

### Common Message Format

```json
{
    "message_type": "<type>",
    ...additional fields depending on message type
}
```

## Message Types

### 1. Configuration Message

Sent from server to client immediately after connection.

```json
{
    "message_type": "config",
    "config": {
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
}
```

### 2. Action Request Message

Sent from client to server when a player takes an action.

```json
{
    "message_type": "action_request",
    "action_type": "<attack|defend|heal>"
}
```

### 3. Action Result Message

Sent from server to client after processing an action.

```json
{
    "message_type": "action_result",
    "action": "<attack|defend|heal>",
    "success": true|false,
    "value": <number>,           // Only for attack and heal actions
    "message": "<string>"
}
```

### 4. Game Over Message

Sent from server to client when the game has ended.

```json
{
    "game_over": true,
    "winner": "<me|opponent>"    // From recipient's perspective
}
```

## Communication Flow

1. **Connection Establishment**
   - Client connects to server
   - Server accepts connection
   - Server sends configuration to client

2. **Gameplay Loop**
   - Client sends action request to server
   - Server processes action and updates game state
   - Server sends action result to client
   - Client applies action result to local game state
   - Client waits for server to process opponent's action
   - Server sends opponent action result to client
   - Client applies opponent action result to local game state

3. **Game Termination**
   - When game is over, server sends game over message
   - Client displays game result and returns to connection screen

## Error Handling

- Network errors are logged using the Python logging system
- Connection failures result in returning to the connection screen
- JSON decode errors are caught and logged

## Security Considerations

- All random number generation for game outcomes happens server-side
- Client never generates random values for game actions
- Server is the authority for all game state changes

## Implementation Details

The networking components are implemented in `network.py` and consist of two main classes:
- `Server`: Handles server-side networking
- `Client`: Handles client-side networking

Both classes provide methods for sending and receiving JSON-formatted messages over TCP sockets.
