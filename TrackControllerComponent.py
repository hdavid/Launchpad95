from .Log import log
from _Framework.MixerComponent import MixerComponent
from _Framework.ButtonElement import ButtonElement
import time


class TrackControllerComponent(MixerComponent):

	""" provide a one strip control on the current track  : arm,solo,mute
			navigate in tracks left/right
			navigate in scenes up and down
			fire/stop selected clip.
			enable/disable session_record
	"""

	def __init__(self, control_surface = None, implicit_arm = False, skin_name = "Session", enabled = False):
		self._prev_track_button = None
		self._next_track_button = None
		self._prev_scene_button = None
		self._next_scene_button = None
		self._start_stop_button = None
		self._lock_button = None
		self._locked_to_track = False
		self._session_record_button = None
		self._mute_button = None
		self._solo_button = None
		self._undo_button = None
		self._arm_button = None
		self._selected_track = None

		self._control_surface = control_surface
		self._implicit_arm = implicit_arm
		self._skin_name = skin_name
		MixerComponent.__init__(self, 1)
		self.set_enabled(enabled)

		now = int(round(time.time() * 1000))
		self._last_arm_button_press = now
		self._last_session_record_button_press = now
		self._last_undo_button_press = now
		self._last_solo_button_press = now
		self._last_start_stop_button_press = now
		self._long_press = 500
		

	def disconnect(self):
		self.set_prev_scene_button(None)
		self.set_next_scene_button(None)
		self.set_prev_track_button(None)
		self.set_next_track_button(None)
		self.set_mute_button(None)
		self.set_lock_button(None)
		self.set_start_stop_button(None)
		self.set_session_record_button(None)
		self.set_solo_button(None)
		self.set_arm_button(None)

		MixerComponent.disconnect(self)

	def set_enabled(self, enabled):
		if self.is_enabled and not enabled:
			# disable implicit arm while leaving.
			if self._implicit_arm:
				if self.selected_track.can_be_armed:
					self.selected_track.implicit_arm = False
		MixerComponent.set_enabled(self, enabled)

	#def _do_select_scene(self, scene):
	#	view = self.song().view
	#	if view.selected_scene != self.selected_scene:
	#		view.selected_scene = self._scene


	def set_prev_scene_button(self, prev_scene=None):
		assert isinstance(prev_scene, (ButtonElement, type(None)))
		if self._prev_scene_button != None:
			self._prev_scene_button.remove_value_listener(self._prev_scene_value)
		self._prev_scene_button = prev_scene
		if self._prev_scene_button != None:
			self._prev_scene_button.add_value_listener(self._prev_scene_value, identify_sender=True)
			self._prev_scene_button.turn_off()

	def set_next_scene_button(self, next_scene=None):
		assert isinstance(next_scene, (ButtonElement, type(None)))
		if self._next_scene_button != None:
			self._next_scene_button.remove_value_listener(self._next_scene_value)
		self._next_scene_button = next_scene
		if self._next_scene_button != None:
			self._next_scene_button.add_value_listener(self._next_scene_value, identify_sender=True)
			self._next_scene_button.turn_off()

	def set_session_record_button(self, session_record=None):
		assert isinstance(session_record, (ButtonElement, type(None)))
		if self._session_record_button != None:
			self._session_record_button.remove_value_listener(self._session_record_value)
		self._session_record_button = session_record
		if self._session_record_button != None:
			self._session_record_button.add_value_listener(self._session_record_value)
			self._session_record_button.turn_off()

	def set_lock_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if self._lock_button != None:
			self._lock_button.remove_value_listener(self._lock_value)
		self._lock_button = button
		if self._lock_button != None:
			self._lock_button.add_value_listener(self._lock_value)
			self._lock_button.turn_off()


	def set_start_stop_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if self._start_stop_button != None:
			self._start_stop_button.remove_value_listener(self._start_stop_value)
		self._start_stop_button = button
		if self._start_stop_button != None:
			self._start_stop_button.add_value_listener(self._start_stop_value)
			self._start_stop_button.turn_off()

	def set_mute_button(self, mute=None):
		assert isinstance(mute, (ButtonElement, type(None)))
		if self._mute_button != None:
			self._mute_button.remove_value_listener(self._mute_value)
		self._mute_button = mute
		if self._mute_button != None:
			self._mute_button.add_value_listener(self._mute_value)
			self._mute_button.turn_off()

	def set_solo_button(self, solo=None):
		assert isinstance(solo, (ButtonElement, type(None)))
		if self._solo_button != None:
			self._solo_button.remove_value_listener(self._solo_value)
		self._solo_button = solo
		if self._solo_button != None:
			self._solo_button.add_value_listener(self._solo_value)
			self._solo_button.turn_off()

	def set_arm_button(self, arm=None):
		assert isinstance(arm, (ButtonElement, type(None)))
		if self._arm_button != None:
			self._arm_button.remove_value_listener(self._arm_value)
		self._arm_button = arm
		if self._arm_button != None:
			self._arm_button.add_value_listener(self._arm_value)
			self._arm_button.turn_off()

	def set_undo_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if self._undo_button != None:
			self._undo_button.remove_value_listener(self._undo_value)
		self._undo_button = button
		if self._undo_button != None:
			self._undo_button.add_value_listener(self._undo_value)
			self._undo_button.turn_off()

# TRACKS Buttons
	def update_track_buttons(self):
		# tracks
		if self.is_enabled():
			if self._prev_track_button != None:
				self._prev_track_button.set_on_off_values("Mode."+self._skin_name)
				if self.selected_track_idx > 0:
					self._prev_track_button.turn_on()
				else:
					self._prev_track_button.turn_off()
			if self._next_track_button != None :
				self._next_track_button.set_on_off_values("Mode."+self._skin_name)
				if self.selected_track_idx < len(self.song().tracks) - 1:
					self._next_track_button.turn_on()
				else:
					self._next_track_button.turn_off()

	def set_next_track_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if self._next_track_button != None:
			self._next_track_button.remove_value_listener(self._next_track_value)
		self._next_track_button = button
		if self._next_track_button != None:
			self._next_track_button.add_value_listener(self._next_track_value, identify_sender=True)
			self._next_track_button.turn_off()
			
	def _next_track_value(self, value, sender):
		assert (self._next_track_button != None)
		assert (value in range(128))
		if self.is_enabled() and not self._locked_to_track:
			if not sender.is_momentary() or value is not 0:
				if self.selected_track_idx < len(self.song().tracks) - 1:
					self.song().view.selected_track = self.song().tracks[self.selected_track_idx + 1]
					self._do_implicit_arm()

#PREV TRACK
	def set_prev_track_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if self._prev_track_button != None:
			self._prev_track_button.remove_value_listener(self._prev_track_value)
		self._prev_track_button = button
		if self._prev_track_button != None:
			self._prev_track_button.add_value_listener(self._prev_track_value, identify_sender=True)
			self._prev_track_button.turn_off()
	
	def _prev_track_value(self, value, sender):
		assert (self._prev_track_button != None)
		assert (value in range(128))
		if self.is_enabled() and not self._locked_to_track:
			if not sender.is_momentary() or value is not 0:
				if self.selected_track_idx > 0:
					self.song().view.selected_track = self.song().tracks[self.selected_track_idx - 1]
					self._do_implicit_arm()

# SCENE BUTTONS
	def update_scene_buttons(self):
		# scenes
		if self.is_enabled():
			if self._prev_scene_button != None:
				self._prev_scene_button.set_on_off_values("Mode."+self._skin_name)
				if self.selected_scene_idx > 0:
					self._prev_scene_button.turn_on()
				else:
					self._prev_scene_button.turn_off()

			if self._next_scene_button != None:
				self._next_scene_button.set_on_off_values("Mode."+self._skin_name)
				if self.selected_scene_idx < len(self.song().scenes) - 1:
					self._next_scene_button.turn_on()
				else:
					self._next_scene_button.turn_off()

	def _prev_scene_value(self, value, sender):
		assert (self._prev_scene_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if not sender.is_momentary() or value is not 0:
				if self.selected_scene_idx > 0:
					self.song().view.selected_scene = self.song().scenes[self.selected_scene_idx - 1]
				
	def _next_scene_value(self, value, sender):
		assert (self._next_scene_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if not sender.is_momentary() or value is not 0:
				if self.selected_scene_idx < len(self.song().scenes) - 1:
					self.song().view.selected_scene = self.song().scenes[self.selected_scene_idx + 1]			


# PREV SCENE			
	def _session_record_value(self, value):
		assert (self._session_record_button != None)
		assert (value in range(128))
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if value != 0 or not self._session_record_button.is_momentary():
				self._last_session_record_button_press = now
			else:
				if now - self._last_session_record_button_press > self._long_press * 4:
					self._implicit_arm = not self._implicit_arm
					self._do_implicit_arm()
					if self._implicit_arm:
						self._control_surface.show_message("implicit arm : on")
					else:
						self._control_surface.show_message("implicit arm : off")
					self.update()
				elif now - self._last_session_record_button_press > self._long_press:
					self.song().metronome = not self.song().metronome
					if self.song().metronome :
						self._control_surface.show_message("metronome : on")
					else:
						self._control_surface.show_message("metronome : off")
				else:
					if self._implicit_arm:
						self.song().session_record = not self.song().session_record
						if self.song().session_record :
							self._control_surface.show_message("session record : on")
						else:
							self._control_surface.show_message("session record : off")
					else:
						if self.selected_track.can_be_armed:
							self.selected_track.arm = not self.selected_track.arm
							if self.selected_track.arm :
								self._control_surface.show_message("track "+str(self.selected_track.name)+" armed")
							else:
								self._control_surface.show_message("track "+str(self.selected_track.name)+" unarmed")
					self.update()

	def _lock_value(self, value):
		assert (self._lock_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if value is not 0:
				self._locked_to_track = not self._locked_to_track
				if self._locked_to_track:
					self._lock_button.turn_on()
					self._control_surface.show_message("locked to track")
				else:
					self._lock_button.turn_off()
					self._control_surface.show_message("unlocked from track")
				self.update()


	def update_lock_button(self):
		if self.is_enabled():
			if not self._locked_to_track or self._selected_track == None:
				self._selected_track = self.song().view.selected_track
				self._do_implicit_arm()
			if self._lock_button != None:
				self._lock_button.set_on_off_values("TrackController.Lock.On", "TrackController.Lock.Off")
				if self._locked_to_track:
					self._lock_button.turn_on()
				else:
					self._lock_button.turn_off()


	def _start_stop_value(self, value):
		assert (self._start_stop_button != None)
		assert (value in range(128))
		assert(self.selected_track != None)
		now = int(round(time.time() * 1000))
		if self.is_enabled():
			if value != 0 or not self._start_stop_button.is_momentary():
				self._last_start_stop_button_press = now
			else:
				if now - self._last_start_stop_button_press > self._long_press:
					if self.selected_scene != None:
						slot = self.selected_scene.clip_slots[self.selected_track_idx]
						if slot and slot.has_clip:
							slot.delete_clip()
							self._start_stop_button.turn_off()
							self._control_surface.show_message("delete clip")

				else:
					if self.selected_scene != None:
						slot = self.selected_scene.clip_slots[self.selected_track_idx]
						if slot and slot.has_clip:
							if slot.is_triggered or slot.is_playing:
								slot.stop()
								self._start_stop_button.turn_off()
								self._control_surface.show_message("stop clip")
							else:
								slot.fire()
								self._start_stop_button.turn_on()
								self._control_surface.show_message("fire clip")

	def _mute_value(self, value):
		assert (self._mute_button != None)
		assert (value in range(128))
		assert(self.selected_track != None)
		if self.is_enabled():
			if value != 0 or not self._mute_button.is_momentary():
				self.selected_track.mute = not self.selected_track.mute
				if self.selected_track.mute :
					self._control_surface.show_message("track "+str(self.selected_track.name)+" muted")
				else:
					self._control_surface.show_message("track "+str(self.selected_track.name)+" unmuted")
			self.update()

	def _solo_value(self, value):
		assert (self._solo_button != None)
		assert (value in range(128))
		assert(self.selected_track != None)
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if value != 0 or not self._session_record_button.is_momentary():
				self._last_solo_button_press = now
				self._solo_button.turn_on()
			else:
				self._solo_button.turn_off()
				if now - self._last_solo_button_press > self._long_press:
					self.selected_track.mute = not self.selected_track.mute
					if self.selected_track.mute:
						self._control_surface.show_message("track "+str(self.selected_track.name)+" mute")
					else:
						self._control_surface.show_message("track "+str(self.selected_track.name)+" unmute")
				else:
					self.selected_track.solo = not self.selected_track.solo
					if self.selected_track.solo:
						self._control_surface.show_message("track "+str(self.selected_track.name)+" solo")
					else:
						self._control_surface.show_message("track "+str(self.selected_track.name)+" unsolo")
			self.update()

	def _undo_value(self, value):
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if value != 0 or not self._session_record_button.is_momentary():
				self._last_undo_button_press = now
			else:
				if now - self._last_undo_button_press < self._long_press:
					if self.song().can_undo:
						self.song().undo()
						self._control_surface.show_message("undo!")
				else:
					if self.song().can_redo:
						self.song().redo()
						self._control_surface.show_message("redo!")
			self.update()

	def _arm_value(self, value):
		assert (self._arm_button != None)
		assert (value in range(128))
		assert(self.selected_track != None)
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if value != 0 or not self._arm_button.is_momentary():
				self._last_arm_button_press = now
			else:
				if now - self._last_arm_button_press > self._long_press:
					self._implicit_arm = not self._implicit_arm
					if self._implicit_arm:
						self._control_surface.show_message("implicit arm : on")
					else:
						self._control_surface.show_message("implicit arm : off")
					self._do_implicit_arm()
				else:
					if self.selected_track.can_be_armed:
						self.selected_track.arm = not self.selected_track.arm
						if self.selected_track.arm :
							self._control_surface.show_message("track "+str(self.selected_track.name)+" armed")
						else:
							self._control_surface.show_message("track "+str(self.selected_track.name)+" unarmed")
			self.update()

	def update(self):
		if self.is_enabled():
			self.update_track_buttons()
			self.update_scene_buttons()
			self.update_lock_button()

			if self._session_record_button != None:
				if self._implicit_arm:
					self._session_record_button.set_on_off_values("TrackController.ImplicitRecording")
				else:
					self._session_record_button.set_on_off_values("TrackController.Recording")
				if(self.song().session_record):
					self._session_record_button.turn_on()
				else:
					self._session_record_button.turn_off()
				
			if self._start_stop_button != None:
				self._start_stop_button.set_on_off_values("TrackController.Stop.On", "TrackController.Stop.Off")
				self._start_stop_button.turn_off()
		
			if self._mute_button != None:
				self._mute_button.set_on_off_values("TrackController.Mute")
				if(self.selected_track.mute):
					self._mute_button.turn_off()
				else:
					self._mute_button.turn_on()

			if self._undo_button != None:
				self._undo_button.set_on_off_values("TrackController.Undo")
				if self.song().can_undo:
					self._undo_button.turn_on()
				else:
					self._undo_button.turn_off()

			if self._solo_button != None:
				self._solo_button.set_on_off_values("TrackController.Solo")
				if self.selected_track.solo:
					self._solo_button.turn_on()
				else:
					self._solo_button.turn_off()

			if self._arm_button != None:
				if self._implicit_arm:
					self._arm_button.set_on_off_values("TrackController.ImplicitRecording")
				else:
					self._arm_button.set_on_off_values("TrackController.Recording")

				if(self.selected_track.can_be_armed and self.selected_track.arm):
					self._arm_button.turn_on()
				else:
					self._arm_button.turn_off()

		MixerComponent.update(self)

	def can_implicit_arm_track(self, track):
		return track.can_be_armed and track.has_midi_input

	def _do_implicit_arm(self, arm = True):
		if self.is_enabled() and not self._locked_to_track:
			if self._implicit_arm:
				self._control_surface.set_controlled_track(self.selected_track)
			else:
				self._control_surface.release_controlled_track()
			for track in self.song().tracks:
				if self.can_implicit_arm_track(track):
					track.implicit_arm = self._implicit_arm and arm and self.selected_track == track

		
	def on_selected_track_changed(self):
		if self.is_enabled():
			self._do_implicit_arm()
			self.update()

	def on_selected_scene_changed(self):
		self.update()
	
	@property
	def selected_track(self):
		return self.song().view.selected_track

	@property
	def selected_track_idx(self):
		return list(self.song().tracks).index(self.song().view.selected_track) if self.song().view.selected_track in list(self.song().tracks) else None  

	@property
	def selected_scene_idx(self):
		return list(self.song().scenes).index(self.song().view.selected_scene)
		
	@property
	def selected_scene(self):
		return self.song().view.selected_scene

	@property
	def selected_clip(self):
		clip_slot = self.selected_scene.clip_slots[self.selected_track_idx]
		if clip_slot.has_clip:
			return clip_slot.clip
		else:
			return None

