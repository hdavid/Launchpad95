# -*- coding: utf-8 -*-

from consts import *  # noqa
from _Framework.DeviceComponent import DeviceComponent as LiveDeviceComponent
from _Framework.ButtonElement import ButtonElement
from DeviceControllerStrip import DeviceControllerStrip
import time
import Live


class DeviceComponent(LiveDeviceComponent):
	__module__ = __name__
	__doc__ = ''

	def __init__(self, control_surface = None, name = "device_component", is_enabled = False, matrix = None, side_buttons = None, top_buttons = None):
		self._control_surface = control_surface
		self.name = name
		self._matrix = matrix
		self._prev_track_button = None
		self._next_track_button = None
		self._prev_device_button = None
		self._next_device_button = None
		self._prev_bank_button = None
		self._next_bank_button = None
		self._precision_button = None
		self._precision_mode = False
		self._remaining_buttons = None
		self._device = None
		self._lock_button_slots = [None,None,None,None]
		self._lock_buttons = [None,None,None,None]
		self._locked_devices = [None,None,None,None]
		self._locked_device_index = None
		self._is_active = False
		self._force = True
		self._osd = None

		LiveDeviceComponent.__init__(self)

		# Sliders
		self._sliders = []
		self.set_enabled(is_enabled)

		self._selected_track = None
		
		self._lock_buttons = [None for index in range(4)]
		self._locked_device_bank = [0 for index in range(4)]
		self._lock_button_press = [0 for index in range(4)]
		self._locked_devices = [None for index in range(4)]

		if top_buttons != None:
			# device selection buttons
			self.set_prev_device_button(top_buttons[0])
			self.set_next_device_button(top_buttons[1])
			# track selection buttons
			self.set_prev_track_button(top_buttons[2])
			self.set_next_track_button(top_buttons[3])

		if side_buttons != None:
			# on/off button
			self.set_on_off_button(side_buttons[0])

			# bank nav buttons
			self.set_bank_nav_buttons(side_buttons[1], side_buttons[2])
			self._prev_bank_button = side_buttons[1]
			self._next_bank_button = side_buttons[2]
			# precision
			self.set_precision_button(side_buttons[3])
		
			# lock buttons
			self.set_lock_button1(side_buttons[4])
			self.set_lock_button2(side_buttons[5])
			self.set_lock_button3(side_buttons[6])
			self.set_lock_button4(side_buttons[7])
		
		if matrix != None:
			self.set_matrix(matrix)
		
		
		# selected device listener
		self.song().add_appointed_device_listener(self._on_device_changed)

	def set_matrix(self, matrix):
		self._matrix = matrix
		if self._matrix:
			self._sliders = []
			for column in range(self._matrix.width()):
				slider = DeviceControllerStrip(tuple([self._matrix.get_button(column, (self._matrix.height() - 1 - row)) for row in range(self._matrix.height())]),self._control_surface)
				self._sliders.append(slider)
			self._sliders = tuple(self._sliders)
			self.set_parameter_controls(self._sliders)
		else:
			self.sliders = []
		
	def disconnect(self):
		self.song().remove_appointed_device_listener(self._on_device_changed)
		# LiveDeviceComponent.disconnect(self)
		self._prev_track_button = None
		self._next_track_button = None
		self._prev_device_button = None
		self._next_device_button = None
		self._prev_bank_button = None
		self._next_bank_button = None
		self._precision_button = None
		self._precision_mode = None
		self._remaining_buttons = None
		self._device = None

	@property
	def _locked_to_device2(self):
		return self._locked_device_index != None
		
	def set_enabled(self, active):
		if active:
			self.force = True
			self.on_selected_track_changed()
		# disable matrix.
		for slider in self._sliders:
			slider.set_enabled(active)
		# ping parent
		LiveDeviceComponent.set_enabled(self, active)

	def set_osd(self, osd):
		self._osd = osd

	def _update_OSD(self):
		if self._osd != None:
			self._osd.mode = "Device Controller"
			i = 0
			for slider in self._parameter_controls:
				if slider._parameter_to_map_to != None:
					self._osd.attribute_names[i] = str(slider._parameter_to_map_to.name)
					try:
						self._osd.attributes[i] = str(slider._parameter_to_map_to)
					except:
						self._osd.attributes[i] = str(slider._parameter_to_map_to.value)
				else:
					self._osd.attribute_names[i] = " "
					self._osd.attributes[i] = " "
				i += 1

			if self._selected_track != None:
				if self._locked_to_device2:
					if self._device != None:
						self._osd.info[0] = "track : " + self.get_device_track_name(self._device) + " (locked)"
					else:
						self._osd.info[0] = "track : " + self._selected_track.name
				else:
					self._osd.info[0] = "track : " + self._selected_track.name
			else:
				self._osd.info[0] = " "
			if self._device != None:
				name = self._device.name
				if name == "":
					name = "(unamed device)"
				if self._locked_to_device2:
					self._osd.info[1] = "device : " + name + " (locked)"
				else:
					self._osd.info[1] = "device : " + name
			else:
				self._osd.info[1] = "no device selected"
			self._osd.update()

# DEVICE SELECTION

	def _on_device_changed(self):
		if not self._locked_to_device2:
			self._selected_track = self.song().view.selected_track
			self.set_device(self.song().appointed_device)
			#self.set_device(self._selected_track.view.selected_device)
			if self.is_enabled():
				self.update()

	def on_selected_track_changed(self):
		if not self._locked_to_device2:
			self._selected_track = self.song().view.selected_track
			self.set_device(self._selected_track.view.selected_device)
			if self.is_enabled():
				self.update()
	
	def set_device(self, device):
		if(device != self._device):
			if self._number_of_parameter_banks() <= self._bank_index:
				self._bank_index = 0
			self._device = device
			LiveDeviceComponent.set_device(self, device)


# UPDATE
	def update(self):
		if self.is_enabled():
			if self._number_of_parameter_banks() <= self._bank_index:
				self._bank_index = 0
				
			if(not self._locked_to_device2):
				if(self._device != None):
					if ((not self.application().view.is_view_visible('Detail')) or (not self.application().view.is_view_visible('Detail/DeviceChain'))):
						self.application().view.show_view('Detail')
						self.application().view.show_view('Detail/DeviceChain')
			# update bank buttons colors
			if self._device != None:
				if self._prev_bank_button != None:
					self._prev_bank_button.set_on_off_values("Device.Bank.On", "Device.Bank.Off")
				if self._next_bank_button != None:
					self._next_bank_button.set_on_off_values("Device.Bank.On", "Device.Bank.Off")
			else:
				if self._prev_bank_button != None:
					self._prev_bank_button.set_on_off_values("DefaultButton.Disabled","DefaultButton.Disabled")
				if self._next_bank_button != None:
					self._next_bank_button.set_on_off_values("DefaultButton.Disabled","DefaultButton.Disabled")
			if self._matrix != None:
				for x in range(self._matrix.width()):
					for y in range(self._matrix.height()):
						self._matrix.get_button(x, y).set_enabled(True)
						
			if self._device == None and self._matrix != None:
				for x in range(self._matrix.width()):
					for y in range(self._matrix.height()):
						if self._force:
							self._matrix.get_button(x, y).set_on_off_values("DefaulyButton.Disabled","DefaultButton.Disabled")
							self._matrix.get_button(x, y).turn_off()
						
			# update parent
			LiveDeviceComponent.update(self)
			if self._sliders != None:
				for slider in self._sliders:
					slider.reset_if_no_parameter()
			# additional updates :
			self.update_track_buttons()
			self.update_device_buttons()
			self.update_lock_buttons()
			self.update_on_off_button()
			self.update_precision_button()
			self._update_OSD()
			self._force = False

	def set_prev_bank_button(self, button):
		self._prev_bank_button = button
		if self._prev_bank_button !=None and self._next_bank_button != None or self._prev_bank_button ==None and self._next_bank_button == None:
			self.set_bank_nav_buttons(self._prev_bank_button, self._next_bank_button)
		
	def set_next_bank_button(self, button):
		self._next_bank_button = button
		if self._prev_bank_button !=None and self._next_bank_button != None or self._prev_bank_button ==None and self._next_bank_button == None:
			self.set_bank_nav_buttons(self._prev_bank_button, self._next_bank_button)

# LOCK button
	def update_lock_buttons(self):
		# lock button
		if self.is_enabled():
			for index in range(len(self._locked_devices)):
				if self._lock_buttons[index] != None:
					if self._locked_devices[index] != None:
						self._lock_buttons[index].set_on_off_values("Device.Lock.Locked", "Device.Lock.Set")
					else:
						self._lock_buttons[index].set_on_off_values("Device.Lock.Empty", "Device.Lock.Empty") #LED_OFF
					if self._locked_device_index==index:
						self._lock_buttons[index].turn_on()
					else:
						self._lock_buttons[index].turn_off()
			
	def set_lock_button1(self, button):
		self.set_lock_button(button,1)
	def set_lock_button2(self, button):
		self.set_lock_button(button,2)
	def set_lock_button3(self, button):
		self.set_lock_button(button,3)
	def set_lock_button4(self, button):
		self.set_lock_button(button,4)
		
	def set_lock_button(self, button, index):
		if len(self._lock_buttons)>=index:
			if self._lock_buttons[index-1] != None:
				self._lock_buttons[index-1].remove_value_listener(self._lock_value)
			self._lock_buttons[index-1] = button
			if self._lock_buttons[index-1] != None:
				assert isinstance(self._lock_buttons[index-1], ButtonElement)
				self._lock_buttons[index-1].add_value_listener(self._lock_value, identify_sender=True)
		#self.update_lock_buttons()

	def _lock_value(self, value, sender):
		if self.is_enabled():
			index = 0
			for i in range(len(self._lock_buttons)):
				if self._lock_buttons[i] == sender:
					index = i
			if value != 0:
				self._lock_button_press[index] = time.time()
			else:
				now = time.time()
				if now - self._lock_button_press[index]>0.4:
					if self._locked_devices[index] == None:
						#save locked device
						dev = -1
						for i in range(len(self._locked_devices)):
							if self._locked_devices[i] == self._device:
								dev = i
						if dev>=0:
							if self._device != None:
								self._control_surface.show_message(" '"+self.get_device_track_name(self._device)+" - "+str(self._device.name)+"' is already stored in lock button "+ str(dev+1)+" ! aborting." )
						else:
							if self._device!=None:
								self._locked_devices[index] = self._device
								if self._device != None:
									self._control_surface.show_message(" '"+self.get_device_track_name(self._device)+" - "+str(self._device.name)+"' stored into lock button " + str(index+1))
									self._locked_device_index = index
									self.update()
									
					else:
						#remove saved device
						if self._locked_devices[index] != None:
							self._control_surface.show_message("removing '"+self.get_device_track_name(self._locked_devices[index])+" - "+str(self._locked_devices[index].name)+"' from block button "+ str(index+1) )
							self._locked_devices[index] = None
							self._locked_device_index = None
				else:
					#use selected device
					if self._locked_device_index == index:
						if self._locked_devices[index] != None:
							if self._locked_devices[index]!= None:
								self._control_surface.show_message("unlocked from ' "+self.get_device_track_name(self._locked_devices[index])+" - "+str(self._locked_devices[index].name)+"' ("+str(index+1)+")")
						self._locked_device_index = None
					elif self._locked_devices[index] != None:
						self._locked_device_index = index
						self.set_device(self._locked_devices[index])
						if self._locked_devices[index]!= None:
							self._control_surface.show_message("locked to '"+self.get_device_track_name(self._locked_devices[index])+" - "+str(self._locked_devices[index].name)+" (" +str(index+1)+")" )
						self.update()
			self.update_track_buttons()
			self.update_device_buttons()
			self._update_OSD()
			if self._locked_to_device2:
				self.on_selected_track_changed()		
			self.update_lock_buttons()
				
		
	def get_device_track_name(self, device):
			if str(type(device)) == "<class 'Track.Track'>":
				return str(device.name)
			else:
				return self.get_device_track_name(device.canonical_parent)
			
			

# Precision button
	def update_precision_button(self):
		if self._precision_button != None and self.is_enabled():
			if self._precision_button != None:
				if self._device != None:
					self._precision_button.set_on_off_values("Device.PrecisionSlider.On", "Device.PrecisionSlider.Off")
					if self._precision_mode:
						self._precision_button.turn_on()
					else:
						self._precision_button.turn_off()
				else:
					self._precision_button.set_on_off_values("DefaultButton.Disabled","DefaultButton.Disabled")
					self._precision_button.turn_off()

	def _precision_value(self, value, sender):
		if ((not sender.is_momentary()) or (value is not 0)):
			if (self._precision_button != None and self.is_enabled()):
				self._precision_mode = not self._precision_mode
				self.update_precision_button()
				for slider in self._sliders:
					slider.set_precision_mode(self._precision_mode)

	def set_precision_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if self._precision_button != button:
			if self._precision_button != None:
				self._precision_button.remove_value_listener(self._precision_value)
			self._precision_button = button
			if self._precision_button != None:
				assert isinstance(button, ButtonElement)
				self._precision_button.add_value_listener(self._precision_value, identify_sender=True)
				self.update()


# ON OFF button
	def update_on_off_button(self):
		# on/off button
		if self._on_off_button != None and self.is_enabled():
			if self._on_off_button != None:
				parameter = self._on_off_parameter()
				if parameter != None:
					self._on_off_button.set_on_off_values("Mode.Device.On", "Mode.Device.Off")
					if parameter.is_enabled and parameter.value > 0:
						self._on_off_button.turn_on()
					else:
						self._on_off_button.turn_off()
				else:
					self._on_off_button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")
					self._on_off_button.turn_off()

	def _on_off_value(self, value):
		if self._on_off_button != None and self.is_enabled():
			LiveDeviceComponent._on_off_value(self, value)
			self.update_on_off_button()


	def set_on_off_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if self._on_off_button != button:
			if self._on_off_button != None:
				self._on_off_button.remove_value_listener(self._on_off_value)
			self._on_off_button = button
			if self._on_off_button != None:
				assert isinstance(button, ButtonElement)
				self._on_off_button.add_value_listener(self._on_off_value)

# TRACKS Buttons
	def update_track_buttons(self):
		# tracks
		if self.is_enabled():
			if(self._prev_track_button != None):
				self._prev_track_button.set_on_off_values("Mode.Device.On", "Mode.Device.Off")
				if(self.selected_track_idx > 0 and not self._locked_to_device2):
					self._prev_track_button.turn_on()
				else:
					self._prev_track_button.turn_off()

			if(self._next_track_button != None):
				self._next_track_button.set_on_off_values("Mode.Device.On", "Mode.Device.Off")
				if(self.selected_track_idx < len(self.song().tracks) - 1 and not self._locked_to_device2):
					self._next_track_button.turn_on()
				else:
					self._next_track_button.turn_off()

	def set_next_track_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._next_track_button != button):
			if (self._next_track_button != None):
				self._next_track_button.remove_value_listener(self._next_track_value)
			self._next_track_button = button
			if (self._next_track_button != None):
				assert isinstance(button, ButtonElement)
				self._next_track_button.add_value_listener(self._next_track_value, identify_sender=True)

	def _next_track_value(self, value, sender):
		assert (self._next_track_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value is not 0)):
				if(self.selected_track_idx < len(self.song().tracks) - 1 and not self._locked_to_device2):
					self.song().view.selected_track = self.song().tracks[self.selected_track_idx + 1]

	def set_prev_track_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._prev_track_button != button):
			if (self._prev_track_button != None):
				self._prev_track_button.remove_value_listener(self._prev_track_value)
			self._prev_track_button = button
			if (self._prev_track_button != None):
				assert isinstance(button, ButtonElement)
				self._prev_track_button.set_on_off_values("Mode.Device.On", "Mode.Device.Off")
				self._prev_track_button.add_value_listener(self._prev_track_value, identify_sender=True)

	def _prev_track_value(self, value, sender):
		assert (self._prev_track_button != None)
		assert (value in range(128))
		if ((not sender.is_momentary()) or (value is not 0)):
			if self.is_enabled():
				if(self.selected_track_idx > 0 and not self._locked_to_device2):
					self.song().view.selected_track = self.song().tracks[self.selected_track_idx - 1]
					self.update()

	def selected_track(self):
		return self.song().view.selected_track

	

# DEVICES
	def update_device_buttons(self):
		if self.is_enabled():
			if(self._prev_device_button != None):
				self._prev_device_button.set_on_off_values("Mode.Device.On", "Mode.Device.Off")
				if(len(self.selected_track().devices) > 0 and self.selected_device_idx > 0 and not self._locked_to_device2):
					self._prev_device_button.turn_on()
				else:
					self._prev_device_button.turn_off()
			if(self._next_device_button != None):
				self._next_device_button.set_on_off_values("Mode.Device.On", "Mode.Device.Off")
				if(len(self.selected_track().devices) > 0 and self.selected_device_idx < len(self.selected_track().devices) - 1 and not self._locked_to_device2 ):
					self._next_device_button.turn_on()
				else:
					self._next_device_button.turn_off()

	def set_next_device_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._next_device_button != button):
			if (self._next_device_button != None):
				self._next_device_button.remove_value_listener(self._next_device_value)
			self._next_device_button = button
			if (self._next_device_button != None):
				assert isinstance(button, ButtonElement)
				self._next_device_button.add_value_listener(self._next_device_value, identify_sender=True)

	def _next_device_value(self, value, sender):
		assert (self._next_device_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value is not 0)):
				if self.selected_track() != None and len(self.selected_track().devices) > 0:
					if(self.selected_device_idx < len(self.selected_track().devices) - 1 and not self._locked_to_device2):
						self.song().view.select_device(self.selected_track().devices[self.selected_device_idx + 1])

	def set_prev_device_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._prev_device_button != button):
			if (self._prev_device_button != None):
				self._prev_device_button.remove_value_listener(self._prev_device_value)
			self._prev_device_button = button
			if (self._prev_device_button != None):
				assert isinstance(button, ButtonElement)
				self._prev_device_button.add_value_listener(self._prev_device_value, identify_sender=True)

	def _prev_device_value(self, value, sender):
		assert (self._prev_device_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value is not 0)):
				if self.selected_track() != None and len(self.selected_track().devices) > 0:
					if(self.selected_device_idx > 0 and not self._locked_to_device2):
						self.song().view.select_device(self.selected_track().devices[self.selected_device_idx - 1])

	@property
	def selected_device_idx(self):
		devices = list(self.song().view.selected_track.devices)
		return devices.index(self._device) if self._device in devices else None
		#return self.tuple_idx(self.song().view.selected_track.devices, self._device)

	@property
	def selected_track_idx(self):
		tracks = list(self.song().tracks)
		return tracks.index(self.song().view.selected_track) if self.song().view.selected_track in tracks else None
		#return self.tuple_idx(self.song().tracks, self.song().view.selected_track)

	# utils

	#def tuple_idx(self, tuple, obj):
	#	for i in xrange(0, len(tuple)):
	#		if (tuple[i] == obj):
	#			return i
	#	return(False)
