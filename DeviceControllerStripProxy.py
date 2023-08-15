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
            self._request_queue.put((item, {}, {}))
            return self._response_queue.get()
        return partial(self._call_handler, item)

    def _call_handler(self, name, *args, **kwargs):
        self._request_queue.put((name, args, kwargs))
