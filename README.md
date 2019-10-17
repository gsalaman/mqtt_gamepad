# mqtt_gamepad
This repo implements gamepad control through MQTT.  This allows for an input device to remotely control an application.  To do this, there are 3 pieces:
* gamepad "app" itself.  Could be something that connects to USB joysticks via evdev, or just a tkinter python program, or something else.  It'll broadcast text strings for it's direction and buttons.
* a consumer "wrapper api" that talks MQTT and returns strings.  It allows for both blocking and non-blocking reads, and has a "registration mechanism" (hey, I'm player 1!). The wrapper app is a python module that the game itself imports.
* And then the game.  It uses the wrapper api to acually implement the game.

## Registrations
The first step in registration is for the game app to tell the wrapper how many players it is expecting.  It does so when it intializes the wrapper (as a parameter to the constructor).

Each gamepad is independent of "player"...which means we need a registration concept.  Each gamepad can send a "register" topic with it's client ID (assuming all client IDs are independent), and then the wrapper will respond back with a register/client id topic where "playerX" is the payload (X=1 for player1, 2 for player2, etc...).  There is also a "register/release" message so the client can release "player1" to let a different client take it.
 
Messages used: 


| Topic | Payload | Description |
|-------|---------|-------------|
| register/request | **client_name** | Sent by the input device to request a player identifer.  **client_name** is the string of the actual input device's MQTT client |
| register/**client_name** | **playerX** | Sent by the wrapper to notify the client which player they were assigned. X in **playerX** is an integer number, starting at 1 |
| register/release | **client_name** | Sent by the input device to release it's player identifier.  **client_name** is the string of the actual input device's MQTT client |


Picture goes here.  :)

## Gamepad Inputs
Then the game plays, using player1/player2 messages with directions as the playload.

| Topic | Payload | Description |
|-------|---------|-------------|
| **playerX** | **direction** | Sent from the client associated with that player, with a text string for direction.  "up" "down" "left" and "right" currently implemented. |

To read a message, I'll have a "get" function in the wrapper which will either return "None" if there's no message or the NEXT message.  That way, the game can decide to get & process all messages, or ignore until it gets to the last.  Can do blocking or non-blocking.

The wrapper returns inputs as list items, where the first item in the list is the player identifier (eg player1), and the next is the input string (eg "up")

The wrapper will store these messages for the application, and provides the following methods to retrieve inputs:

| Method | Params | Return Value | Description |
|---|---|---|---|
| blocking_read | none | input list item | This will return the next input in the queue, waiting until there is a valid input.  It will remove that input from the queue, and then return that input. |
| get_next_input | none | input list item or **None** | This is a non-blocking call.  If there is no input, it will return None...otherwise, it will return the input list item (with Player and Input string) |

The API provides a mechanism to clear the entire queue of inputs:  empty_commands.

## Other API commands
The wrapper gives an api to see whether a given player is connected (via a **playerX** string as above)...this returns either True or False based on whether that player is connected.  This is via the "check_connected" method.

It also gives a "player_count" API to return the number of connected players.
