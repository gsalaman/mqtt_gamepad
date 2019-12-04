
def read_broker():
  try: 
    file = open('broker.conf','r')
   
    for line in file:
       # just get the first line
       line = line.strip()
       return line
  except:
    # if no file exists, use Dawson's broker 
    return "mqttbroker"
