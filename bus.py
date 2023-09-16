'''
Communication Bus
'''
import socket , json , os , time , datetime
# import socketio

def send_metadata(socket:socket.socket, meta:dict) -> bool | str:
    '''Dumped as json object and sent
    - on error returns: error(str)
    '''
    try: 
        # print(meta)
        socket.send(json.dumps(meta).encode())
        return True
    except Exception as e: return e

def recv_metadata(socket: socket.socket) -> dict | Exception | str:
    '''Receive and deserialize as a JSON object
    - on error returns: error(str)
    '''
    try:
        meta = socket.recv(1024).decode()
        # print("Received data:", json.loads(meta))
        return json.loads(meta)
    except Exception as e:
        return e

def send_file(file_path:str, client:socket.socket,speed_:int) ->bool:
    '''
    
    - client : socket to send file through
    - file_path : where file located
    #
    - recv(10)
    - send_metadata(.send())

    try:
    
    with file open:
    - recv(10)  | 'sd-ok'

    while loop

    - send(bin)
    - recv(10)    | 'rc-ok'
    
    file close
    - recv(10)

    exception ...

    '''
    # send meta-data (file)
    print(client.recv(10).decode())      # call for meta (client)
    meta = {
        'file_name' : os.path.basename(file_path),
        'size'  : os.path.getsize(file_path),
        'speed' : speed_
    }
    send_metadata(socket=client,meta=meta)
    while True:
        try:
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
                        print('[FROM:send_file] sent ',len(bin_)/1024,'kb')
                        print(client.recv(24).decode())     # client-server sync  (recived-ok)
                    else:
                        print('[FROM:send_file] file sent')
                        break
                file.close()
                client.recv(10).decode()      # transmition sucess!
        except PermissionError as e: continue
        break
    return True

def receive_file(client_socket, save_dir:str) -> bool:
    '''
    - client_socket : connected-socket
    - save_dir : save-dir

    try:
    - send('meta-sd')
    - recv_metadata(.recv())
    
    file open to write:
    - send('sd-ok')

    while loop
    - recv(bin)
    - send('rc-ok')

    file close:
    - send('sd-ok')

    except:
    - send('error')

    '''
    try:
        # ask for meta-data (file)
        client_socket.send('meta-sd'.encode())
        print(meta_ := recv_metadata(socket=client_socket))
        
        # check is-file exists
        if (os.path.isfile(path_:=os.path.join(save_dir,meta_['file_name']))): path_ = os.path.join(save_dir, ((fd:=get_files_metadata(path_=path_))['name']+str(datetime.datetime.now())[::3]+fd['.extn']))
        else: path_ = os.path.join(save_dir,meta_['file_name'])
        print('[FROM:recieve_file] path',path_)

        with open(path_, 'xb') as file:

            print('reciving file...')               # DEBUG[[01]]
            client_socket.send('sd-ok'.encode())    # confirmation:start-sending

            file_recived = 0

            while file_recived < meta_['size']:
                bin_ = client_socket.recv(meta_['speed'])    # speed/s
                print('[FROM:recieve_file] got ',rt:=bytes_toKMG(bin_),type(rt[0]),rt[1])
                file.write(bin_)
                # print(type(bin_))
                file_recived += len(bin_)
                client_socket.send('rc-ok'.encode())    # server-client sync (recived-ok)
            print('[FROM:recieve_file] recived file! size(bytes)',bytes_toKMG(file_recived) ,'/t')
                    # break
            file.close()
            time.sleep(1)
            client_socket.send('sd-ok'.encode())    # recived entire file  (transmition sucess!)
    except Exception as e: 
        print('[FROM:recieve_file] from client',e)
        client_socket.send('error'.encode())  # send error message
        return False
    return True

def bytes_toKMG(bytes_value:bytes) -> tuple[int,str]:
    '''
    bytes size to KIB/MIB/GIB
    '''
    try:
        bytes_value = len(bytes_value)
    except Exception: bytes_value = bytes_value
    if bytes_value < 1024:
        return bytes_value ,"bytes"
    elif bytes_value < 1024 * 1024:
        kibibytes_value = int(bytes_value / 1024)
        return kibibytes_value, "KiB"
    elif bytes_value < 1024 * 1024 * 1024:
        mebibytes_value = int(bytes_value / (1024 * 1024))
        return mebibytes_value, "MiB"
    else:
        gibibytes_value = int(bytes_value / (1024 * 1024 * 1024))
        return gibibytes_value, "GiB"

def get_files_metadata(dir_:str=None,path_:str=None) -> dict|None:
    '''Not dumped as json
    - either path_ or dir_
    '''
    # for a single file:
    if path_ and os.path.isfile(path_): 
        return {
        'name' : os.path.basename(p=path_),
        'size' : os.path.getsize(path_) ,
        '.extn' : os.path.splitext(path_)[-1] 
    }
    # for dir files
    elif dir_ and os.path.isdir(dir_):
        return {
        'name' : (files:=os.listdir(path=dir_)),
        'size' : [os.path.getsize(os.path.join(os.getcwd(),file)) for file in files],
        '.extn' : [os.path.splitext(os.path.join(os.getcwd(),file_))[-1] for file_ in files]
    }
    else: print('path not valid! -from explr')

def sync_Q(socket:socket.socket,Q_DICT:dict) -> None:
    '''
    SYnc Query function that runs on separete thread, provides query topics from Q_DICT
    '''
    print('sync-q  running!....')
    while True:
        # time.sleep(1)
        try:
            # socket.send(json.dumps(Q_DICT).encode())
            # print('[FROM: bus lin193]', Q_DICT)
            # print('[FRO/M: bus lin194]',
            (res:=socket.recv(1024).decode(), type(res))
            if res  in Q_DICT.keys():     
                # print('[FROM: bus lin196]', res)

                if callable(Q_DICT[res]):   val =  Q_DICT[res]()
                else: val = Q_DICT[res]
                # print('[FROM: bus lin200]',val)

                socket.send(
                    json.dumps({res :  val}).encode()
                )
            elif res == 'close-ok': break
            else: socket.send(json.dumps({'Query':'not valid'}).encode())
        except Exception as e : 
            print('[FROM: bus lin 206 Exception]',e)
            break