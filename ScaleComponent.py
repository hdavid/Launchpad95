from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from consts import *  # noqa

class InstrumentPresetsComponent():

	def __init__(self, *a, **k):
		self.octave_index_offset = 0
		self.is_horizontal = True
		self.interval = 3

	def _set_scale_mode(self, octave_index_offset, orientation, interval):
		self.octave_index_offset = octave_index_offset
		self.is_horizontal = (orientation == 'horizontal' or orientation == True)
		self.interval = interval

	def set_orientation(self, orientation):
		self._set_scale_mode(self.octave_index_offset, orientation, self.interval)

	def toggle_orientation(self):
		if(self.is_horizontal):
			self._set_scale_mode(self.octave_index_offset, 'vertical', self.interval)
		else:
			self._set_scale_mode(self.octave_index_offset, 'horizontal', self.interval)

	def set_interval(self, interval):
		# 3rd : interval = 2
		# 4th : interval = 3
		# 6th : interval = 5
		if interval == None:
			self._set_scale_mode(-2, self.is_horizontal, None)
		else:
			self._set_scale_mode(0, self.is_horizontal, interval)

	def cycle_intervals(self):
		if(self.interval == None):
			self.set_interval(2)
		elif(self.interval == 2):
			self.set_interval(3)
		elif(self.interval == 3):
			self.set_interval(5)
		elif(self.interval == 5):
			self.set_interval(2)


class Scale(object):

	def __init__(self, name, notes, *a, **k):
		super(Scale, self).__init__(*a, **k)
		self.name = name
		self.notes = notes


class Modus(Scale):

	def __init__(self, *a, **k):
		super(Modus, self).__init__(*a, **k)

	def scale(self, base_note):
		return Scale(KEY_NAMES[base_note], [base_note + x for x in self.notes])

	def scales(self, base_notes):
		return [self.scale(b) for b in base_notes]


class MelodicPattern(object):

	def __init__(self, steps=[0, 0], scale=range(12), base_note=0, origin=[0, 0], valid_notes=xrange(128), base_note_color=GREEN_HALF, scale_note_color=AMBER_THIRD, scale_highlight_color=GREEN_FULL, foreign_note_color=LED_OFF, invalid_note_color=LED_OFF, chromatic_mode=False, chromatic_gtr_mode=False, diatonic_ns_mode=False, *a, **k):
		super(MelodicPattern, self).__init__(*a, **k)
		self.steps = steps
		self.scale = scale
		self.base_note = base_note
		self.origin = origin
		self.valid_notes = valid_notes
		self.base_note_color = base_note_color
		self.scale_note_color = scale_note_color
		self.scale_highlight_color = scale_highlight_color
		self.foreign_note_color = foreign_note_color
		self.invalid_note_color = invalid_note_color
		self.chromatic_mode = chromatic_mode
		self.chromatic_gtr_mode = chromatic_gtr_mode
		self.diatonic_ns_mode = diatonic_ns_mode

	class NoteInfo:

		def __init__(self, index, channel, color):
			self.index, self.channel, self.color = index, channel, color

	@property
	def _extended_scale(self):
		if self.chromatic_mode:
			first_note = self.scale[0]
			return range(first_note, first_note + 12)
		else:
			return self.scale

	def _octave_and_note(self, x, y):
		scale = self._extended_scale
		scale_size = len(scale)
		if self.chromatic_mode:
			self.steps[1] = 5
		else:
			if self.diatonic_ns_mode:
				self.steps[1] = scale_size
		index = self.steps[0] * (self.origin[0] + x) + self.steps[1] * (self.origin[1] + y)
		if self.chromatic_gtr_mode and y > 3:
			index = index - 1
		octave = index / scale_size
		note = scale[index % scale_size]
		return (octave, note)

	def _color_for_note(self, note):
		if note == self.scale[0]:
			return self.base_note_color
		elif note == self.scale[2] or note == self.scale[4]:
			return self.scale_highlight_color
		elif note in self.scale:
			return self.scale_note_color
		else:
			return self.foreign_note_color

	def note(self, x, y):
		octave, note = self._octave_and_note(x, y)
		index = 12 * octave + note + self.base_note
		if index in self.valid_notes:
			return self.NoteInfo(index, x, self._color_for_note(note))
		else:
			return self.NoteInfo(None, x, self.invalid_note_color)


class ScalesComponent(ControlSurfaceComponent):

	def __init__(self, *a, **k):
		super(ScalesComponent, self).__init__(*a, **k)
		self._modus_list = [Modus(MUSICAL_MODES[v], MUSICAL_MODES[v + 1]) for v in xrange(0, len(MUSICAL_MODES), 2)]
		self._modus_names = [MUSICAL_MODES[v] for v in xrange(0, len(MUSICAL_MODES), 2)]
		self._selected_modus = 0
		self._selected_key = 0
		self._is_chromatic = False
		self._is_chromatic_gtr = False  # variable for chromatic guitar mode
		self._is_diatonic = True
		self._is_diatonic_ns = False  # variable for diatonic non-staggered mode
		self._is_drumrack = False
		self.is_absolute = False
		self.is_quick_scale = False
		self.base_note_color = AMBER_THIRD
		self.scale_note_color = GREEN_THIRD
		self.scale_highlight_color = GREEN_HALF
		self._presets = InstrumentPresetsComponent()
		self._matrix = None
		self._octave_index = 3
		# C  D  E  F  G  A  B
		self._index = [0, 2, 4, 5, 7, 9, 11]
		self._parent = None
		self._current_minor_mode = 1
		self._minor_modes = [1, 13, 14]

	def set_parent(self, parent):
		self._parent = parent

	def is_diatonic(self):
		return not self._is_drumrack and (self._is_diatonic or self._is_diatonic_ns)

	def is_chromatic(self):
		return not self._is_drumrack and (self._is_chromatic or self._is_chromatic_gtr)

	def is_diatonic_ns(self):
		return self._is_diatonic_ns

	def is_chromatic_gtr(self):
		return self._is_chromatic_gtr

	def is_drumrack(self):
		return self._is_drumrack

	def get_base_note_color(self):
		return self.base_note_color

	def get_scale_note_color(self):
		return self.scale_note_color

	def get_scale_highlight_color(self):
		return self.scale_highlight_color

	def set_diatonic(self, interval=-1):
		self._is_drumrack = False
		self._is_chromatic = False
		self._is_chromatic_gtr = False
		self._is_diatonic = True
		self._is_diatonic_ns = False
		if interval != -1:
			self._presets.set_interval(interval)

	def set_diatonic_ns(self):
		self._is_drumrack = False
		self._is_chromatic = False
		self._is_chromatic_gtr = False
		self._is_diatonic = False
		self._is_diatonic_ns = True

	def set_chromatic(self):
		self._is_drumrack = False
		self._is_chromatic = True
		self._is_chromatic_gtr = False
		self._is_diatonic = False
		self._is_diatonic_ns = False

	def set_chromatic_gtr(self):
		self._is_drumrack = False
		self._is_chromatic = False
		self._is_chromatic_gtr = True
		self._is_diatonic = False
		self._is_diatonic_ns = False

	def set_drumrack(self, value):
		self._is_drumrack = value

	@property
	def notes(self):
		return self.modus.scale(self._selected_key).notes

	@property
	def modus(self):
		return self._modus_list[self._selected_modus]

	def set_key(self, n):
		self._selected_key = n % 12


	def set_octave_index(self, n):
		self._octave_index = n

	def set_selected_modus(self, n):
		if n > -1 and n < len(self._modus_list):
			self._selected_modus = n
			

	def _set_preset(self, n):
		if n > -1 and n < 6:
			self._selected_modus = n

	def set_matrix(self, matrix):
		if matrix:
			matrix.reset()
		if (matrix != self._matrix):
			if (self._matrix != None):
				self._matrix.remove_value_listener(self._matrix_value)
			self._matrix = matrix
			if (self._matrix != None):
				self._matrix.add_value_listener(self._matrix_value)
			self.update()


	def _matrix_value(self, value, x, y, is_momentary):  # matrix buttons listener
		if self.is_enabled():
			if ((value != 0) or (not is_momentary)):
				# modes
				if y == 0:
					if not self.is_drumrack():
						if x == 0:
							self.is_absolute = not self.is_absolute
							if self.is_absolute:
								self._parent._parent._parent.show_message("absolute root")
							else:
								self._parent._parent._parent.show_message("relative root")
						if x == 1:
							self._presets.toggle_orientation()
					if x == 2:
						self.set_chromatic_gtr()
						self._presets.set_orientation('horizontal')
						self._parent._parent._parent.show_message("mode: chromatic gtr")
					if x == 3:
						self.set_diatonic_ns()
						self._presets.set_orientation('horizontal')
						self._parent._parent._parent.show_message("mode: diatonic not staggered")
					if x == 4:
						self.set_diatonic(2)
						self._presets.set_orientation('vertical')
						self._parent._parent._parent.show_message("mode: diatonic vertical (chords)")
					if x == 5:
						self.set_diatonic(3)
						self._presets.set_orientation('horizontal')
						self._parent._parent._parent.show_message("mode: diatonic")
					if x == 6:
						self.set_chromatic()
						self._presets.set_orientation('horizontal')
						self._parent._parent._parent.show_message("mode: chromatic")
					if x == 7:
						self.set_drumrack(True)
						self._parent._parent._parent.show_message("mode: drumrack")
				
				keys = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
				# root note
				if not self.is_drumrack():
					root = -1
					selected_key = self._selected_key
					selected_modus = self._selected_modus
					if y == 1 and x in[0, 1, 3, 4, 5] or y == 2 and x < 7:
						root = [0, 2, 4, 5, 7, 9, 11, 12][x]
						if y == 1:
							root = root + 1
						self._parent._parent._parent.show_message("root "+keys[root])

					# if root == selected_key:#alternate minor/major
					# 	if selected_modus==0:
					# 		selected_modus = self._current_minor_mode
					# 	elif selected_modus in [1,13,14]:
					# 		self._current_minor_mode = selected_modus
					# 		selected_modus = 0
					# 	elif selected_modus==11:
					# 		selected_modus = 12
					# 	elif selected_modus==12:
					# 		selected_modus = 11

					if y == 2 and x == 7:  # nav circle of 5th right
						root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) + 1 + 12) % 12]
						self._parent._parent._parent.show_message("circle of 5ths -> "+keys[selected_key]+" "+str(self._modus_names[selected_modus])+" => "+keys[root]+" "+str(self._modus_names[selected_modus]))
					if y == 1 and x == 6:  # nav circle of 5th left
						root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) - 1 + 12) % 12]
						self._parent._parent._parent.show_message("circle of 5ths <- "+keys[selected_key]+" "+str(self._modus_names[selected_modus])+" => "+keys[root]+" "+str(self._modus_names[selected_modus]))
					if y == 1 and x == 2:  # relative scale
						if self._selected_modus == 0:
							selected_modus = self._current_minor_mode
							root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) + 3) % 12]
						elif self._selected_modus in [1, 13, 14]:
							self._current_minor_mode = selected_modus
							selected_modus = 0
							root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) - 3 + 12) % 12]
						elif self._selected_modus == 11:
							selected_modus = 12
							root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) + 3) % 12]
						elif self._selected_modus == 12:
							selected_modus = 11
							root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) - 3 + 12) % 12]
						self._parent._parent._parent.show_message("Relative scale : "+keys[root]+" "+str(self._modus_names[selected_modus]))
					if root != -1:
						self.set_selected_modus(selected_modus)
						self.set_key(root)

				if y == 1 and x == 7 and not self.is_drumrack():
					self.is_quick_scale = not self.is_quick_scale
					self._parent._parent._parent.show_message("Quick scale")
				# octave
				if y == 3:
					self._octave_index = x
					self._parent._parent._parent.show_message("octave : "+str(self._octave_index))
				# modus
				if y > 3 and not self.is_drumrack():
					self.set_selected_modus((y - 4) * 8 + x)
					self._parent._parent._parent.show_message("mode : "+str(self._modus_names[self._selected_modus]))
					

				self.update()

	def tuple_idx(self, tuple, obj):
		for i in xrange(0, len(tuple)):
			if (tuple[i] == obj):
				return i
		return(False)

	def set_osd(self, osd):
		self._osd = osd

	def _update_OSD(self):
		if self._osd != None:
			self._osd.attributes[0] = ""
			self._osd.attribute_names[0] = ""
			self._osd.attributes[1] = MUSICAL_MODES[self._selected_modus * 2]
			self._osd.attribute_names[1] = "Scale"
			self._osd.attributes[2] = KEY_NAMES[self._selected_key % 12]
			self._osd.attribute_names[2] = "Root Note"
			self._osd.attributes[3] = self._octave_index
			self._osd.attribute_names[3] = "Octave"
			self._osd.attributes[4] = " "
			self._osd.attribute_names[4] = " "
			self._osd.attributes[5] = " "
			self._osd.attribute_names[5] = " "
			self._osd.attributes[6] = " "
			self._osd.attribute_names[6] = " "
			self._osd.attributes[7] = " "
			self._osd.attribute_names[7] = " "
			self._osd.update()

	def update(self):
		if self.is_enabled():
			self._update_OSD()
			for button, (x, y) in self._matrix.iterbuttons():
				button.use_default_message()
				button.set_enabled(True)
				button.force_next_send()

			self._matrix.get_button(7, 2).set_on_off_values(LED_OFF, LED_OFF)
			self._matrix.get_button(7, 2).turn_off()

			absolute_button = self._matrix.get_button(0, 0)
			orientation_button = self._matrix.get_button(1, 0)
			quick_scale_button = self._matrix.get_button(7, 1)

			drumrack_button = self._matrix.get_button(7, 0)
			drumrack_button.set_on_off_values(RED_FULL, RED_THIRD)
			drumrack_button.force_next_send()

			chromatic_button = self._matrix.get_button(6, 0)
			chromatic_button.set_on_off_values(RED_FULL, RED_THIRD)
			chromatic_button.force_next_send()

			diatonic_button_4th = self._matrix.get_button(5, 0)
			diatonic_button_4th.set_on_off_values(RED_FULL, RED_THIRD)
			diatonic_button_4th.force_next_send()

			diatonic_button_3rd = self._matrix.get_button(4, 0)
			diatonic_button_3rd.set_on_off_values(RED_FULL, RED_THIRD)
			diatonic_button_3rd.force_next_send()

			chromatic_gtr_button = self._matrix.get_button(2, 0)
			chromatic_gtr_button.set_on_off_values(RED_FULL, RED_THIRD)
			chromatic_gtr_button.force_next_send()

			diatonic_ns_button = self._matrix.get_button(3, 0)
			diatonic_ns_button.set_on_off_values(RED_FULL, RED_THIRD)
			diatonic_ns_button.force_next_send()

			# circle of 5th nav right
			button = self._matrix.get_button(7, 2)
			button.set_on_off_values(RED_THIRD, RED_THIRD)
			button.force_next_send()
			button.turn_on()
			# circle of 5th nav left
			button = self._matrix.get_button(6, 1)
			button.set_on_off_values(RED_THIRD, RED_THIRD)
			button.force_next_send()
			button.turn_on()
			# relative scale button
			button = self._matrix.get_button(2, 1)
			button.set_on_off_values(RED_THIRD, RED_THIRD)
			button.force_next_send()
			button.turn_on()

			# mode buttons
			if self.is_drumrack():
				drumrack_button.turn_on()
				chromatic_gtr_button.turn_off()
				diatonic_ns_button.turn_off()
				chromatic_button.turn_off()
				diatonic_button_4th.turn_off()
				diatonic_button_3rd.turn_off()
				absolute_button.set_on_off_values(LED_OFF, LED_OFF)
				absolute_button.turn_off()
				orientation_button.set_on_off_values(LED_OFF, LED_OFF)
				orientation_button.turn_off()
				quick_scale_button.set_on_off_values(LED_OFF, LED_OFF)
				quick_scale_button.turn_off()
			else:
				quick_scale_button.set_on_off_values(GREEN_FULL, GREEN_THIRD)
				if self.is_quick_scale:
					quick_scale_button.turn_on()
				else:
					quick_scale_button.turn_off()
				orientation_button.set_on_off_values(AMBER_THIRD, AMBER_FULL)
				if self._presets.is_horizontal:
					orientation_button.turn_on()
				else:
					orientation_button.turn_off()

				absolute_button.set_on_off_values(AMBER_THIRD, AMBER_FULL)
				if self.is_absolute:
					absolute_button.turn_on()
				else:
					absolute_button.turn_off()

				drumrack_button.turn_off()
				if self.is_chromatic():
					if self.is_chromatic_gtr():
						chromatic_button.turn_off()
						chromatic_gtr_button.turn_on()
					else:
						chromatic_button.turn_on()
						chromatic_gtr_button.turn_off()
					diatonic_button_4th.turn_off()
					diatonic_button_3rd.turn_off()
					diatonic_ns_button.turn_off()
				else:
					chromatic_button.turn_off()
					chromatic_gtr_button.turn_off()
					if self.is_diatonic_ns():
						diatonic_button_4th.turn_off()
						diatonic_button_3rd.turn_off()
						diatonic_ns_button.turn_on()
					else:
						if self._presets.interval == 3:
							diatonic_button_4th.turn_on()
							diatonic_button_3rd.turn_off()
						else:
							diatonic_button_4th.turn_off()
							diatonic_button_3rd.turn_on()
						diatonic_ns_button.turn_off()

			# Octave
			scene_index = 3
			for track_index in range(8):
				button = self._matrix.get_button(track_index, scene_index)
				button.set_on_off_values(RED_FULL, RED_THIRD)
				if track_index == self._octave_index:
					button.turn_on()
				else:
					button.turn_off()

			if self.is_drumrack():
				# clear scales buttons
				for scene_index in range(1, 3):
					for track_index in range(8):
						button = self._matrix.get_button(track_index, scene_index)
						button.set_on_off_values(GREEN_FULL, LED_OFF)
						button.turn_off()
				for scene_index in range(4, 8):
					for track_index in range(8):
						button = self._matrix.get_button(track_index, scene_index)
						button.set_on_off_values(GREEN_FULL, LED_OFF)
						button.turn_off()
			else:
				# root note button
				scene_index = 1
				for track_index in [0, 1, 3, 4, 5]:
					button = self._matrix.get_button(track_index, scene_index)
					if track_index in [0, 1, 3, 4, 5]:
						button.set_on_off_values(AMBER_FULL, AMBER_THIRD)
					if self._selected_key % 12 == (self._index[track_index] + 1) % 12:
						button.turn_on()
					else:
						button.turn_off()

				scene_index = 2
				for track_index in range(7):
					button = self._matrix.get_button(track_index, scene_index)
					button.set_on_off_values(AMBER_FULL, AMBER_THIRD)
					if self._selected_key % 12 == self._index[track_index] % 12:
						button.turn_on()
					else:
						button.turn_off()

				# modus buttons
				for scene_index in range(4):
					for track_index in range(8):
						button = self._matrix.get_button(track_index, scene_index + 4)
						if scene_index * 8 + track_index < len(self._modus_list):
							button.set_on_off_values(GREEN_FULL, GREEN_THIRD)
							if self._selected_modus == scene_index * 8 + track_index:
								button.turn_on()
							else:
								button.turn_off()
						else:
							button.set_on_off_values(LED_OFF, LED_OFF)
							button.turn_off()
