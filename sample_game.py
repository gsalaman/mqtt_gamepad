from gamepad_wrapper import Gamepad_wrapper

wrapper = Gamepad_wrapper(1)
print("Waiting for players")
while wrapper.player_count() != 1:
  pass
  
print ("Controller connected.  Main loop time")

while True:
  input = wrapper.get_next_input()
  if (input != None):
    print ("Input processed: "+input[0]+" "+input[1])
