#################################################
# cycles.py - tron style light cycle game
#
# Four player version!!! 
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
yellow = (0,255,255)
purple = (255,0,255)

wall_color = red 

player_color = [green, blue, yellow, purple] 

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

####################################################
# show_crash() 
####################################################
def show_crash(crash_x, crash_y):

  crash_color = (255,255,255)
  
  temp_image = Image.new("RGB", (1,1))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.rectangle((0,0,0,0), outline=crash_color, fill=crash_color)
  matrix.SetImage(temp_image, crash_x,crash_y)

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
def play_game(num_players):
  global total_rows
  global total_columns
  global collision
  global matrix

  # this version is hardcoded to 4 players
  if (num_players != 4):
    print("num_players = "+str(num_players))
    exit(1)

  player_pos = [
    [total_columns/2,5],
    [total_columns/2,total_rows - 5], 
    [5,total_rows/2],
    [total_columns - 5, total_rows/2]
  ]

  display_text("Get Ready",red, 3)
  display_text("3",red,1)
  display_text("2",red,1)
  display_text("1",red,1)
  display_text("GO!!!",red,1)

  reset_collision()

  init_walls()

  player_image = []
  player_draw = []

  for player_index in range(0,num_players): 
    pos = player_pos[player_index]
    collision[pos[0]][pos[1]] = 1
  
    color = player_color[player_index]

    temp_image = Image.new("RGB", (1,1))
    temp_draw = ImageDraw.Draw(temp_image)
    temp_draw.rectangle((0,0,0,0), 
                        outline=color,
                        fill=color)
    player_image.append(temp_image)
    player_draw.append(temp_draw)
    matrix.SetImage(temp_image, pos[0], pos[1])
    
  player_dir = ["down", "up", "right", "left"]
 
  player_crashed = [False, False, False, False]
 
  last_update_time = datetime.now()

  while True:

    dir_pressed = False
    current_time = datetime.now()
    deltaT = current_time - last_update_time

    # get the next input, checking for direction changes...but don't let that 
    # player back into themselves.
    input = wrapper.get_next_input()
    if input != None:
      if input[0] == "player1":
        index = 0
      elif input[0] == "player2":
        index = 1
      elif input[0] == "player3":
        index = 2
      elif input[0] == "player4":
        index = 3
      else:
        print("unexpected player input: ")
        print input[0]
        exit(1)
      new_dir = apply_input(player_dir[index], input[1])
      if (new_dir != None):
        player_dir[index] = input[1]
        dir_pressed = True

    # Should probably use positive logic here to update the current direciton,
    # but instead, I'm using the continue construct.
    if ((deltaT.total_seconds() < speed_delay) & (dir_pressed == False)):
      time.sleep(.001)
      continue

    last_update_time = current_time

    # The engine!
    # Figure out the new spots for all players
    for index in range(0,num_players):
      # Don't update for crashed players
      if (player_crashed[index]):
        continue

      new_pos = next_player_location(player_pos[index], player_dir[index])

      # will the new spot cause a crash?
      if (collision[new_pos[0]][new_pos[1]] == 1):
        print("Player "+str(index+1)+" crashes!!!")
        player_crashed[index] = True
        show_crash(player_pos[index][0],player_pos[index][1])
      else:
        collision[new_pos[0]][new_pos[1]] = 1
        player_pos[index] = new_pos
        matrix.SetImage(player_image[index], new_pos[0], new_pos[1])

    # I think this needs to be a separate loop from above, as I want the crash
    # checks to happen *AFTER* updating all players.  Better tie resolution?
    # Confirm later...
    crash_count = 0
    for index in range(0, num_players):
      if (player_crashed[index]):
        crash_count += 1 

    # If there's only one (or zero!) players left, we're done.
    if ((num_players - crash_count) <= 1):
      break;

    time.sleep(speed_delay)
  
  # End of while loop.  
  # Who was left standing?
  for winner_index in range(0, num_players):
    if (player_crashed[winner_index] == False):
      winner_str="Player "+str(winner_index+1)+" WINS!!!"
      display_text(winner_str, red, 3)
      break;

  if winner_index == num_players:
    display_text("TIE GAME", red, 3)
  

###################################
# Main loop 
###################################

# since this is the two player version, wait for 2 players to connect.
display_text("Waiting for\nPlayer1\nPlayer2\nPlayer3\nPlayer4",red,0)
wrapper = Gamepad_wrapper(2)
while wrapper.player_count() == 0:
  # no display update needed...just suspend for a little
  time.sleep(0.001)
display_text("Waiting for\nPlayer2\nPlayer3\nPlayer4",red,0)
while wrapper.player_count() == 1:
  # suspend again...
  time.sleep(0.001)
display_text("Waiting for\nPlayer3\nPlayer4",red,0)
while wrapper.player_count() == 2:
  # suspend again...
  time.sleep(0.001)
display_text("Waiting for\nPlayer4",red,0)
while wrapper.player_count() == 3:
  # suspend again...
  time.sleep(0.001)

# now we should have 4 players connected.

while True:

  # Wait to start until one of the two players hits a key
  display_text("Press Any\nButton to\nStart", green, 3)
  wrapper.blocking_read()

  play_game(4)
