from consts import *  # noqa
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

	def __init__(self):

		self._prev_track_button = None
		self._next_track_button = None
		self._prev_scene_button = None
		self._next_scene_button = None
		self._play_button = None
		self._stop_button = None
		self._session_record_button = None
		self._mute_button = None
		self._solo_button = None
		self._undo_button = None
		self._arm_button = None
		self._parent = None
		self._implicit_arm = True
		self._notify_parent = True
		MixerComponent.__init__(self, 1)
		self.set_enabled(False)

		now = int(round(time.time() * 1000))
		self._last_arm_button_press = now
		self._last_session_record_button_press = now
		self._last_undo_button_press = now
		self._last_solo_button_press = now
		self._last_stop_button_press = now
		self._long_press = 500

		self._selected_track = self.song().view.selected_track
		self._selected_scene = self.song().view.selected_scene

	def disconnect(self):
		self.set_prev_scene_button(None)
		self.set_next_scene_button(None)
		self.set_prev_track_button(None)
		self.set_next_track_button(None)
		self.set_mute_button(None)
		self.set_play_button(None)
		self.set_stop_button(None)
		self.set_session_record_button(None)
		self.set_solo_button(None)
		self.set_arm_button(None)

		MixerComponent.disconnect(self)

	def set_enabled(self, enabled):
		if self.is_enabled and not enabled:
			# disable implicit arm while leaving.
			if(self._parent != None and self._notify_parent):
				if (self._selected_track.can_be_armed):
					self._selected_track.implicit_arm = False
		MixerComponent.set_enabled(self, enabled)

	def _do_select_scene(self, scene):
		view = self.song().view
		if view.selected_scene != self._scene:
			view.selected_scene = self._scene

	def set_parent(self, parent):
		self._parent = parent

	def set_prev_scene_button(self, prev_scene=None):
		assert isinstance(prev_scene, (ButtonElement, type(None)))
		if (self._prev_scene_button != None):
			self._prev_scene_button.remove_value_listener(self._prev_scene_value)
		self._prev_scene_button = prev_scene
		if (self._prev_scene_button != None):
			self._prev_scene_button.add_value_listener(self._prev_scene_value, identify_sender=True)
			self._prev_scene_button.turn_off()

	def set_next_scene_button(self, next_scene=None):
		assert isinstance(next_scene, (ButtonElement, type(None)))
		if (self._next_scene_button != None):
			self._next_scene_button.remove_value_listener(self._next_scene_value)
		self._next_scene_button = next_scene
		if (self._next_scene_button != None):
			self._next_scene_button.add_value_listener(self._next_scene_value, identify_sender=True)
			self._next_scene_button.turn_off()

	def set_session_record_button(self, session_record=None):
		assert isinstance(session_record, (ButtonElement, type(None)))
		if (self._session_record_button != None):
			self._session_record_button.remove_value_listener(self._session_record_value)
		self._session_record_button = session_record
		if (self._session_record_button != None):
			self._session_record_button.add_value_listener(self._session_record_value)
			self._session_record_button.turn_off()

	def set_play_button(self, play=None):
		assert isinstance(play, (ButtonElement, type(None)))
		if (self._play_button != None):
			self._play_button.remove_value_listener(self._play_value)
		self._play_button = play
		if (self._play_button != None):
			self._play_button.add_value_listener(self._play_value)
			self._play_button.turn_off()

	def set_stop_button(self, stop=None):
		assert isinstance(stop, (ButtonElement, type(None)))
		if (self._stop_button != None):
			self._stop_button.remove_value_listener(self._stop_value)
		self._stop_button = stop
		if (self._stop_button != None):
			self._stop_button.add_value_listener(self._stop_value)
			self._stop_button.turn_off()

	def set_mute_button(self, mute=None):
		assert isinstance(mute, (ButtonElement, type(None)))
		if (self._mute_button != None):
			self._mute_button.remove_value_listener(self._mute_value)
		self._mute_button = mute
		if (self._mute_button != None):
			self._mute_button.add_value_listener(self._mute_value)
			self._mute_button.turn_off()

	def set_solo_button(self, solo=None):
		assert isinstance(solo, (ButtonElement, type(None)))
		if (self._solo_button != None):
			self._solo_button.remove_value_listener(self._solo_value)
		self._solo_button = solo
		if (self._solo_button != None):
			self._solo_button.add_value_listener(self._solo_value)
			self._solo_button.turn_off()

	def set_arm_button(self, arm=None):
		assert isinstance(arm, (ButtonElement, type(None)))
		if (self._arm_button != None):
			self._arm_button.remove_value_listener(self._arm_value)
		self._arm_button = arm
		if (self._arm_button != None):
			self._arm_button.add_value_listener(self._arm_value)
			self._arm_button.turn_off()

	def set_undo_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if (self._undo_button != None):
			self._undo_button.remove_value_listener(self._undo_value)
		self._undo_button = button
		if (self._undo_button != None):
			self._undo_button.add_value_listener(self._undo_value)
			self._undo_button.turn_off()

# TRACKS Buttons
	def update_track_buttons(self):
		# tracks
		if self.is_enabled():
			if(self._prev_track_button != None):
				if(self.selected_track_idx() > 0):
					self._prev_track_button.set_on_off_values(GREEN_FULL, GREEN_FULL)
					self._prev_track_button.turn_on()
				else:
					self._prev_track_button.set_on_off_values(GREEN_THIRD, GREEN_THIRD)
					self._prev_track_button.turn_off()
			if(self._next_track_button != None):
				if(self.selected_track_idx() < len(self.song().tracks) - 1):
					self._next_track_button.set_on_off_values(GREEN_FULL, GREEN_FULL)
					self._next_track_button.turn_on()
				else:
					self._next_track_button.set_on_off_values(GREEN_THIRD, GREEN_THIRD)
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
				if(self.selected_track_idx() < len(self.song().tracks) - 1):
					self.song().view.selected_track = self.song().tracks[self.selected_track_idx() + 1]
					self._do_implicit_arm()
					# self.update()

	def set_prev_track_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._prev_track_button != button):
			if (self._prev_track_button != None):
				self._prev_track_button.remove_value_listener(self._prev_track_value)
			self._prev_track_button = button
			if (self._prev_track_button != None):
				assert isinstance(button, ButtonElement)
				self._prev_track_button.add_value_listener(self._prev_track_value, identify_sender=True)

	def _prev_track_value(self, value, sender):
		assert (self._prev_track_button != None)
		assert (value in range(128))
		if ((not sender.is_momentary()) or (value is not 0)):
			if self.is_enabled():
				if(self.selected_track_idx() > 0):
					self.song().view.selected_track = self.song().tracks[self.selected_track_idx() - 1]
					self._do_implicit_arm()
					# self.update()

	def update_scene_buttons(self):
		# tracks
		if self.is_enabled():
			self._scene = self.song().view.selected_scene
			if(self._prev_scene_button != None):
				self._prev_scene_button.set_on_off_values(GREEN_FULL, GREEN_THIRD)
				if(self.selected_scene_idx() > 0):
					self._prev_scene_button.turn_on()
				else:
					self._prev_scene_button.turn_off()

			if(self._next_scene_button != None):
				self._next_scene_button.set_on_off_values(GREEN_FULL, GREEN_THIRD)
				if(self.selected_scene_idx() < len(self.song().scenes) - 1):
					self._next_scene_button.turn_on()
				else:
					self._next_scene_button.turn_off()

	def _prev_scene_value(self, value, sender):
		assert (self._prev_scene_button != None)
		assert (value in range(128))
		if ((not sender.is_momentary()) or (value is not 0)):
			if self.is_enabled():
				if self.is_enabled():
					if(self.selected_scene_idx() > 0):
						self.song().view.selected_scene = self.song().scenes[self.selected_scene_idx() - 1]
						# self.update()

	def _next_scene_value(self, value, sender):
		assert (self._next_scene_button != None)
		assert (value in range(128))
		if ((not sender.is_momentary()) or (value is not 0)):
			if self.is_enabled():
				if ((not sender.is_momentary()) or (value is not 0)):
					if(self.selected_scene_idx() < len(self.song().scenes) - 1):
						self.song().view.selected_scene = self.song().scenes[self.selected_scene_idx() + 1]
						# self.update()

	def _session_record_value(self, value):
		assert (self._session_record_button != None)
		assert (value in range(128))
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if ((value != 0) or (not self._session_record_button.is_momentary())):
				self._last_session_record_button_press = now
			else:
				if now - self._last_session_record_button_press > self._long_press * 4:
					self._implicit_arm = not self._implicit_arm
					self._do_implicit_arm()
					if self._implicit_arm:
						self._parent.show_message("implicit arm : on")
					else:
						self._parent.show_message("implicit arm : off")
					self.update()
				elif now - self._last_session_record_button_press > self._long_press:
					self.song().metronome = not self.song().metronome
					if self.song().metronome :
						self._parent.show_message("metronome : on")
					else:
						self._parent.show_message("metronome : off")
				else:
					if self._implicit_arm:
						self.song().session_record = not self.song().session_record
						if self.song().session_record :
							self._parent.show_message("session record : on")
						else:
							self._parent.show_message("session record : off")
					else:
						if (self._selected_track.can_be_armed):
							self._selected_track.arm = not self._selected_track.arm
							if self._selected_track.arm :
								self._parent.show_message("track "+str(self._selected_track.name)+" armed")
							else:
								self._parent.show_message("track "+str(self._selected_track.name)+" unarmed")
					self.update()

	def _play_value(self, value):
		assert (self._play_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((value != 0) or (not self._play_button.is_momentary())):
				self._play_button.turn_on()
				if self.song().view.selected_scene != None:
					slot = self.song().view.selected_scene.clip_slots[self.selected_track_idx()]
					slot.fire()
					self._parent.show_message("fire clip")
			else:
				self._play_button.turn_off()

	def _stop_value(self, value):
		assert (self._stop_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		now = int(round(time.time() * 1000))
		if self.is_enabled():
			if ((value != 0) or (not self._stop_button.is_momentary())):
				self._last_stop_button_press = now
				self._stop_button.turn_on()
			else:
				if now - self._last_stop_button_press > self._long_press:
					if self.song().view.selected_scene != None:
						slot = self.song().view.selected_scene.clip_slots[self.selected_track_idx()]
						if slot and slot.has_clip:
							slot.delete_clip()
							self._parent.show_message("delete clip")
				else:

					if self.song().view.selected_scene != None:
						slot = self.song().view.selected_scene.clip_slots[self.selected_track_idx()]
						slot.stop()
						self._parent.show_message("stop clip")
				self._stop_button.turn_off()

	def _mute_value(self, value):
		assert (self._mute_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			if ((value != 0) or (not self._mute_button.is_momentary())):
				self._selected_track.mute = not self._selected_track.mute
				if self._selected_track.mute :
					self._parent.show_message("track "+str(self._selected_track.name)+" muted")
				else:
					self._parent.show_message("track "+str(self._selected_track.name)+" unmuted")
				self.update()

	def _solo_value(self, value):
		assert (self._solo_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if ((value != 0) or (not self._session_record_button.is_momentary())):
				self._last_solo_button_press = now
				self._solo_button.turn_on()
			else:
				self._solo_button.turn_off()
				if now - self._last_solo_button_press > self._long_press:
					self._selected_track.mute = not self._selected_track.mute
				else:
					self._selected_track.solo = not self._selected_track.solo
					if self._selected_track.solo :
						self._parent.show_message("track "+str(self._selected_track.name)+" solo")
					else:
						self._parent.show_message("track "+str(self._selected_track.name)+" unsolo")
					self.update()

	def _undo_value(self, value):
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if ((value != 0) or (not self._session_record_button.is_momentary())):
				self._last_undo_button_press = now
			else:
				if now - self._last_undo_button_press < self._long_press:
					if self.song().can_undo:
						self.song().undo()
						self._parent.show_message("undo!")
				else:
					if self.song().can_redo:
						self.song().redo()
						self._parent.show_message("redo!")
			self.update()

	def _arm_value(self, value):
		assert (self._arm_button != None)
		assert (value in range(128))
		assert(self._selected_track != None)
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if ((value != 0) or (not self._arm_button.is_momentary())):
				self._last_arm_button_press = now
			else:
				if now - self._last_arm_button_press > self._long_press:
					self._implicit_arm = not self._implicit_arm
					if self._implicit_arm:
						self._parent.show_message("implicit arm : on")
					else:
						self._parent.show_message("implicit arm : off")
					self._do_implicit_arm()
				else:
					if self._selected_track.can_be_armed:
						self._selected_track.arm = not self._selected_track.arm
						if self._selected_track.arm :
							self._parent.show_message("track "+str(self._selected_track.name)+" armed")
						else:
							self._parent.show_message("track "+str(self._selected_track.name)+" unarmed")
				self.update()

	def update(self):
		if self.is_enabled():
			self.update_track_buttons()
			self.update_scene_buttons()

			if self._session_record_button != None:
				if self._implicit_arm:
					self._session_record_button.set_on_off_values(RED_FULL, RED_THIRD)
				else:
					self._session_record_button.set_on_off_values(AMBER_FULL, AMBER_THIRD)
				if(self.song().session_record):
					self._session_record_button.turn_on()
				else:
					self._session_record_button.turn_off()

			if self._play_button != None:
				self._play_button.set_on_off_values(RED_FULL, RED_THIRD)
				self._play_button.turn_off()

			if self._stop_button != None:
				self._stop_button.set_on_off_values(RED_FULL, RED_THIRD)
				self._stop_button.turn_off()

			if self._mute_button != None:
				self._mute_button.set_on_off_values(AMBER_FULL, AMBER_THIRD)
				if(self._selected_track.mute):
					self._mute_button.turn_off()
				else:
					self._mute_button.turn_on()

			if self._undo_button != None:
				self._undo_button.set_on_off_values(AMBER_FULL, AMBER_THIRD)
				if(self.song().can_undo):
					self._undo_button.turn_on()
				else:
					self._undo_button.turn_off()

			if self._solo_button != None:
				self._solo_button.set_on_off_values(AMBER_FULL, AMBER_THIRD)
				if(self._selected_track.solo):
					self._solo_button.turn_on()
				else:
					self._solo_button.turn_off()

			if self._arm_button != None:
				if self._implicit_arm:
					self._arm_button.set_on_off_values(GREEN_FULL, GREEN_THIRD)
				else:
					self._arm_button.set_on_off_values(RED_FULL, RED_THIRD)

				if(self._selected_track.can_be_armed and self._selected_track.arm):
					self._arm_button.turn_on()
				else:
					self._arm_button.turn_off()

		MixerComponent.update(self)

	def can_implicit_arm_track(self, track):
		return track.can_be_armed and track.has_midi_input

	def _do_implicit_arm(self, arm=True):
		self._selected_track = self.selected_track()
		if(self._parent != None and self._notify_parent and self._is_enabled):
			if self._implicit_arm:
				self._parent.set_controlled_track(self._selected_track)
			else:
				self._parent.release_controlled_track()

			for track in self.song().tracks:
				if self.can_implicit_arm_track(track):
					track.implicit_arm = arm and self._implicit_arm and self._selected_track == track

	def selected_track(self):
		return self.song().view.selected_track

	def selected_track_idx(self):
		return self.tuple_idx(self.song().tracks, self.song().view.selected_track)

	def selected_scene_idx(self):
		return self.tuple_idx(self.song().scenes, self.song().view.selected_scene)

	def on_selected_track_changed(self):
		self._selected_track = self.selected_track()
		self._do_implicit_arm()
		self.update()

	def on_selected_scene_changed(self):
		self._selected_scene = self.song().view.selected_scene
		self.update()

	def tuple_idx(self, tuple, obj):
		for i in xrange(0, len(tuple)):
			if (tuple[i] == obj):
				return i
		return(False)
