import datetime
import socket , threading
import os , time , json , glob
from bus import bytes_toKMG ,receive_file , get_files_metadata  as gtfm , sync_Q ,send_file,recv_,send_ , ask_sync_Q
from tools.Btools import Tools as T


SYNC_DIR = ''
'''
Dir to save files
'''
if SYNC_DIR == '': SYNC_DIR = os.path.join(os.getcwd(),'client')
if not os.path.isdir(SYNC_DIR): os.mkdir(SYNC_DIR)
'''
Dir to save files
'''

# INPUT IP | 
ip_ = str(input("connect IP:"))
server_ip = ip_

# server_ip = '192.168.1.2'  # Replace with the server's IP address
server_port = 25200  # Replace with the server's port number

def client():
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

    print('conected to:',server_ip,':',server_port)

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
    threading.Thread(target=sync_Q,args=(server_Q_socket_2,Q_DICT,'client')).start()


    # main-loop:
    c = T()
    c._debug = 'c-main-loop'

    while True:
        print('client-lloop.....')
        msgg = recv_(s=client_socket,debug='client',e=['req-file-path','close-ok','file-path'],e_=str)    # prepare for recv-file
        print('[FROM:lin 57] llop',msgg)

        if msgg == 'close-ok':
            print('clss')
            server_Q_socket_2.send('close-ok'.encode())
            server_Q_socket.send('close-ok'.encode())
            break
        
        elif msgg == 'req-file-path': 
            send_(s=client_socket,payload='req-file-path-ok',debug='client',)
            res = recv_(s=client_socket,debug='client',e_=dict,e=['req-file-path'])
            c.print_((res,),s='client')
            file_path = (res)['req-file-path']
            # c.print_((res,file_path,),s='client',)

            # get speed from server (Query: speed)
            '''
            server_Q_socket.send('current_speed'.encode())
            c.print_((res:= json.loads(server_Q_socket.recv(1024).decode()),),s='client',)
            '''
            res = ask_sync_Q(s=server_Q_socket,q='current_speed')
            speed = res['current_speed']

            # send file-notice  (sending-file now)
            send_(s=client_socket,payload='sd-ok',debug='client',)
            # send file to client
            send_file(client=client_socket,file_path=file_path,speed_=speed)
            # client_socket.

        elif msgg == 'file-path':
            # print(os.getcwd())
            send_(s=client_socket,payload='file-path-ok',debug='client',)    # all resources prepared, ready to recv-file!
            # for file in msgg:
            c.print_((receive_file(client_socket=client_socket,save_dir=SYNC_DIR),),s='client',)

        # error in socket-connection (server)   
        elif msgg == 'connection-error':...
        else: print('client: [ERROR] unknown msg:',msgg)

    print('done!')
    client_socket.close()

client()