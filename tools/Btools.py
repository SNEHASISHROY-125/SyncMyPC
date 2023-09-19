'''
Bus-Tools
'''

import inspect

class Tools:
    '''
    - if debug('') not set, will not print
    '''
    def __init__(self) -> None:
        self._debug = ''
    def print_(self,payload:tuple) -> None:
        if self._debug: 
            payload = (self._debug,) + payload
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

# t = Tools()

# t._debug = 'bus'
# t.print_((t.get_line_number(),'hi',))
# t = (9,)
# z = (10,12)
# print(
    # t+z
# )