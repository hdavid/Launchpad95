# -*- coding: utf-8 -*-

from _Framework.SessionComponent import SessionComponent
from consts import *


class SpecialSessionComponent(SessionComponent):

	""" Special session subclass that handles ConfigurableButtons """

	def __init__(self, num_tracks, num_scenes, stop_clip_buttons,parent):
		self._stop_clip_buttons=stop_clip_buttons
		self._osd = None
		self._parent = parent
		SessionComponent.__init__(self, num_tracks, num_scenes)

	def link_with_track_offset(self, track_offset):
		assert (track_offset >= 0)
		if self._is_linked():
			self._unlink()
		self.set_offsets(track_offset, 0)
		self._link()

	def set_osd(self, osd):
		self._osd = osd

	def _update_OSD(self):
		if self._osd != None:
			self._osd.mode = "Session"
			for i in range(self._num_tracks):
				self._osd.attribute_names[i] = " "
				self._osd.attributes[i] = " "

			tracks = self.tracks_to_use()
			idx = 0
			for i in range(len(tracks)):
				if idx < self._num_tracks and len(tracks) > i + self._track_offset:
					track = tracks[i + self._track_offset]
					if track != None:
						self._osd.attribute_names[idx] = str(track.name)
					else:
						self._osd.attribute_names[idx] = " "
					self._osd.attributes[idx] = " "
				idx += 1

			self._osd.info[0] = " "
			self._osd.info[1] = " "
			self._osd.update()

	def unlink(self):
		if self._is_linked():
			self._unlink()

	def update(self):
		SessionComponent.update(self)
		if self._parent._main_mode_index == 0:
			self._update_OSD()

	def set_enabled(self, enabled):
		SessionComponent.set_enabled(self, enabled)
		if self._parent._main_mode_index == 0:
			self._update_OSD()

	def _reassign_tracks(self):
		SessionComponent._reassign_tracks(self)
		if self._parent._main_mode_index == 0:
			self._update_OSD()

	def _update_stop_clips_led(self, index):
		if self.is_enabled() and self._stop_clip_buttons != None:
			if index<len(self._stop_clip_buttons):
				button = self._stop_clip_buttons[index]
				tracks_to_use = self.tracks_to_use()
				track_index = index + self.track_offset()
				if 0 <= track_index < len(tracks_to_use):
					track = tracks_to_use[track_index]
					if track.fired_slot_index == -2:
						button.send_value(self._stop_clip_triggered_value)
					elif track.playing_slot_index >= 0:
						button.send_value(AMBER_THIRD)
					else:
						#self._parent._parent.log_message("index:"+str(index))
						button.turn_off()
				else:
					button.send_value(4)
