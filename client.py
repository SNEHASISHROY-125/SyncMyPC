import datetime
import socket , threading
import os , time , json , glob
from bus1 import bytes_toKMG ,recv_metadata , get_files_metadata  as gtfm

server_ip = '192.168.1.4'  # Replace with the server's IP address
server_port = 25200  # Replace with the server's port number

def receive_file(client_socket, file_path) -> bool:
    '''
    - file-model: recv-send
    '''
    # print('client-ex', os.path.join(file_path, ((fd:=gtfm(path_=os.path.join(os.getcwd(),'geek.png')))['name']+str(datetime.datetime.now())[::3]+fd['.extn'])))

    try:
        # ask for meta-data (file)
        client_socket.send('meta-sd'.encode())
        print(meta_ := recv_metadata(socket=client_socket))
        
        # check is-file exists
        if (os.path.isfile(path_:=os.path.join(file_path,meta_['file_name']))): path_ = os.path.join(file_path, ((fd:=gtfm(path_=path_))['name']+str(datetime.datetime.now())[::3]+fd['.extn']))
        else: path_ = os.path.join(file_path,meta_['file_name'])
        print('path',path_)

        with open(path_, 'xb') as file:

            print('reciving file...')               # DEBUG[[01]]
            client_socket.send('sd-ok'.encode())    # confirmation:start-sending

            file_recived = 0

            while file_recived < meta_['size']:
                bin_ = client_socket.recv(meta_['speed'])    # speed/s
                print('got ',rt:=bytes_toKMG(bin_),type(rt[0]),rt[1])
                file.write(bin_)
                # print(type(bin_))
                file_recived += len(bin_)
                client_socket.send('rc-ok'.encode())    # server-client sync (recived-ok)
            print('recived file! size(bytes)',bytes_toKMG(file_recived) ,'/t')
                    # break
            file.close()
            time.sleep(1)
            client_socket.send('sd-ok'.encode())    # recived entire file  (transmition sucess!)
    except Exception as e: 
        print('from client',e)
        client_socket.send('error'.encode())  # send error message
        return False
    return True


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

# get Query-port
client_socket.send('sd-port'.encode())
server_Q_port = json.loads(client_socket.recv(1024).decode())['Qport']

# connect to server Query socket
server_Q_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_Q_socket.connect((server_ip, server_Q_port))

print('conected')

SYNC_DIR = os.path.join(os.getcwd(),'client')

def func_list_dir() -> list: return glob.glob(os.path.join(SYNC_DIR,'**/*.*'), recursive=True)

# print(os.path.isfile(SYNC_DIR))
Q_DICT = {
    'dir_[list]'  :   func_list_dir,
    'sync_dir'  : SYNC_DIR
}
'''
Query Dict: server-client (query)
'''

# client_socket.recv(1024)
def sync_Q(socket:socket.socket=server_Q_socket):
    while True:
        print('sync-q  running!....')
        try:
            # socket.send(json.dumps(Q_DICT).encode())
            if  (res:=socket.recv(1024).decode()) in Q_DICT.keys():     

                if callable(Q_DICT[res]):   val =  Q_DICT[res]()
                else: val = Q_DICT[res]

                socket.send(
                    json.dumps({res :  val}).encode()
                )
                
            else: socket.send(json.dumps({'Query':'not valid'}).encode())
        except Exception as e : 
            print(e)
            break
            
threading.Thread(target=sync_Q).start()

while True:
    print('client-lloop.....')
    msgg = client_socket.recv(1024).decode()    # prepare for recv-file
    print('llop',msgg)

    if msgg == 'close-ok':
        break
    print(os.getcwd())
    client_socket.send(msgg.encode())    # all resources prepared, ready to recv-file!
    # for file in msgg:
    print(receive_file(client_socket=client_socket,file_path=os.path.join(os.getcwd(),'client')))

'''
for _ in range(2):
    if (in_:=input('...')) == 'y': 
        client_socket.send(in_.encode())
        receive_file(client_socket=client_socket,file_path=os.path.join(os.getcwd(),'client'))
'''
# in_ = input('...')
# if in_ == 'y': 
#     client_socket.send(in_.encode())
#     receive_file(client_socket=client_socket,file_path=os.path.join(os.getcwd(),'client'))

# print(res:=recv_metadata(socket=client_socket),type(res))