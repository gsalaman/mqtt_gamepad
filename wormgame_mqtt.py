
# Persistent High Score version of the worm game.

# instead of using time and delays, I'm going to use datetime
# to determine whether I want to run the "update" portion of my loop.
# Still need time for "end game" pause though.

import os

import time
from datetime import datetime

import random

from gamepad_wrapper import Gamepad_wrapper

_shutdown = False

###################################
# Graphics imports, constants and structures
###################################
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

fntLG = ImageFont.truetype('Pillow/Tests/fonts/Courier_New_Bold.ttf', 14)
fntSM = ImageFont.truetype('Pillow/Tests/fonts/times.ttf', 12)

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

sprite_size = 1

# the "draw size" for the apple
apple_size = 7  #apple_size needs to be odd or it will look weird 

###################################
# High Score data
#   High scores are stored as a list of (score,name) tuples
#   Initialize the list with some default data.
###################################
num_high_scores = 5
high_scores = \
[ \
  (0,"DAW"),  \
  (0,"DAW"),  \
  (0,"DAW"),  \
  (0,"DAW"),  \
  (0,"DAW")   \
]

##################################
# Sort Scores
#  Want to sort based on first value
################################## 
def sort_scores(val):
  return(val[0])

##################################
# Show High Scores 
###################################
def show_high_scores():
  global high_scores

  temp_image = Image.new("RGB", (total_columns, total_rows))
  temp_draw = ImageDraw.Draw(temp_image)
  row = 0
  row_size = 14 
  
  high_score_color = (255,0,0)
  
  temp_draw.text((4,row),"High Scores:", fill=(255,0,0), font = fntLG)
  row += row_size

  high_scores.sort(key = sort_scores, reverse=True)

  for score in high_scores:
    temp_draw.text((4,row),score[1]+"  "+str(score[0]), fill=(255,0,0), font = fntLG)
    row += row_size

  matrix.SetImage(temp_image, 0, 0)

##################################
# Eval score 
#   This function checks a passed score to see if it's worthy of our high-score
#   list. 
###################################
def eval_score(score):
  global high_scores
 
  # Make sure we're sorted properly
  high_scores.sort(key=sort_scores,reverse=True)

  if (score > high_scores[-1][0]):
    return True
  else:
    return False
  
##################################
#  Write high score data
#     Will overwrite the "high_scores.txt" file
##################################
def write_high_scores():
  global high_scores

  try:
    with open("high_scores.txt","w") as file:
      for score in high_scores:
        file.write(str(score[0])+","+score[1]+"\n")
  except:
    print("Unable to write high score file");
      
####################################
# Read high score file into high_scores list
####################################
def read_high_scores():
  global high_scores

  try:
    with open('high_scores.txt','r') as f:
      del high_scores[:]
      for line in f:
        line = line.strip()
        score = line.split(",")     
        score[0] = int(score[0])
        high_scores.append(score)
  except:
    print("No high score file found.  Using defaults");
      
##################################
# Input name 
#   This function will return a 3 character string
#   built on arcade-style PS3 inputs
###################################
def input_name():
  global wrapper 
  blacklist_strings = ["ASS","SEX","FAG","FUK","FCK","FUC"]

  # Strings are immutable in Python, so I'm going to operate on this 
  # as a list, and only make it a string (via the "join" method) when needed.
  name = list("AAA")

  temp_image = Image.new("RGB", (total_columns, total_rows))
  temp_draw = ImageDraw.Draw(temp_image)

  # Going to display the 3 chars in the middle, with a 'v' and '^' 
  # above and below to show which char the user is tweaking.
  top_row = 0
  string_row = 10
  bottom_row = 20
  current_char = 0
  column_spacing = 8
  column_offset = 10 
  
  input_color = (0,255,0)
  highlight_color = (255,0,0)
  
  while current_char < 3:
    # Start by indicating which letter we're changing
    # we're gonna erase all three lines first, and then redraw
    temp_draw.rectangle((0,top_row,3*column_spacing+column_offset,bottom_row+10), fill = (0,0,0))

    indicator_position = current_char*column_spacing+column_offset
    temp_draw.text((indicator_position,top_row),"v", highlight_color, font = fntLG)
    temp_draw.text((column_offset,string_row), "".join(name), fill = input_color, font = fntLG)
    temp_draw.text((indicator_position,bottom_row),"^", highlight_color, font = fntLG)
    matrix.SetImage(temp_image, 0, 0)

    # now wait for an input from our gamepad.  
    tmp_input = wrapper.get_next_input()
    while (tmp_input == None):
      if (_shutdown == True):
        exit(0)
      time.sleep(0.001)
      tmp_input = wrapper.get_next_input()

    current_input = (tmp_input)[1]
    
    #if it's an "up", decrement the character
    if (current_input == "up"):
      if (name[current_char] == "A"):
        name[current_char] = "Z"
      else:
        name[current_char] =chr(ord(name[current_char]) - 1)

    #if it's a "down", increment the character
    if (current_input == "down"):
      if (name[current_char] == "Z"):
        name[current_char] = "A"
      else:
        name[current_char] =chr(ord(name[current_char]) + 1)

    #if it's "left", go back one character (if you can). 
    if (current_input == "left"):
      if (current_char > 0):
        current_char = current_char - 1 
    
    #if it's "right", go to the next character
    # note our while loop will end when we finish the third char.
    if (current_input == "right"):
      current_char = current_char + 1
  
  # Now that we've built our string, make sure it's an appropriate 3 letters.
  name_string = "".join(name)
  for bad_name in blacklist_strings:
    if bad_name == name_string:
      return("XXX")
  
  # return our final string.
  return(name_string) 
  
###################################################
#Creates global data
##################################################
#startRange = (matrix_size/4)
edgeBuffer = 10  # number of pixels to avoid around the boarder
wormStartLength = 10
headX = random.randint(edgeBuffer,total_columns- edgeBuffer)
headY = random.randint(edgeBuffer,total_rows- edgeBuffer)

worm = [[headX,headY]]
for i in range(1,wormStartLength):
    worm.append([headX,headY+i])

appleX = 0
appleY = 0
    
worm_color = (255,0,100)
apple_color = (0,255,50)
stem_color = (146,98,13)
black = (0,0,0)

# initial score is 0
score = 0

# initial speed is set with a delay between moving of .1
speed_delay = .5

###############################
# reset globals
###############################
def reset_globals():
  global headX
  global headY
  global edgeBuffer
  global startRange
  global worm
  global wormStartLength
  global score
  global speed_delay

  headX = random.randint(edgeBuffer,total_columns- edgeBuffer)
  headY = random.randint(edgeBuffer,total_rows- edgeBuffer)

  wormStartLength = 10
  del worm[:]

  worm = [[headX,headY]]
  for i in range(1,wormStartLength):
    worm.append([headX,headY+i])

  # initial score is 0
  score = 0

  speed_delay = .08

###################################################
# show_worm
################################################### 
def show_worm(show):
  if show:
    temp_color = worm_color
  else:
    temp_color = black

  temp_image = Image.new("RGB", (sprite_size, sprite_size))
  temp_draw = ImageDraw.Draw(temp_image)

  # Start with a worm as an list of x,y coordinates.
  temp_draw.rectangle((0,0,sprite_size-1,sprite_size-1), outline=temp_color, fill=temp_color)
  for segment in worm:
    matrix.SetImage(temp_image, segment[0],segment[1])

####################################################
# show_head
####################################################
def show_head(): 
  worm_color= (255,0,100)
  temp_image = Image.new("RGB", (sprite_size, sprite_size))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.rectangle((0,0,sprite_size-1,sprite_size-1), outline=worm_color, fill=worm_color)
  matrix.SetImage(temp_image, worm[0][0],worm[0][1])

####################################################
# delete_tail
####################################################
def delete_tail(): 
  worm_color = (0,0,0)  
  temp_image = Image.new("RGB", (sprite_size,sprite_size))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.rectangle((0,0,sprite_size-1,sprite_size-1), outline=black, fill=black)
  matrix.SetImage(temp_image, worm[-1][0],worm[-1][1])


####################################################
# worm_death
####################################################
def worm_death():
  #hide worm
  show_worm(False)  
  
  #animate worm explosion  
  death_color = (255,0,0)
  death_fill = (255,255,255)
  for deathloop in range(3,13,2):
    ellipse_offset = (deathloop-1)/2
    temp_image = Image.new("RGB", (deathloop,deathloop))
    temp_draw = ImageDraw.Draw(temp_image)
    temp_draw.ellipse((0,0,deathloop-1,deathloop-1), outline=death_color, fill=death_fill)
    matrix.SetImage(temp_image, worm[0][0]-ellipse_offset,worm[0][1]-ellipse_offset)
    time.sleep(.1)


####################################################
# show_apple
####################################################
def show_apple(show):
  global edgeBuffer
  global appleX
  global appleY
  if show:
    temp_color = apple_color
    temp_color_stem = stem_color
    appleX = random.randint(edgeBuffer,total_columns - edgeBuffer)
    appleY = random.randint(edgeBuffer,total_rows - edgeBuffer)
  
  else:
    temp_color = black
    temp_color_stem = black

  temp_image = Image.new("RGB", (apple_size, apple_size))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.ellipse((1,2,apple_size-2,apple_size-1), outline=temp_color, fill=temp_color)
  temp_draw.line(((apple_size+1)/2,0,(apple_size-1)/2,1), fill=temp_color_stem)
  matrix.SetImage(temp_image, appleX, appleY)


# temp_draw.line((4,0,3,1), fill=worm_color)
# temp_draw.point((0,0),fill=worm_color)


#######################################################
# check_self_collision
#######################################################
def check_self_collision(passedX, passedY):
  for segment in worm:
    if(segment[0] == passedX) & (segment[1] == passedY):
      return True
  return False

#######################################################
# check_apple_collision
#######################################################
def check_apple_collision(passedX, passedY):
  global wormStartLength
  global speed_delay
  global score
  for segment in worm:
    if(((passedX >= appleX+1) & (passedX <= appleX+5)) & ((passedY >= appleY+2) & (passedY <= appleY+6))):
      wormStartLength= wormStartLength + 1
      score = score + 1
      show_score()
      speed_delay = speed_delay*.9
      return True
  return False

#########################################################
# Print Updates to Terminal
########################################################
def print_updates():
  print "apples hit=", score, "wormLength =", wormStartLength, "speed_delay =", speed_delay

###################################
# show_Score Show score after While Loop is broken
###################################
def show_score():
    global score
    temp_image = Image.new("RGB", (24, 12))
    temp_draw = ImageDraw.Draw(temp_image)
#temp_draw.point((1,1), fill=(255,0,0))
    temp_draw.text((0,0),str(score), fill=(255,0,0), font = fntLG)
    matrix.SetImage(temp_image,3,0)

##########################################
# Play game
#   This is the main game loop.  Will return
#   when this game is over.
##########################################
def play_game():
  global worm
  global score
  global wrapper
  global _shutdown

  reset_globals()

  # player starts in the middle of the screen
  show_worm(True)
  show_apple(True)
  show_score()
  # player starts going up 
  current_dir = "up"

  last_update_time = datetime.now()
  

  while True:
    # start by checking for exit
    if (_shutdown == True):
      exit(0)

    dir_pressed = False
    current_time = datetime.now()
    deltaT = current_time - last_update_time

    input = wrapper.get_next_input()
    if (input == None):
      key = None
    else:
      key = input[1]
    if (key == "up") & (current_dir != "down"):
       current_dir = "up" 
       dir_pressed = True
    if (key == "down") & (current_dir != "up"):
       current_dir = "down" 
       dir_pressed = True
    if (key == "left") & (current_dir != "right"):
       current_dir = "left" 
       dir_pressed = True
    if (key == "right") & (current_dir != "left"):
       current_dir = "right" 
       dir_pressed = True

    # Should probably use positive logic here to update the current direction, 
    # but instead, I'm using the continue construct.
    if ((deltaT.total_seconds() < speed_delay) & (dir_pressed == False)):
      # want to briefly suspend our thread
      time.sleep(0.001)
      continue 
 
    last_update_time = current_time
    
    if current_dir == "up":
      # only move the player if there is room to go up.
      if worm[0][1] > 0:
        newX = worm[0][0]
        newY = worm[0][1]-1
        if check_self_collision(newX,newY):
            worm_death()
            break
        if check_apple_collision(newX,newY):
            print_updates()
            show_apple(False)
            show_worm(True)
            show_apple(True)     
        else:
            delete_tail()
            del worm[-1]

        worm.insert(0,[newX,newY])

        show_head()
      else:
        worm_death()
        break
 
    if current_dir == "left":
      # only move the player if there is room to go up.
      if worm[0][0] > 0:
        newX = worm[0][0]-1
        newY = worm[0][1]
        if check_self_collision(newX,newY):
            worm_death()
            break
        if check_apple_collision(newX,newY):
            print_updates()
            show_apple(False)
            show_worm(True)
            show_apple(True)     
        else:
            delete_tail()
            del worm[-1]

        worm.insert(0,[newX,newY])

        show_head()
      else:
        worm_death()
        break

    if current_dir == "right":
      # only move the player if there is room to go up.
      if worm[0][0] < total_columns-1:
        newX = worm[0][0]+1
        newY = worm[0][1]
        if check_self_collision(newX,newY):
            worm_death()
            break
        if check_apple_collision(newX,newY):
            print_updates()
            show_apple(False)
            show_worm(True)
            show_apple(True)     
        else:
            delete_tail()
            del worm[-1]

        worm.insert(0,[newX,newY])

        show_head()
      else:
        worm_death()
        break

    if current_dir == "down":
      # only move the player if there is room to go up.
      if worm[0][1] < total_rows-1:
        newX = worm[0][0]
        newY = worm[0][1]+1
        if check_self_collision(newX,newY):
            worm_death()
            break
        if check_apple_collision(newX,newY):
            print_updates()
            show_apple(False)
            show_worm(True)
            show_apple(True)     
        else:
            delete_tail()
            del worm[-1]

        worm.insert(0,[newX,newY])

        show_head()
      else:
        worm_death()
        break

  # Now that were done, empty any move commands outta the queue.
  wrapper.empty_commands()

def shutdown_cb():
  global _shutdown

  print("Got the shutdown callback!!!")
  _shutdown = True 

####################################
# Main loop
####################################
# wait for a controller to connexct.
temp_image = Image.new("RGB", (total_columns, total_rows))
temp_draw = ImageDraw.Draw(temp_image)
temp_draw.text((0,0),"Waiting for controller", fill=(255,0,0), font = fntLG)
matrix.SetImage(temp_image, 0, 0)

wrapper = Gamepad_wrapper(1)
wrapper.set_shutdown_cb(shutdown_cb)
while wrapper.player_count() != 1:
  # check for exit
  if (_shutdown == True):
    exit(0)

  # briefly suspend our thread
  time.sleep(0.001)


while True:
  # Show High Scores, waiting for any input to start.
  read_high_scores()
  show_high_scores()
  
  # Because we now need to look for shutdown events, we cannot block.
  # change this to a non-blocking read, checking for input and shutdown.  
  #wrapper.blocking_read()
  while (wrapper.get_next_input() == None):
    if (_shutdown == True):
      exit(0)

  #blank the screen
  temp_image = Image.new("RGB", (total_columns, total_rows))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.rectangle((0,0,total_columns, total_rows), fill=(0,0,0))
  matrix.SetImage(temp_image, 0, 0)

  # play the game
  play_game()

  # How did you do?  If good enough, input a new high score.
  if eval_score(score):
    my_name = input_name()
    high_scores.append([score,my_name]) 
    high_scores.sort(key=sort_scores,reverse=True)
    del high_scores[-1]
    write_high_scores()
  else:
    show_score()
    time.sleep(5)

