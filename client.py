import datetime
import socket , threading
import os , time , json , glob
from bus import bytes_toKMG ,receive_file , get_files_metadata  as gtfm , sync_Q ,send_file


SYNC_DIR = os.path.join(os.getcwd(),'client')
if not os.path.isdir(SYNC_DIR): os.mkdir(SYNC_DIR)
'''
Dir to save files
'''

server_ip = '192.168.1.4'  # Replace with the server's IP address
server_port = 25200  # Replace with the server's port number


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''File_Transfer ,PORT 25200'''
client_socket.connect((server_ip, server_port))


# get Query-port
client_socket.send('sd-port'.encode())
server_Q_port = json.loads(client_socket.recv(1024).decode())['Qport']


# connect to server Query socket
server_Q_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''Client-Query-socket to connect with server_syncQ ,PORT 25250'''
server_Q_socket.connect((server_ip, server_Q_port[0]))


# connect to server Query socket
server_Q_socket_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''Client-syncQ-socket ,PORT 25300'''
server_Q_socket_2.connect((server_ip, server_Q_port[1]))

print('conected')

def func_list_dir() -> list: return glob.glob(os.path.join(SYNC_DIR,'**/*.*'), recursive=True)

# print(os.path.isfile(SYNC_DIR))
Q_DICT = {
    'dir_[list]'  :   func_list_dir,
    'sync_dir'  : SYNC_DIR
}
'''
Query Dict: server-client (query)
'''

# s_lock = threading.Lock()         
threading.Thread(target=sync_Q,args=(server_Q_socket_2,Q_DICT)).start()

while True:
    print('client-lloop.....')
    msgg = client_socket.recv(1024).decode()    # prepare for recv-file
    print('[FROM:lin 57] llop',msgg)

    if msgg == 'close-ok':
        print('clss')
        server_Q_socket_2.send('close-ok'.encode())
        break
    
    elif msgg == 'req-file-path': 
        client_socket.send('req-file-path-ok'.encode())
        res = client_socket.recv(1024).decode()
        print('[FROM: lin 51]' ,res)
        file_path = json.loads(res)['req-file-path']
        print('[FROM: lin 53]' ,file_path,)

        # get speed from server (Query: speed)
        server_Q_socket.send('current_speed'.encode())
        print('[FROM: lin 57]',res:= json.loads(server_Q_socket.recv(1024).decode()))
        speed = res['current_speed']

        # send file-notice  (sending-file now)
        client_socket.send('sd-ok'.encode())
        # send file to client
        send_file(client=client_socket,file_path=file_path,speed_=speed)
        # client_socket.

    else:
        print(os.getcwd())
        client_socket.send(msgg.encode())    # all resources prepared, ready to recv-file!
        # for file in msgg:
        print(receive_file(client_socket=client_socket,save_dir=SYNC_DIR))

print('done!')
client_socket.close()