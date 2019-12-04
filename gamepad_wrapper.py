import time
import paho.mqtt.client as mqtt
from broker import read_broker

_input_q = []

# _player_list is a list of (client, player) pairs.  This needs to be outside 
# the GamepadWrapper class because the MQTT callback needs to access it.
# 
# This will be initialized in the constructor for the GamepadWrapper class 
# with the max possible number of players.  Each entry will start out as None,
# and as clients register, we'll fill in the appropriate item of the list.
# If a client de-registers, we'll change that entry back to None.
# 
_player_list = []

_client = mqtt.Client("Gamepad_Wrapper")

def default_shutdown_cb():
  #default shutdown does nothing
  print("default shutdown callback:  does nothing");

_shutdown_cb = default_shutdown_cb

def process_shutdown():
  global _shutdown_cb

  # call the shutdown callback
  _shutdown_cb()


def process_register_release(payload):
  global _player_list

  # find the client
  index = 0
  for player in _player_list:
    if (player != None):
      if (player[0] == payload):
        print("Deregistering client "+payload)
        _player_list[index] = None
        return
    index += 1
      
def process_register_request(payload):
  global _player_list
  global _client

  # First check:  Make sure that player's client isn't already registered.
  for player in _player_list:
    if (player != None):
      if (player[0] == payload):
        print("Client "+payload+" already registered!!!")
        return

  # Next, find an empty spot in our client/player mappings
  player_index = 0
  found_empty_spot = False
  for player in _player_list:
    if (player == None):
      # note player_index is the index of our empty slot in the player list.
      # player NUMBER is 1-based...index 0 corresponds with player1, 
      #   index 1 with player2, etc.
      player_number = player_index+1 
      found_empty_spot = True
      break;
    player_index += 1

  # if we didn't find an empty spot, don't give a player back to the client.
  # eventually, we'll want a reject code here.
  if (found_empty_spot == False):
    print("No empty spots found!")
    return 
      
  # the payload of a register/request is the client ID.  Build that into
  # our response
  topic = "register/"+payload
  player_string = "player"+str(player_number)

  print ("Subscribing to "+player_string)
  _client.subscribe(player_string)
  print ("Responding to client "+payload+" with "+player_string)
  _client.publish(topic, player_string)
  _player_list[player_index] = [payload,player_string]

def process_player_command(player, payload):
  global _input_q

  #print ("process player command")
  print("added "+payload+" to "+player)

  _input_q.append([player,payload])


def on_message(client,userdata,message):

  print("Received "+message.topic+","+message.payload)

  if (message.topic == "register/request"):
    process_register_request(message.payload)
  elif (message.topic == "register/release"):
    process_register_release(message.payload)
  elif (message.topic == "shutdown"):
    process_shutdown()
  else:
    process_player_command(message.topic,message.payload)

class Gamepad_wrapper():

  def __init__(self, max_num_players):
    global _client
 
    # initialize our client/player mapping. 
    for i in range(0,max_num_players):
      _player_list.append(None)

    self.brokername = read_broker()
 
    _client.on_message=on_message
    try:
      _client.connect(self.brokername)
    except:
      print("Unable to connect to MQTT broker: "+self.brokername)
      exit(0)

    _client.loop_start()
    
    # don't want this to be "register/#" because then we'd see the registration
    # responses, and our callback won't handle those.
    _client.subscribe("register/request") 
    _client.subscribe("register/release")
    _client.subscribe("shutdown");
    
  def set_shutdown_cb(self, cb):
    global _shutdown_cb

    _shutdown_cb = cb
    print("set shutdown callback")

  def get_next_input(self):
    global _input_q

    if (len(_input_q) > 0):
      input = _input_q[0]
      del _input_q[0]
      return input
    else:
      return None

  def blocking_read(self):
    global _input_q
 
    # wait until we have something in our queue
    queue_length = len(_input_q)
    while (queue_length == 0):
      time.sleep(0.001)
      queue_length = len(_input_q)
  
    # now read and return the next item.
    input = _input_q[0]
    del _input_q[0]
    return input

  def player_count(self):
    global _player_list

    # walk through the player list and count the number of connected players
    player_count = 0
    for player in _player_list:
      if player != None:
        player_count += 1
    return player_count 
  
  def empty_commands(self):
    global _input_q

    del _input_q
    _input_q = []

  def check_connected(self, player_name):
    global _player_list
    

    # find that player in our list.
    found = False
    for player in _player_list:
      if (player != None):
        if (player[1] == player_name):
          found = True
          break

    return found
