# emacs-mode: -*- python-*-
import Live
from consts import *
from _Framework.MixerComponent import MixerComponent
from DefChannelStripComponent import DefChannelStripComponent 
from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
import time

class TrackControlerComponent(MixerComponent):
	""" provide a one strip control on the current track  : arm,solo,mute
		navigate in tracks left/right
		navigate in scenes up and down
		fire/stop selected clip.
		enable/disable overdub
	"""

	def __init__(self,top_buttons,side_buttons):
		
		self._prev_track_button = None
		self._next_track_button=None
		self._prev_scene_button = None
		self._next_scene_button = None
		self._play_button = None
		self._stop_button = None
		self._overdub_button = None
		self._mute_button = None
		self._solo_button = None
		self._arm_button = None
		self._last_arm_button_press=int(round(time.time() * 1000))
		self._last_overdub_button_press=int(round(time.time() * 1000))
		self._auto_arm = True
		
		MixerComponent.__init__(self,1)
		self._selected_track = self.song().view.selected_track
		self._selected_scene = self.song().view.selected_scene
		
		self.set_prev_scene_button(top_buttons[0])
		self.set_next_scene_button(top_buttons[1])
		self.set_prev_track_button(top_buttons[2])
		self.set_next_track_button(top_buttons[3])

		self.set_play_button(side_buttons[3])
		self.set_stop_button(side_buttons[4])
		#self.set_mute_button(side_buttons[4])
		self.set_overdub_button(side_buttons[5])
		self.set_solo_button(side_buttons[6])
		self.set_arm_button(side_buttons[7])
	
	def _do_select_scene(self, scene):
		view = self.song().view
		if view.selected_scene != self._scene:
			view.selected_scene = self._scene	
		
	def disconnect(self):
		self.set_prev_scene_button(None)
		self.set_next_scene_button(None)
		self.set_prev_track_button(None)
		self.set_next_track_button(None)
		self.set_mute_button(None)
		self.set_play_button(None)
		self.set_stop_button(None)
		self.set_overdub_button(None)
		self.set_solo_button(None)
		self.set_arm_button(None)

		MixerComponent.disconnect(self)


	def set_prev_scene_button(self, prev_scene=None):
		assert isinstance(prev_scene, (ButtonElement,type(None)))
		if (self._prev_scene_button != None):
			self._prev_scene_button.remove_value_listener(self._prev_scene_value)
		self._prev_scene_button = prev_scene
		if (self._prev_scene_button != None):
			self._prev_scene_button.add_value_listener(self._prev_scene_value, identify_sender=True)
			self._prev_scene_button.turn_off()
			
	def set_next_scene_button(self, next_scene=None):
		assert isinstance(next_scene, (ButtonElement,type(None)))
		if (self._next_scene_button != None):
			self._next_scene_button.remove_value_listener(self._next_scene_value)
		self._next_scene_button = next_scene
		if (self._next_scene_button != None):
			self._next_scene_button.add_value_listener(self._next_scene_value, identify_sender=True)
			self._next_scene_button.turn_off()
			
	def set_overdub_button(self, overdub=None):
		assert isinstance(overdub, (ButtonElement,type(None)))	
		if (self._overdub_button != None):
			self._overdub_button.remove_value_listener(self._overdub_value)
		self._overdub_button = overdub
		if (self._overdub_button != None):
			self._overdub_button.add_value_listener(self._overdub_value)
			self._overdub_button.turn_off()
			
	def set_play_button(self, play=None):
		assert isinstance(play, (ButtonElement,type(None)))		
		if (self._play_button != None):
			self._play_button.remove_value_listener(self._play_value)
		self._play_button = play
		if (self._play_button != None):
			self._play_button.add_value_listener(self._play_value)
			self._play_button.turn_off()

	def set_stop_button(self, stop=None):
		assert isinstance(stop, (ButtonElement,type(None)))		
		if (self._stop_button != None):
			self._stop_button.remove_value_listener(self._stop_value)
		self._stop_button = stop
		if (self._stop_button != None):
			self._stop_button.add_value_listener(self._stop_value)
			self._stop_button.turn_off()

	def set_mute_button(self, mute=None):
		assert isinstance(mute, (ButtonElement,type(None)))
		if (self._mute_button != None):
			self._mute_button.remove_value_listener(self._mute_value)
		self._mute_button = mute
		if (self._mute_button != None):
			self._mute_button.add_value_listener(self._mute_value)
			self._mute_button.turn_off()

	def set_solo_button(self, solo=None):
		assert isinstance(solo, (ButtonElement,type(None)))		
		if (self._solo_button != None):
			self._solo_button.remove_value_listener(self._solo_value)
		self._solo_button = solo
		if (self._solo_button != None):
			self._solo_button.add_value_listener(self._solo_value)
			self._solo_button.turn_off()
			
	def set_arm_button(self, arm=None):
		assert isinstance(arm, (ButtonElement,type(None)))	
		if (self._arm_button != None):
			self._arm_button.remove_value_listener(self._arm_value)
		self._arm_button = arm
		if (self._arm_button != None):
			self._arm_button.add_value_listener(self._arm_value)
			self._arm_button.turn_off()
	
# TRACKS Buttons
	def update_track_buttons(self):
		#tracks
		if self.is_enabled():
			if(self._prev_track_button!=None):
				self._prev_track_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				if(self.selected_track_idx() >0):
					self._prev_track_button.turn_on()
				else:
					self._prev_track_button.turn_off()

			if(self._next_track_button!=None):
				self._next_track_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				if(self.selected_track_idx() < len(self.song().tracks)-1):
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
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value is not 0)):
				if(self.selected_track_idx() < len(self.song().tracks)-1):
					self.song().view.selected_track=self.song().tracks[self.selected_track_idx() + 1]
					self._do_auto_arm()
					self.update()
					
	def set_prev_track_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._prev_track_button != button):
			if (self._prev_track_button  != None):
				self._prev_track_button.remove_value_listener(self._prev_track_value)
			self._prev_track_button = button
			if (self._prev_track_button  != None):
				assert isinstance(button, ButtonElement)
				self._prev_track_button.add_value_listener(self._prev_track_value, identify_sender=True)

	def _prev_track_value(self, value, sender):
		assert (self._prev_track_button != None)
		assert (value in range(128))
		if ((not sender.is_momentary()) or (value is not 0)):
			if self.is_enabled():
				if(self.selected_track_idx() >0):
					self.song().view.selected_track=self.song().tracks[self.selected_track_idx() - 1]
					self._do_auto_arm()
					self.update()
					
	def update_scene_buttons(self):
		#tracks
		if self.is_enabled():
			self._scene = self.song().view.selected_scene
			if(self._prev_scene_button!=None):
				self._prev_scene_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				if(self.selected_scene_idx() >0):
					self._prev_scene_button.turn_on()
				else:
					self._prev_scene_button.turn_off()

			if(self._next_scene_button!=None):
				self._next_scene_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				if(self.selected_scene_idx() < len(self.song().scenes)-1):
					self._next_scene_button.turn_on()
				else:
					self._next_scene_button.turn_off()
	
	def _prev_scene_value(self, value, sender):
		assert (self._prev_scene_button != None)
		assert (value in range(128))
		if ((not sender.is_momentary()) or (value is not 0)):
			if self.is_enabled():
				if self.is_enabled():
					if(self.selected_scene_idx() >0):
						self.song().view.selected_scene=self.song().scenes[self.selected_scene_idx() - 1]
						self.update()

	def _next_scene_value(self, value, sender):
		assert (self._next_scene_button != None)
		assert (value in range(128))
		if ((not sender.is_momentary()) or (value is not 0)):
			if self.is_enabled():
				if ((not sender.is_momentary()) or (value is not 0)):
					if(self.selected_scene_idx() < len(self.song().scenes)-1):
						self.song().view.selected_scene=self.song().scenes[self.selected_scene_idx() + 1]
						self.update()

	def _overdub_value(self, value):
		assert (self._overdub_button != None)
		assert (value in range(128))
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if ((value != 0) or (not self._overdub_button.is_momentary())):
				self._last_overdub_button_press=now
			else:
				if now-self._last_overdub_button_press > 500:
					self.song().metronome = not self.song().metronome
				else:
					self.song().overdub = not self.song().overdub
					self.update()
				
				
	
	def _play_value(self, value):
		assert (self._play_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((value != 0) or (not self._play_button.is_momentary())):
				self._play_button.turn_on()
				if self.song().view.selected_scene!=None:
					slot = self.song().view.selected_scene.clip_slots[self.selected_track_idx()]
					slot.fire()
			else:
				self._play_button.turn_off()
	
	def _stop_value(self, value):
		assert (self._stop_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			if ((value != 0) or (not self._stop_button.is_momentary())):
				self._stop_button.turn_on()
				if self.song().view.selected_scene!=None:
					slot = self.song().view.selected_scene.clip_slots[self.selected_track_idx()]
					slot.stop()
			else:
				self._stop_button.turn_off()
					
	def _mute_value(self, value):
		assert (self._mute_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			if ((value != 0) or (not self._mute_button.is_momentary())):
				self._selected_track.mute = not self._selected_track.mute
				self.update()

	def _solo_value(self, value):
		assert (self._solo_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			if ((value != 0) or (not self._solo_button.is_momentary())):
				self._selected_track.solo = not self._selected_track.solo
				self.update()
	
	
	def _undo_value(self, value):
		if self.is_enabled():
			if value != 0 or not self._undo_button.is_momentary():
				if not self._shift_button.is_pressed():
					if self.song().can_undo:
						self.song().undo()
				elif self.song().can_redo:
					self.song().redo()
				self._update_undo_button()
				
	def _arm_value(self, value):
		assert (self._arm_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if ((value != 0) or (not self._arm_button.is_momentary())):
				self._last_arm_button_press=now
			else:
				if (self._selected_track.can_be_armed):
					if now-self._last_arm_button_press > 500:
						self._auto_arm = not self._auto_arm
						if self._auto_arm:
							self._do_auto_arm()
					else:
						self._selected_track.arm = not self._selected_track.arm
					self.update()
					


	def update(self):
		if self.is_enabled():
			self.update_track_buttons()
			self.update_scene_buttons()
			
			if self._overdub_button != None:
				self._overdub_button.set_on_off_values(RED_FULL,RED_THIRD)
				if(self.song().overdub):
					self._overdub_button.turn_on()
				else:
					self._overdub_button.turn_off()
			
			if self._play_button != None:
				self._play_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
				self._play_button.turn_off()
				
			if self._stop_button != None:
				self._stop_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
				self._stop_button.turn_off()
					
			if self._mute_button != None:
				self._mute_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
				if(self._selected_track.mute):
					self._mute_button.turn_off()
				else:
					self._mute_button.turn_on()

			if self._solo_button != None:
				self._solo_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
				if(self._selected_track.solo):
					self._solo_button.turn_on()
				else:
					self._solo_button.turn_off()

			if self._arm_button != None:
				if self._auto_arm:
					self._arm_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				else:
					self._arm_button.set_on_off_values(RED_FULL,RED_THIRD)
					
				if(self._selected_track.can_be_armed and self._selected_track.arm):
					self._arm_button.turn_on()
				else:
					self._arm_button.turn_off()

		MixerComponent.update(self)

	def _do_auto_arm(self):
		self._selected_track=self.song().view.selected_track
		if self._auto_arm and self._selected_track.has_midi_input and self._selected_track.can_be_armed:
			for track in self.song().tracks:
				if track.can_be_armed and track.has_midi_input:
					track.arm = False
				self._selected_track.arm = True

	def selected_track(self):
		return self.song().view.selected_track

	def selected_track_idx(self):
		return self.tuple_idx(self.song().tracks, self.song().view.selected_track)
	
	def selected_scene_idx(self):
		return self.tuple_idx(self.song().scenes, self.song().view.selected_scene)
	
	def on_selected_track_changed(self):
		self._selected_track = self.song().view.selected_track				
		self.update()

	def on_selected_scene_changed(self):
		self._selected_scene = self.song().view.selected_scene
		self.update()
			
	def tuple_idx(self,tuple, obj):
		for i in xrange(0,len(tuple)):
			if (tuple[i] == obj):
				return i
		return(False)
