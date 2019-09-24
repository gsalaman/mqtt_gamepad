# mqtt_gamepad
This repo implements gamepad control through MQTT.  This allows for an input device to remotely control an application.  To do this, there are 3 pieces:
* gamepad "app" itself.  Could be something that connects to USB joysticks via evdev, or just a tkinter python program, or something else.  It'll broadcast text strings for it's direction and buttons.
* a consumer "wrapper api" that talks MQTT and returns strings.  It allows for both blocking and non-blocking reads, and has a "registration mechanism" (hey, I'm player 1!). The wrapper app is a python module that the game itself imports.
* And then the game.  It uses the wrapper api to acually implement the game.

## Registrations
The first step in registration is for the game app to tell the wrapper how many players it is expecting.  It does so when it intializes the wrapper (as a parameter to the constructor).

Each gamepad is independent of "player"...which means we need a registration concept.  Each gamepad can send a "register" topic with it's client ID (assuming all client IDs are independent), and then the wrapper will respond back with a register/client id topic where "playerX" is the payload (X=1 for player1, 2 for player2, etc...).  Eventually I'll probably add a "register/release" message so the client can release "player1" to let a different client take it....but that's longer term.
 
Messages used: 


| Topic | Payload | Description |
|-------|---------|-------------|
| register/request | **client_name** | Sent by the input device to request a player identifer.  **client_name** is the string of the actual input device's MQTT client |
| register/**client_name** | **playerX** | Sent by the wrapper to notify the client which player they were assigned. X in **playerX** is an integer number, starting at 1 |

Finally, the wrapper gives a "player_count" api that the game can use to see how many players have already registered.

Picture goes here.  :)

## Gamepad Inputs
Then the game plays, using player1/player2 messages with directions as the playload.

| Topic | Payload | Description |
|-------|---------|-------------|
| **playerX** | **direction** | Sent from the client associated with that player, with a text string for direction.  "up" "down" "left" and "right" currently implemented. |

To read a message, I'll have a "get" function in the wrapper which will either return "None" if there's no message or the NEXT message.  That way, the game can decide to get & process all messages, or ignore until it gets to the last.  Can do blocking or non-blocking.
