import time

import paho.mqtt.client as mqtt

_input_q = []
_player_list = []
_client = mqtt.Client("Gamepad_Wrapper")

def process_register_request(payload):
  global _player_list
  global _client

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

  print ("process player command")
  print("added "+payload+" to "+player)

  _input_q.append([player,payload])


def on_message(client,userdata,message):

  print("Received "+message.payload)

  if (message.topic == "register/request"):
    process_register_request(message.payload)
  else:
    print "else clause"
    process_player_command(message.topic,message.payload)

class Gamepad_wrapper():

  def __init__(self, players):
    global _client
 

    self.expected_players = players

    self.brokername = "10.0.0.17"
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

  def player_count(self):
    global _player_list
    return len(_player_list) 
