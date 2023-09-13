'''
Communication Bus
'''
import socket , json , os

def send_metadata(socket:socket.socket, meta:dict) -> bool | str:
    '''Dumped as json object and sent
    - on error returns: error(str)
    '''
    try: 
        # print(meta)
        socket.send(json.dumps(meta).encode())
        return True
    except Exception as e: return e

def recv_metadata(socket: socket.socket) -> dict | str:
    '''Receive and deserialize as a JSON object
    - on error returns: error(str)
    '''
    try:
        meta = socket.recv(1024).decode()
        # print("Received data:", json.loads(meta))
        return json.loads(meta)
    except Exception as e:
        return e

def send_file(socket:socket.socket, file_path:str , buff: [int]=1024) -> bool | None:
    try:
        # check path: 
        if not os.path.isfile(path=file_path):
            raise FileNotFoundError
        with open(file_path, 'rb') as file:
            while True:
                bin_ = file.read(1024)
                if bin_:
                    socket.send(bin_)
                    print('sending file!')
                else: break
            file.close()
    except FileNotFoundError: return False 
    finally: return True

def recv_file(socket:socket.socket, file_path:str , buff: [int]=4096) -> bool|None:
    try:
        # check file
        # if os.path.isfile(file_path) : raise FileExistsError
        with open(file_path, 'xb') as file:
            while True:
                bin_ = socket.recv()
                if bin_:
                    file.write(bin_)
                    print('reciving file!')
                else: break
            file.close()
    except Exception as e: return False 
    finally: return True

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
    '''Not dumped as json'''
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
