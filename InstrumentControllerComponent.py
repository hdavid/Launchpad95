import Live
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SubjectSlot import subject_slot
from _Framework.ButtonElement import ButtonElement
from _Framework.Util import find_if
from itertools import imap
from TrackControllerComponent import TrackControllerComponent
from ScaleComponent import *  # noqa
from StepSequencerComponent import StepSequencerComponent
from consts import *  # noqa

class InstrumentControllerComponent(CompoundComponent):

	def __init__(self, matrix, side_buttons, top_buttons, parent):
		super(InstrumentControllerComponent, self).__init__()
		self._parent = parent
		self._osd = None
		self._matrix = None
		self._side_buttons = side_buttons
		self._remaining_buttons = []
		self._track_controller = None
		self.base_channel = 11
		self._quick_scales = [0, 1, 2, 3, 4, 5, 6, 7, 10, 13, 14, 15, 17, 18, 24]
		self._quick_scale_root = True
		self._normal_feedback_velocity = AMBER_FULL
		self._recordind_feedback_velocity = RED_FULL
		self._drum_group_device = None
		self._octave_up_button = None
		self._octave_down_button = None
		self._scales_toggle_button = None
		self.set_scales_toggle_button(side_buttons[0])
		self.set_octave_up_button(side_buttons[2])
		self.set_octave_down_button(side_buttons[3])

		self._track_controller = self.register_component(TrackControllerComponent())
		self._track_controller.set_enabled(False)
		self._track_controller.set_parent(self._parent._parent)
		self._track_controller.set_prev_scene_button(top_buttons[0])
		self._track_controller.set_next_scene_button(top_buttons[1])
		self._track_controller.set_prev_track_button(top_buttons[2])
		self._track_controller.set_next_track_button(top_buttons[3])
		self._track_controller.set_undo_button(side_buttons[1])
		self._track_controller.set_stop_button(side_buttons[4])
		self._track_controller.set_play_button(side_buttons[5])
		self._track_controller.set_session_record_button(side_buttons[7])
		self._track_controller.set_solo_button(side_buttons[6])

		self._scales = self.register_component(ScalesComponent())
		self._scales.set_enabled(False)
		self.set_matrix(matrix)
		self._scales.set_parent(self)
		self._scales.set_matrix(matrix)
		self._scales.set_osd(self._osd)

		self._on_session_record_changed.subject = self.song()

	def set_enabled(self, enabled):
		CompoundComponent.set_enabled(self, enabled)
		if self._track_controller != None:
			self._track_controller.set_enabled(enabled)
		feedback_channels = [self.base_channel, self.base_channel + 1, self.base_channel + 2, self.base_channel + 3]
		# non_feedback_channel = self.base_channel + 4
		self._set_feedback_velocity()
		self._parent._parent.set_feedback_channels(feedback_channels)
		if not enabled:
			self._parent._parent.release_controlled_track()
		else:
			self._parent._parent.set_controlled_track(self.song().view.selected_track)

		if self._track_controller != None:
			self._track_controller._do_implicit_arm(enabled)
			self._track_controller.set_enabled(enabled)
		if enabled:
			self._update_OSD()

	def _set_feedback_velocity(self):
		if self.song().session_record:
			self._parent._parent._c_instance.set_feedback_velocity(self._recordind_feedback_velocity)
		else:
			self._parent._parent._c_instance.set_feedback_velocity(self._normal_feedback_velocity)

	@subject_slot('session_record')
	def _on_session_record_changed(self):
		self._set_feedback_velocity()

	def set_scales_toggle_button(self, button):
		assert isinstance(button, (ButtonElement, type(None)))
		if (self._scales_toggle_button != None):
			self._scales_toggle_button.remove_value_listener(self._scales_toggle)
		self._scales_toggle_button = button
		if (self._scales_toggle_button != None):
			self._scales_toggle_button.add_value_listener(self._scales_toggle, identify_sender=True)
			self._scales_toggle_button.turn_off()

	def set_octave_up_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if (self._octave_up_button != None):
			self._octave_up_button.remove_value_listener(self._scroll_octave_up)
		self._octave_up_button = button
		if (self._octave_up_button != None):
			self._octave_up_button.add_value_listener(self._scroll_octave_up, identify_sender=True)
			self._octave_up_button.turn_off()

	def set_octave_down_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if (self._octave_down_button != None):
			self._octave_down_button.remove_value_listener(self._scroll_octave_down)
		self._octave_down_button = button
		if (self._octave_down_button != None):
			self._octave_down_button.add_value_listener(self._scroll_octave_down, identify_sender=True)
			self._octave_down_button.turn_off()

	def _scales_toggle(self, value, sender):
		if self.is_enabled():
			self._scales_toggle_button.set_on_off_values(AMBER_FULL, AMBER_THIRD)
			if (value is not 0):
				self._osd_mode_backup = self._osd.mode
				self._scales.set_enabled(True)
				self._osd.mode = self._osd_mode_backup + ' - Scale'
				self._scales_toggle_button.turn_on()
				self._scales.update()
			else:
				self._scales_toggle_button.turn_off()
				self._scales.set_enabled(False)
				self._osd.mode = self._osd_mode_backup
				self.update()

	def _can_scroll_octave_up(self):
		return self._scales._octave_index + self._scales._presets.octave_index_offset < 10

	def _can_scroll_octave_down(self):
		return self._scales._octave_index + self._scales._presets.octave_index_offset > -2

	def _scroll_octave_up(self, value, sender):
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value is not 0)):
				if self._can_scroll_octave_up():
					self._scales._octave_index += 1
					self.update()

	def _scroll_octave_down(self, value, sender):
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value is not 0)):
				if self._can_scroll_octave_down():
					self._scales._octave_index -= 1
					self.update()

	def tuple_idx(self, tuple, obj):
		for i in xrange(0, len(tuple)):
			if (tuple[i] == obj):
				return i
		return(False)

	def _matrix_value_quickscale(self, value, x, y, is_momentary):  # matrix buttons listener for advanced mode
		if self.is_enabled() and not self._scales.is_enabled() and self._scales.is_quick_scale:
			keys = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
			if ((value != 0) or (not is_momentary)):
				if self._quick_scale_root:
					root = -1
					selected_key = self._scales._selected_key
					selected_modus = self._scales._selected_modus
					if y == 1 and x < 7 or y == 0 and x in[0, 1, 3, 4, 5]:
						if y == 1:
							root = [0, 2, 4, 5, 7, 9, 11, 12][x]
							self._parent._parent.show_message(keys[root]+" "+str(self._scales._modus_names[selected_modus]))
						if y == 0 and x < 6:
							root = [0, 2, 4, 5, 7, 9, 11, 12][x] + 1
							self._parent._parent.show_message(keys[root]+" "+str(self._scales._modus_names[selected_modus]))
						if root == selected_key:  # alternate minor/major
							if selected_modus == 0:
								selected_modus = self._scales._current_minor_mode
							elif selected_modus in [1, 13, 14]:
								self._scales._current_minor_mode = selected_modus
								selected_modus = 0
							elif selected_modus == 11:
								selected_modus = 12
							elif selected_modus == 12:
								selected_modus = 11
							self._parent._parent.show_message(keys[root]+" "+str(self._scales._modus_names[selected_modus]))
					else:
						if y == 0 and x == 7:  # change mode
							self._quick_scale_root = not self._quick_scale_root
							if self._quick_scale_root:
								self._parent._parent.show_message("quick scale : root")
							else:
								self._parent._parent.show_message("quick scale : modes")
							self.update()
						if y == 1 and x == 7 and False:  # rotate minor scales
							if self._scales._selected_modus in self._scales._minor_modes:
								self._scales.set_selected_modus(self._scales._minor_modes[(self.tuple_idx(self._scales._minor_modes, self._scales._selected_modus) + 1) % 3])
								self._parent._parent.show_message(keys[root]+" "+str(self._scales._modus_names[self._scales._selected_modus]))
								self.update()
						if y == 1 and x == 7:  # nav circle of 5th right
							root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) + 1 + 12) % 12]
							self._parent._parent.show_message("circle of 5ths -> "+keys[selected_key]+" "+str(self._scales._modus_names[selected_modus])+" => "+keys[root]+" "+str(self._scales._modus_names[selected_modus]))
						if y == 0 and x == 6:  # nav circle of 5th left
							root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) - 1 + 12) % 12]
							self._parent._parent.show_message("circle of 5ths <- "+keys[selected_key]+" "+str(self._scales._modus_names[selected_modus])+" => "+keys[root]+" "+str(self._scales._modus_names[selected_modus]))
						if y == 0 and x == 2:  # relative scale
							if selected_modus == 0:
								selected_modus = self._scales._current_minor_mode
								root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) + 3) % 12]
							elif selected_modus in [1, 13, 14]:
								self._scales._current_minor_mode = selected_modus
								selected_modus = 0
								root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) - 3 + 12) % 12]
							elif selected_modus == 11:
								selected_modus = 12
								root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) + 3) % 12]
							elif selected_modus == 12:
								selected_modus = 11
								root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) - 3 + 12) % 12]
							self._parent._parent.show_message("Relative scale : "+keys[root]+" "+str(self._scales._modus_names[selected_modus]))

					if root != -1:
						self._scales.set_selected_modus(selected_modus)
						self._scales.set_key(root)
						self.update()

				else:
					if(y == 0):
						if x < 7 and self._quick_scales[x] != -1:
							self._scales.set_selected_modus(self._quick_scales[x])
							self._parent._parent.show_message("mode : "+str(self._scales._modus_names[self._scales._selected_modus]))
							self.update()
						if x == 7:
							self._quick_scale_root = not self._quick_scale_root
							if self._quick_scale_root:
								self._parent._parent.show_message("quick scale : root")
							else:
								self._parent._parent.show_message("quick scale : modes")
							self.update()
					if(y == 1):
						if x < 8 and self._quick_scales[x + 7] != -1:
							self._scales.set_selected_modus(self._quick_scales[x + 7])
							self._parent._parent.show_message("mode : "+str(self._scales._modus_names[self._scales._selected_modus]))
							self.update()

	def update(self):
		if self.is_enabled():
			if self._track_controller != None:
				self._track_controller.set_enabled(True)

			self._update_matrix()

			for button in self._remaining_buttons:
				button.set_on_off_values(LED_OFF, LED_OFF)
				button.turn_off()

			if self._scales_toggle_button != None:
				self._scales_toggle_button.set_on_off_values(AMBER_FULL, AMBER_THIRD)
				self._scales_toggle_button.turn_off()

			if self._octave_up_button != None:
				self._octave_up_button.set_on_off_values(GREEN_FULL, GREEN_THIRD)
				if(self._can_scroll_octave_up()):
					self._octave_up_button.turn_on()
				else:
					self._octave_up_button.turn_off()

			if self._octave_down_button != None:
				self._octave_down_button.set_on_off_values(GREEN_FULL, GREEN_THIRD)
				if(self._can_scroll_octave_down()):
					self._octave_down_button.turn_on()
				else:
					self._octave_down_button.turn_off()

			self._update_OSD()

	def set_osd(self, osd):
		self._osd = osd

	def _update_OSD(self):
		if self._osd != None:
			if self._scales.is_quick_scale:
				self._osd.mode = "Instrument (quick scale)"
			else:
				self._osd.mode = "Instrument"
			self._osd.attributes[0] = MUSICAL_MODES[self._scales._selected_modus * 2]
			self._osd.attribute_names[0] = "Scale"
			self._osd.attributes[1] = KEY_NAMES[self._scales._selected_key % 12]
			self._osd.attribute_names[1] = "Root Note"
			self._osd.attributes[2] = self._scales._octave_index
			self._osd.attribute_names[2] = "Octave"
			self._osd.attributes[3] = " "
			self._osd.attribute_names[3] = " "
			self._osd.attributes[4] = " "
			self._osd.attribute_names[4] = " "
			self._osd.attributes[5] = " "
			self._osd.attribute_names[5] = " "
			self._osd.attributes[6] = " "
			self._osd.attribute_names[6] = " "
			self._osd.attributes[7] = " "
			self._osd.attribute_names[7] = " "

			if self.song().view.selected_track != None:
				self._osd.info[0] = "track : " + self.song().view.selected_track.name
			else:
				self._osd.info[0] = " "

			self._osd.info[1] = " "
			self._osd.update()

	def set_matrix(self, matrix):
		self._matrix = matrix
		if matrix:
			matrix.reset()
		if (matrix != self._matrix):
			if (self._matrix != None):
				self._matrix.remove_value_listener(self._matrix_value_quickscale)
		self._matrix = matrix
		if (self._matrix != None):
			self._matrix.add_value_listener(self._matrix_value_quickscale)
		self._update_matrix()

	def on_selected_track_changed(self):
		if self._track_controller._implicit_arm:
			self._get_drumrack_device()
			if self._drum_group_device != None:
				self._scales.set_drumrack(True)
			else:
				self._scales.set_drumrack(False)
			self.update()

	def _get_drumrack_device(self):
		if self.song().view.selected_track != None:
			track = self.song().view.selected_track
			if(track.devices != None and len(track.devices) > 0):
				#device = track.devices[0]
				device = self.find_drum_group_device(track)
				if(device != None and device.can_have_drum_pads and device.has_drum_pads):
					self._drum_group_device = device
				else:
					self._drum_group_device = None
			else:
				self._drum_group_device = None
		else:
			self._drum_group_device = None
	
	def find_drum_group_device(self, track):
		device = find_if(lambda d: d.type == Live.Device.DeviceType.instrument, track.devices)
		if device:
			if device.can_have_drum_pads:
				return device
			elif device.can_have_chains:
				return find_if(bool, imap(self.find_drum_group_device, device.chains))
		else:
			return None
			
	def _update_matrix(self):

		if not self.is_enabled() or not self._matrix or self._scales.is_enabled():
			self._parent._parent.release_controlled_track()
			# self._parent._parent.set_feedback_channels([])
		else:
			# feedback_channels = [self.base_channel, self.base_channel + 1, self.base_channel + 2, self.base_channel + 3]
			non_feedback_channel = self.base_channel + 4

			# create array to keep last channel used for note.
			note_channel = range(128)
			for i in range(128):
				note_channel[i] = self.base_channel

			# select drumrack device
			self._get_drumrack_device()

			if self._scales.is_drumrack() and not self._scales._is_diatonic and not self._scales._is_chromatic:
				if self._drum_group_device != None:
					self._scales.set_drumrack(True)
				else:
					self._scales.set_diatonic()

			for button, (x, y) in self._matrix.iterbuttons():
				button.use_default_message()
				button.set_channel(non_feedback_channel)
				button.force_next_send()

			if self._scales.is_drumrack():

				for button, (x, y) in self._matrix.iterbuttons():
					if button:
						note = 0
						if(x < 4):
							note = 12 * self._scales._octave_index + x + 4 * (7 - y)
						else:
							note = 12 * self._scales._octave_index + 32 + x - 4 + 4 * (7 - y)

						if note < 128 and note >= 0:
							if self._drum_group_device != None and self._drum_group_device.can_have_drum_pads and self._drum_group_device.has_drum_pads and self._drum_group_device.drum_pads[note].chains:
								button.set_on_off_values(RED_FULL, GREEN_THIRD)
								button.set_enabled(False)
								button.set_channel(self.base_channel)
								button.set_identifier(note)
							else:
								button.set_on_off_values(GREEN_FULL, LED_OFF)
								button.set_enabled(False)
								button.set_channel(self.base_channel)
								button.set_identifier(note)
						else:
							button.set_on_off_values(LED_OFF, LED_OFF)
							button.set_enabled(True)
							button.set_channel(non_feedback_channel)
						button.force_next_send()
						button.turn_off()

			else:
				if self._scales.is_quick_scale:
					quick_scale_root_button = self._matrix.get_button(7, 0)
					quick_scale_root_button.set_on_off_values(RED_THIRD, RED_FULL)
					quick_scale_root_button.set_enabled(True)
					quick_scale_root_button.force_next_send()
					if self._quick_scale_root:
						quick_scale_root_button.turn_on()
					else:
						quick_scale_root_button.turn_off()

					selected_modus = self._scales._selected_modus
					selected_key = self._scales._selected_key

					if self._quick_scale_root:
						if selected_modus == 0 or selected_modus == 12:
							off_color = AMBER_THIRD
							on_color = AMBER_FULL
							fifth_button_color = RED_THIRD
							mode_button_color = RED_THIRD
							relative_scale_button_color = RED_THIRD
						elif selected_modus == 1 or selected_modus == 11:
							off_color = RED_THIRD
							on_color = RED_FULL
							fifth_button_color = GREEN_THIRD
							mode_button_color = GREEN_THIRD
							relative_scale_button_color = GREEN_THIRD
						else:
							off_color = GREEN_THIRD
							on_color = GREEN_FULL
							fifth_button_color = RED_THIRD
							mode_button_color = RED_THIRD
							relative_scale_button_color = RED_THIRD

						# circle of 5th nav right
						button = self._matrix.get_button(7, 1)
						button.set_on_off_values(fifth_button_color, fifth_button_color)
						button.force_next_send()
						button.turn_on()
						# circle of 5th nav left
						button = self._matrix.get_button(6, 0)
						button.set_on_off_values(fifth_button_color, fifth_button_color)
						button.force_next_send()
						button.turn_on()
						# mode button
						button = self._matrix.get_button(7, 0)
						button.set_on_off_values(mode_button_color, mode_button_color)
						button.force_next_send()
						button.turn_on()
						# relative scale button
						button = self._matrix.get_button(2, 0)
						button.set_on_off_values(relative_scale_button_color, relative_scale_button_color)
						button.force_next_send()
						button.turn_on()

						for x in [0, 1, 3, 4, 5]:
							button = self._matrix.get_button(x, 0)
							button.set_enabled(True)
							button.set_on_off_values(on_color, off_color)
							button.force_next_send()
							if [0, 2, 4, 5, 7, 9, 11, 12][x] + 1 == selected_key:
								button.turn_on()
							else:
								button.turn_off()

						for x in [0, 1, 2, 3, 4, 5, 6]:
							button = self._matrix.get_button(x, 1)
							button.set_enabled(True)
							button.set_on_off_values(on_color, off_color)
							button.force_next_send()
							if [0, 2, 4, 5, 7, 9, 11, 12][x] == selected_key:
								button.turn_on()
							else:
								button.turn_off()
					else:
						for x in range(7):
							button = self._matrix.get_button(x, 0)
							button.set_enabled(True)
							if self._quick_scales[x] != -1:
								button.set_on_off_values(AMBER_FULL, AMBER_THIRD)
							else:
								button.set_on_off_values(LED_OFF, LED_OFF)
							button.force_next_send()
							if self._quick_scales[x] == selected_modus:
								button.turn_on()
							else:
								button.turn_off()

						for x in range(8):
							button = self._matrix.get_button(x, 1)
							button.set_enabled(True)
							if self._quick_scales[x + 7] != -1:
								button.set_on_off_values(AMBER_FULL, AMBER_THIRD)
							else:
								button.set_on_off_values(LED_OFF, LED_OFF)
							button.force_next_send()
							if self._quick_scales[x + 7] == selected_modus:
								button.turn_on()
							else:
								button.turn_off()

				interval = self._scales._presets.interval
				pattern = self._get_pattern(interval)
				max_j = self._matrix.width() - 1
				for button, (i, j) in self._matrix.iterbuttons():
					if button and (not self._scales.is_quick_scale or j > 1):
						note_info = pattern.note(i, max_j - j)
						if note_info.index != None:
							button.set_on_off_values(RED_FULL, note_info.color)
							button.set_enabled(False)
							button.set_channel(note_channel[note_info.index])
							# comment the line above and use the one below if you want instrument controller to use one channel instead of 3
							# button.set_channel(note_channel[0])
							button.set_identifier(note_info.index)
							note_channel[note_info.index] = note_channel[note_info.index] + 1
						else:
							button.set_channel(non_feedback_channel)
							button.set_on_off_values(LED_OFF, LED_OFF)
							button.set_light(note_info.color)
							button.set_enabled(True)
						button.force_next_send()
						button.turn_off()

			for button in self._side_buttons:
				button.use_default_message()
				button.set_channel(non_feedback_channel)
				button.set_enabled(True)
				button.force_next_send()

			self._parent._config_button.send_value(32)

	def _get_pattern(self, interval):
		if(self._scales.is_drumrack()):
			pass
		else:
			# notes
			notes = self._scales.notes

			# origin
			if not self._scales.is_absolute:
				origin = 0
			elif self._scales.is_diatonic():
				origin = 0
				for k in xrange(len(notes)):
					if notes[k] >= 12:
						origin = k - len(notes)
						break
			else:
				origin = -notes[0]

			# interval
			if interval == None:
				interval = 8
			elif self._scales.is_chromatic():
				interval = [0, 2, 4, 5, 7, 9, 10, 11][interval]
			else:
				interval = interval
			# self._parent.log_message("interval:"+str(interval))

			# layout
			if self._scales._presets.is_horizontal:
				steps = [1, interval]
				origin = [origin, 0]
			else:
				steps = [interval, 1]
				origin = [0, origin]

			return MelodicPattern(steps=steps, scale=notes, origin=origin, base_note=self._scales._octave_index * 12, base_note_color=self._scales.get_base_note_color(), scale_note_color=self._scales.get_scale_note_color(), scale_highlight_color=self._scales.get_scale_highlight_color(), chromatic_mode=self._scales.is_chromatic(), chromatic_gtr_mode=self._scales.is_chromatic_gtr(), diatonic_ns_mode=self._scales.is_diatonic_ns())
