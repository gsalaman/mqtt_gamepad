###################################################
# MQTT GAMEPAD WRAPPER
#
# Takes any number of connected gamepads, registers them
# with our broker, and then sends inputs over MQTT.
###################################################

import evdev
from broker import read_broker
import paho.mqtt.client as mqtt
import time

# Broker init
broker_address = read_broker()

# list of evdev gamepads. 
dev_list = []

# list of MQTT clients.  
client_list = []

# Client name will be our index into the associated lists tagged on to 
# the following string.
client_name_base = "mqtt_gamepad"

# list of player names associated with those clients
player_name_list = [] 

supported_gamepads = [ 
    'Sony PLAYSTATION(R)3 Controller'
]

#################################
# parse_ps3 
#   parses a single event and returns a string that represents that event.
#################################
def parse_ps3(event):

    # These are the key definitions for the ps3 controller 
    d_up = 544
    d_down = 545
    d_left = 546
    d_right = 547

    # parse keypress events
    if event.type ==evdev.ecodes.EV_KEY:

      # 1 indicates key press.  0 indicates release
      if event.value == 1:
        if event.code == d_up:
          return("up")
        elif event.code == d_down:
          return("down")
        elif event.code == d_left:
          return("left") 
        elif event.code == d_right: 
          return("right")

#################################
# parse_generic_usb 
#   parses a single event and returns a string that represents that event.
#  NEEDS TO BE UPDATED!!!
#################################
def parse_generic_usb(event):

    # These are the key definitions for the generic USB joystick
    d_up = 544
    d_down = 545
    d_left = 546
    d_right = 547
    x = 288
    y = 291
    a = 289
    b = 290
    select = 296
    start = 297
    right_bumper = 293
    left_bumper = 292 

    # parse keypress events
    if event.type ==ecodes.EV_KEY:

      # 1 indicates key press.  0 indicates release
      if event.value == 1:
        if event.code == x:
          return("X")
        elif event.code == y:
          return("Y")
        elif event.code == a:
          return("A") 
        elif event.code == b: 
          return("B")
        elif event.code == select:
          return("Select")
        elif event.code == start:
          return("Start")
        elif event.code == right_bumper:
          return("Right-bumper")
        elif event.code == left_bumper:
          return("Left-bumper")

    # type 3 are absolute axis events.  The D-pad uses these.
    if event.type == 3:
      # code 0 are x axis events
      if (event.code == 0):
        if event.value == 0:
          return("D-left")
        if event.value == 255:
          return("D-right")
        # ignoring the "return to center" value of 127.

      # code 1 are y axis events
      if (event.code == 1):
        if event.value == 0:
          return("D-up")
        if event.value == 255:
          return("D-down")
  
################################################
# parse_event 
#  
################################################
def parse_event(device, event):

  if event == None:
    return None

  # figure out which lookup translation we need based on gamepad index
  gamepad_name = device.name
  if (gamepad_name == "Sony PLAYSTATION(R)3 Controller"):
    return parse_ps3(event)
  elif (gamepad_name == "USB Gamepad "):
    return parse_generic_usb(event)
  else:
    print "Unsupported gamepad type in parse event: "+gamepad_name
    exit(0)

# The only message I'm subscribed to is the client's registration response,
# and those are happening one at a time, so I *think* I can reuse this 
# callback for all client registrations.  I'm using the global "player_string"
# to pass info back and forth.
player_string = None
def on_message(client,userdata,message):
  global player_string
 
  print("Message Callback")
  player_string = message.payload


valid_gamepad_count = 0

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
  for supported_gamepad in supported_gamepads:
    if device.name == supported_gamepad:

        # at this point, we've found a supported gamepad.  We'll
        # start by adding it to our dev_list
        dev_list.append(evdev.InputDevice(device.path)) 
        print "found "+device.name+" as "+device.path
 
        # next, we need a unique MQTT client identifier for this gamepad
        client_name = client_name_base+str(valid_gamepad_count)
        print("connecting to "+broker_address+" as "+client_name)
        client = mqtt.Client(client_name)
        try:
          client.connect(broker_address)
        except:
          print("Unable to connect")
          exit(1)
        print("Connected!")
        
        # now we need to get a player ID for this client, via a handshake
        # with the broker.   
        player_string = None
        client.loop_start()
        client.on_message=on_message
        subscribe_str = "register/"+client_name
        print("subscribing to "+subscribe_str)
        client.subscribe(subscribe_str)
        client.publish("register/request",client_name)
        print("waiting for game...")
        while (player_string == None):
          time.sleep(0.001)
        print ("received "+player_string)

        # okay, we've registered.  Go ahead and add this client and name
        # to the appropriate lists.
        client_list.append(client)
        player_name_list.append(player_string) 
       
        valid_gamepad_count = valid_gamepad_count + 1

        print("-----------------")

if (valid_gamepad_count == 0):
    print("No gamepads found")
    exit(1)

### The big loop!
while True:
  for index in range(0,len(dev_list)):
    dev = dev_list[index]
    player = player_name_list[index]
    client = client_list[index]
    event = dev_list[index].read_one()
    event_string = parse_event(dev,event)
    if (event_string != None):
      client.publish(player, event_string)
      print("published "+event_string+" as "+player)
