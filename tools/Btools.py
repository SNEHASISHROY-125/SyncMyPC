'''
Bus-Tools
'''

import inspect

class Tools:
    '''
    - if _debug('') not set, will not print
    '''
    def __init__(self) -> None:
        self._debug = ''


    def print_(self,payload:tuple,lin:bool=True,s:any=None,d:bool=True) -> None:
        '''
        SAME as normal print ,but with DEBUG , by default prints line-number along
        with debug suffix, if lin set to FALSE ,will not print line-number
        - payload > tuple of items to print
        - s > add-on suffix to add with debug
        - d > if not (TRUE) ,no print DEBUG
        '''
        if self._debug and d:
            if lin: 
                frame_info = inspect.currentframe()
                try:
                    caller_frame = frame_info.f_back
                    line_number = caller_frame.f_lineno
                finally:
                    del frame_info
                    _debug = self._debug + ' line ' + str(line_number)
                    if s: _debug = self._debug + ' ' + str(s) + ' line ' + str(line_number)
                    # self._debug = _debug
            payload = (_debug,) + payload
            try:
                # traceback.print_stack(limit=2)                
                print(
                    '[FROM '+ " ".join(payload) + ']'
                )
            except Exception:
                p_ = []
                [p_.append(str(_)) for _ in payload]
                print('[FROM '+ " ".join(p_) + ']')
    
    def get_line_number(t=None) -> None:
        '''
        RETURNS: lin-no. from where it is called
        '''
        frame_info = inspect.currentframe()
        try:
            caller_frame = frame_info.f_back
            line_number = caller_frame.f_lineno
            return line_number
        finally:
            del frame_info

t = Tools()

t._debug = 'bus'
# t = (9,)
# z = (10,12)
# print(
# t.print_(('hi',),)
# t.print_(('hi',),)
    # t+z
# )