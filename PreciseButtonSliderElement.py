
from _Framework.ButtonSliderElement import ButtonSliderElement
SLIDER_MODE_SINGLE = 0
SLIDER_MODE_VOLUME = 1
SLIDER_MODE_PAN = 2

class PreciseButtonSliderElement(ButtonSliderElement):
	""" Class representing a set of buttons used as a slider """

	def __init__(self, buttons):
		ButtonSliderElement.__init__(self, buttons)
		num_buttons = len(buttons)
		self._disabled = False
		self._mode = SLIDER_MODE_VOLUME
		self._value_map = tuple([ float(index / num_buttons) for index in range(num_buttons) ])

	def set_disabled(self, disabled):
		assert isinstance(disabled, type(False))
		self._disabled = disabled

	def set_mode(self, mode):
		assert mode in (SLIDER_MODE_SINGLE, SLIDER_MODE_VOLUME, SLIDER_MODE_PAN)
		if (mode != self._mode):
			self._mode = mode

	def set_value_map(self, value_map):
		assert isinstance(value_map, (tuple, type(None)))
		assert len(value_map) == len(self._buttons)
		self._value_map = value_map

	def send_value(self, value):
		if (not self._disabled):
			assert (value != None)
			assert isinstance(value, int)
			assert (value in range(128))
			if value != self._last_sent_value:
				if self._mode == SLIDER_MODE_SINGLE:
					ButtonSliderElement.send_value(self, value)
				elif self._mode == SLIDER_MODE_VOLUME:
					self._send_value_volume(value)
				elif self._mode == SLIDER_MODE_PAN:
					self._send_value_pan(value)
				else:
					assert False
				self._last_sent_value = value

	def connect_to(self, parameter):
		ButtonSliderElement.connect_to(self, parameter)
		if self._parameter_to_map_to != None:
			self._last_sent_value = -1
			self._on_parameter_changed()

	def release_parameter(self):
		old_param = self._parameter_to_map_to
		ButtonSliderElement.release_parameter(self)
		if not self._disabled and old_param != None:
			for button in self._buttons:
				button.reset()

	def reset(self):
		if not self._disabled and self._buttons != None:
			for button in self._buttons:
				if button != None:
					button.reset()

	def _send_value_volume(self, value):
		index_to_light = -1
		normalised_value = float(value) / 127.0
		if normalised_value > 0.0:
			for index in range(len(self._value_map)):
				if normalised_value <= self._value_map[index]:
					index_to_light = index
					break

		self._send_mask(tuple([ index <= index_to_light for index in range(len(self._buttons)) ]))

	def _send_value_pan(self, value):
		num_buttons = len(self._buttons)
		button_bits = [ False for index in range(num_buttons) ]
		normalised_value = float(2 * value / 127.0) - 1.0
		if value in (63, 64):
			normalised_value = 0.0
		if normalised_value < 0.0:
			for index in range(len(self._buttons)):
				button_bits[index] = self._value_map[index] >= normalised_value
				if self._value_map[index] >= 0:
					break

		elif normalised_value > 0.0:
			for index in range(len(self._buttons)):
				r_index = len(self._buttons) - 1 - index
				button_bits[r_index] = self._value_map[r_index] <= normalised_value
				if self._value_map[r_index] <= 0:
					break

		else:
			for index in range(len(self._buttons)):
				button_bits[index] = self._value_map[index] == normalised_value

		self._send_mask(tuple(button_bits))

	def _send_mask(self, mask):
		assert isinstance(mask, tuple)
		assert (len(mask) == len(self._buttons))
		for index in range(len(self._buttons)):
			if mask[index]:
				self._buttons[index].turn_on()
			else:
				self._buttons[index].turn_off()

	def _button_value(self, value, sender):
		assert isinstance(value, int)
		assert (sender in self._buttons)
		self._last_sent_value = -1
		if (self._parameter_to_map_to != None and (not self._disabled) and ((value != 0) or (not sender.is_momentary()))):
			index_of_sender = list(self._buttons).index(sender)
			# handle precision mode
			#if(not self._precision_mode):
			if self._parameter_to_map_to != None and self._parameter_to_map_to.is_enabled:
				self._parameter_to_map_to.value = self._value_map[index_of_sender]
			#else:
			#	inc = float(self._parameter_to_map_to.max - self._parameter_to_map_to.min) / 64
			#	if index_of_sender >= 4:
			#		inc = inc * (index_of_sender - 3)
			#		if self._parameter_to_map_to.value + inc <= self._parameter_to_map_to.max:
			#			self._parameter_to_map_to.value = self._parameter_to_map_to.value + inc
			#		else:
			#			self._parameter_to_map_to.value = self._parameter_to_map_to.max
			#	else:
			#		inc = inc * (4 - index_of_sender)
			#		if self._parameter_to_map_to.value - inc >= self._parameter_to_map_to.min:
			#			self._parameter_to_map_to.value = self._parameter_to_map_to.value - inc
			#		else:
			#			self._parameter_to_map_to.value = self._parameter_to_map_to.min
			self.notify_value(value)
			
	def _on_parameter_changed(self):
		assert (self._parameter_to_map_to != None)
		param_range = abs(self._parameter_to_map_to.max - self._parameter_to_map_to.min)
		param_value = self._parameter_to_map_to.value
		param_min = self._parameter_to_map_to.min
		param_mid = param_range / 2 + param_min
		midi_value = 0
		if self._mode == SLIDER_MODE_PAN:
			if param_value == param_mid:
				midi_value = 64
			else:
				diff = abs(param_value - param_mid) / param_range * 127
				if param_value > param_mid:
					midi_value = 64 + int(diff)
				else:
					midi_value = 63 - int(diff)
		else:
			midi_value = int(127 * abs(param_value - self._parameter_to_map_to.min) / param_range)
		self.send_value(midi_value)
