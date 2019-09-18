###############################
#  Imports for reading keyboard
##############################
import sys, os
import termios, fcntl

# used to slow down our main loop
import time

import paho.mqtt.client as mqtt

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
 
###
# main code here...
###
broker_address = "10.0.0.17"
#broker_address = "makerlabPi1"
client = mqtt.Client("key_term")
try:
  client.connect(broker_address)
except:
  print "Unable to connect to MQTT broker"
  exit(0)


print_cmds()
player = "player1"

while True:
  key = getch_noblock()

  if key == 'i':
    client.publish(player+"/up", "1")
    print "Up"
  elif key == 'j':
    client.publish(player+"/left", "1")
    print "Left"
  elif key == 'k':
    client.publish(player+"/down", "1")
    print "down"
  elif key == 'l':
    client.publish(player+"/right", "1")
    print "right"
  elif key == 'q':
    break;
  elif key == None:
    continue;
  else:  
    print "unknown key: "+key
    print_cmds()

###################################
# Reset the terminal on exit
###################################
termios.tcsetattr(fd, termios.TCSANOW, oldterm)

fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
