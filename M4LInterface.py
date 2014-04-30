#import Tkinter
#from tkinter import *
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

class M4LInterface(ControlSurfaceComponent):

	def __init__(self):
		ControlSurfaceComponent.__init__(self)
		self._name = 'OSD'
		self._update_listener = None
		self._updateML_listener = None
		self.mode = ' '
		self.clear()
		#self._ui = Tkinter.Tk()
		#self._ui.geometry('100*500+500+500')
		# set up your interface, then run it with:
		#self._ui.mainloop()
		#self._ui.title('Launchpad95')
	
	def disconnect(self):
		self._updateM4L_listener = None

	def set_mode(self,mode):
		self.clear()
		self.mode = mode
		
	def clear(self):
		self.info = [' ', ' ']
		self.attributes = [ ' ' for _ in range(8) ]
		self.attribute_names = [ ' ' for _ in range(8) ]
	
	def set_update_listener(self, listener):
		self._update_listener = listener

	def remove_update_listener(self, listener):
		self._update_listener = None

	def update_has_listener(self):
		return self._update_listener is not None
			
	def set_update_listener(self, listener):
		self._update_listener = listener

	def remove_update_listener(self, listener):
		self._update_listener = None
		
	def update_has_listener(self):
		return self._update_listener is not None
	
	@property
	def updateML(self):
		return True

	def set_updateML_listener(self, listener):
		self._updateML_listener = listener
			
	def add_updateML_listener(self, listener):
		self._updateML_listener = listener
		return

	def remove_updateML_listener(self, listener):
		self._updateML_listener = None
		return
	
	def updateML_has_listener(self, listener):
		return self._updateML_listener is not None
		
	def update(self, args = None):
		if self.updateML_has_listener(None):
			self._updateML_listener()
			

	
	