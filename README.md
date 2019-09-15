# mqtt_gamepad
## Requirement/Design Thoughts
3 pieces:
* gamepad "app" itself.  Could be something that connects to USB joysticks via evdev, or just a tkinter python program, or something else.  It'll broadcast text strings for it's direction and buttons.
* a consumer "wrapper api" that talks MQTT and returns strings.  Probably want blocking and non-blocking reads, and some way eventually "register" (hey, I'm player 1!). The wrapper app should be a python module that the game itself imports.
* And then the game.  It uses the wrapper api to acually implement the game.

So, with that, here's a simple starting example:  
Write a gui app that does "up/down/left/right".  Each command will publish "player1/dir" with the payload being direction.  Could also embed it and make the topic "player1/dir/up" with the expandablily being "start" and "stop" to reflect button press and release.

The wrapper API is going to store ALL the received commands.  I can come up with cases where the api wants to consume all, or just the last one.  If we've got some sort of a "queue-size" indicator, we can do both blocking and non-blocking (wait for queue to be non-zero if blocking...if non-blocking, don't do anything)

