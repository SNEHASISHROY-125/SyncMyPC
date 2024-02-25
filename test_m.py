# import test
import client as c, time 

c.start_client()

while True:
    time.sleep(3)
    print(c.memry_dict['restart'])
    print(c.memry_dict['client_running'])