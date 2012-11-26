# emacs-mode: -*- python-*-
import Live
from consts import *
from _Framework.MixerComponent import MixerComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from PreciseButtonSliderElement import PreciseButtonSliderElement

# todo :
# - XXX fix precise mode increments
# - if no device selected => turn matrix led off.

class DeviceControllerComponent(DeviceComponent):
	__module__ = __name__
	__doc__ = ''

	def __init__(self,matrix,side_buttons,top_buttons,parent):
		self._parent=parent
		self._matrix=matrix
		self._prev_track_button=None
		self._next_track_button=None
		self._prev_device_button=None
		self._next_device_button=None
		self._prev_bank_button=None
		self._next_bank_button=None
		self._precision_button=None
		self._precision_mode=False
		self._remaining_buttons=None
		self._device= None
		self._is_active = False

		DeviceComponent.__init__(self)

		#Sliders
		self._sliders = []
		self.set_enabled(False)
		
		for column in range(8):
			slider = PreciseButtonSliderElement(tuple([self._matrix.get_button(column, (7 - row)) for row in range(8) ]))
			slider.set_parent(self)
			slider.set_mode(3)
			self._sliders.append(slider)
		self._sliders=tuple(self._sliders)
		self.set_parameter_controls(self._sliders)
		
		#device selection buttons
		self.set_prev_device_button(top_buttons[0])
		self.set_next_device_button(top_buttons[1])
		#track selection buttons
		self.set_prev_track_button(top_buttons[2])
		self.set_next_track_button(top_buttons[3])
				
		#on/off button
		self.set_on_off_button(side_buttons[0])
		#lock button
		self.set_lock_button(side_buttons[1])
		self.set_lock_callback(self._lock_callback_function)
		#bank nav buttons
		self.set_bank_nav_buttons(side_buttons[2],side_buttons[3])
		self._prev_bank_button=side_buttons[2]
		self._next_bank_button=side_buttons[3]
		#precision
		self.set_precision_button(side_buttons[4])
		#remaining buttons that need to be turned off !
		self.set_remaining_buttons([side_buttons[5],side_buttons[6],side_buttons[7]])
		
		#selected device listener
		self.song().add_appointed_device_listener(self._on_device_changed)
		

	def disconnect(self):
		self.song().remove_appointed_device_listener(self._on_device_changed)
		#DeviceComponent.disconnect(self)
		self._prev_track_button=None
		self._next_track_button=None
		self._prev_device_button=None
		self._next_device_button=None
		self._prev_bank_button=None
		self._next_bank_button=None
		self._precision_button=None
		self._precision_mode=None
		self._remaining_buttons=None
		self._device=None
		

	def set_enabled(self,active):
		#disable matrix.
		for slider in self._sliders:
			slider.set_disabled(not active)
		#ping parent
		DeviceComponent.set_enabled(self,active)
		
#DEVICE SELECTION
	def _on_device_changed(self):
 		if self._locked_to_device != True:		
			self.set_device(self.song().appointed_device)
			if self.is_enabled():
				self.update()
	
	def on_selected_track_changed(self):
 		if self._locked_to_device != True:
 			track = self.song().view.selected_track
  			self.set_device(track.view.selected_device)
			if self.is_enabled():
				self.update()
					
	def set_device(self,device):
		if(device != self._device):
			self._device=device
			DeviceComponent.set_device(self,device)
			
#UPDATE		
	def update(self):
		if self.is_enabled():
			if(not self._locked_to_device):
				if(self._device==None):
					if ((not self.application().view.is_view_visible('Detail')) or (not self.application().view.is_view_visible('Detail/DeviceChain'))):
 						self.application().view.show_view('Detail')
 						self.application().view.show_view('Detail/DeviceChain')
			#update bank buttons colors
			if self._device != None :
				if(self._prev_bank_button != None):
					self._prev_bank_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
				if(self._next_bank_button != None):
					self._next_bank_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
			else :
					self._prev_bank_button.set_on_off_values(LED_OFF,LED_OFF)
					self._next_bank_button.set_on_off_values(LED_OFF,LED_OFF)
			#update parent
			DeviceComponent.update(self)
			#reset sliders if no device
			if(self._device==None):
				for slider in self._sliders:
					slider.reset()
			#additional updates :
			self.update_track_buttons()
			self.update_device_buttons()
			self.update_lock_button()	
			self.update_on_off_button()
			self.update_precision_button()
			self.update_remaining_buttons()
			

#REMAINING buttons
	def set_remaining_buttons(self,remaining_buttons):
		self._remaining_buttons=remaining_buttons
		for index in range(len(self._remaining_buttons)):
			self._remaining_buttons[index].set_on_off_values(LED_OFF,LED_OFF)
				
	def update_remaining_buttons(self):
		if(self._remaining_buttons!=None):
			for index in range(len(self._remaining_buttons)) :
				if(self._remaining_buttons[index]!=None):
					self._remaining_buttons[index].set_on_off_values(LED_OFF,LED_OFF)
					self._remaining_buttons[index].turn_off()
				


# LOCK button
	def update_lock_button(self):
		#lock button
		if (self._lock_button!=None and self.is_enabled()):
			if (self._device != None):
				self._lock_button.set_on_off_values(RED_FULL,RED_THIRD)
				if (self._locked_to_device):
					self._lock_button.turn_on()
				else:
					self._lock_button.turn_off()
			else:
				self._lock_button.set_on_off_values(LED_OFF,LED_OFF)
				self._lock_button.turn_off()
	
	def _lock_callback_function(self):
		#lock to a one device
		self.set_lock_to_device(not self._locked_to_device, self._device)
		#display a message about the lock status
		if(self._locked_to_device and  self._device != None):
			self._parent._parent.show_message("Launchpad locked to " + str(self._device.name)+" !")
		self.update_track_buttons()
		self.update_device_buttons()
		if(self._locked_to_device):
			self.on_selected_track_changed()
		
	
		
						
# Precision button
	def update_precision_button(self):
		if (self._precision_button!=None and self.is_enabled()):
			if (self._precision_button!=None):
				if self._device != None : 
					self._precision_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
					if self._precision_mode:
						self._precision_button.turn_on()
					else:
						self._precision_button.turn_off()
				else:
					self._precision_button.set_on_off_values(LED_OFF,LED_OFF)
					self._precision_button.turn_off()

	def _precision_value(self, value,sender):
		if ((not sender.is_momentary()) or (value is not 0)):
			if (self._precision_button!=None and self.is_enabled()):
				self._precision_mode=not self._precision_mode
				self.update_precision_button()
				for slider in self._sliders:
					slider.set_precision_mode(self._precision_mode)
				
	def set_precision_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._precision_button != button):
			if (self._precision_button  != None):
				self._precision_button.remove_value_listener(self._precision_value)
			self._precision_button = button
			if (self._precision_button  != None):
				assert isinstance(button, ButtonElement)
				self._precision_button.add_value_listener(self._precision_value, identify_sender=True)
				self.update()

					
# ON OFF button
	def update_on_off_button(self):
		#on/off button
		if (self._lock_button!=None and self.is_enabled()):
			if (self._on_off_button!=None):
				parameter = self._on_off_parameter()
				if parameter != None :
					self._on_off_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
					if parameter.is_enabled and parameter.value>0:
						self._on_off_button.turn_on()
					else:
						self._on_off_button.turn_off()
				else:
					self._on_off_button.set_on_off_values(LED_OFF,LED_OFF)
					self._on_off_button.turn_off()

	def _on_off_value(self, value):
		if (self._lock_button!=None and self.is_enabled()):
			DeviceComponent._on_off_value(self,value)
			self.update_on_off_button()



# TRACKS Buttons
	def update_track_buttons(self):
		#tracks
		if self.is_enabled():
			if(self._prev_track_button!=None):
				self._prev_track_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				if(self.selected_track_idx() >0 and not self._locked_to_device):
					self._prev_track_button.turn_on()
				else:
					self._prev_track_button.turn_off()

			if(self._next_track_button!=None):
				self._next_track_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				if(self.selected_track_idx() < len(self.song().tracks)-1 and not self._locked_to_device):
					self._next_track_button.turn_on()
				else:
					self._next_track_button.turn_off()

	def set_next_track_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._next_track_button != button):
			if (self._next_track_button  != None):
				self._next_track_button.remove_value_listener(self._next_track_value)
			self._next_track_button = button
			if (self._next_track_button  != None):
				assert isinstance(button, ButtonElement)
				self._next_track_button.add_value_listener(self._next_track_value, identify_sender=True)

	def _next_track_value(self, value, sender):
		assert (self._next_track_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._is_active:
			if ((not sender.is_momentary()) or (value is not 0)):
				#self._parent._parent.log_message(str(self.selected_track_idx()))
				if(self.selected_track_idx() < len(self.song().tracks)-1 and not self._locked_to_device):
					self.song().view.selected_track=self.song().tracks[self.selected_track_idx() + 1]
	
	def set_prev_track_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._prev_track_button != button):
			if (self._prev_track_button  != None):
				self._prev_track_button.remove_value_listener(self._prev_track_value)
			self._prev_track_button = button
			self._prev_track_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
			if (self._prev_track_button  != None):
				assert isinstance(button, ButtonElement)
				self._prev_track_button.add_value_listener(self._prev_track_value, identify_sender=True)

	def _prev_track_value(self, value, sender):
		assert (self._prev_track_button != None)
		assert (value in range(128))
		if ((not sender.is_momentary()) or (value is not 0)):
			if self.is_enabled() and self._is_active:
				if(self.selected_track_idx() >0 and not self._locked_to_device):
					self.song().view.selected_track=self.song().tracks[self.selected_track_idx() - 1]
					self.update()
				


	def selected_track(self):
		return self.song().view.selected_track

	def selected_track_idx(self):
		return self.tuple_idx(self.song().tracks, self.song().view.selected_track)



# DEVICES
	def update_device_buttons(self):
		if self.is_enabled():
			if(self._prev_device_button!=None):
				self._prev_device_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				if(self.selected_device_idx() >0  and not self._locked_to_device and len(self.selected_track().devices)>0):
					self._prev_device_button.turn_on()
				else:
					self._prev_device_button.turn_off()		
			if(self._next_device_button!=None):
				self._next_device_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				if(self.selected_device_idx() < len(self.selected_track().devices)-1 and not self._locked_to_device and len(self.selected_track().devices)>0):
					self._next_device_button.turn_on()
				else:
					self._next_device_button.turn_off()

	def set_next_device_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._next_device_button != button):
			if (self._next_device_button  != None):
				self._next_device_button.remove_value_listener(self._next_device_value)
			self._next_device_button = button
			if (self._next_device_button  != None):
				assert isinstance(button, ButtonElement)
				self._next_device_button.add_value_listener(self._next_device_value, identify_sender=True)

	def _next_device_value(self, value, sender):
		assert (self._next_device_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._is_active:
			if ((not sender.is_momentary()) or (value is not 0)):
				#self._parent._parent.log_message(str(self.selected_track()))
				if self.selected_track()!=None and len(self.selected_track().devices)>0:
					if(self.selected_device_idx() < len(self.selected_track().devices)-1 and not self._locked_to_device):
						self.song().view.select_device(self.selected_track().devices[self.selected_device_idx() + 1])

	def set_prev_device_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._prev_device_button != button):
			if (self._prev_device_button  != None):
				self._prev_device_button.remove_value_listener(self._prev_device_value)
			self._prev_device_button = button
			if (self._prev_device_button  != None):
				assert isinstance(button, ButtonElement)
				self._prev_device_button.add_value_listener(self._prev_device_value, identify_sender=True)

	def _prev_device_value(self, value, sender):
		assert (self._prev_device_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._is_active:
			if ((not sender.is_momentary()) or (value is not 0)):
				#self._parent._parent.log_message(str(self.selected_track()))
				if self.selected_track()!=None and len(self.selected_track().devices)>0:
					if(self.selected_device_idx()>0 and not self._locked_to_device):
						self.song().view.select_device(self.selected_track().devices[self.selected_device_idx() - 1])
						#self.update()

	def selected_device_idx(self):
		return self.tuple_idx(self.song().view.selected_track.devices, self._device)



	#utils
	
	def tuple_idx(self,tuple, obj):
		for i in xrange(0,len(tuple)):
			if (tuple[i] == obj):
				return i
		return(False)

	def log_message(self, message):
		self._parent.log_message(message)
