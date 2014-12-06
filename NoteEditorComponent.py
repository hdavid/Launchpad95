from consts import *  # noqa
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
import time


class NoteEditorComponent(ControlSurfaceComponent):

	def __init__(self, parent, matrix):
		ControlSurfaceComponent.__init__(self)
		self.set_enabled(False)
		self._parent = parent

		self._clip = None
		self._note_cache = None
		self._playhead = None

		# metronome
		self.display_metronome = True
		self.metronome_color = AMBER_FULL

		# Velocity colour map. this must remain of lengh 3.
		self.velocity_map = [70, 90, 110]
		self.velocity_color_map = [GREEN_THIRD, GREEN_HALF, GREEN_FULL]
		# other colors
		self.muted_note_color = RED_THIRD
		self.playing_note_color = RED_FULL

		self.long_button_press = 0.500

		# buttons
		self._matrix = None
		self._mute_shift_button = None
		self._velocity_button = None
		self._velocity_shift_button = None

		# matrix
		self.set_button_matrix(matrix)
		self._width = self._matrix.width()
		self._height = self._matrix.height()
		self._grid_buffer = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]
		self._grid_back_buffer = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]

		# time
		self._page = 0
		self._display_page = False
		self._display_page_time = time.time()

		# notes
		self._key_indexes = [36, 37, 38, 39, 40, 41, 42, 43]
		self._key_index_is_in_scale = [True, False, True, True, False, True, False, True]
		self._key_index_is_root_note = [True, False, False, False, False, False, False, False]
		self._number_of_lines_per_note = 1

		# clip
		self._force_update = True

		# quantization
		self._quantization = 16

		# velocity
		self._velocity_index = 2
		self._velocity = self.velocity_map[self._velocity_index]
		self._is_velocity_shifted = False
		self._velocity_notes_pressed = 0
		self._velocity_last_press = time.time()

		# modes
		self._is_mute_shifted = False
		self._is_mutlinote = False

	def disconnect(self):
		self._parent = None
		self._matrix = None
		self._velocity_button = None
		#self._mute_shift_button = None
		self._clip = None

	@property
	def is_multinote(self):
		return self._is_mutlinote

	def set_multinote(self, is_mutlinote, number_of_lines_per_note):
		self._is_mutlinote = is_mutlinote
		self._number_of_lines_per_note = number_of_lines_per_note

	@property
	def quantization(self):
		return self._quantization

	def set_quantization(self, quantization):
		self._quantization = quantization

	def set_scale(self, scale):
		self._scale = scale

	def set_diatonic(self, diatonic):
		self._diatonic = diatonic

	@property
	def key_indexes(self):
		return self._key_indexes

	def set_key_indexes(self, key_indexes):
		self._key_indexes = key_indexes

	def set_key_index_is_in_scale(self, key_index_is_in_scale):
		self._key_index_is_in_scale = key_index_is_in_scale

	def set_key_index_is_root_note(self, key_index_is_root_note):
		self._key_index_is_root_note = key_index_is_root_note

	@property
	def height(self):
		return self._height

	def set_height(self, height):
		self._height = height

	@property
	def width(self):
		return self._width

	@property
	def number_of_lines_per_note(self):
		if self.is_multinote:
			return self._number_of_lines_per_note
		else:
			return self.height

	def set_page(self, page):
		if self.is_multinote:
			self._page = page
		else:
			self._page = page / 4  # number of line per note ?

	def set_clip(self, clip):
		self._clip = clip

	def set_note_cache(self, note_cache):
		self._note_cache = note_cache

	def set_playhead(self, playhead):
		self._playhead = playhead
		self._update_matrix()

	def update_notes(self):
		if self._clip != None:
			self._clip.select_all_notes()
			note_cache = self._clip.get_selected_notes()
			self._clip.deselect_all_notes()
			if self._clip_notes != note_cache:
				self._clip_notes = note_cache
		self._update_matrix()

	def update(self, force=False):
		if force:
			self._force_update = True
		if self.is_enabled():
			self._update_velocity_button()
			self._update_matrix()

	def _display_selected_page(self):
		for i in range(0, self._height):
			self._grid_back_buffer[self._page % self.width][i] = AMBER_FULL

	def _display_note_markers(self):
		for i in range(0, self.height / self.number_of_lines_per_note):
			if self._key_index_is_root_note[i]:
				for j in range(0, self.number_of_lines_per_note):
					self._grid_back_buffer[0][self.height - i * self.number_of_lines_per_note - j - 1] = AMBER_FULL
					self._grid_back_buffer[1][self.height - i * self.number_of_lines_per_note - j - 1] = AMBER_FULL
					self._grid_back_buffer[2][self.height - i * self.number_of_lines_per_note - j - 1] = AMBER_FULL
			elif self._key_index_is_in_scale[i]:
				for j in range(0, self.number_of_lines_per_note):
					self._grid_back_buffer[0][self.height - i * self.number_of_lines_per_note - j - 1] = AMBER_FULL
# MATRIX

	def set_button_matrix(self, matrix):
		assert isinstance(matrix, (ButtonMatrixElement, type(None)))
		if (matrix != self._matrix):
			if (self._matrix != None):
				self._matrix.remove_value_listener(self._matrix_value)
			self._matrix = matrix
			if (self._matrix != None):
				self._matrix.add_value_listener(self._matrix_value)

	def _update_matrix(self):  # step grid LEDs are updated here
		if self.is_enabled():
			# clear back buffer
			for x in range(self.width):
				for y in range(self.height):
					self._grid_back_buffer[x][y] = 0

			# update back buffer
			if self._clip != None and self._note_cache != None:

				# play back position
				if self._playhead != None:
					play_position = self._playhead  # position in beats (1/4 notes in 4/4 time)
					play_page = int(play_position / self.quantization / self.width / self.number_of_lines_per_note)
					play_row = int(play_position / self.quantization / self.width) % self.number_of_lines_per_note

					play_x_position = int(play_position / self.quantization) % self.width
					play_y_position = int(play_position / self.quantization / self.width) % self.height
				else:
					play_position = -1
					play_page = -1
					play_row = -1
					play_x_position = -1
					play_y_position = -1

				# add play positition in amber
				if(self.display_metronome):
					if self._clip.is_playing and self.song().is_playing:
						self._grid_back_buffer[play_x_position][play_y_position] = self.metronome_color

				if(self._display_page):
					self._display_selected_page()
					if self._display_page_time + 0.25 < time.time():
						self._display_page = False

				if self.is_multinote:
					self._display_note_markers()

				# display clip notes
				for note in self._note_cache:
					note_position = note[1]
					note_key = note[0]  # key: 0-127 MIDI note #
					note_velocity = note[3]
					note_muted = note[4]
					note_page = int(note_position / self.quantization / self.width / self.number_of_lines_per_note)
					note_grid_x_position = int(note_position / self.quantization) % self.width
					note_grid_y_position = int(note_position / self.quantization / self.width) % self.height

					if self.is_multinote:
						# compute base note, taking into account number_of_lines_per_note
						note_grid_y_base = index_of(self.key_indexes, note_key) * self.number_of_lines_per_note
						if(note_grid_y_base >= 0):
							note_grid_y_base = (7 - note_grid_y_base) - (self.number_of_lines_per_note - 1)
						if(note_grid_y_base < 0):
							note_grid_y_base = -1

						note_grid_y_offset = int(note_position / self.quantization / self.width) % self.number_of_lines_per_note
						# self._parent._parent._parent.log_message("index:"+str(index_of(self.key_indexes,note_key))+" note_grid_y_base:"+str(note_grid_y_base)+" note_grid_y_offset:"+ str(note_grid_y_offset))
					else:
						if index_of(self.key_indexes, note_key) == 0:
							note_grid_y_base = 0
						else:
							note_grid_y_base = -1
					note_grid_y_offset = int(note_position / self.quantization / self.width) % self.number_of_lines_per_note

					if note_grid_y_base != -1 and note_grid_y_base < self.height:
						note_grid_y_position = note_grid_y_base + note_grid_y_offset
					else:
						note_grid_x_position = -1
						note_grid_y_position = -1

					if note_grid_x_position >= 0:
						# compute colors
						velocity_color = self.velocity_color_map[0]
						for index in range(len(self.velocity_map)):
							if note_velocity >= self.velocity_map[index]:
								velocity_color = self.velocity_color_map[index]
						# highligh playing notes in red. even if they are from other pages.
						if not note_muted and note_page == play_page and play_x_position == note_grid_x_position and (play_y_position == note_grid_y_position and not self.is_multinote or self.is_multinote and note_grid_y_offset == play_row) and self.song().is_playing and self._clip.is_playing:
							self._grid_back_buffer[note_grid_x_position][note_grid_y_position] = self.playing_note_color
						elif note_page == self._page:  # if note is in current page, then update grid
							# do not erase current note highlight
							if self._grid_back_buffer[note_grid_x_position][note_grid_y_position] != self.playing_note_color:
								if note_muted:
									self._grid_back_buffer[note_grid_x_position][note_grid_y_position] = self.muted_note_color
								else:
									self._grid_back_buffer[note_grid_x_position][note_grid_y_position] = velocity_color

				if self._display_page:
					if time.time() - self._display_page_time > 0.5:
						self._display_page = False
					self._display_selected_page()

			# caching : compare back buffer to buffer and update grid. this should minimize midi traffic quite a bit.

			for x in range(self.width):
				for y in range(self.height):
					if(self._grid_back_buffer[x][y] != self._grid_buffer[x][y] or self._force_update):
						self._grid_buffer[x][y] = self._grid_back_buffer[x][y]
						self._matrix.send_value(x, y, self._grid_buffer[x][y])
			self._force_update = False

	def request_display_page(self):
		self._display_page = True
		self._display_page_time = time.time()

	def _matrix_value(self, value, x, y, is_momentary):  # matrix buttons listener
		if self.is_enabled() and y <= self.height:
			if ((value != 0) or (not is_momentary)):
				self._parent._was_velocity_shifted = False
				self._matrix_value_message([value, x, y, is_momentary])

	def _matrix_value_message(self, values):  # value, x, y, is_momentary): #matrix buttons listener
		value = values[0]
		x = values[1]
		y = values[2]
		is_momentary = values[3]
		"""(pitch, time, duration, velocity, mute state)"""
		assert (self._matrix != None)
		assert (value in range(128))
		assert (x in range(self._matrix.width()))
		assert (y in range(self._matrix.height()))
		assert isinstance(is_momentary, type(False))

		if self.is_enabled() and self._clip == None:
			self._parent.create_clip()

		elif self.is_enabled() and self._clip != None and y < self.height:

			# self._parent._parent._parent.log_message("got: x:"+ str(x)+" y:"+str(y))
			# self._parent._parent._parent.log_message("clip:"+ str(self._clip))
			# self._parent._parent._parent.log_message("h:"+ str(self.height))

			if value != 0 or not is_momentary:
				if(self._is_velocity_shifted):
					self._velocity_notes_pressed = self._velocity_notes_pressed + 1

				# note data

				if self.is_multinote:
					time = self.quantization * (self._page * self.width * self.number_of_lines_per_note + x + (y % self.number_of_lines_per_note * self.width))
					pitch = self._key_indexes[8 / self.number_of_lines_per_note - 1 - y / self.number_of_lines_per_note]
				else:
					time = self.quantization * (self._page * self.width * self.number_of_lines_per_note + y * self.width + x)
					pitch = self._key_indexes[0]
				velocity = self._velocity
				duration = self.quantization

				# TODO: use new better way for editing clip

				self._clip.select_all_notes()
				note_cache = self._clip.get_selected_notes()
				if self._note_cache != note_cache:
					self._note_cache = note_cache

				note_cache = list(self._note_cache)
				for note in note_cache:
					if pitch == note[0] and time == note[1]:
						if self._is_velocity_shifted:
							# update velocity of the note
							new_velocity_index = 0
							for index in range(len(self.velocity_map)):
								if note[3] >= self.velocity_map[index]:
									new_velocity_index = (index + 1) % len(self.velocity_map)
							note_cache.append([note[0], note[1], note[2], self.velocity_map[new_velocity_index], note[4]])
						elif not self._is_mute_shifted:
							note_cache.remove(note)
						else:
							# mute / un mute note.
							note_cache.append([note[0], note[1], note[2], note[3], not note[4]])
						break
				else:
					note_cache.append([pitch, time, duration, velocity, self._is_mute_shifted])
				self._clip.select_all_notes()
				self._clip.replace_selected_notes(tuple(note_cache))

				note_cache = self._clip.get_selected_notes()
				if self._note_cache != note_cache:
					self._note_cache = note_cache

	# VELOCITY and VELOCITY SHIFT
	def _update_velocity_button(self):
		if self.is_enabled() and self._velocity_button != None:
			if self._clip != None:
				if self._is_velocity_shifted:
					self._velocity_button.set_on_off_values(GREEN_FULL, GREEN_THIRD)
					self._velocity_button.turn_on()
				else:
					self._velocity_button.set_on_off_values(self.velocity_color_map[self._velocity_index], LED_OFF)
					self._velocity_button.turn_on()
			else:
				self._velocity_button.set_on_off_values(LED_OFF, LED_OFF)
				self._velocity_button.turn_off()

	def set_velocity_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (button != self._velocity_button):
			if (self._velocity_button != None):
				self._velocity_button.remove_value_listener(self._velocity_value)
			self._velocity_button = button
			if (self._velocity_button != None):
				self._velocity_button.add_value_listener(self._velocity_value, identify_sender=True)

	def _velocity_value(self, value, sender):
		assert (self._velocity_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((value is 0) or (not sender.is_momentary())):
				# button released
				if self._velocity_notes_pressed == 0 and time.time() - self._velocity_last_press < self.long_button_press:
					# cycle thru velocities
					self._velocity_index = (len(self.velocity_map) + self._velocity_index + 1) % len(self.velocity_map)
					self._velocity = self.velocity_map[self._velocity_index]
				self._parent._track_controller._implicit_arm = False
				if self._is_velocity_shifted:
					self._parent._track_controller._do_implicit_arm(False)
				self._is_velocity_shifted = False
				self._update_velocity_button()
			if ((value is not 0) or (not sender.is_momentary())):
				# button pressed
				self._velocity_notes_pressed = 0
				self._is_velocity_shifted = True
				self._parent._track_controller._implicit_arm = True
				self._parent._track_controller._do_implicit_arm(True)
				self._velocity_last_press = time.time()
			self._parent._note_selector.update()

	# MUTE SHIFT
	# def _update_mute_shift_button(self):
	# 		if self.is_enabled() and self._mute_shift_button != None:
	# 			if self._clip != None and self._clip.is_midi_clip:
	# 				self._mute_shift_button.set_on_off_values(RED_FULL, RED_THIRD)
	# 				if self._is_mute_shifted:
	# 					self._mute_shift_button.turn_on()
	# 				else:
	# 					self._mute_shift_button.turn_off()
	# 			else:
	# 				self._mute_shift_button.set_on_off_values(LED_OFF, LED_OFF)
	# 				self._mute_shift_button.turn_off()
	# 
	# 	def set_mute_shift_button(self, button):
	# 		assert (isinstance(button, (ButtonElement, type(None))))
	# 		if (button != self._mute_shift_button):
	# 			if (self._mute_shift_button != None):
	# 				self._mute_shift_button.remove_value_listener(self._mute_shift_value)
	# 			self._mute_shift_button = button
	# 			if (self._mute_shift_button != None):
	# 				self._mute_shift_button.add_value_listener(self._mute_shift_value)
	# 
	# 	def _mute_shift_value(self, value):
	# 		assert (self._mute_shift_button != None)
	# 		assert (value in range(128))
	# 		if self.is_enabled() and value==0:
	# 			self._is_mute_shifted = not self._is_mute_shifted
	# 			self._update_mute_shift_button()

	def mute_lane(self, pitch_to_mute):
		if self.is_enabled() and self._clip != None:
			self._clip.select_all_notes()
			note_cache = self._clip.get_selected_notes()
			if self._note_cache != note_cache:
				self._note_cache = note_cache
			note_cache = list(self._note_cache)
			notes_changed = 0
			for note in self._note_cache:
				if note[0] == pitch_to_mute:
					notes_changed = notes_changed + 1
					note_to_mute = note
					note_cache.remove(note)
					note_cache.append([note_to_mute[0], note_to_mute[1], note_to_mute[2], note_to_mute[3], not note_to_mute[4]])
			if notes_changed > 0:
				self._clip.select_all_notes()
				self._clip.replace_selected_notes(tuple(note_cache))
				note_cache = self._clip.get_selected_notes()
			self.update()
