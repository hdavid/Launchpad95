from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ToggleComponent import ToggleComponent
#from _Framework.Control import PlayableControl, ButtonControl, ToggleButtonControl, control_matrix

KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CIRCLE_OF_FIFTHS = [7 * k % 12 for k in range(12)]
# KEY_CENTERS = CIRCLE_OF_FIFTHS[0:6] + CIRCLE_OF_FIFTHS[-1:5:-1]

MUSICAL_MODES = [

	'Major',			[0, 2, 4, 5, 7, 9, 11],
	'Minor',			[0, 2, 3, 5, 7, 8, 10],
	'Dorian',			[0, 2, 3, 5, 7, 9, 10],
	'Mixolydian',		[0, 2, 4, 5, 7, 9, 10],
	'Lydian',			[0, 2, 4, 6, 7, 9, 11],
	'Phrygian',			[0, 1, 3, 5, 7, 8, 10],
	'Locrian',			[0, 1, 3, 5, 6, 8, 10],
	'Diminished',		[0, 1, 3, 4, 6, 7, 9, 10],

	'Whole-half',		[0, 2, 3, 5, 6, 8, 9, 11],
	'Whole Tone',		[0, 2, 4, 6, 8, 10],
	'Minor Blues',		[0, 3, 5, 6, 7, 10],
	'Minor Pentatonic', [0, 3, 5, 7, 10],
	'Major Pentatonic', [0, 2, 4, 7, 9],
	'Harmonic Minor',	[0, 2, 3, 5, 7, 8, 11],
	'Melodic Minor',	[0, 2, 3, 5, 7, 9, 11],
	'Super Locrian',	[0, 1, 3, 4, 6, 8, 10],

	'Bhairav',			[0, 1, 4, 5, 7, 8, 11],
	'Hungarian Minor',	[0, 2, 3, 6, 7, 8, 11],
	'Minor Gypsy',		[0, 1, 4, 5, 7, 8, 10],
	'Hirojoshi',		[0, 2, 3, 7, 8],
	'In-Sen',			[0, 1, 5, 7, 10],
	'Iwato',			[0, 1, 5, 6, 10],
	'Kumoi',			[0, 2, 3, 7, 9],
	'Pelog',			[0, 1, 3, 4, 7, 8],

	'Spanish',			[0, 1, 3, 4, 5, 6, 8, 10],
	'IonEol',			[0, 2, 3, 4, 5, 7, 8, 9, 10, 11]
]

class ScaleComponent(ControlSurfaceComponent):
	
	#matrix = control_matrix(PlayableControl)

	def __init__(self, control_surface = None, enabled = False, mode = "diatonic", *a, **k):
		self._layout_set = False
		self._modus_list = [Modus(MUSICAL_MODES[v], MUSICAL_MODES[v + 1]) for v in xrange(0, len(MUSICAL_MODES), 2)]
		self._modus_names = [MUSICAL_MODES[v] for v in xrange(0, len(MUSICAL_MODES), 2)]
		self._control_surface = control_surface
		self._osd = None
		self._modus = 0
		self._key = 0
		self._octave = 3 
		self._mode = mode #chromatic, diatonic
		self._is_drumrack = False
		self._quick_scale = False
		self._is_horizontal = True
		self._is_absolute = False
		self._interval = 3
		self._matrix = None
		
		# C  D  E  F  G  A  B
		self._white_notes_index = [0, 2, 4, 5, 7, 9, 11]
		
		self._current_minor_mode = 1
		self._minor_modes = [1, 13, 14]
		
		super(ScaleComponent, self).__init__(*a, **k)
		self.set_enabled(enabled)
		
	@property
	def notes(self):
		return self.modus.scale(self._key).notes

	@property
	def modus(self):
		return self._modus_list[self._modus]

	def set_key(self, key, message = True):
		if key>=0 and key<=11:
			self._key = key % 12
			if message:
				self._control_surface.show_message(str("selected key: " + KEY_NAMES[self._key])+" "+str(self._modus_names[self._modus]))
		
	def set_octave(self, octave, message = True):
		if octave>=0 and octave<=7:
			self._octave = octave
			if message:
				self._control_surface.show_message("selected octave: " + str(octave))

	def octave_up(self, message = True):
		self.set_octave(self._octave + 1, message) 
	
	def octave_down(self, message = True):
		self.set_octave(self._octave - 1, message) 
		
	def set_modus(self, index, message = True):
		if index > -1 and index < len(self._modus_list):
			self._modus = index
			if message:
				self._control_surface.show_message(str("selected scale: " + KEY_NAMES[self._key])+" "+str(self._modus_names[self._modus]))
	
	def set_drumrack(self, drumrack):
		self._is_drumrack = drumrack
		
	#def set_matrix(self, matrix):
	#	if not matrix or not self._layout_set:
	#		self._matrix = matrix
	#		#self._matrix.set_control_element(matrix)
	#		for index, button in enumerate(self._matrix):
	#			#button.set_playable(False)
	#			self._layout_set = bool(matrix)
	#		self.update()
	def set_matrix(self, matrix):
		self._matrix = matrix
		if matrix:
			matrix.reset()
		if (matrix != self._matrix):
			if (self._matrix != None):
				self._matrix.remove_value_listener(self._matrix_pressed)
		self._matrix = matrix
		if (self._matrix != None):
			self._matrix.add_value_listener(self._matrix_pressed)
		self.update()


	
	def set_osd(self, osd):
		self._osd = osd

	def _update_OSD(self):
		if self._osd != None:
			self._osd.attributes[0] = ""
			self._osd.attribute_names[0] = ""
			self._osd.attributes[1] = MUSICAL_MODES[self._modus * 2]
			self._osd.attribute_names[1] = "Scale"
			self._osd.attributes[2] = KEY_NAMES[self._key % 12]
			self._osd.attribute_names[2] = "Root Note"
			self._osd.attributes[3] = self._octave
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
		if self.is_enabled() and self._matrix!=None:
			#self._control_surface.log_message("update scale: "+str(self._matrix))
			super(ScaleComponent, self).update()
			self._update_OSD()
			#for index, button in enumerate(self._matrix):
			for button, (col, row) in self._matrix.iterbuttons():
				#row, col = button.coordinate
				button.set_enabled(True)
				if row==0:
					if col == 0:
						if self._is_absolute:
							button.set_light("Scale.AbsoluteRoot")
						else:
							button.set_light("Scale.RelativeRoot")
					elif col == 1:
						button.set_light("DefaultButton.Disabled")
					elif col == 2:
						if not self.is_drumrack and self._mode == "chromatic_gtr":
							button.set_light("Scale.Mode.On")
						else:
							button.set_light("Scale.Mode.Off")
						button.turn_on()
					elif col == 3:
						if not self.is_drumrack and self._mode == "diatonic_ns":
							button.set_light("Scale.Mode.On")
						else:
							button.set_light("Scale.Mode.Off")
					elif col == 4:
						if not self.is_drumrack and self._mode == "diatonic_chords":
							button.set_light("Scale.Mode.On")
						else:
							button.set_light("Scale.Mode.Off")
					elif col == 5:
						if not self.is_drumrack and self._mode == "diatonic":
							button.set_light("Scale.Mode.On")
						else:
							button.set_light("Scale.Mode.Off")
					elif col == 6:
						if not self.is_drumrack and self._mode == "chromatic":
							button.set_light("Scale.Mode.On")
						else:
							button.set_light("Scale.Mode.Off")
					elif col == 7:
						if self.is_drumrack:
							button.set_light("Scale.Mode.On")
						else:
							button.set_light("Scale.Mode.Off")
				
				elif row==1:
					if self.is_drumrack:
						button.set_light("DefaultButton.Disabled")
					else:
						if col==0 or col==1 or col==3 or col==4 or col==5:
							if self._key == self._white_notes_index[col]+1:
								button.set_light("Scale.Key.On")
							else:
								 button.set_light("Scale.Key.Off")
						elif col==2:
							button.set_light("Scale.RelativeScale")
						elif col==6:
							button.set_light("Scale.CircleOfFifths")
						elif col==7:
							if self._quick_scale:
								button.set_light("Scale.QuickScale.On")
							else:
								button.set_light("Scale.QuickScale.Off")
				elif row==2:
					if self.is_drumrack:
						button.set_light("DefaultButton.Disabled")
					else:
						if col<7:
							if self._key == self._white_notes_index[col]:
								button.set_light("Scale.Key.On")
							else:
								 button.set_light("Scale.Key.Off")
						else:
							button.set_light("Scale.CircleOfFifths")
				elif row==3:
					if self._octave == col:
						button.set_light("Scale.Octave.On")
					else:
						button.set_light("Scale.Octave.Off")
				elif row==4:
					if self.is_drumrack:
						button.set_light("DefaultButton.Disabled")
					else:
						if self._modus == col:
							button.set_light("Scale.Modus.On")
						else:
							button.set_light("Scale.Modus.Off")
				elif row==5:
					if self.is_drumrack:
						button.set_light("DefaultButton.Disabled")
					else:
						if self._modus == col+8:
							button.set_light("Scale.Modus.On")
						else:
							button.set_light("Scale.Modus.Off")
				elif row==6:
					if self.is_drumrack:
						button.set_light("DefaultButton.Disabled")
					else:
						if self._modus == col+16:
							button.set_light("Scale.Modus.On")
						else:
							button.set_light("Scale.Modus.Off")
				elif row==7:
					if self.is_drumrack:
						button.set_light("DefaultButton.Disabled")
					else:
						if col+24>len(self._modus_list):
							button.set_light("DefaultButton.Disabled")
						elif self._modus == col+24:
							button.set_light("Scale.Modus.On")
						else:
							button.set_light("Scale.Modus.Off")
				#button.set_enabled(False)
				#button.update()
			
		
		
	#@matrix.pressed
	def _matrix_pressed(self, value, x, y, is_momentary):
		if self.is_enabled() and value>0:
		 	#y, x = pad.coordinate
			# modes
			if y == 0:
				if not self.is_drumrack:
					if x == 0:
						self._is_absolute = not self._is_absolute
						if self._is_absolute:
							self._control_surface.show_message("absolute root")
						else:
							self._control_surface.show_message("relative root")
					if x == 1:
						self._is_horizontal = not self._is_horizontal
				if x == 2:
					self._mode = "chromatic_gtr"
					self._is_drumrack = False
					self._interval=3
					self._is_horizontal= True
					self._control_surface.show_message("mode: chromatic gtr")
				if x == 3:
					self._mode = "diatonic_ns"
					self._is_drumrack = False
					self._interval=3
					self._is_horizontal= True
					self._control_surface.show_message("mode: diatonic not staggered")
				if x == 4:
					self._mode="diatonic_chords"
					self._is_drumrack = False
					self._interval=2
					self._is_horizontal= False
					self._control_surface.show_message("mode: diatonic vertical (chords)")
				if x == 5:
					self._mode="diatonic"
					self._is_drumrack = False
					self._interval=3
					self._is_horizontal= True
					self._control_surface.show_message("mode: diatonic")
				if x == 6:
					self._mode="chromatic"
					self._is_drumrack = False
					self._interval=3
					self._is_horizontal=True
					self._control_surface.show_message("mode: chromatic")
				if x == 7:
					self._is_drumrack = True
					self._control_surface.show_message("mode: drumrack")
		
			keys = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
			# root note
			if not self.is_drumrack:
				root = -1
				selected_key = self._key
				selected_modus = self._modus
				if y == 1 and x in[0, 1, 3, 4, 5] or y == 2 and x < 7:
					root = [0, 2, 4, 5, 7, 9, 11, 12][x]
					if y == 1:
						root = root + 1
					self._control_surface.show_message("root "+keys[root])

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
					root = CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(selected_key) + 1 + 12) % 12]
					self._control_surface.show_message("circle of 5ths -> "+keys[selected_key]+" "+str(self._modus_names[selected_modus])+" => "+keys[root]+" "+str(self._modus_names[selected_modus]))
				if y == 1 and x == 6:  # nav circle of 5th left
					root = CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(selected_key) - 1 + 12) % 12]
					self._control_surface.show_message("circle of 5ths <- "+keys[selected_key]+" "+str(self._modus_names[selected_modus])+" => "+keys[root]+" "+str(self._modus_names[selected_modus]))
				if y == 1 and x == 2:  # relative scale
					if self._modus == 0:
						selected_modus = self._current_minor_mode
						root = CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(selected_key) + 3) % 12]
					elif self._modus in [1, 13, 14]:
						self._current_minor_mode = selected_modus
						selected_modus = 0
						root = CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(selected_key) - 3 + 12) % 12]
					elif self._modus == 11:
						selected_modus = 12
						root = CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(selected_key) + 3) % 12]
					elif self._modus == 12:
						selected_modus = 11
						root = CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(selected_key) - 3 + 12) % 12]
					self._control_surface.show_message("Relative scale : "+keys[root]+" "+str(self._modus_names[selected_modus]))
				if root != -1:
					self.set_modus(selected_modus)
					self.set_key(root)

			if y == 1 and x == 7 and not self.is_drumrack:
				self._quick_scale = not self._quick_scale
				self._control_surface.show_message("Quick scale")
			# octave
			if y == 3:
				self._octave = x
				self._control_surface.show_message("octave : " + str(self._octave))
			# modus
			if y > 3 and not self.is_drumrack:
				self.set_modus((y - 4) * 8 + x)
				self._control_surface.show_message("mode : " + str(self._modus_names[self._modus]))
			self.update()
	
	#@matrix.released
	def matrix_release(self, pad):
		pass
		# selected_drum_pad = self._coordinate_to_pad_map[pad.coordinate]
		# if selected_drum_pad in self._selected_pads:
		# 	self._selected_pads.remove(selected_drum_pad)
		# 	if not self._selected_pads:
		# 		self._update_control_from_script()
		# 	self.notify_pressed_pads()
		# self._update_led_feedback()			

			
	@property
	def is_drumrack(self):
		return self._is_drumrack
		
	@property
	def is_diatonic(self):
		return not self.is_drumrack and  (self._mode == "diatonic" or self._mode == "diatonic_ns" or self._mode == "diatonic_chords")

	@property
	def is_chromatic(self):
		return not self.is_drumrack  and  (self._mode =="chromatic" or self._mode == "chromatic_gtr")

	@property
	def is_diatonic_ns(self):
		return self._mode == "diatonic_ns"
	
	@property	
	def is_chromatic_gtr(self):
		return self._mode == "chromatic_gtr"
		
	@property
	def is_quick_scale(self):
		return self._quick_scale
	
	
	def get_pattern(self):
		notes = self.notes
		# origin
		if not self._is_absolute:
			origin = 0
		elif self.is_diatonic:
			origin = 0
			for k in xrange(len(notes)):
				if notes[k] >= 12:
					origin = k - len(notes)
					break
		else:
			origin = -notes[0]

		# interval
		if self._interval == None:
			interval = 8
		elif self.is_chromatic:
			interval = [0, 2, 4, 5, 7, 9, 10, 11][self._interval]
		else:
			interval = self._interval
		
		# layout
		if self._is_horizontal:
			steps = [1, interval]
			origin = [origin, 0]
		else:
			steps = [interval, 1]
			origin = [0, origin]
		
		return MelodicPattern(
			steps = steps, 
			scale = notes, 
			origin = origin, 
			base_note = (self._octave + 1) * 12, 
			chromatic_mode = self.is_chromatic, 
			chromatic_gtr_mode = self.is_chromatic_gtr, 
			diatonic_ns_mode = self.is_diatonic_ns
		)
		

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

	def __init__(self,
	 		steps=[0, 0], 
			scale=range(12), 
			base_note=0, 
			origin=[0, 0], 
			valid_notes=xrange(128), 
			chromatic_mode=False,
			chromatic_gtr_mode=False,
			diatonic_ns_mode=False,
			*a, **k):
		super(MelodicPattern, self).__init__(*a, **k)
		self.steps = steps
		self.scale = scale
		self.base_note = base_note
		self.origin = origin
		self.valid_notes = valid_notes
		self.chromatic_mode = chromatic_mode
		self.chromatic_gtr_mode = chromatic_gtr_mode
		self.diatonic_ns_mode = diatonic_ns_mode

	class NoteInfo:

		def __init__(self, index, channel, root = False, highlight = False, in_scale = False, valid = False):
			self.index = index
			self.channel = channel
			self.root = root
			self.highlight = highlight
			self.in_scale = in_scale
			self.valid = valid

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

	def note(self, x, y):
		octave, note = self._octave_and_note(x, y)
		index = self.base_note + 12 * octave + note 
	 	root = note == self.scale[0]
		highlight =  note == self.scale[2] or note == self.scale[4]
		in_scale = note in self.scale
		valid = index in self.valid_notes
		return self.NoteInfo(
			index, 
			x,
			root = root,
			highlight = highlight,
			in_scale = in_scale,
			valid = valid
		)


