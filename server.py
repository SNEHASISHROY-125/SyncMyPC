
''''
SERVER: targeted to run on PC ,as requires more computational power.
- all network related functions are in bus(communication bus)

- SyncQ function works as Query-Server, waits for response-looks for parameters in Query_Dict-
returns. if query not in Query_Dict returns{not_found}
- Sync_dir function checks for updates both in local as well as remote (if socket provided)-
returns as list | dict (local-remote)
- Q_DICT dictionary of constants such as conneted-sockets,speed,local/save-sir
- close_client_API requires bool, closes connected client-thread
 ,runs in seperate thread 

- opeartion: 
    - sets up three sever-sockets: server_socket, query_socket, query_socket2
    - start Sync_Q in seperate thread
    - start ...

'''

import glob , json
import socket, threading
import os , time , sys
from bus import send_file , receive_file , sync_Q

def get_wifi_ip_address() -> str:
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


SYNC_DIR = os.path.join(os.getcwd(),'server')
if not os.path.isdir(SYNC_DIR): os.mkdir(SYNC_DIR)
'''
Dir to save files
'''

s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''
Server-Socket, PORT 25200
'''
Q_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''
Server-Query-Socket, PORT 25250   
'''
Q_socket_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''
Server-Query-Socket2, PORT 25300 
'''

global port
port = 25200
s_socket.bind(
    (get_wifi_ip_address(), port)
    )

# bind Q-socket (Query):
Q_socket.bind(
    (get_wifi_ip_address(), 25250)
    )

# bind Q-socket (Query):
Q_socket_2.bind(
    (get_wifi_ip_address(), 25300)
    )

s_socket.listen(5)
print(get_wifi_ip_address())

client, _ = s_socket.accept()
'''File_Transfer ,PORT 25200'''

# on acceptig client ,pass query_socket-port
client.recv(10).decode()
client.send(
    json.dumps(
        {'Qport'  :   (25250,25300)}
    ).encode()
)

Q_socket.listen(5)
client_Q_socket, Q_  =  Q_socket.accept()
'''Server-SyncQ-socket ,PORT 25250'''

Q_socket_2.listen(5)
client_Q_socket2, Q_  =  Q_socket_2.accept()
'''socket to connect with client-SyncQ-server ,PORT 25300'''


SPEED_10 = 10485760   # 10MBPS
SPEED_50 = 52428800   # 50MBPS

# Function to send a file



def func_list_dir() -> list: return glob.glob(os.path.join(SYNC_DIR,'**/*.*'), recursive=True)


Q_DICT = {
    'dir_[list]'  :  func_list_dir ,
    'sync_dir'  : SYNC_DIR,
    'supported_speed'    :   [SPEED_10, SPEED_50],
    'current_speed'    :    SPEED_10 ,
    'client_sockets'    :   [client,client_Q_socket,client_Q_socket2]
}
'''
Dict of server constant values
'''         


def sync_dir(socket:socket.socket=None,dir_:str=None,dir_vs:str=SYNC_DIR,file_meta:list=None) -> list[str] | dict[str : list[str]] | None |Exception:
    # change to dir-location
    '''Return file_paths as list on any updates in dir_vs(add-only) that are not present in dir_
    - dir_ -> dir to compare    (remote)
    - dir_vs -> dir to check against    (local)
    - file_meta -> file-paths-list of dir_ to compare
    - socket: requests file-path[list] (remote) as json 
    #
    if changes found in remote dir(client) returns as dict,
    or changes in local dir returns as list
    '''
    try: 
        if socket and not dir_ and dir_vs: 
            socket.send('dir_[list]'.encode())
            file_meta = json.loads(socket.recv(1024).decode())['dir_[list]']  # recv_metadata (dir_)
            # print('[FROM: server lin111]',file_meta)
        elif dir_ and dir_vs:
            file_meta = glob.glob(os.path.join(dir_,'**/*.*'), recursive=True) #(path) list of file-paths to ccheck against

        # while True:
        files = glob.glob(os.path.join(dir_vs,'**/*.*'), recursive=True) #(path) list of file-paths
        if (files_:=[file for file in files if os.path.basename(file) not in [os.path.basename(file_base) for file_base in file_meta]]) : return files_
        
        elif (files_:=[file for file in file_meta if os.path.basename(file) not in [os.path.basename(file_base) for file_base in files]]) : return {'client-file-list':files_}
        
        else: return None
    except Exception as e: return e


print('chilling!')


# kick-start sync_Q in seperate Thread (Query from Q_DICT exchange through socket)
threading.Thread(target=sync_Q,args=(client_Q_socket,Q_DICT ,)).start()

# close client-API
def close_Client(d:bool=False) -> None:
    '''Closes client socckets'''
    if d:
        print(client.send('close-ok'.encode()))
        print(client_Q_socket2.send('close-ok'.encode()))


while True:
    # checks for dir updates(both remote and local) ,if changes in dir;
    # func returns list or dict ,containing file paths, in each eteration
    (_:=sync_dir(dir_vs=SYNC_DIR,socket=client_Q_socket2)) #dir_=os.path.join(os.getcwd(),'client')))
    
    # [list]changes in local dir |  send files to client(remote)
    if type(_) is list :
        # print(_)
        for file in _:
            client.send(os.path.basename(file).encode())

            msgg = client.recv(1024).decode()

            print(send_file(file_path=file,client=client, speed_=Q_DICT['current_speed'])) 
            print(_,'done!')
        print('sync-end')
    
    # {}chaanges in remote dir  |  recive files from client(remote)
    elif type(_) is dict: 
        files_list = _['client-file-list']
        print('[FROM: lin 157]',files_list)
        # send file-path-request
        client.send('req-file-path'.encode())
        # check respponse (req-file-path-ok)
        if client.recv(1024).decode() == 'req-file-path-ok':
            for file in files_list:
                # send file path (request file) as dict
                client.send(json.dumps({'req-file-path':file}).encode())

                # check sd-ok
                print('[FROM: lin 167]',msgg := client.recv(1024).decode())
                if msgg == 'sd-ok': 
                    print(receive_file(save_dir=SYNC_DIR,client_socket=client))
                print(_,'done!')
            print('sync-end')
