#################################################
# cycles.py - tron style light cycle game
#
# Two players (green and blue).
# Input from MQTT wrapper 
# Lose when you hit something.
################################################# 

import time
from datetime import datetime

import random

from gamepad_wrapper import Gamepad_wrapper

###################################
# Graphics imports, constants and structures
###################################
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

# this is the size of ONE of our matrixes. 
matrix_rows = 64 
matrix_columns = 64 

# how many matrixes stacked horizontally and vertically 
matrix_horizontal = 1 
matrix_vertical = 1

total_rows = matrix_rows * matrix_vertical
total_columns = matrix_columns * matrix_horizontal

options = RGBMatrixOptions()
options.rows = matrix_rows 
options.cols = matrix_columns 
options.chain_length = matrix_horizontal
options.parallel = matrix_vertical 

#options.hardware_mapping = 'adafruit-hat-pwm' 
#options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
options.hardware_mapping = 'regular'  

options.gpio_slowdown = 2

matrix = RGBMatrix(options = options)

###################################################
#Creates global data
# Update this comment!!!
###################################################

black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)

wall_color = red 

# start positions:  p1 at the top middle going down, p2 at bottom middle going up.
p1_start_x = total_columns / 2
p1_start_y = 5
p2_start_x = p1_start_x
p2_start_y = total_rows - p1_start_y

player1 = [p1_start_x,p1_start_y]
p1_color = green 

player2 = [p2_start_x,p2_start_y]
p2_color = blue 


# The collision matrix is a 2d matrix of our full playfield size.
# Zero means there's nothing in that slot.
# One means you can't move there.
collision = []
#collision = [[0] * total_rows for i in range(total_columns)]

speed_delay = .1

###################################
# reset_collision()
###################################
def reset_collision():

  # The collision matrix is a 2d matrix of our full playfield size.
  # Zero means there's nothing in that slot.
  # One means you can't move there.
  global collision

  del collision[:]
  collision = [[0] * total_rows for i in range(total_columns)]

###################################
# init_walls()
###################################
def init_walls():
  global collision
  global wall_color

  #top and bottom boarders
  for x in range(total_columns):
    collision[x][0] = 1
    collision[x][total_rows-1] = 1

  #left and right boarders
  for y in range(total_rows):
    collision[0][y]= 1
    collision[total_columns-1][y] = 1

  #now draw the box
  temp_image = Image.new("RGB", (total_columns, total_rows))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.rectangle((0,0,total_columns-1,total_rows-1), outline=wall_color)
  matrix.SetImage(temp_image, 0,0)

###################################
# init_players
###################################
def init_players():
  global collision
  global p1_start_x
  global p1_start_y
  global p2_start_x
  global p2_start_y
  global p1_color
  global p2_color
  global player1
  global player2

  player1 = [p1_start_x,p1_start_y]
  player2 = [p2_start_x,p2_start_y]

  collision[p1_start_x][p1_start_y] = 1
  collision[p2_start_x][p2_start_y] = 1

  temp_image = Image.new("RGB", (1,1))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.rectangle((0,0,0,0), outline=p1_color, fill=p1_color)
  matrix.SetImage(temp_image, p1_start_x, p1_start_y)
  temp_draw.rectangle((0,0,0,0), outline=p2_color, fill=p2_color)
  matrix.SetImage(temp_image, p2_start_x, p2_start_y)

####################################################
# show_crash() 
####################################################
def show_crash(crash_x, crash_y):
  
  crash_color = (255,0,0)
  crash_fill = (255,255,255)
  for crashloop in range(3,13,2):
    ellipse_offset = (crashloop-1)/2
    temp_image = Image.new("RGB", (crashloop,crashloop))
    temp_draw = ImageDraw.Draw(temp_image)
    temp_draw.ellipse((0,0,crashloop-1,crashloop-1), outline=crash_color, fill=crash_fill)
    matrix.SetImage(temp_image, crash_x-ellipse_offset,crash_y-ellipse_offset)
    time.sleep(.15)

  time.sleep(1)

###################################
#  display_text()
###################################
def display_text(my_text, text_color, delay):
    temp_image = Image.new("RGB", (total_columns, total_rows))
    temp_draw = ImageDraw.Draw(temp_image)
    temp_draw.text((0,0),my_text, fill=text_color)
    matrix.SetImage(temp_image,0,0)
    time.sleep(delay)

########################################
# apply_input
########################################
def apply_input(new_input, current_dir):

    # check for direction changes, but don't let them back into themselves
    if (new_input == "up") & (current_dir != "down"):
      return "up" 
    elif (new_input == "down") & (current_dir != "up"):
      return "down" 
    elif (new_input == "left") & (current_dir != "right"):
      return "left" 
    elif (new_input == "right") & (current_dir != "left"):
      return "right"
    else:
      return None
########################################
# next_player_location
########################################   
def next_player_location(current_pos, dir):

    # current_pos is a tuple of the current (x,y) position
    new_x = current_pos[0]
    new_y = current_pos[1]

    #figure out next spot for that player 
    if (dir == "up"):
      new_y = new_y - 1
    if (dir == "down"):
      new_y = new_y + 1
    if (dir == "left"):
      new_x = new_x - 1
    if (dir == "right"):
      new_x = new_x + 1

    # now return the new position as a tuple
    return [new_x,new_y]

###################################
# play_game 
###################################
def play_game():
  global player1
  global player2

  display_text("Get Ready",red, 3)
  display_text("3",red,1)
  display_text("2",red,1)
  display_text("1",red,1)
  display_text("GO!!!",red,1)

  reset_collision()
  init_walls()
  init_players()
 
  p1_dir = "down"
  p2_dir = "up"

  p1_image = Image.new("RGB", (1,1))
  p1_draw = ImageDraw.Draw(p1_image)
  p1_draw.rectangle((0,0,0,0), outline=p1_color, fill=p1_color)

  p2_image = Image.new("RGB", (1,1))
  p2_draw = ImageDraw.Draw(p2_image)
  p2_draw.rectangle((0,0,0,0), outline=p2_color, fill=p2_color)

  p1_crash = False
  p2_crash = False

  last_update_time = datetime.now()

  while True:

    dir_pressed = False
    current_time = datetime.now()
    deltaT = current_time - last_update_time

    # get the next input, checking for direction changes...but don't let that player
    # back into themselves.
    input = wrapper.get_next_input()
    if input != None:
      if input[0] == "player1":
        new_dir = apply_input(p1_dir, input[1])
        if (new_dir != None):
          p1_dir = input[1]
          dir_pressed = True
      elif input[0] == "player2":
        new_dir = apply_input(p2_dir, input[1])
        if (new_dir != None):
          p2_dir = input[1]
          dir_pressed = True
      else:
        print("unexpected player input: ")
        print input[0]
        exit(1)

    # Should probably use positive logic here to update the current direciton,
    # but instead, I'm using the continue construct.
    if ((deltaT.total_seconds() < speed_delay) & (dir_pressed == False)):
      time.sleep(.001)
      continue

    last_update_time = current_time

    # The engine!
    # If both p1 and p2 are going to hit something, it's a draw.
    # If only p1 or p2 hits something, it's a win for the other one.
    # if neither are going to hit anything, update the collision matrix 
    # and add the new "dot"

    #figure out next spot for p1
    p1_new_pos = next_player_location(player1,p1_dir)

    # will the new spot for p1 cause a crash?
    if (collision[p1_new_pos[0]][p1_new_pos[1]] == 1):
      print "Player 1 crashes!!!"
      p1_crash = True
    else:
      collision[p1_new_pos[0]][p1_new_pos[1]] = 1
      player1 = p1_new_pos
      matrix.SetImage(p1_image, p1_new_pos[0], p1_new_pos[1])

    #figure out next spot for p2
    p2_new_pos = next_player_location(player2,p2_dir)

    # will the new spot for p1 cause a crash?
    if (collision[p2_new_pos[0]][p2_new_pos[1]] == 1):
      print "Player 2 crashes!!!"
      p2_crash = True
    else:
      collision[p2_new_pos[0]][p2_new_pos[1]] = 1
      player2 = p2_new_pos
      matrix.SetImage(p2_image, p2_new_pos[0], p2_new_pos[1])

    if (p1_crash & p2_crash):
      print "Tie game!!!"
      show_crash(p1_new_pos[0],p1_new_pos[1])
      display_text("TIE!", red, 3)
      break;

    if (p1_crash):
      print "Player 2 wins!"
      show_crash(p1_new_pos[0],p1_new_pos[1])
      display_text("Player 2\nWins!",blue,3)
      break;

    if (p2_crash):
      print "Player 1 wins!"
      show_crash(p2_new_pos[0],p2_new_pos[1])
      display_text("Player 1\nWins!",green,3)
      break;

    time.sleep(speed_delay)

###################################
# Main loop 
###################################

# since this is the two player version, wait for 2 players to connect.
display_text("Waiting for\nPlayer1\nPlayer2",red,0)
wrapper = Gamepad_wrapper(2)
while wrapper.player_count() == 0:
  # no display update needed...just suspend for a little
  time.sleep(0.001)
display_text("Waiting for\n\nPlayer2",red,0)
while wrapper.player_count() == 1:
  # suspend again...
  time.sleep(0.001)

# now we should have 2 players connected.

while True:

  # Wait to start until one of the two players hits a key
  display_text("Press Any\nButton to\nStart", green, 3)
  wrapper.blocking_read()

  play_game()
