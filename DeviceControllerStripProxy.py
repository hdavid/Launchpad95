import traceback
from threading import Thread
from functools import partial
import queue
from .DeviceControllerStripServer import DeviceControllerStripServer
from .Log import log


class DeviceControllerStripProxy():
    def __init__(self, buttons, control_surface, column, parent=None):
        self._request_queue = queue.Queue()
        self._response_queue = queue.Queue()
        self.failed = False
        self.column = column
        self.request_id = 0
        self.server = DeviceControllerStripServer(buttons, control_surface,
                                                  column,
                                                  request_queue=self._request_queue,
                                                  response_queue=self._response_queue,
                                                  parent=parent)
        self._server_process = Thread(target=self.server.run)
        self._server_process.start()

    def __getattr__(self, item):
        #log(f'Proxy: __getattr__ {item}')
        if item == '_parameter_to_map_to':
            self.request_id += 1
            request_id = self.request_id
            #log(f'Proxy{self.column}: __getattr__ {item} request_id: {request_id}')
            self._request_queue.put((item,request_id, {}, {}))
            try:
                while True:
                    token,response = self._response_queue.get(timeout=20)
                    if token == request_id:
                        break
                    else:
                        log(f"GOT WRONG TOKEN {token} != {request_id}")
                        self._response_queue.put((token,response))
                if response == 'None':
                    return None
                return response
            except queue.Empty as e:
                self.failed = True
                log(traceback.format_stack())
                log(f'Proxy{self.column}: __getattr__ {item} failed')
                return None
        return partial(self._call_handler, item)

    def _call_handler(self, name, *args, **kwargs):
        self.request_id += 1
        request_id = self.request_id
        self._request_queue.put((name,self.request_id,args, kwargs))
        if name == "shutdown":
            return
        try:
            while True:
                token,response = self._response_queue.get(timeout=20)
                if token == request_id:
                    break
                else:
                    log(f"GOT WRONG TOKEN {token} != {request_id}")
                    self._response_queue.put((token,response))
            if response == 'None':
                return
            #log(f'Proxy{self.column}: _call_handler {name} {args} {kwargs} {response}')
            return response
        except queue.Empty as e:
            self.failed = True
            log(traceback.format_stack())
            return
