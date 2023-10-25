import time
from random import randrange

from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent


class MelodicNoteEditorComponent(ControlSurfaceComponent):

	def __init__(self, step_sequencer, matrix, side_buttons, control_surface):
		ControlSurfaceComponent.__init__(self)
		self._control_surface = control_surface
		self.set_enabled(False)

		self._step_sequencer = step_sequencer

		self._clip = None
		self._playhead = None

		self._matrix = matrix
		self._side_buttons = side_buttons

		# buttons
		self._matrix = None

		# matrix
		self.set_matrix(matrix)
		self._grid_buffer = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]
		self._grid_back_buffer = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]

		# clip
		self._clip = None
		self._note_cache = []
		self._force_update = True
		self._init_data()

		self._velocity_map = [0, 30, 60, 80, 100, 115, 127]
		self._length_map = [1, 2, 3, 4, 8, 16, 32]

		# time
		self._playhead = 0
		self._page = 0

		# notes
		self._key_indexes = [36, 37, 38, 39, 40, 41, 42, 43]
		self._key_index_is_in_scale = [True, False, True, True, False, True, False, True]
		self._key_index_is_root_note = [True, False, False, False, False, False, False, False]
		self._is_monophonic = False

		# quantization
		self._quantization = 16

		# MODE
		self._mode = STEPSEQ_MODE_NOTES

		# buttons
		self._random_button = None
		self.set_random_button(self._side_buttons[3])

		self._mode_notes_lengths_button = None
		self.set_mode_notes_lengths_button(self._side_buttons[4])
		self._is_notes_lengths_shifted = False
		self._last_notes_lengths_button_press = time.time()

		self._mode_notes_octaves_button = None
		self.set_mode_notes_octaves_button(self._side_buttons[5])
		self._is_octave_shifted = False
		self._last_notes_octaves_button_press = time.time()

		self._mode_notes_velocities_button = None
		self.set_mode_notes_velocities_button(self._side_buttons[6])
		self._is_notes_velocity_shifted = False
		self._last_notes_velocity_button_press = time.time()

		self._mode_notes_pitches_button = None
		self.set_mode_notes_pitches_button(self._side_buttons[7])
		self._is_notes_pitches_shifted = False
		self._last_notes_pitches_button_press = time.time()

		self._is_velocity_shifted = False
		self._is_mute_shifted = False

	def disconnect(self):
		self._step_sequencer = None
		self._matrix = None
		self._mode_notes_lengths_button = None
		self._mode_notes_octaves_button = None
		self._mode_notes_velocities_button = None
		self._mode_notes_pitches_button = None
		self._notes_pitches = None
		self._notes_velocities = None
		self._notes_octaves = None
		self._notes_lengths = None
		self._clip = None

	def _init_data(self):
		pages = 128
		self._notes_pitches = [0] * (7 * pages)
		self._notes_velocities = [4] * pages
		self._notes_octaves = [2] * pages
		self._notes_lengths = [3] * pages

	def set_mode(self, mode):
		self._mode = mode
		self._force_update = True
		self.update()

	def set_clip(self, clip):
		if self._clip != clip:
			self._init_data()
			self._clip = clip

	def set_note_cache(self, note_cache):
		if self._note_cache != note_cache:
			self._note_cache = note_cache
			self._parse_notes()

	def set_playhead(self, playhead):
		self._playhead = playhead
		self._update_matrix()

	def set_multinote(self, x=0, y=0):
		pass

	@property
	def quantization(self):
		return self._quantization

	def set_quantization(self, quantization):
		old_quantize = self._quantization
		self._quantization = quantization
		# update loop point
		if self._clip != None and old_quantize != self._quantization:
			self._loop_start = int(self._clip.loop_start * self._quantization / old_quantize)
			self._loop_end = int(self._clip.loop_end * self._quantization / old_quantize)
			if self._loop_start >= self._clip.loop_end:
				self._clip.loop_end = self._loop_end
				self._clip.loop_start = self._loop_start
				self._clip.end_marker = self._loop_end
				self._clip.start_marker = self._loop_start
			else:
				self._clip.loop_start = self._loop_start
				self._clip.loop_end = self._loop_end
				self._clip.start_marker = self._loop_start
				self._clip.end_marker = self._loop_end
		# update clip notes
		self._update_clip_notes()

	def set_diatonic(self, diatonic):
		self._diatonic = diatonic

	def set_key_indexes(self, key_indexes):
		if self._key_indexes != key_indexes:
			self._key_indexes = key_indexes
			self._update_clip_notes()

	def set_key_index_is_in_scale(self, key_index_is_in_scale):
		self._key_index_is_in_scale = key_index_is_in_scale

	def set_key_index_is_root_note(self, key_index_is_root_note):
		self._key_index_is_root_note = key_index_is_root_note

	def set_page(self, page):
		self._page = page

	def _parse_notes(self):
		# clear notes
		for i in range(len(self._notes_pitches)):
			self._notes_pitches[i] = 0

		first_note = [True] * 128

		for note in self._note_cache:
			note_position = note[1]
			note_key = note[0]
			note_length = note[2]
			note_velocity = note[3]
			note_muted = note[4]
			i = int(note_position / self._quantization)

			if not note_muted:
				if first_note[i]:
					first_note[i] = False

					# velocity
					for x in range(7):
						if note_velocity >= self._velocity_map[x]:
							self._notes_velocities[i] = x

					# length
					for x in range(7):
						if note_length * 4 >= self._length_map[x] * self._quantization:
							self._notes_lengths[i] = x

					# note and octave
					found = False
					for j in range(max(7, len(self._key_indexes))):
						for octave in range(7):
							if note_key == self._key_indexes[j] + 12 * (octave - 2) and not found:
								found = True
								self._notes_octaves[i] = octave
								self._notes_pitches[i * 7 + j] = 1
				elif not self._is_monophonic:
					# note
					found = False
					for j in range(max(7, len(self._key_indexes))):
						if note_key == self._key_indexes[j] + 12 * (self._notes_octaves[i] - 2) and not found:
							found = True
							self._notes_pitches[i * 7 + j] = 1
		self._update_matrix()

	def _update_clip_notes(self):
		if self._clip != None and self._step_sequencer.is_enabled():
			note_cache = list()
			for x in range(len(self._notes_velocities)):
				for note_index in range(7):
					if self._notes_pitches[x * 7 + note_index] == 1:
						time = x * self._quantization
						velocity = self._velocity_map[self._notes_velocities[x]]
						length = self._length_map[self._notes_lengths[x]] * self._quantization / 4.0
						pitch = self._key_indexes[note_index] + 12 * (self._notes_octaves[x] - 2)
						if(pitch >= 0 and pitch < 128 and velocity >= 0 and velocity < 128 and length >= 0):
							note_cache.append([pitch, time, length, velocity, False])
			self._clip.select_all_notes()
			self._clip.replace_selected_notes(tuple(note_cache)) # Todo : deprecated
			#self._control_surface.schedule_message(1, self._sch_update, ([self._clip,tuple(note_cache)]))

	def _sch_update(self, data):
			clip = data[0]
			note_cache = data[1]
			clip.select_all_notes()
			if(note_cache == None):
				clip.replace_selected_notes(tuple())
			else:
				clip.replace_selected_notes(note_cache)

	def update(self, force=False):
		if force:
			self._force_update = True
		if self.is_enabled():
			self._update_mode_notes_octaves_button()
			self._update_mode_notes_lengths_button()
			self._update_mode_notes_velocities_button()
			self._update_mode_notes_pitches_button()
			self._update_random_button()
			self._update_matrix()

	def request_display_page(self):
		pass

	def set_height(self, height):
		pass

# MATRIX

	def set_matrix(self, matrix):
		assert isinstance(matrix, (ButtonMatrixElement, type(None)))
		self._grid_buffer = [
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0]
		]
		self._grid_back_buffer = [
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
		 	[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0]
		]
		if matrix != self._matrix:
			if self._matrix != None:
				self._matrix.remove_value_listener(self._matrix_value)
			self._matrix = matrix
			if self._matrix != None:
				self._matrix.add_value_listener(self._matrix_value)

	def _update_matrix(self):  # step grid LEDs are updated here
		if self.is_enabled() and self._matrix != None:
			# clear back buffer
			for x in range(8):
				for y in range(8):
					self._grid_back_buffer[x][y] = 0

			# update back buffer
			if self._clip != None:

				for x in range(8):
					has_note = False
					for y in range(7):
						if self._notes_pitches[(x + 8 * self._page) * 7 + 6 - y] == 1:
							has_note = True

					for y in range(7):
						if self._mode == STEPSEQ_MODE_NOTES:
							if self._notes_pitches[(x + 8 * self._page) * 7 + 6 - y] == 1:
								self._grid_back_buffer[x][y] = "StepSequencer2.Pitch.On"
							else:
								self._grid_back_buffer[x][y] = "StepSequencer2.Pitch.Off"

						elif self._mode == STEPSEQ_MODE_NOTES_OCTAVES:
							if(has_note):
								if self._notes_octaves[x + 8 * self._page] == 6 - y:
									self._grid_back_buffer[x][y] = "StepSequencer2.Octave.On"
								else:
									self._grid_back_buffer[x][y] = "StepSequencer2.Octave.Off"
							else:
								if self._notes_octaves[x + 8 * self._page] == 6 - y:
									self._grid_back_buffer[x][y] = "StepSequencer2.Octave.Dim"
								else:
									self._grid_back_buffer[x][y] = "StepSequencer2.Octave.Off"

						elif self._mode == STEPSEQ_MODE_NOTES_VELOCITIES:
							if(has_note):
								if self._notes_velocities[x + 8 * self._page] >= 6 - y:
									self._grid_back_buffer[x][y] = "StepSequencer2.Velocity.On"
								else:
									self._grid_back_buffer[x][y] = "StepSequencer2.Velocity.Off"
							else:
								if self._notes_velocities[x + 8 * self._page] >= 6 - y:
									self._grid_back_buffer[x][y] = "StepSequencer2.Velocity.Dim"
								else:
									self._grid_back_buffer[x][y] = "StepSequencer2.Velocity.Off"

						elif self._mode == STEPSEQ_MODE_NOTES_LENGTHS:
							if has_note:
								if self._notes_lengths[x + 8 * self._page] >= 6 - y:
									self._grid_back_buffer[x][y] = "StepSequencer2.Length.On"
								else:
									self._grid_back_buffer[x][y] = "StepSequencer2.Length.Off"
							else:
								if self._notes_lengths[x + 8 * self._page] >= 6 - y:
									self._grid_back_buffer[x][y] = "StepSequencer2.Length.Dim"
								else:
									self._grid_back_buffer[x][y] = "StepSequencer2.Length.Off"
				# metronome
				if self._playhead != None:
					play_position = int(self._playhead / self.quantization)
					play_x_position = int(self._playhead / self.quantization) % 8
					page = int(self._playhead / self.quantization / 8)
					if self._mode == STEPSEQ_MODE_NOTES_LENGTHS:
						if page == self._page:
							metronome_color = "StepSequencer2.NoteEditor.MetronomeInPage"
						else:
							metronome_color = "StepSequencer2.NoteEditor.MetronomeInOtherPage"
					else:
						if page == self._page:
							metronome_color = "StepSequencer2.NoteEditor.MetronomeInPage"
						else:
							metronome_color = "StepSequencer2.NoteEditor.MetronomeInOtherPage"
					self._grid_back_buffer[play_x_position][6] = metronome_color

					# playing notes
					if self._mode == STEPSEQ_MODE_NOTES:
						for y in range(7):
							if self._notes_pitches[play_position * 7 + 6 - y] == 1:
								if page == self._page:
									self._grid_back_buffer[play_x_position][y] = "StepSequencer2.NoteEditor.PlayInPage"
								else:
									self._grid_back_buffer[play_x_position][y] = "StepSequencer2.NoteEditor.PlayInOtherPage"

			else:
				for x in range(8):
					for y in range(7):
						self._grid_back_buffer[x][y] = "DefaultButton.Disabled"

			# caching : compare back buffer to buffer and update grid. this should minimize midi traffic quite a bit.
			for x in range(8):
				for y in range(7):
					if self._grid_back_buffer[x][y] != self._grid_buffer[x][y] or self._force_update:
						self._grid_buffer[x][y] = self._grid_back_buffer[x][y]
						self._matrix.get_button(x,y).set_light(self._grid_buffer[x][y])

			self._force_update = False

	def _matrix_value(self, value, x, y, is_momentary):  # matrix buttons listener
		if self.is_enabled() and self._matrix!=None:
			if self._clip == None:
				self._step_sequencer.create_clip()
			else:
				start = int(self._clip.loop_start / self._quantization)
				end = int(self._clip.loop_end / self._quantization)
				if (self._page + 1) * 8 > end or self._page * 8 < start:
					# current page is outside of running loop.
					# only update this page.
					start = self._page * 8
					end = (self._page + 1) * 8

				if ((value != 0) or (not is_momentary)) and y < 7:
					if self._mode == STEPSEQ_MODE_NOTES:
						if self._is_notes_pitches_shifted:
							for x in range(start, end):
								for yy in range(7):
									self._notes_pitches[(x) * 7 + 6 - yy] = 0
								self._notes_pitches[(x) * 7 + 6 - y] = 1
						else:
							# clear note
							if self._notes_pitches[(x + 8 * self._page) * 7 + 6 - y] == 1:
								self._notes_pitches[(x + 8 * self._page) * 7 + 6 - y] = 0
							else:
								# clear step
								if self._is_monophonic:
									for yy in range(7):
										self._notes_pitches[(x + 8 * self._page) * 7 + 6 - yy] = 0
								self._notes_pitches[(x + 8 * self._page) * 7 + 6 - y] = 1
					elif self._mode == STEPSEQ_MODE_NOTES_OCTAVES:
						if self._is_notes_octaves_shifted:
							if(x < 4):
								for x in range(start, end):
									self._notes_octaves[x] = 6 - y
							else:
								for x in range(start, end):
									if y < 3 and self._notes_octaves[x] < 6:
										self._notes_octaves[x] = self._notes_octaves[x] + 1
									if y > 3 and self._notes_octaves[x] > 0:
										self._notes_octaves[x] = self._notes_octaves[x] - 1
						else:
							self._notes_octaves[x + 8 * self._page] = 6 - y
					elif self._mode == STEPSEQ_MODE_NOTES_VELOCITIES:
						if self._is_notes_velocities_shifted:
							if(x < 4):
								for x in range(start, end):
									self._notes_velocities[x] = 6 - y
							else:
								for x in range(start, end):
									if y < 3 and self._notes_velocities[x] < 6:
										self._notes_velocities[x] = self._notes_velocities[x] + 1
									if y > 3 and self._notes_velocities[x] > 0:
										self._notes_velocities[x] = self._notes_velocities[x] - 1

						else:
							self._notes_velocities[x + 8 * self._page] = 6 - y
					elif self._mode == STEPSEQ_MODE_NOTES_LENGTHS:
						if self._is_notes_lengths_shifted:
							if(x < 4):
								for x in range(start, end):
									self._notes_lengths[x] = 6 - y
							else:
								for x in range(start, end):
									if y < 3 and self._notes_lengths[x] < 6:
										self._notes_lengths[x] = self._notes_lengths[x] + 1
									if y > 3 and self._notes_lengths[x] > 0:
										self._notes_lengths[x] = self._notes_lengths[x] - 1
						else:
							self._notes_lengths[x + 8 * self._page] = 6 - y
					self._update_matrix()
					self._update_clip_notes()


# RANDOM
	def _update_random_button(self):
		if self.is_enabled():
			if (self._random_button != None):
				if self._clip != None:
					self._random_button.set_on_off_values("StepSequencer2.Random.On", "StepSequencer2.Random.Off")
					self._random_button.turn_off()
				else:
					self._random_button.set_light("DefaultButton.Disabled")

	def set_random_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._random_button != button):
			if (self._random_button != None):
				self._random_button.remove_value_listener(self._random_button_value)
			self._random_button = button
			if (self._random_button != None):
				assert isinstance(button, ButtonElement)
				self._random_button.add_value_listener(self._random_button_value, identify_sender=True)

	def _random_button_value(self, value, sender):
		assert (self._random_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			self._random_button.set_on_off_values("StepSequencer2.Random.On", "StepSequencer2.Random.Off")
			if ((value is 0) and (sender.is_momentary())):
				self._random_button.turn_off()
				self._control_surface.show_message("randomise")
				self._randomise()
			else:
				self._random_button.turn_on()

	def _randomise(self):
		start = int(self._clip.loop_start / self._quantization)
		end = int(self._clip.loop_end / self._quantization)
		if (self._page + 1) * 8 > end or self._page * 8 < start:
			# current page is outside of running loop.
			# only update this page.
			start = self._page * 8
			end = (self._page + 1) * 8

		for x in range(start, end):
			if self._mode == STEPSEQ_MODE_NOTES:
				val2 = randrange(0, 9)
				for y in range(7):
					self._notes_pitches[x * 7 + 6 - y] = val2 == y
			elif self._mode == STEPSEQ_MODE_NOTES_OCTAVES:
				val = randrange(2, 6)
				self._notes_octaves[x] = val
			elif self._mode == STEPSEQ_MODE_NOTES_VELOCITIES:
				val = randrange(0, 7)
				self._notes_velocities[x] = val
			elif self._mode == STEPSEQ_MODE_NOTES_LENGTHS:
				val = randrange(0, 4)
				self._notes_lengths[x] = val

		self._update_clip_notes()


# PITCHES
	def _update_mode_notes_pitches_button(self):
		if self.is_enabled():
			if (self._mode_notes_pitches_button != None):
				if self._clip != None:
					self._mode_notes_pitches_button.set_on_off_values("StepSequencer2.Pitch.On", "StepSequencer2.Pitch.Dim")
					if self._mode == STEPSEQ_MODE_NOTES:
						self._mode_notes_pitches_button.turn_on()
					else:
						self._mode_notes_pitches_button.turn_off()
				else:
					self._mode_notes_pitches_button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")
					self._mode_notes_pitches_button.turn_off()

	def set_mode_notes_pitches_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._mode_notes_pitches_button != button):
			if (self._mode_notes_pitches_button != None):
				self._mode_notes_pitches_button.remove_value_listener(self._mode_button_notes_pitches_value)
			self._mode_notes_pitches_button = button
			if (self._mode_notes_pitches_button != None):
				assert isinstance(button, ButtonElement)
				self._mode_notes_pitches_button.add_value_listener(self._mode_button_notes_pitches_value, identify_sender=True)

	def _mode_button_notes_pitches_value(self, value, sender):
		assert (self._mode_notes_pitches_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if ((value is 0) and (sender.is_momentary())):
				self._is_notes_pitches_shifted = False
				self._is_mute_shifted = False
				self._is_velocity_shifted = False
				self._is_notes_pitches_shifted = False
				if time.time() - self._last_notes_pitches_button_press < 0.500:
					self._is_monophonic = not self._is_monophonic
					self._update_clip_notes()
					self._step_sequencer._update_OSD()
				else:
					self.set_mode(STEPSEQ_MODE_NOTES)
					self._control_surface.show_message("pitch")
					self.update()
					self._step_sequencer._update_OSD()
				self._last_notes_pitches_button_press = time.time()
			else:
				self._is_notes_pitches_shifted = True
				self._is_mute_shifted = True
				self._is_velocity_shifted = True
				self._is_notes_pitches_shifted = True

# OCTAVES
	def _update_mode_notes_octaves_button(self):
		if self.is_enabled():
			if (self._mode_notes_octaves_button != None):
				if self._clip != None:
					self._mode_notes_octaves_button.set_on_off_values("StepSequencer2.Octave.On", "StepSequencer2.Octave.Dim")
					if self._mode == STEPSEQ_MODE_NOTES_OCTAVES:
						self._mode_notes_octaves_button.turn_on()
					else:
						self._mode_notes_octaves_button.turn_off()
				else:
					self._mode_notes_octaves_button.set_light("DefaultButton.Disabled")

	def set_mode_notes_octaves_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._mode_notes_octaves_button != button):
			if (self._mode_notes_octaves_button != None):
				self._mode_notes_octaves_button.remove_value_listener(self._mode_button_notes_octaves_value)
			self._mode_notes_octaves_button = button
			if (self._mode_notes_octaves_button != None):
				assert isinstance(button, ButtonElement)
				self._mode_notes_octaves_button.add_value_listener(self._mode_button_notes_octaves_value, identify_sender=True)

	def _mode_button_notes_octaves_value(self, value, sender):
		assert (self._mode_notes_octaves_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if ((value is 0) and (sender.is_momentary())):
				self._is_notes_octaves_shifted = False
				self.set_mode(STEPSEQ_MODE_NOTES_OCTAVES)
				self._control_surface.show_message("octave")
				self.update()
				self._step_sequencer._update_OSD()
			else:
				self._is_notes_octaves_shifted = True

# VELOCITIES
	def _update_mode_notes_velocities_button(self):
		if self.is_enabled():
			if (self._mode_notes_velocities_button != None):
				if self._clip != None:
					self._mode_notes_velocities_button.set_on_off_values("StepSequencer2.Velocity.On", "StepSequencer2.Velocity.Dim")
					if self._mode == STEPSEQ_MODE_NOTES_VELOCITIES:
						self._mode_notes_velocities_button.turn_on()
					else:
						self._mode_notes_velocities_button.turn_off()
				else:
					self._mode_notes_velocities_button.set_light("DefaultButton.Disabled")

	def set_mode_notes_velocities_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._mode_notes_velocities_button != button):
			if (self._mode_notes_velocities_button != None):
				self._mode_notes_velocities_button.remove_value_listener(self._mode_button_notes_velocities_value)
			self._mode_notes_velocities_button = button
			if (self._mode_notes_velocities_button != None):
				assert isinstance(button, ButtonElement)
				self._mode_notes_velocities_button.add_value_listener(self._mode_button_notes_velocities_value, identify_sender=True)

	def _mode_button_notes_velocities_value(self, value, sender):
		assert (self._mode_notes_velocities_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if ((value is 0) and (sender.is_momentary())):
				self._is_mute_shifted = False
				self._is_notes_velocities_shifted = False
				self.set_mode(STEPSEQ_MODE_NOTES_VELOCITIES)
				self._control_surface.show_message("velocity")
				self.update()
				self._step_sequencer._update_OSD()
			else:
				self._is_mute_shifted = True
				self._is_notes_velocities_shifted = True
			self._step_sequencer._is_mute_shifted = self._is_mute_shifted

# LENGTHS
	def _update_mode_notes_lengths_button(self):
		if self.is_enabled():
			if (self._mode_notes_lengths_button != None):
				if self._clip != None:
					self._mode_notes_lengths_button.set_on_off_values("StepSequencer2.Length.On", "StepSequencer2.Length.Dim")
					if self._mode == STEPSEQ_MODE_NOTES_LENGTHS:
						self._mode_notes_lengths_button.turn_on()
					else:
						self._mode_notes_lengths_button.turn_off()
				else:
					self._mode_notes_lengths_button.set_light("DefaultButton.Disabled")


	def set_mode_notes_lengths_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._mode_notes_lengths_button != button):
			if (self._mode_notes_lengths_button != None):
				self._mode_notes_lengths_button.remove_value_listener(self._mode_button_notes_lengths_value)
			self._mode_notes_lengths_button = button
			if (self._mode_notes_lengths_button != None):
				assert isinstance(button, ButtonElement)
				self._mode_notes_lengths_button.add_value_listener(self._mode_button_notes_lengths_value, identify_sender=True)

	def _mode_button_notes_lengths_value(self, value, sender):
		assert (self._mode_notes_lengths_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if ((value is 0) and (sender.is_momentary())):
				self._is_notes_lengths_shifted = False
				self.set_mode(STEPSEQ_MODE_NOTES_LENGTHS)
				self.update()
				self._control_surface.show_message("length")
				self._step_sequencer._update_OSD()
			else:
				self._is_notes_lengths_shifted = True


STEPSEQ_MODE_NOTES = 1
STEPSEQ_MODE_NOTES_OCTAVES = 2
STEPSEQ_MODE_NOTES_VELOCITIES = 3
STEPSEQ_MODE_NOTES_LENGTHS = 4
