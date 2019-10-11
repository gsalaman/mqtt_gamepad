################################################
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
from PIL import Image, ImageDraw, ImageFont

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
    global display_text_font

    temp_image = Image.new("RGB", (total_columns, total_rows))
    temp_draw = ImageDraw.Draw(temp_image)
    temp_draw.text((0,0),my_text, fill=text_color, font=display_text_font)
    matrix.SetImage(temp_image,0,0)
    time.sleep(delay)

###################################
#  centered_text()
###################################
def centered_text(my_text, box_color, text_color, font, delay):
    global total_columns
    global total_rows
    global matrix

    # getsize returns a tuple of the x and y size of the font string.
    text_size = font.getsize(my_text)
    
    # we're going to draw a box around that text, so we need a little buffer
    # this is going to be the buffer for each side.
    pixel_buffer = 2
    box_size_x = text_size[0] + (2*pixel_buffer)
    box_size_y = text_size[1] + (2*pixel_buffer)

    text_image = Image.new("RGB", (box_size_x, box_size_y))
    text_draw = ImageDraw.Draw(text_image)
    box = (0,0,box_size_x-1,box_size_y-1)
    text_draw.rectangle(box, outline=box_color)

    # do some math to center our box
    # box_x and box_y define the top left corner
    box_x = (total_columns - box_size_x)/2 
    box_y = (total_rows - box_size_y)/2

    text_draw.text((pixel_buffer,pixel_buffer),my_text, fill=text_color, font=font)

    matrix.SetImage(text_image,box_x,box_y)
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
  global player_data_list
  global display_text_font
  

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
  player_place = []  
 
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
        player_place.append(player_data_list[index].name_str) 
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

  # End of while loop.  

  # Who was left standing?
  for winner_index in range(0, num_players):
    if (player_crashed[winner_index] == False):
      player_place.append(player_data_list[winner_index].name_str)
      winner_string = player_data_list[winner_index].name_str+" WINS!!!"
      winner_color = player_data_list[winner_index].color
      centered_text(winner_string,(255,255,255),winner_color,display_text_font, 10) 
      break;
  
  if winner_index == num_players:
    display_text("TIE GAME", red, 3)

  return player_place
  
class PlayerData():
  def __init__(self, name, color, num):
    self.name_str = name
    self.color = color 
    self.state = "Disconnect"
    self.player_name_size = 7
    self.ready_index = self.player_name_size
    self.char_index = 0
    self.row_height = 14
    
    # A note on character width:  we're using truetype fonts, which means
    # the character can be drawn *BEFORE* the left-hand boundary.  To 
    # combat this, we'll put in a "buffer zone" 
    self.char_width =  9 
    self.char_buffer = 2  

    self.player_number = num
    self.disconnect_color = (255,0,0)
    self.name_color = (0,0,255)
    self.highlight_color = (255,0,0)
    
  def erase_line(self):
    player_data_draw.rectangle((0,self.player_number*self.row_height, 
                         total_columns, self.row_height*(self.player_number+1)),
                         fill = (0,0,0)) 
    matrix.SetImage(player_data_image, 0, 0)

  def show_disconnect(self):
    global matrix
    global player_data_image
    global player_data_draw
    global player_data_font

    disc_color = (255,0,0)
    tmp_str = "P"+str(self.player_number + 1)+" DISCONNECTED"
    player_data_draw.text((0, self.player_number*self.row_height),
                   tmp_str,
                   fill = disc_color, font = player_data_font)
    matrix.SetImage(player_data_image, 0, 0)

  def show_line(self):
    self.erase_line()
    index = 0
    for c in self.name_str:
      self.show_char(c, index,(index == self.char_index)) 
      index += 1
    self.show_ready()

  def set_connected(self):
    self.state = "Input"
    self.show_line()

  def show_color(self):
    #coming soon
    pass
  
  def show_ready(self):
    # for now, start ready 2 chars after the player name.
    #ready_start_column = self.char_width * (self.player_name_size + 2) 
    ready_start_column = self.char_width * (self.player_name_size) 

    # start by setting the text string to either ready or not.
    if (self.state == "Ready"):
      text = " READY"
    else:
      text = "!READY"

    # if our cursor is on the ready indicator, make the text white
    if (self.char_index == self.ready_index):
      color = (255,255,255)
    elif (self.state == "Ready"):
      color = (0,255,0)
    else:
      color = (255,0,0)

    # where is the top left corner of this string?
    corner = (ready_start_column, 
              self.player_number*self.row_height)

    #start by blanking the space this string is going into
    player_data_draw.rectangle(
       (corner[0],
        corner[1],
        corner[0]+(self.char_width*len(text)),
        corner[1]+self.row_height),
       fill = (0,0,0)) 

    # and now write the ready (or not ready) string
    player_data_draw.text(corner ,text, fill = color, font = player_data_font)
    matrix.SetImage(player_data_image, 0, 0)
    
  def show_char(self, c, index, highlight):
    global matrix
    global player_data_image
    global player_data_draw
    global player_data_font
    
    highlight_color = (255,255,255)
    regular_color = (0,255,0)

    # where is the top left corner of this character?
    corner = ( index * self.char_width,    
               self.player_number*self.row_height)

    #start by blanking the space this character is going into
    player_data_draw.rectangle(
       (corner[0],
        corner[1],
        corner[0]+self.char_width-self.char_buffer,  
        corner[1]+self.row_height),
       fill = (0,0,0)) 

    # now print the character
    if (highlight == True):
      color = highlight_color
    else:
      color = regular_color
    char_x = corner[0] + self.char_buffer
    char_y = corner[1]
    player_data_draw.text((char_x, char_y),c, fill = color, font = player_data_font)
    matrix.SetImage(player_data_image, 0, 0)

  def toggle_ready(self):
    if self.state == "Ready":
      self.state = "Input"
    elif self.state == "Input":
      self.state = "Ready"
    else:
      print("Unexpected state in toggle_ready: ")
      print(self.state)
      exit(1)
    self.show_ready()

  def process_input(self, input):
   
    # an up backs up our current char. A goes to space, goes to 9-0, goes to Z
    if input == "up":
      # are we on the "ready" indicator?
      if (self.char_index == self.ready_index):
        self.toggle_ready()
        
      # we're somewhere in the string.  tweak that char.
      else:
        old_char = self.name_str[self.char_index]

        if (old_char == "A"):
          new_char = " "
        elif (old_char == " "):
          new_char = "9"
        elif (old_char == "0"): 
          new_char = "Z"
        else:
          new_char = chr(ord(old_char) - 1)
      
        self.show_char(new_char, self.char_index, True)
       
        # update our data.
        # unfortunately, strings don't allow for character assignment, so 
        # im gonna make this a list first, tweak the char, then put it back.
        name_list = list(self.name_str)
        name_list[self.char_index] = new_char
      
        self.name_str = "".join(name_list)

    # a down increments our current char. 
    # Z goes to 0, 9 goes to space, space goes to A 
    if input == "down":
      if (self.char_index == self.ready_index):
        self.toggle_ready()
      else:

        old_char = self.name_str[self.char_index]

        if (old_char == "Z"):
          new_char = "0"
        elif (old_char == "9"):
          new_char = " "
        elif (old_char == " "): 
          new_char = "A"
        else:
          new_char = chr(ord(old_char) + 1)
      
        self.show_char(new_char, self.char_index, True)
       
        # update our data.
        
        # unfortunately, strings don't allow for character assignment, so 
        # im gonna make this a list first, tweak the char, then put it back.
        name_list = list(self.name_str)
        name_list[self.char_index] = new_char
      
        self.name_str = "".join(name_list)

    if input == "right":
      # don't let the cursor move past the "ready" indicator
      if self.char_index == self.ready_index:
        return
      
      # change the highlighting on the "current" location back to normal.
      old_char = self.name_str[self.char_index]
      self.show_char(old_char, self.char_index, False)

      # "normal case"...move the cursor one to the right.
      self.char_index += 1
      if (self.char_index < self.ready_index):
        new_char = self.name_str[self.char_index]
        self.show_char(new_char, self.char_index, True)

      # "special case"...jump the cursor over to the ready indicator
      else:
        self.show_ready()
 
    if input == "left":
      # don't let the cursor move past the first character 
      if self.char_index == 0:
        return

      # if we were on the "ready" indicator, change its highlighting
      if (self.char_index == self.ready_index):
        # in this case, we need to change the char index first so that 
        # show_ready isn't highlighted.
        self.char_index -= 1
        self.show_ready()
      else:
        # change the highlighting on the "current" location back to normal.
        old_char = self.name_str[self.char_index]
        self.show_char(old_char, self.char_index, False)
        
        # update the character index to properly highlight the next char.
        self.char_index -= 1

      new_char = self.name_str[self.char_index]
      self.show_char(new_char, self.char_index, True)

def check_all_ready():
  global player_data_list

  for player in player_data_list:
    if player.state != "Ready":
      return False

  return True
    

def pregame():
  global player_data_list
  global total_rows
  global total_columns
  global matrix

  for player in player_data_list:
    player.show_disconnect()
    
  # number of connected clients at last check.
  last_num_connected = 0

  while (check_all_ready() == False):
    # do we have any new connections?
    num_connected = wrapper.player_count()
    for player_index in range(last_num_connected, num_connected):
      player_data_list[player_index].set_connected() 
    last_num_connected = num_connected
    
    input = wrapper.get_next_input()
    if input != None:
      # this is a little dangerous...I'm looking at the 6th char to get the
      # index.  Won't work if we have more than 9 players...and won't work
      # if we change the input strings.
      player_index = int(input[0][6]) - 1
     
      print "Processing "+input[1]+" for player index "+str(player_index)

      player_data_list[player_index].process_input(input[1])

    # Quick sleep to allow other threads to run
    time.sleep(0.001)

######################################################
# Class HighScoreData
# 
#   This class is responsible for maintaining high score data.
#   
#   Persistent data is written as a file (cycles.scores by default).
#   Each line contains a name, followed by comma, followed by the current
#   High score for that player.
#
#######################################################
class HighScoreData():
 
  def __init__(self):
    # High score list is a list of lists, with each entry being (name,score)
    self.high_score_list = []

    self.high_score_file = "cycles.scores"
    self.read_high_scores()

  ######################################
  # read_high_scores
  #
  # Reads the high scores from the specified file into our high score list.
  # File (and list) format:  name,score
  ####################################### 
  def read_high_scores(self):
    try:
      file = open(self.high_score_file, 'r')
      for line in file:
        line=line.strip()
        self.high_score_list.append(line.split(','))
      print("High score file processed")
      file.close()
     
    except:
      # if no file exists, there's nothing to do..we're okay with an empty list.
      print ("No high score file available.  Empty high score list.")

  ####################################
  # print_high_scores
  #
  # debug function, used to print out our high score list.
  ####################################
  def print_high_scores(self):
    for item in self.high_score_list:
      tmp_str = "Player: "+item[0]+", Score: "+item[1] 
      print tmp_str

  ####################################
  # update_score
  #
  # This function updates the cumulative score for a given player.
  ####################################
  def update_score(self, player, score):
    
    # Look for the player in our high score list.
    for player_data in self.high_score_list:

      # if they exist, add the score to their current score.
      if (player_data[0] == player):

        print("updating score for "+player)
        print("old points: "+player_data[1])
        print("adding "+str(score))

        new_score = int(player_data[1]) + score
        player_data[1] = str(new_score)

        print("new score: "+player_data[1])

        return

    # if that player doesn't exist yet, add them to the list.
    self.high_score_list.append([player, str(score)])

  ####################################
  # write_scores
  #
  # This function writes the high score file
  ####################################
  def write_score_file(self):
    with open(self.high_score_file, 'w') as file:
      for line in self.high_score_list:
        file.write(line[0]+","+line[1]+"\n")
      print("High score file updated")

  ####################################
  # get_score 
  #
  # This function return a high score (as a string) for a given player. 
  ####################################
  def get_score(self, player):
    # Look for the player in our high score list.
    for player_data in self.high_score_list:
      # if they exist, add the score to their current score.
      if (player_data[0] == player):
        return player_data[1]

    # if that player doesn't exist, their score is zero. 
    return "0" 

  ####################################
  # get_top_scores 
  ####################################
  def get_top_scores(self, number):

    # start by sorting the scores
    self.high_score_list.sort(key = score_sort_helper, reverse=True)

    # then return the top scores
    sorted_list = []
    count = 0
    for line in self.high_score_list:
      sorted_list.append(line)
      count += 1
      if count == number:
        break;

    return sorted_list

def score_sort_helper(val):
  return (int(val[1]))

###################################
# Main loop 
###################################


high_score_data = HighScoreData()
points_first = 5
points_second = 3
points_third = 1
points_fourth = 1

wrapper = Gamepad_wrapper()

player_data_list = []
player_data_image = Image.new("RGB", (total_columns, total_rows))
player_data_draw = ImageDraw.Draw(player_data_image)
player_data_font = ImageFont.truetype('Pillow/Tests/font/Courier_New_Bold.ttf', 10)

display_text_font = player_data_font

start_text = "Cycles Game"
centered_text(start_text, (255,0,0), (0,0,255), display_text_font,5)

for i in range(0,4):
  name = "PLAYER"+str(i+1)
  color = player_color[i] 
  new_player = PlayerData(name, color, i)
  player_data_list.append(new_player)

while True:
  pregame()

  places = play_game(4)

  # update the score for each player
  first_total = int(high_score_data.get_score(places[3])) + points_first
  high_score_data.update_score(places[3], points_first)

  second_total = int(high_score_data.get_score(places[2])) + points_second
  high_score_data.update_score(places[2], points_second)

  third_total = int(high_score_data.get_score(places[1])) + points_third
  high_score_data.update_score(places[1], points_third)

  fourth_total = int(high_score_data.get_score(places[0])) + points_fourth
  high_score_data.update_score(places[0], points_fourth)

  print("1st place: " + places[3] +
        " score: " + str(points_first) +
        " total: "+ str(first_total) )
  
  print("2nd place: " + places[2] +
        " score: " + str(points_second) +
        " total: "+ str(second_total) )

  print("1st place: " + places[1] +
        " score: " + str(points_third) +
        " total: "+ str(third_total) )

  print("1st place: " + places[0] +
        " score: " + str(points_fourth) +
        " total: "+ str(fourth_total) )

  # save the high score file
  high_score_data.write_score_file()

  # print out the winner
  first = "1st: "+places[3]+" ("+str(first_total)+")"
  second = "2nd: "+places[2]+" ("+str(second_total)+")"
  third = "3rd: "+places[1]+" ("+str(third_total)+")"
  fourth = "4th: "+places[0]+" ("+str(fourth_total)+")"
  display_text(
    first+"\n"+second+"\n"+third+"\n"+fourth,
    green,
    10)
    
  # now show high scores
  top_score_string = ""
  top_scores = high_score_data.get_top_scores(8)
  for score in top_scores:
    top_score_string = top_score_string+score[0]+":"+score[1]+"\n"
  display_text(top_score_string,green,10)

  # at this point, we're going to make all players "not ready", but keep their
  # MQTT connnections
  for i in range(0,4):
    player_data_list[i].state = "Input" 
    player_data_list[i].char_index = player_data_list[i].ready_index
