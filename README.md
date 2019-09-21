# mqtt_gamepad
## Requirement/Design Thoughts
3 pieces:
* gamepad "app" itself.  Could be something that connects to USB joysticks via evdev, or just a tkinter python program, or something else.  It'll broadcast text strings for it's direction and buttons.
* a consumer "wrapper api" that talks MQTT and returns strings.  Probably want blocking and non-blocking reads, and some way eventually "register" (hey, I'm player 1!). The wrapper app should be a python module that the game itself imports.
* And then the game.  It uses the wrapper api to acually implement the game.

So, with that, here's a simple starting example:  
Write a gui app that does "up/down/left/right".  Each command will publish "player1/dir" with the payload being direction.  Could also embed it and make the topic "player1/dir/up" with the expandablily being "start" and "stop" to reflect button press and release.

The wrapper API is going to store ALL the received commands.  I can come up with cases where the api wants to consume all, or just the last one.  If we've got some sort of a "queue-size" indicator, we can do both blocking and non-blocking (wait for queue to be non-zero if blocking...if non-blocking, don't do anything)

## Registrations
I'd like each gamepad app to be independent of "player"...which means we need a registration concept.  Each gamepad can send a "register" topic with it's client ID (assuming all client IDs are independent), and then the wrapper will respond back with a register/client id topic where "playerX" is the payload (X=1 for player1, 2 for player2, etc...).  Eventually I'll probably add a "register/release" message so the client can release "player1" to let a different client take it....but that's longer term.
 
Picture goes here.  :)

With this flow, the game will tell the wrapper how many players it's expecting, and then the wrapper can return "ready" when it has that number of players registered.

Then the game plays, using player1/player2 messages with directions as the playload.

To read a message, I'll have a "get" function in the wrapper which will either return "None" if there's no message or the NEXT message.  That way, the game can decide to get & process all messages, or ignore until it gets to the last.  Can do blocking or non-blocking.
