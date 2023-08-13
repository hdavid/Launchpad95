from threading import Thread
from functools import partial
from .ButtonSliderElement import ButtonSliderElement
from multiprocessing import Process
import queue
from .DeviceControllerStrip import DeviceControllerStrip
from .DeviceControllerStripServer import DeviceControllerStripServer
from .Test import log
import time


class DeviceControllerStripProxy():
    def __init__(self, buttons, control_surface, column, parent=None):
        log('DCSProxy init ' + str(column))
        self._request_queue = queue.Queue()
        self._response_queue = queue.Queue()
        self.failed = False
        self.column = column
        try:
            self.server = DeviceControllerStripServer(buttons, control_surface,
                                                      column,
                                                      request_queue=self._request_queue,
                                                      response_queue=self._response_queue,
                                                      parent=parent)
            log('DCSServer created ' + str(column))
        except Exception as e:
            log('Error instantiating DCSServer: ' + str(e))
            self.failed = True
        try:
            self._server_process = Thread(target=self.server.run)
            log('DCSServer Thread created ' + str(column))
        except Exception as e:
            log('Error instantiating Thread DCSServer: ' + str(
                e))
            self.failed = True
        try:
            self._server_process.start()
            log('DCSServer Thread started ' + str(column))
        except Exception as e:
            log('Error starting DCSServer Thread: ' + str(e))
            self.failed = True
        log('DCSProxy Done! ' + str(column))
        if self.failed:
            self.server = DeviceControllerStrip(buttons, control_surface,
                                                column, parent=parent)

    def __getattr__(self, item):
        # log('DCStripProxy call for : ' + item)
        try:
            if self.failed:
                return getattr(self.server, item)
            else:
                return partial(self._call_handler, item)
        except Exception as e:
            log('DCStripProxy failed: ' + str(e) + ' ' + str(item))

    def _call_handler(self, name, *args, **kwargs):
        try:
            self._request_queue.put((name, args, kwargs))
        except Exception as e:
            log('DCSProxy: _call_handler failed: ' + str(e))
        if name == 'shutdown':
            log('DCSProxy: _call_handler shutdown')
        elif name == 'update':
            pass
