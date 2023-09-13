import glob , json
import socket, threading
import os , time , sys
from bus1 import send_metadata

def get_wifi_ip_address() -> str:
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''
Server-Socket, PORT 25200
'''
Q_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''
Server-Query-Socket, PORT 25250   
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

s_socket.listen(5)
print(get_wifi_ip_address())

client, _ = s_socket.accept()

# on acceptig client ,pass query_socket-port
client.recv(10).decode()
client.send(
    json.dumps(
        {'Qport'  :   25250}
    ).encode()
)

Q_socket.listen(5)
client_Q_socket, Q_  =  Q_socket.accept()


SPEED_10 = 10485760   # 10MBPS
SPEED_50 = 52428800   # 50MBPS

# Function to send a file
def send_file(file_path, client:socket.socket,speed_:int=SPEED_10) ->bool:
    '''
    - file-model: send-recv
    '''
    # send meta-data (file)
    print(client.recv(10).decode())      # call for meta (client)
    meta = {
        'file_name' : os.path.basename(file_path),
        'size'  : os.path.getsize(file_path),
        'speed' : speed_
    }
    send_metadata(socket=client,meta=meta)

    with open(file_path, 'rb') as file:
        # confirmation:start
        if client.recv(10).decode() == 'error': return False    # confirmation: excepts -> 'sd-ok' (send-ok)
                                            # if error messg is passed --> ends call
        # send-size(file)
        # import struct
        # client.send(st:=struct.pack('!ii', os.path.getsize(file_path),speed_))

        while True:
            bin_ = file.read(speed_)
            if bin_:
                client.send(bin_)                   # send file-data(B)
                print('sent ',len(bin_)/1024,'kb')
                print(client.recv(24).decode())     # client-server sync  (recived-ok)
            else:
                print('file sent')
                break
        file.close()
        client.recv(10).decode()      # transmition sucess!
    return True


def sync_dir(socket:socket.socket=None,dir_:str=None,dir_vs:str=None,file_meta:list=None) -> list[str] | None |Exception:
    # change to dir-location
    '''Return file_paths as list on any updates in dir_vs(add-only) that are not present in dir_
    - dir_ -> dir to compare    (remote)
    - dir_vs -> dir to check against    (local)
    - file_meta -> file-paths-list of dir_ to compare
    - socket: requests file-path[list] (remote) as json 
    '''
    try: 
        if socket and not dir_ and dir_vs: 
            socket.send('dir_[list]'.encode())
            file_meta = json.loads(socket.recv(1024).decode())['dir_']  # recv_metadata (dir_)
        elif dir_ and dir_vs:
            file_meta = glob.glob(os.path.join(dir_,'**/*.*'), recursive=True) #(path) list of file-paths to ccheck against

        # while True:
        files = glob.glob(os.path.join(dir_vs,'**/*.*'), recursive=True) #(path) list of file-paths
        if (files_:=[file for file in files if os.path.basename(file) not in [os.path.basename(file_base) for file_base in file_meta]]) : return files_
        else: return None
    except Exception as e: return e


# Sending the first file
# send_file(os.path.join(os.getcwd(), 'test/geek.png'))

# Receiving acknowledgment from the client
# ack = client.recv(1024).decode()

print('chilling!')

# Sending the second file
# if ack == '00reccived-ok':
#     send_file(os.path.join(os.getcwd(), 'test/network.png'))

# Receiving acknowledgment from the client
# meta = glob.glob(os.path.join(os.getcwd() ,'test/client/**/*.*'), recursive=True)
# print(meta, os.getcwd())

SYNC_DIR = os.path.join(os.getcwd(),'sub2')

def func_list_dir() -> list: return glob.glob(os.path.join(SYNC_DIR,'**/*.*'), recursive=True)


Q_DICT = {
    'dir_[list]'  :  func_list_dir ,
    'sync_dir'  : SYNC_DIR
}

def sync_Q(socket:socket.socket=client_Q_socket):
    while True:
        print('sync-q  running!....')
        try:
            # print(json.loads(socket.recv(1024).decode()))
            in_ = str(input('say...'))
            socket.send(in_.encode())
            print(json.loads(socket.recv(1024).decode()))
        # try:
        #     if  print(res:=socket.recv(1024).decode()) in Q_DICT.keys():     
        #         socket.send(
        #             json.dumps({'dir_':Q_DICT[res]}).encode()
        #         )
        except Exception as e : 
            print(e)
            break
            
threading.Thread(target=sync_Q).start()

# client_Q_socket.send('dir_[list]'.encode())
# print('test_Q_Thread',json.loads(client_Q_socket.recv(1024).decode()))
while True:
    # print('in sync')
    # client.send()
    (_:=sync_dir(dir_vs=SYNC_DIR,dir_=os.path.join(os.getcwd(),'client'))) 
    if _ :
        # print(_)
        for file in _:
            client.send(os.path.basename(file).encode())

            msgg = client.recv(1024).decode()
            
            print(send_file(file_path=file,client=client))
            print(_,'done!')
        print('sync-end')
        


# for path in ['test/network.png','test/vid_2.mp4']:
#     ack = client.recv(1024).decode()
#     if ack == 'y': 
#         print('y: sending file') 
#         send_file(client=client,speed_=SPEED_10,file_path=path)
        # break
    # print(ack)
# Sending a text message
# in_ = input('send:')
# client.send(in_.encode('utf-8'))

# client.close()
# s_socket.close()

# ack = client.recv(1024).decode()
# if ack == 'y': 
#     print('y: sending file') 
#     send_file(speed_=SPEED_10,file_path='test/vid_2.mp4')
# print(ack)

# meta =  {
#     'speed':SPEED_10,
#     'file_name': 'abz.tx',
#     'size': 90
# }

# send_metadata(socket=client,meta=meta)