#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/InstrumentComponent.py
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ModesComponent import DisplayingModesComponent, ModesComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.Util import recursive_map, forward_property
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.ScrollComponent import ScrollComponent, Scrollable
from _Framework.ButtonElement import ButtonElement
from TrackControllerComponent import TrackControllerComponent
from consts import *

NOTE_NAMES = ('C', 'D\x1b', 'D', 'E\x1b', 'E', 'F', 'G\x1b', 'G', 'A\x1b', 'A', 'B\x1b', 'B')
#CIRCLE_OF_FIFTHS = [ 7 * k % 12 for k in range(12) ]
#KEY_CENTERS = CIRCLE_OF_FIFTHS[0:6] + CIRCLE_OF_FIFTHS[-1:5:-1]


class InstrumentPresetsComponent():
	
	def __init__(self, *a, **k):
		self.octave_index_offset = 0
		self.is_horizontal = True
		self.interval = 3
		self.mode = 'scale_p4_vertical'

	def _set_scale_mode(self, octave_index_offset, is_horizontal, interval, mode):
		self.octave_index_offset = octave_index_offset
		self.is_horizontal = is_horizontal
		self.interval = interval
		self.mode = mode
 	
	def set_orientation(self, orientation):
		if orientation == 'vertical':
			if mode==0 or mode=='scale_p4_vertical' or mode==3 or mode=='scale_p4_horizontal': #4th ^
				self._set_scale_mode(0, True, 3, 'scale_p4_vertical')
			if mode==1 or mode=='scale_m3_vertical' or mode==4 or mode=='scale_m3_horizontal': #3rd ^
				self._set_scale_mode(0, True, 2, 'scale_m3_vertical')
			if mode==2 or mode=='scale_m6_vertical' or mode==5 or mode=='scale_m6_horizontal':#sequent ^
				self._set_scale_mode(-2, True, None, 'scale_m6_vertical')
		else:
			if mode==0 or mode=='scale_p4_vertical' or mode==3 or mode=='scale_p4_horizontal': #4th ^
				self._set_scale_mode(0, False, 3, 'scale_p4_horizontal')
			if mode==1 or mode=='scale_m3_vertical' or mode==4 or mode=='scale_m3_horizontal': #3rd ^
				self._set_scale_mode(0, False, 2, 'scale_m3_horizontal')
			if mode==2 or mode=='scale_m6_vertical' or mode==5 or mode=='scale_m6_horizontal':#sequent ^
				self._set_scale_mode(-2, False, None, 'scale_m6_horizontal')
	
	def set_interval(self, interval):
		if interval == 4:	
			if mode==0 or mode=='scale_p4_vertical' or mode==1 or mode=='scale_m3_vertical' or mode==2 or mode=='scale_m6_vertical': 
				self._set_scale_mode(0, True, 3, 'scale_p4_vertical')
			if mode==3 or mode=='scale_p4_horizontal' or mode==4 or mode=='scale_m3_horizontal' or mode==3 or mode=='scale_p4_horizontal':
				self._set_scale_mode(0, False, 3, 'scale_p4_horizontal')
		if interval == 3:
			if mode==0 or mode=='scale_p4_vertical' or mode==1 or mode=='scale_m3_vertical' or mode==2 or mode=='scale_m6_vertical': 
				self._set_scale_mode(0, True, 2, 'scale_m3_vertical')
			if mode==3 or mode=='scale_p4_horizontal' or mode==4 or mode=='scale_m3_horizontal' or mode==3 or mode=='scale_p4_horizontal':
				self._set_scale_mode(0, False, 2, 'scale_m3_horizontal')
		if interval == 6:
			if mode==0 or mode=='scale_p4_vertical' or mode==1 or mode=='scale_m3_vertical' or mode==2 or mode=='scale_m6_vertical': 
				self._set_scale_mode(-2, True, None, 'scale_m6_vertical')
			if mode==3 or mode=='scale_p4_horizontal' or mode==4 or mode=='scale_m3_horizontal' or mode==3 or mode=='scale_p4_horizontal':
				self._set_scale_mode(-2, False, None, 'scale_m6_horizontal')

	def set_mode(self, mode):
		if mode==0 or mode=='scale_p4_vertical': #4th ^
			self._set_scale_mode(0, True, 3, 'scale_p4_vertical')
		if mode==1 or mode=='scale_m3_vertical': #3rd ^
			self._set_scale_mode(0, True, 2, 'scale_m3_vertical')
		if mode==2 or mode=='scale_m6_vertical':#sequent ^
			self._set_scale_mode(-2, True, None, 'scale_m6_vertical')
		if mode==3 or mode=='scale_p4_horizontal': #4th >
			self._set_scale_mode(0, False, 3, 'scale_p4_horizontal')
		if mode==4 or mode=='scale_m3_horizontal': #3rd >
			self._set_scale_mode(0, False, 2, 'scale_m3_horizontal')
		if mode==5 or mode=='scale_m6_horizontal':#sequent >
			self._set_scale_mode(-2, False, None, 'scale_m6_horizontal')
		
class Scale(object):

	def __init__(self, name, notes, *a, **k):
		super(Scale, self).__init__(*a, **k)
		self.name = name
		self.notes = notes

class Modus(Scale):

	def __init__(self, *a, **k):
		super(Modus, self).__init__(*a, **k)

	def scale(self, base_note):
		return Scale(NOTE_NAMES[base_note], [ base_note + x for x in self.notes ])

	def scales(self, base_notes):
		return [ self.scale(b) for b in base_notes ]


class MelodicPattern(object):

	def __init__(self, steps = [0, 0], scale = range(12), base_note = 0, origin = [0, 0], valid_notes = xrange(128), base_note_color = GREEN_HALF, scale_note_color = AMBER_THIRD, foreign_note_color = LED_OFF, invalid_note_color = LED_OFF, chromatic_mode = False, chromatic_gtr_mode = False, diatonic_ns_mode = False, *a, **k):
		super(MelodicPattern, self).__init__(*a, **k)
		self.steps = steps
		self.scale = scale
		self.base_note = base_note
		self.origin = origin
		self.valid_notes = valid_notes
		self.base_note_color = base_note_color
		self.scale_note_color = scale_note_color
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
		elif note in self.scale:
			return self.scale_note_color
		else:
			return self.foreign_note_color

	def note(self, x, y):
		octave, note = self._octave_and_note(x, y)
		index = 12 * octave + note + self.base_note
		if index in self.valid_notes:
			return self.NoteInfo(index, x , self._color_for_note(note))
		else:
			return self.NoteInfo(None, x , self.invalid_note_color)

class ScalesComponent(ControlSurfaceComponent):
	
	def __init__(self, *a, **k):
		super(ScalesComponent, self).__init__(*a, **k)
		self._modus_list = [ Modus(MUSICAL_MODES[k], MUSICAL_MODES[k + 1]) for k in xrange(0, len(MUSICAL_MODES), 2) ]
		self._modus_names = [ MUSICAL_MODES[k] for k in xrange(0, len(MUSICAL_MODES), 2) ]
		self._selected_modus = 0
		self._selected_key = 0
		self._is_chromatic = False
		self._is_chromatic_gtr = False #variable for chromatic guitar mode
		self._is_diatonic = True
		self._is_diatonic_ns = False  #variable for diatonic non-staggered mode
		self._is_drumrack = False
		self.is_absolute = False
		self.base_note_color = AMBER_THIRD
		self.scale_note_color = GREEN_THIRD
		self._presets = InstrumentPresetsComponent()
		self._matrix = None
		self._octave_index = 3
		#C  D  E  F  G  A  B
		self._index = [0, 2, 4, 5, 7, 9, 11]
		self._parent = None
		
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
		
	def set_diatonic(self):
	 	self._is_drumrack=False
		self._is_chromatic=False
		self._is_chromatic_gtr=False
		self._is_diatonic=True
		self._is_diatonic_ns=False
		
	def set_diatonic_ns(self):
		self._is_drumrack=False
		self._is_chromatic=False
		self._is_chromatic_gtr=False
		self._is_diatonic=False
		self._is_diatonic_ns=True

	def set_chromatic(self):
		self._is_drumrack=False
		self._is_chromatic=True
		self._is_chromatic_gtr=False
		self._is_diatonic=False
		self._is_diatonic_ns=False
		
	def set_chromatic_gtr(self):
		self._is_drumrack=False
		self._is_chromatic=False
		self._is_chromatic_gtr=True
		self._is_diatonic=False
		self._is_diatonic_ns=False

	def set_drumrack(self,value):
		self._is_drumrack=value

	@property
	def notes(self):
		return self.modus.scale(self._selected_key).notes

	@property
	def modus(self):
		return self._modus_list[self._selected_modus]
	
	def set_key(self, n):
		self._selected_key = n%12

	def set_octave_index(self, n):
		self._octave_index = n

	def _set_selected_modus(self, n):
		if n > -1 and n < len(self._modus_list):
			self._selected_modus = n
			#show message not working in live 9
			if self._parent != None:
				self._parent._parent._parent.log_message(str(self._modus_names[n]))
				
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
			
	def _matrix_value(self, value, x, y, is_momentary): #matrix buttons listener
		if self.is_enabled():
			if ((value != 0) or (not is_momentary)):
				
				if y==0:
					if x==7:
						self.set_drumrack(True)
					if x==6:
						self.set_chromatic()
					if x==5:
						self.set_diatonic()
					if x==4:
						self.set_chromatic_gtr()
					if x==3:
						self.set_diatonic_ns()
				
						
				if y==1 and x<7 and not self.is_drumrack():
					self.set_key((self._index[x]+1)%12)
				if y==2 and x<7 and not self.is_drumrack():
					self.set_key(self._index[x])
					
				if y==3:
					self._octave_index = x
					
				if y>3 and not self.is_drumrack():
					self._set_selected_modus((y-4)*8+x)
					
				self.update()			
						
	def update(self):
		if self.is_enabled():
			
			for button, (x, y) in self._matrix.iterbuttons():
				button.use_default_message()
				button.set_enabled(True)
				button.force_next_send()
				
			#display chromatic / diatonic / drumrack
			for i in range(3):
				self._matrix.get_button(i, 0).set_on_off_values(LED_OFF,LED_OFF)
				self._matrix.get_button(i, 0).turn_off()
			
			self._matrix.get_button(7, 1).set_on_off_values(LED_OFF,LED_OFF)
			self._matrix.get_button(7, 1).turn_on()	
			self._matrix.get_button(7, 2).set_on_off_values(LED_OFF,LED_OFF)
			self._matrix.get_button(7, 2).turn_off()
			
			drumrack_button  = self._matrix.get_button(7, 0)  
			drumrack_button.set_on_off_values(RED_FULL,RED_THIRD)
			drumrack_button.force_next_send()
			
			chromatic_button  = self._matrix.get_button(6, 0)
			chromatic_button.set_on_off_values(RED_FULL,RED_THIRD)
			chromatic_button.force_next_send()
			
			diatonic_button  = self._matrix.get_button(5, 0)
			diatonic_button.set_on_off_values(RED_FULL,RED_THIRD)
			diatonic_button.force_next_send()
			
			chromatic_gtr_button  = self._matrix.get_button(4, 0)
			chromatic_gtr_button.set_on_off_values(RED_FULL,RED_THIRD)
			chromatic_gtr_button.force_next_send()
			
			diatonic_ns_button  = self._matrix.get_button(3, 0)
			diatonic_ns_button.set_on_off_values(RED_FULL,RED_THIRD)
			diatonic_ns_button.force_next_send()
			
			
			#mode buttons
			if self.is_drumrack():
				drumrack_button.turn_on()
				chromatic_gtr_button.turn_off()
				diatonic_ns_button.turn_off()
				chromatic_button.turn_off()
				diatonic_button.turn_off()
			else:
				drumrack_button.turn_off()
				if self.is_chromatic():
					if self.is_chromatic_gtr():
						chromatic_button.turn_off()
						chromatic_gtr_button.turn_on()
					else:
						chromatic_button.turn_on()
						chromatic_gtr_button.turn_off()
					diatonic_button.turn_off()
					diatonic_ns_button.turn_off()
				else:
					chromatic_button.turn_off()
					chromatic_gtr_button.turn_off()
					if self.is_diatonic_ns():
						diatonic_button.turn_off()
						diatonic_ns_button.turn_on()
					else:
						diatonic_button.turn_on()
						diatonic_ns_button.turn_off()
				
			#Octave
			scene_index=3		
			for track_index in range(8):
				button  = self._matrix.get_button(track_index, scene_index)
				button.set_on_off_values(RED_FULL,RED_THIRD)
				if track_index==self._octave_index:
					button.turn_on()
				else:
					button.turn_off()
					
			if self.is_drumrack():
				#clear scales buttons
				for scene_index in range(1,3):
					for track_index in range(8):
						button = self._matrix.get_button(track_index, scene_index)
						button.set_on_off_values(GREEN_FULL,LED_OFF)
						button.turn_off()
				for scene_index in range(4,8):
					for track_index in range(8):
						button = self._matrix.get_button(track_index, scene_index)
						button.set_on_off_values(GREEN_FULL,LED_OFF)
						button.turn_off()
			else:
				#root note button
				scene_index=1
				for track_index in range(7):
					button  = self._matrix.get_button(track_index, scene_index)
					if track_index in [0,1,3,4,5]:
						button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
					else:
						button.set_on_off_values(LED_OFF,LED_OFF)
					if self._selected_key%12==(self._index[track_index]+1)%12:
						button.turn_on()
					else:
						button.turn_off()
				
				scene_index=2
				for track_index in range(7):
					button  = self._matrix.get_button(track_index, scene_index)
					button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
					if self._selected_key%12==self._index[track_index]%12:
						button.turn_on()
					else:
						button.turn_off()
						
				#modus buttons
				for scene_index in range(4):		
					for track_index in range(8):
						button  = self._matrix.get_button(track_index, scene_index+4)
						if scene_index*8+track_index< len(self._modus_list):
							button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
							if  self._selected_modus==scene_index*8+track_index:
								button.turn_on()
							else:
								button.turn_off()
						else:
							button.set_on_off_values(LED_OFF,LED_OFF)
							button.turn_off()
						

