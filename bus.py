'''
Communication Bus
'''
import socket , json , os , time , datetime 
from tools.Btools import Tools as T
# import socketio
t  =  T()
t._debug = (d:='(BUS)')

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
                t.print_(('syncQ','line',T.get_line_number(), res))

                if callable(Q_DICT[res]):   val =  Q_DICT[res]()
                else: val = Q_DICT[res]
                t.print_(('syncQ','line',T.get_line_number(),val))

                socket.send(
                    json.dumps({res :  val}).encode()
                )
            elif res == 'close-ok': break
            else: socket.send(json.dumps({'Query':'not valid'}).encode())
        except Exception as e : 
            t.print_(('syncQ','line',T.get_line_number(),'Exception',e))
            break

def recv_(s:socket.socket,debug:str,e:list[str],e_:type,buff:int=1024,res=None,) ->any:
    '''
    recv-Mod: (str | dict) for protocol build only, not for file transfer
    - s > socket to connect
    - debug > suffix to add for DEBUG
    - e > expected items (iterable)
    - e_ > expected types (not bytes)
    - res > response: sent back to socket(s) [OPTIONAL]
    - buff > Buffer-size(1024)
    # 
    prints (DEBUG) [FROM (BUS) debug + ...]
    
    OPERATION-until recieved ones are not in e or e_ type ,prints DEBUG ,cotinues to recv
    
    if expecting to recv str, pass expected values(str) to e
    or expecting dict to recv, passed values(str) to e will be checked in the received dict-keys
    
     '''

    res_ =  str(e_)+' '+str(e)
    t  =  T()
    t._debug = (d:='(BUS) ' + debug)

    run = True
    while run :
        t.print_(payload=('recving...',))
        rec = s.recv(buff)
        # try to decode
        try: rec = json.loads(rec.decode()) # try json
        except json.decoder.JSONDecodeError: 
            try:rec = rec.decode() # try to ->str 
            except Exception:rec = rec  # keep it as bytes
        
        # match with e or e_
        if e_ is dict and type(rec) is e_: 
            t.print_(('lin ',T.get_line_number(),'got dict',))
            # t.print_(('lin ',tl.get_line_number(),rec,))
            res_ = {  e_ : e  }
            if [ _ for _ in e if _ in rec.keys()]:
                try:
                    s.send('ok'.encode())
                    return rec
                except: ...
                run = False
                time.sleep(1)

        elif rec == 'close':
            t.print_(payload=(f'socket-{s}-down',))
            break

        elif e_ is str and type(rec) is e_:
            t.print_(('lin ',T.get_line_number(),'got str',))
            for item in e : 
                if item == rec: 
                    t.print_(payload=('lin',T.get_line_number(),rec,))
                    run = False
                    s.send('ok'.encode())
                    try: return rec
                    except: ...
                    time.sleep(1)
                    break
        # if not mathced print >DEBUG
        t.print_(payload=('not same as expected!', type(rec),rec,))
        # send response: (str)
        if res: s.send(  f'{d}-{T.get_line_number()}-{res}'.encode()  )
        else:   s.send(  f'{d}-{T.get_line_number()}-expected:{res_}'.encode()  )

def send_(s:socket.socket,debug:str,payload:any,res:str='ok',try_:int=2,_DEBUG:bool=True) ->any:
    '''
    recv-Mod: (str | dict) for protocol build only, not for file transfer
    - s > socket to connect
    - debug > suffix to add for DEBUG
    - _DEBUG > (True) if true prints DEBUG
    - payload > item to send 
    - try_ > expected times to try sending (if not got res from recv_ ,ask for interruption)
    - res > response: (expeccted)get back from socket(s) 
    # 
    prints (DEBUG) [FROM (BUS) suf + ...]
    

    OPERATION-sends payload(any), prints DEBUG, match with res-if not matched, 
    try: sending payload (try_) times, if stil res not matched, ask-for-INTERRUPTION
    '''

    t  =  T()
    if _DEBUG : t._debug = '(BUS)' + debug
    t_ = try_
    run = True
    while run :
        t.print_(('sending...',))
        if type(payload) is not dict: s.send(  str(payload).encode()   )
        elif type(payload) is dict: s.send(  json.dumps(payload).encode()   )
        rec = s.recv(1024).decode()
        # try to match
        if rec == res: 
            t.print_((rec,))
            break
        else: 
            if try_ !=0:
                try_ -= 1
            else:
                t.print_(('line',T.get_line_number(),f'tried {t_} times, getting {rec} not {res}'))
                if input('try again (y/n)') == 'y': 
                    try_ = t_
                    continue
                else:
                    # s.send('close'.encode())
                    break
        #
# i = t()
# i._debug = 'bus'
# i.print_(('line',t.get_line_number(),))