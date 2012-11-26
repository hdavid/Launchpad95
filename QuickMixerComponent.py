# emacs-mode: -*- python-*-
import Live
from consts import *
from _Framework.MixerComponent import MixerComponent
from DefChannelStripComponent import DefChannelStripComponent 
from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

class QuickMixerComponent(MixerComponent):
	__module__ = __name__
	__doc__ = ' provide a one strip control on the current track (arm,solo,mute)+left/right nav '

	def __init__(self,top_buttons,side_buttons,parent):
		self._clip_up_button = None
		self._clip_down_button = None
		self._overdub_button = None
		self._play_button = None
		self._stop_button = None
		self._mute_button = None
		self._solo_button = None
		self._arm_button = None
		self._selected_track = self.song().view.selected_track
		self._parent=parent
		MixerComponent.__init__(self,8)
		self._set_buttons(side_buttons[0],side_buttons[1],side_buttons[2],side_buttons[3],side_buttons[4],side_buttons[5],side_buttons[6],side_buttons[7])
		
		


	def disconnect(self):
	
		if (self._clip_up_button != None):
			self._clip_up_button.remove_value_listener(self._clip_up_value)
			self._clip_up_button = None
			
		if (self._clip_down_button != None):
			self._clip_down_button.remove_value_listener(self._clip_down_button_value)
			self._clip_down_button = None
			
		if (self._overdub_button != None):
			self._overdub_button.remove_value_listener(self._overdub_button)
			self._overdub_button = None
		
		if (self._play_button != None):
			self._play_button.remove_value_listener(self._play_button_value)
			self._play_button = None
		
		if (self._stop_button != None):
			self._stop_button.remove_value_listener(self._stop_button_value)
			self._stop_button = None
						
		if (self._solo_button != None):
			self._solo_button.remove_value_listener(self._solo_value)
			self._solo_button = None

		if (self._mute_button != None):
			self._mute_button.remove_value_listener(self._mute_value)
			self._mute_button = None
			
		if (self._arm_button != None):
			self._arm_button.remove_value_listener(self._arm_value)
			self._arm_button = None


		MixerComponent.disconnect(self)



	def _set_buttons(self,clip_up=None, clip_down=None, overdub=None, play = None, stop = None, mute=None, solo=None,arm=None):
		assert isinstance(clip_up, (ButtonElement,type(None)))
		assert isinstance(clip_down, (ButtonElement,type(None)))
		assert isinstance(overdub, (ButtonElement,type(None)))
		assert isinstance(play, (ButtonElement,type(None)))
		assert isinstance(stop, (ButtonElement,type(None)))
		assert isinstance(mute, (ButtonElement,type(None)))
		assert isinstance(solo, (ButtonElement,type(None)))
		assert isinstance(arm, (ButtonElement,type(None)))
		

		if (self._clip_up_button != None):
			self._clip_up_button.remove_value_listener(self._clip_up_value)
		self._clip_up_button = clip_up
		if (self._clip_up_button != None):
			self._clip_up_button.add_value_listener(self._clip_up_value)
			self._clip_up_button.turn_off()
		
		if (self._clip_down_button != None):
			self._clip_down_button.remove_value_listener(self._clip_down_value)
		self._clip_down_button = clip_down
		if (self._clip_down_button != None):
			self._clip_down_button.add_value_listener(self._clip_down_value)
			self._clip_down_button.turn_off()
			
		if (self._overdub_button != None):
			self._overdub_button.remove_value_listener(self._overdub_value)
		self._overdub_button = overdub
		if (self._overdub_button != None):
			self._overdub_button.add_value_listener(self._overdub_value)
			self._overdub_button.turn_off()
			
		if (self._play_button != None):
			self._play_button.remove_value_listener(self._play_value)
		self._play_button = play
		if (self._play_button != None):
			self._play_button.add_value_listener(self._play_value)
			self._play_button.turn_off()
			
		if (self._stop_button != None):
			self._mute_button.remove_value_listener(self._stop_value)
		self._stop_button = stop
		if (self._stop_button != None):
			self._stop_button.add_value_listener(self._stop_value)
			self._stop_button.turn_off()

		if (self._mute_button != None):
			self._mute_button.remove_value_listener(self._mute_value)
		self._mute_button = mute
		if (self._mute_button != None):
			self._mute_button.add_value_listener(self._mute_value)
			self._mute_button.turn_off()
			
		if (self._solo_button != None):
			self._solo_button.remove_value_listener(self._solo_value)
		self._solo_button = solo
		if (self._solo_button != None):
			self._solo_button.add_value_listener(self._solo_value)
			self._solo_button.turn_off()
		
		if (self._arm_button != None):
			self._arm_button.remove_value_listener(self._arm_value)
		self._arm_button = arm
		if (self._arm_button != None):
			self._arm_button.add_value_listener(self._arm_value)
			self._arm_button.turn_off()
	

	def _clip_up_value(self, value):
		assert (self._clip_up_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((value != 0) or (not self._clip_up_button.is_momentary())):
				track = self._selected_track
				if track.mute:
					track.mute = not track.mute


	def _clip_down_value(self, value):
		assert (self._clip_down_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((value != 0) or (not self._clip_down_button.is_momentary())):
				track = self._selected_track
				if track.mute:
					track.mute = not track.mute


	def _overdub_value(self, value):
		assert (self._overdub_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((value != 0) or (not self._overdub_button.is_momentary())):
				self.song().overdub= not self.song().overdub
	
	def _play_value(self, value):
		assert (self._play_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((value != 0) or (not self._play_button.is_momentary())):
				track = self._selected_track
				if track.mute:
					track.mute = not track.mute
	
	
	def _stop_value(self, value):
		assert (self._stop_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			if ((value != 0) or (not self._stop_button.is_momentary())):
				track = self._selected_track
				if track.mute:
					track.mute = not track.mute

	def _mute_value(self, value):
		assert (self._mute_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			if ((value != 0) or (not self._mute_button.is_momentary())):
				track = self._selected_track
				if track.mute:
					track.mute = not track.mute

	def _solo_value(self, value):
		assert (self._solo_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			if ((value != 0) or (not self._solo_button.is_momentary())):
				track = self._selected_track
				if track.solo:
					track.solo = not track.solo

	def _arm_value(self, value):
		assert (self._arm_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			if ((value != 0) or (not self._arm_button.is_momentary())):
				track = self._selected_track
				if (track.can_be_armed):
					track.arm = not track.arm



	def update(self):
		if self.is_enabled():
			if self._clip_up_button != None:
				self._clip_up_button.set_on_off_values(GREEN_FULL,LED_OFF)
				if(True):
					self._clip_up_button.turn_off()
				else:
					self._clip_up_button.turn_on()
			
			if self._clip_down_button != None:
				self._clip_down_button.set_on_off_values(GREEN_FULL,LED_OFF)
				if(True):
					self._clip_down_button.turn_off()
				else:
					self._clip_down_button.turn_on()
			
			if self._overdub_button != None:
				self._overdub_button.set_on_off_values(RED_FULL,RED_THIRD)
				if(self.song().overdub):
					self._overdub_button.turn_off()
				else:
					self._overdub_button.turn_on()
			
			if self._play_button != None:
				self._play_button.set_on_off_values(RED_FULL,RED_THIRD)
				if(False):
					self._play_button.turn_off()
				else:
					self._play_button.turn_on()
				
			if self._stop_button != None:
				self._stop_button.set_on_off_values(RED_FULL,RED_THIRD)
				if(False):
					self._stop_button.turn_off()
				else:
					self._stop_button.turn_on()
					
			if self._mute_button != None:
				self._mute_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
				if(self._selected_track.arm):
					self._mute_button.turn_off()
				else:
					self._mute_button.turn_on()

			if self._solo_button != None:
				self._solo_button.set_on_off_values(RED_FULL,RED_THIRD)
				if(self._selected_track.solo):
					self._solo_button.turn_on()
				else:
					self._solo_button.turn_off()

			if self._arm_button != None:
				self._arm_button.set_on_off_values(RED_FULL,RED_THIRD)
				if(self._selected_track.mute):
					self._arm_button.turn_on()
				else:
					self._arm_button.turn_off()

		MixerComponent.update(self)

	def on_selected_track_changed(self):
		self._selected_track = self.song().view.selected_track
		self.update()


# local variables:
# tab-width: 4
