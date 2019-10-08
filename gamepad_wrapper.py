import time
import paho.mqtt.client as mqtt
from broker import read_broker

_input_q = []
_player_list = []
_client = mqtt.Client("Gamepad_Wrapper")

def process_register_request(payload):
  global _player_list
  global _client

  # First check:  Make sure that player's client isn't already registered.
  for player in _player_list:
    if (player[0] == payload):
      print("Client "+payload+" already registered!!!")
      return

  player_count = len(_player_list) + 1
  
  # the payload of a register/request is the client ID.  Build that into
  # our response
  topic = "register/"+payload
  player_string = "player"+str(player_count)

  print ("Subscribing to "+player_string)
  _client.subscribe(player_string)
  print ("Responding to client "+payload+" with "+player_string)
  _client.publish(topic, player_string)
  
  _player_list.append([payload,player_string])


def process_player_command(player, payload):
  global _input_q

  #print ("process player command")
  print("added "+payload+" to "+player)

  _input_q.append([player,payload])


def on_message(client,userdata,message):

  print("Received "+message.payload)

  if (message.topic == "register/request"):
    process_register_request(message.payload)
  else:
    process_player_command(message.topic,message.payload)

class Gamepad_wrapper():

  def __init__(self):
    global _client
 
    self.brokername = read_broker()
 
    _client.on_message=on_message
    try:
      _client.connect(self.brokername)
    except:
      print("Unable to connect to MQTT broker: "+self.brokername)
      exit(0)

    _client.loop_start()
    _client.subscribe("register/request") 
    
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
    return len(_player_list) 
  
  def empty_commands(self):
    global _input_q

    del _input_q
    _input_q = []
