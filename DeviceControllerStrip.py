# -*- coding: utf-8 -*-

from _Framework.ButtonSliderElement import ButtonSliderElement
from _Framework.InputControlElement import *  # noqa
from consts import *  # noqa
import math

SLIDER_MODE_OFF = 0
SLIDER_MODE_TOGGLE = 1
SLIDER_MODE_SLIDER = 2
SLIDER_MODE_PRECISION_SLIDER = 3
SLIDER_MODE_SMALL_ENUM = 4
SLIDER_MODE_BIG_ENUM = 5

#TODO: repeat buttons.
# not exact / rounding values in slider and precision slider


class DeviceControllerStrip(ButtonSliderElement):


	def __init__(self, buttons, control_surface, parent = None):
		ButtonSliderElement.__init__(self, buttons)
		self._control_surface = control_surface
		self._parent = parent
		self._num_buttons = len(buttons)
		self._value_map = tuple([float(index) / (self._num_buttons-1) for index in range(self._num_buttons)])
		self._precision_mode = False
		self._enabled = True
	
	def set_enabled(self,enabled):
		self._enabled = enabled
	
	def set_precision_mode(self, precision_mode):
		self._precision_mode = precision_mode
		self.update()
	
	@property
	def _value(self):
		if self._parameter_to_map_to != None:	
			return self._parameter_to_map_to.value
		else:
			return 0
			
	@property
	def _max(self):
		if self._parameter_to_map_to != None:	
			return self._parameter_to_map_to.max
		else:
			return 0
	
	@property
	def _min(self):
		if self._parameter_to_map_to != None:	
			return self._parameter_to_map_to.min
		else:
			return 0

	@property
	def _range(self):
		if self._parameter_to_map_to != None:	
			return self._parameter_to_map_to.max - self._parameter_to_map_to.min
		else:
			return 0

	@property
	def _default_value(self):
		if self._parameter_to_map_to != None:	
			return self._parameter_to_map_to._default_value
		else:
			return 0
				
	@property
	def _is_quantized(self):
		if self._parameter_to_map_to != None:	
			return self._parameter_to_map_to.is_quantized
		else:
			return false
					
	@property
	def _mode(self):
		if self._parameter_to_map_to != None:	
			if self._is_quantized:
			 	if self._range == 1:
					return SLIDER_MODE_TOGGLE
				elif self._range<=self._num_buttons:
					return SLIDER_MODE_SMALL_ENUM
				else:
					return SLIDER_MODE_BIG_ENUM
			else:
				if self._precision_mode:
					return SLIDER_MODE_PRECISION_SLIDER
				else:
					return SLIDER_MODE_SLIDER				
		else:
			return SLIDER_MODE_OFF
				

	def update(self):
		if self._enabled:
			if self._mode == SLIDER_MODE_TOGGLE:
				self._update_toggle()
			elif self._mode == SLIDER_MODE_SMALL_ENUM:
				self._update_small_enum()
			elif self._mode == SLIDER_MODE_BIG_ENUM:
				self._update_big_enum()
			elif (self._mode == SLIDER_MODE_SLIDER):
				self._update_slider()
			elif (self._mode == SLIDER_MODE_PRECISION_SLIDER):
				self._update_precision_slider()
			else:
				self._update_off()


	def reset(self):
		self._update_off()
		
	def reset_if_no_parameter(self):
		if self._parameter_to_map_to == None:
			self.reset()
			
	def _update_off(self):
		v =  ["DefaultButton.Disabled" for index in range(len(self._buttons))]
		self._update_buttons(tuple(v))
	
	def _update_toggle(self):
		v =  ["DefaultButton.Disabled" for index in range(len(self._buttons))]
		if self._value==self._max:
		 	v[0]="Device.Toggle.On"
		else:
			v[0]="Device.Toggle.Off"
		self._update_buttons(tuple(v))

	def _update_small_enum(self):
		v =  ["DefaultButton.Disabled" for index in range(len(self._buttons))]
		for index in range(int(self._range+1)):
			if self._value==index+self._min:
				v[index]="Device.Enum.On"
			else:
				v[index]="Device.Enum.Off"
		self._update_buttons(tuple(v))

	def _update_big_enum(self):
		v =  ["DefaultButton.Disabled" for index in range(len(self._buttons))]
		if self._value>self._min:
			v[3]="Device.BigEnum.On"
		else:
			v[3]="Device.BigEnum.Off"
		if self._value<self._max:
			v[4]="Device.BigEnum.On"
		else:
			v[4]="Device.BigEnum.Off"
		self._update_buttons(tuple(v))
	
	def _update_slider(self):
		v =  ["DefaultButton.Disabled" for index in range(len(self._buttons))]
		for index in range(len(self._buttons)):
			if self._value >=self._value_map[index]*self._range+self._min:
				v[index]="Device.Slider.On"
			else:
				v[index]="Device.Slider.Off"
		self._update_buttons(tuple(v))
		
	def _update_precision_slider(self):
		v =  ["DefaultButton.Disabled" for index in range(len(self._buttons))]
		if self._value>self._min:
			v[3]="Device.PrecisionSlider.On"
		else:
			v[3]="Device.PrecisionSlider.Off"
			
		if self._value<self._max:
			v[4]="Device.PrecisionSlider.On"
		else:
			v[4]="Device.PrecisionSlider.Off"
		self._update_buttons(tuple(v))
			
	def _update_buttons(self, buttons):
		assert isinstance(buttons, tuple)
		assert (len(buttons) == len(self._buttons))
		for index in range(len(self._buttons)):
			self._buttons[index].set_on_off_values(buttons[index],buttons[index])
			if buttons[index]>0:
				self._buttons[index].turn_on()
			else:
				self._buttons[index].turn_off()

	def _button_value(self, value, sender):
		assert isinstance(value, int)
		assert (sender in self._buttons)
		self._last_sent_value = -1
		if (self._parameter_to_map_to != None and self._enabled and ((value != 0) or (not sender.is_momentary()))):
			if (value != self._last_sent_value):
				index_of_sender = list(self._buttons).index(sender)
				if (self._mode == SLIDER_MODE_TOGGLE) and index_of_sender==0:
					if self._value == self._max:
						self._parameter_to_map_to.value = self._min
					else:
						self._parameter_to_map_to.value = self._max
						
				elif self._mode == SLIDER_MODE_SMALL_ENUM:
					self._parameter_to_map_to.value = index_of_sender + self._min
					
				elif self._mode == SLIDER_MODE_BIG_ENUM:
					if index_of_sender>=4:
						inc = 2**(index_of_sender - 3 -1)
						if self._value + inc <= self._max:
							self._parameter_to_map_to.value += inc
						else:
							self._parameter_to_map_to.value = self._max
					else:	
						inc = 2**(4 - index_of_sender -1)
						if self._value - inc >= self._min:
							self._parameter_to_map_to.value -= inc
						else:
							self._parameter_to_map_to.value = self._min
							
							
				elif (self._mode == SLIDER_MODE_SLIDER):
					self._parameter_to_map_to.value = self._value_map[index_of_sender]*self._range + self._min

					
				elif (self._mode == SLIDER_MODE_PRECISION_SLIDER):
					inc = float(self._range) / 128
					if self._range>7 and inc<1:
						inc=1
					if index_of_sender >= 4:
						inc = inc * 2**(index_of_sender - 3-1)
						if self._value + inc <= self._max:
							self._parameter_to_map_to.value += inc
						else:
							self._parameter_to_map_to.value = self._max
					else:
						inc = inc * 2**(4 - index_of_sender-1)
						if self._value - inc >= self._min:
							self._parameter_to_map_to.value -= inc
						else:
							self._parameter_to_map_to.value = self._min
				
				
			self.notify_value(value)
			if self._parent is not None:
				self._parent._update_OSD()

	def _on_parameter_changed(self):
		assert (self._parameter_to_map_to != None)
		if self._parent is not None:
			self._parent._update_OSD()
		self.update()
