import Live
from _Framework.MixerComponent import MixerComponent
from DefChannelStripComponent import DefChannelStripComponent
from _Framework.ButtonElement import ButtonElement

class SpecialMixerComponent(MixerComponent):
	""" Class encompassing several defaultable channel strips to form a mixer """

	def __init__(self, num_tracks, num_returns = 0, with_eqs = False, with_filters = False):
		MixerComponent.__init__(self, num_tracks, num_returns, with_eqs, with_filters)
		self._unarm_all_button = None
		self._unsolo_all_button = None
		self._unmute_all_button = None

	def disconnect(self):
		if self._unarm_all_button != None:
			self._unarm_all_button.remove_value_listener(self._unarm_all_value)
			self._unarm_all_button = None
		if self._unsolo_all_button != None:
			self._unsolo_all_button.remove_value_listener(self._unsolo_all_value)
			self._unsolo_all_button = None
		if self._unmute_all_button != None:
			self._unmute_all_button.remove_value_listener(self._unmute_all_value)
			self._unmute_all_button = None
		MixerComponent.disconnect(self)

	def set_global_buttons(self, unarm_all, unsolo_all, unmute_all):
		assert isinstance(unarm_all, (ButtonElement, type(None)))
		assert isinstance(unsolo_all, (ButtonElement, type(None)))
		assert isinstance(unmute_all, (ButtonElement, type(None)))
		if (self._unarm_all_button != None):
			self._unarm_all_button.remove_value_listener(self._unarm_all_value)
		self._unarm_all_button = unarm_all
		if (self._unarm_all_button != None):
			self._unarm_all_button.add_value_listener(self._unarm_all_value)
			self._unarm_all_button.turn_off()
		if (self._unsolo_all_button != None):
			self._unsolo_all_button.remove_value_listener(self._unsolo_all_value)
		self._unsolo_all_button = unsolo_all
		if (self._unsolo_all_button != None):
			self._unsolo_all_button.add_value_listener(self._unsolo_all_value)
			self._unsolo_all_button.turn_off()
		if (self._unmute_all_button != None):
			self._unmute_all_button.remove_value_listener(self._unmute_all_value)
		self._unmute_all_button = unmute_all
		if (self._unmute_all_button != None):
			self._unmute_all_button.add_value_listener(self._unmute_all_value)
			self._unmute_all_button.turn_off()

	def _create_strip(self):
		return DefChannelStripComponent()

	def _unarm_all_value(self, value):
		assert self.is_enabled()
		assert (self._unarm_all_button != None)
		assert (value in range(128))
		if ((value != 0) or (not self._unarm_all_button.is_momentary())):
			for track in self.song().tracks:
				if track.can_be_armed and track.arm:
					track.arm = False

	def _unsolo_all_value(self, value):
		assert self.is_enabled()
		assert (self._unsolo_all_button != None)
		assert (value in range(128))
		if value != 0 or not self._unsolo_all_button.is_momentary():
			for track in tuple(self.song().tracks) + tuple(self.song().return_tracks):
				if track.solo:
					track.solo = False

	def _unmute_all_value(self, value):
		assert self.is_enabled()
		assert (self._unmute_all_button != None)
		assert (value in range(128))
		if value != 0 or not self._unmute_all_button.is_momentary():
			for track in tuple(self.song().tracks) + tuple(self.song().return_tracks):
				if track.mute:
					track.mute = False
