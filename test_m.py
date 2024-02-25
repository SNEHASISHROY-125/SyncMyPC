# import test
import server, time 

server.start_server()

while True:
    time.sleep(3)
    print(server.memry_dict['server_running'])