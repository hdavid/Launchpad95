
MODE_NAMES = ('Session',	'Instrument Controller', 'Device Controller', 'User 1', 'Drum Step Sequencer', 'Melodic Step Sequencer', 'User 2', 'Mixer', 'Scale', 'Quick Scale', 'MultiNote')
MAP_NAMES = ('Session Mode', 	'Instrument Mode','Device Mode', 'User1 Mode', 'Combined Mode', 'Melodic Step Mode', 'User2 Mode', 'Mixer Mode', 'Scale Mode', 'Quick Scale Mode','MultiNote Mode')


class Launchpad95M4LInterfaceMixin(object):
	""" LPCM4LInterfaceMixin is a mixin to be used with MainSelectorComponent that provides a listenable property for M4L and refresh functions for classes. """

	def init_m4l_interface(self):
		""" Initializes the interface. """
		self._refresh_type = 'map'
		self._refresh_listener = None
		self._m4lmode_index = 0		
		self._attributes = [ ' ' for _ in range(8) ]
		self._attribute_names = [ ' ' for _ in range(8) ]
		self._info = [' ', ' ']
		self._map_name = MAP_NAMES[self._m4lmode_index]
		return
	
	def set_m4lmode(self,mode_str):
		#self.log(mode_str)
		if mode_str == 'SCALE':			
			self._m4lmode_index = 8
		elif mode_str == 'QUICK_SCALE':
			self._m4lmode_index = 9
		elif mode_str == 'MULTINOTE':			
			self._m4lmode_index = 10
		elif mode_str == 'INST':
			self._m4lmode_index = 1
		elif mode_str == 'STEP':
			self._m4lmode_index = 4
		self.refresh_map_display()
		
	@property
	def mode_name(self):
		""" Returns the name of the current mode. """
		return MODE_NAMES[self._m4lmode_index]

	@property
	def mode_attributes(self):
		""" Returns the attributes of the current mode. """
		return self._attributes

	@property
	def mode_attribute_names(self):
		""" Returns the names of the attributes of the current mode. """
		return self._attribute_names

	@property
	def mode_info(self):
		""" Returns info about the current mode. """
		return self._info

	def clear_mode_info(self):
		self._info = [' ', ' ']
		
	def clear_attributes(self):
		self._attributes = [ ' ' for _ in range(8) ]
		self._attribute_names = [ ' ' for _ in range(8) ]
		
	@property
	def mode_map(self):
		""" Returns the name of the relevant map for the current mode. """
		return MAP_NAMES[self._m4lmode_index]
		
	def disconnect_m4l_interface(self):
		""" Disconnects the interface. """
		self._refresh_listener = None
		return

	@property
	def refresh(self):
		""" Returns the type of refresh to perform. """
		return self._refresh_type

	def add_refresh_listener(self, listener):
		""" Adds a refresh listener.  This only allows one listener to be added. """
		self._refresh_listener = listener

	def remove_refresh_listener(self, listener):
		""" Removes the refresh listener. """
		self._refresh_listener = None
		return

	def refresh_has_listener(self, listener):
		""" Returns whether refresh has a listener. """
		return self._refresh_listener is not None

	def refresh_map_display(self, args = None):
		""" Refreshes the M4L device's map display. """
		self._refresh_type = 'map'
		self._notify_listener()

	def refresh_status_display(self, args = None):
		""" Refreshes the M4L device's entire status display. """
		self._refresh_type = 'status'
		self._notify_listener()

	def refresh_attributes(self, args = None):
		""" Refreshes the M4L device's attribute display. """
		self._refresh_type = 'attributes'
		self._notify_listener()

	def refresh_info(self, args = None):
		""" Refreshes the M4L device's info display. """
		self._refresh_type = 'info'
		self._notify_listener()

	def toggle_status(self, args = None):
		""" Toggles the status display on/off. """
		self._refresh_type = 'status_toggle'
		self._notify_listener()

	def toggle_map(self, args = None):
		""" Toggles the map display on/off. """
		self._refresh_type = 'map_toggle'
		self._notify_listener()

	def _notify_listener(self):
		""" Notifies listener (M4L device) that a refresh is needed. """
		if self._refresh_listener is not None:
			self._refresh_listener()
		return
	
	