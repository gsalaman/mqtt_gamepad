###############################
#  Imports for reading keyboard
##############################
import sys, os
import termios, fcntl

# used to slow down our main loop
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from broker import read_broker

player = ""
registration_complete = False

##################################
# Non-blocking character read function.
#################################
def getch_noblock():
  try:
    return sys.stdin.read()
  except (IOError, TypeError) as e:
    return None

################################
#  Initialize keyboard reading. 
#  Save the old terminal configuration, and
#  tweak the terminal so that it doesn't echo, and doesn't block.
################################

fd = sys.stdin.fileno()
newattr = termios.tcgetattr(fd)

oldterm = termios.tcgetattr(fd)
oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)

newattr[3] = newattr[3] & ~termios.ICANON
newattr[3] = newattr[3] & ~termios.ECHO

fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

termios.tcsetattr(fd, termios.TCSANOW, newattr)


###################
def print_cmds():
  print ("Controls:")
  print ("Up:    i")
  print ("Left:  j")
  print ("Down:  k")
  print ("right: l")
  print ("q to quit")
 
####################
def on_message(client,userdata,message):
  global registration_complete 
  global player

  # right now, the only message we've subscribed to is the registration
  # response, so I don't need to check topic.

  print("Message callback")

  player = message.payload
  registration_complete = True
  

###
# main code here...
###
broker_address = read_broker()
client_name = "key_term"
client = mqtt.Client(client_name)
client.will_set("register/release", client_name)
try:
  client.connect(broker_address)
except:
  print "Unable to connect to MQTT broker"
  exit(0)
client.loop_start()
client.on_message=on_message

# send the registration request
subscribe_str = "register/"+client_name
print("subscribing to "+subscribe_str)
client.subscribe(subscribe_str)
client.publish("register/request", client_name)
last_reg_time = datetime.now()


try:
  print("waiting for game...")
  while (registration_complete != True):
    # is it time to try registering again?
    current_time = datetime.now()
    deltaT = current_time - last_reg_time
    if (deltaT.total_seconds() > 2):
      print("registration timed out.  Retrying...")
      client.publish("register/request", client_name)
      last_reg_time = current_time;
  print("registration complete")

  print_cmds()
  while True:
    key = getch_noblock()

    if key == 'i':
      client.publish(player,"up")
      print "up"
    elif key == 'j':
      client.publish(player,"left")
      print "left"
    elif key == 'k':
      client.publish(player,"down")
      print "down"
    elif key == 'l':
      client.publish(player,"right")
      print "right"
    elif key == 'q':
      break;
    elif key == None:
      continue;
    else:  
      print "unknown key: "+key
      print_cmds()
except KeyboardInterrupt:
  pass

###################################
# Reset the terminal on exit
###################################
termios.tcsetattr(fd, termios.TCSANOW, oldterm)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

# No explicit release needed...last will takes care of this.
