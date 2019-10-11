# a matrix config file format is as follows:
# The following 4 lines are used to specifiy each panel's rows and columns...
#    and how many panels are stacked vertically and horizontaly.
# Example:
#   panel_rows=64
#   panel_columns=64
#   num_horiz=1
#   num_vert=1
# Any missing lines are set to the default value...32x32, one vert, on horiz.
# all other lines are ignored.

def read_matrix():
  panel_rows = 32
  panel_columns = 32
  num_horiz =1
  num_vert = 1

  try: 
    file = open('matrix.conf','r')
   
    for line in file:
       # just get the first line
       line = line.strip()
       line = line.split("=")
       param = line[0]
       if (param == "panel_rows"):
         panel_rows = int(line[1])
       elif (param == "panel_columns"):
         panel_columns = int(line[1])
       elif (param == "num_horiz"):
         num_horiz = int(line[1])
       elif (param == "num_vert"):
         num_vert = int(line[1])
       else:
         print("ignored config line")
  except:
    print("No config file exists; using defaults")

  return (panel_columns, panel_rows, num_horiz, num_vert) 
