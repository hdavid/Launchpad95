#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/InstrumentComponent.py
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ModesComponent import DisplayingModesComponent, ModesComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.Util import recursive_map, forward_property
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.ScrollComponent import ScrollComponent, Scrollable
from _Framework.ButtonElement import ButtonElement
from TrackControlerComponent import TrackControlerComponent
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

	def __init__(self, steps = [0, 0], scale = range(12), base_note = 0, origin = [0, 0], valid_notes = xrange(128), base_note_color = RED_THIRD, scale_note_color = GREEN_THIRD, foreign_note_color = LED_OFF, invalid_note_color = LED_OFF, chromatic_mode = False, *a, **k):
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
		index = self.steps[0] * (self.origin[0] + x) + self.steps[1] * (self.origin[1] + y)
		scale = self._extended_scale
		scale_size = len(scale)
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
		self._is_diatonic = True
		self._is_drumrack = False
		self.is_absolute = False
		self._presets = InstrumentPresetsComponent()
		self._matrix = None
		self._octave_index = 3
		#C  D  E  F  G  A  B
		self._index = [0, 2, 4, 5, 7, 9, 11]
		self._parent = None
		
	def set_parent(self, parent):
		self._parent = parent
		
	def is_diatonic(self):
		return not self._is_drumrack and self._is_diatonic

	def is_chromatic(self):
		return not self._is_drumrack and self._is_chromatic

	def is_drumrack(self):
		return self._is_drumrack
		
	def set_diatonic(self):
	 	self._is_drumrack=False
		self._is_chromatic=False
		self._is_diatonic=True

	def set_chromatic(self):
		self._is_drumrack=False
		self._is_chromatic=True
		self._is_diatonic=False

	def set_drumrack(self,value):
		self._is_drumrack=value

	@property
	def notes(self):
		return self.modus.scale(self._selected_key).notes

	@property
	def modus(self):
		return self._modus_list[self._selected_modus]
	
	def _set_key(self, n):
		if n > -1 and n < 12:
			self._selected_key = n

	def _set_selected_modus(self, n):
		if n > -1 and n < len(self._modus_list):
			self._selected_modus = n
			#show message not working in live 9
			self._parent._parent._parent.log_message(str(self._modus_names[n]))
				
	def _set_preset(self, n):
		if n > -1 and n < 6:
				self._selected_modus = n

	def update(self):
		if self.is_enabled():
			self._update_matrix()
			
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
						
				if y==1 and x<7 and not self.is_drumrack():
					self._set_key((self._index[x]+1)%12)
				if y==2 and x<7 and not self.is_drumrack():
					self._set_key(self._index[x])
					
				if y==3:
					self._octave_index = x
					
				if y>3 and not self.is_drumrack():
					self._set_selected_modus((y-4)*8+x)
					
				self.update()
					
						
	def _update_matrix(self):
		
		if self.is_enabled():
			
			for button, (x, y) in self._matrix.iterbuttons():
				button.use_default_message()
				button.set_enabled(True)
				button.force_next_send()
				
			#display chromatic / diatonic / drumrack
			for i in range(5):
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
			
			#mode buttons
			if self.is_drumrack():
				drumrack_button.turn_on()
				chromatic_button.turn_off()
				diatonic_button.turn_off()
			else:
				drumrack_button.turn_off()
				if self.is_chromatic():
					chromatic_button.turn_on()
					diatonic_button.turn_off()
				else:
					chromatic_button.turn_off()
					diatonic_button.turn_on()	
					
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

class InstrumentControllerComponent(CompoundComponent):
	
	def __init__(self, matrix, side_buttons, top_buttons, parent):
		super(InstrumentControllerComponent, self).__init__()
		self._parent = parent
		self._matrix = None
		self._side_buttons=side_buttons
		self._remaining_buttons = []
		
		self._drum_group_device  = None
		self._octave_up_button = None
		self._octave_down_button = None
		self._scales_toggle_button = None
		self.set_scales_toggle_button(side_buttons[0])
		self.set_octave_up_button(side_buttons[2])
		self.set_octave_down_button(side_buttons[3])
		
		self.set_enabled(False)
		self.set_matrix(matrix)
		
		self._track_controller = self.register_component(TrackControlerComponent())
		self._track_controller.set_enabled(False)
		self._track_controller.set_parent(self._parent._parent)
		self._track_controller.set_prev_scene_button(top_buttons[0])
		self._track_controller.set_next_scene_button(top_buttons[1])
		self._track_controller.set_prev_track_button(top_buttons[2])
		self._track_controller.set_next_track_button(top_buttons[3])
		self._track_controller.set_undo_button(side_buttons[1])
		self._track_controller.set_stop_button(side_buttons[4])
		self._track_controller.set_play_button(side_buttons[5])
		self._track_controller.set_overdub_button(side_buttons[7])
		self._track_controller.set_solo_button(side_buttons[6])
		
		self._scales = self.register_component(ScalesComponent())
		self._scales.set_enabled(False)
		self._scales.set_parent(self)
		self._scales.set_matrix(matrix)

	def set_scales_toggle_button(self, button):
		assert isinstance(button, (ButtonElement,type(None)))
		if (self._scales_toggle_button != None):
			self._scales_toggle_button.remove_value_listener(self._scales_toggle)
		self._scales_toggle_button = button
		if (self._scales_toggle_button != None):
			self._scales_toggle_button.add_value_listener(self._scales_toggle, identify_sender=True)
			self._scales_toggle_button.turn_off()

	def set_octave_up_button(self, button=None):
		assert isinstance(button, (ButtonElement,type(None)))
		if (self._octave_up_button != None):
			self._octave_up_button.remove_value_listener(self._scroll_octave_up)
		self._octave_up_button = button
		if (self._octave_up_button != None):
			self._octave_up_button.add_value_listener(self._scroll_octave_up, identify_sender=True)
			self._octave_up_button.turn_off()
			
	def set_octave_down_button(self, button=None):
		assert isinstance(button, (ButtonElement,type(None)))
		if (self._octave_down_button != None):
			self._octave_down_button.remove_value_listener(self._scroll_octave_down)
		self._octave_down_button = button
		if (self._octave_down_button != None):
			self._octave_down_button.add_value_listener(self._scroll_octave_down, identify_sender=True)
			self._octave_down_button.turn_off()
			
	def _scales_toggle(self,value, sender):
		if self.is_enabled():
			self._scales_toggle_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
			if (value is not 0):
				self._scales.set_enabled(True)
				self._scales_toggle_button.turn_on()
				self._scales.update()
			else:
				self._scales_toggle_button.turn_off()
				self._scales.set_enabled(False)
				self.update()	
	
	def _can_scroll_octave_up(self):
		return self._scales._octave_index + self._scales._presets.octave_index_offset < 10

	def _can_scroll_octave_down(self):
		return self._scales._octave_index + self._scales._presets.octave_index_offset > -2

	def _scroll_octave_up(self,value, sender):
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value is not 0)):
				if self._can_scroll_octave_up():
					self._scales._octave_index += 1
				self.update()

	def _scroll_octave_down(self,value, sender):
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value is not 0)):
				if self._can_scroll_octave_down():
					self._scales._octave_index -= 1
				self.update()

	def update(self):
		if self.is_enabled():
			self._track_controller.set_enabled(True)
			self._update_matrix()
			
			for button in self._remaining_buttons:
				button.set_on_off_values(LED_OFF,LED_OFF)
				button.turn_off()
			
			if self._scales_toggle_button != None:
				self._scales_toggle_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
				self._scales_toggle_button.turn_off()
					
			if self._octave_up_button != None:
				self._octave_up_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				if(self._can_scroll_octave_up()):
					self._octave_up_button.turn_on()
				else:
					self._octave_up_button.turn_off()
					
			if self._octave_down_button != None:
				self._octave_down_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
				if(self._can_scroll_octave_down()):
					self._octave_down_button.turn_on()
				else:
					self._octave_down_button.turn_off()
		
	def set_matrix(self, matrix):
		self._matrix = matrix
		#self._on_matrix_value.subject = matrix
		if matrix:
			matrix.reset()
		self._update_matrix()
		
	def on_selected_track_changed(self):
		self._get_drumrack_device()
		if self._drum_group_device != None:
			self._scales.set_drumrack(True)
		else:
			self._scales.set_drumrack(False)
		self.update()
	
	def _get_drumrack_device(self):
		if self.song().view.selected_track != None:
			track = self.song().view.selected_track
			if(track.devices != None and len(track.devices)>0):
				device = track.devices[0];
				if(device.can_have_drum_pads and device.has_drum_pads):
					self._drum_group_device  = device
				else:
					self._drum_group_device  = None
			else:
				self._drum_group_device  = None
		else:
			self._drum_group_device  = None
		
	def _update_matrix(self):
			
		if not self.is_enabled() or not self._matrix or self._scales.is_enabled():
			#self._parent._parent.set_controlled_track(None)
			self._parent._parent.set_feedback_channels([])
			pass
		else:
			
			BASE_CHANNEL = 11
			FEEDBACK_CHANNELS = [11,12,13]
			NON_FEEDBACK_CHANNEL = 14
			self._parent._parent.set_feedback_channels(FEEDBACK_CHANNELS)
			self._parent._parent.set_controlled_track(self.song().view.selected_track)
			
			# create array to keep last channel used for note.
			note_channel = range(128)
			for i in range(128):
				note_channel[i]=BASE_CHANNEL
				
			#select drumrack device
			self._get_drumrack_device()
			
			if self._scales.is_drumrack() and not self._scales._is_diatonic and not self._scales._is_chromatic:
				if self._drum_group_device!=None:
					self._scales.set_drumrack(True)
				else:
					self._scales.set_diatonic()
				
			for button, (x, y) in self._matrix.iterbuttons():
				button.use_default_message()
				button.set_channel(NON_FEEDBACK_CHANNEL)
				button.force_next_send()

			i=0
			for button in self._side_buttons:
					button.use_default_message()
					#button.turn_off()
					button.set_channel(NON_FEEDBACK_CHANNEL)
					button.set_enabled(True)
					button.set_identifier(120+i)
					button.force_next_send()
					i=i+1
					
			if self._scales.is_drumrack():

				for button, (x, y) in self._matrix.iterbuttons():
					if button:
						note = 0
						if(x<4):
							note = 12 * self._scales._octave_index + x + 4 * (7-y)
						else:
							note = 12 * self._scales._octave_index + 32 + x-4 + 4 * (7-y)
						if note<128 and note >=0:
							if self._drum_group_device != None and self._drum_group_device.can_have_drum_pads and self._drum_group_device.has_drum_pads and self._drum_group_device.drum_pads[note].chains:
								button.set_on_off_values(RED_FULL, GREEN_THIRD)
								button.set_enabled(False)
								button.set_channel(BASE_CHANNEL)
								button.set_identifier(note)
								button.force_next_send()
							else:
								button.set_on_off_values(GREEN_FULL, LED_OFF)
								button.set_enabled(False)
								button.set_channel(BASE_CHANNEL)
								button.set_identifier(note)
								button.force_next_send()
						else:
							button.set_on_off_values(GREEN_FULL, LED_OFF)
							button.set_enabled(True)
							button.set_channel(NON_FEEDBACK_CHANNEL)
							button.force_next_send()
						button.turn_off()
											
			else:
				interval = self._scales._presets.interval
				pattern = self._get_pattern(interval)
				max_j = self._matrix.width() - 1
				for button, (i, j) in self._matrix.iterbuttons():
					if button:
						note_info = pattern.note(i, max_j - j)
						if note_info.index != None:
							button.set_on_off_values(RED_FULL, note_info.color)
							button.set_enabled(False)
							button.set_channel(note_channel[note_info.index])
							button.set_identifier(note_info.index)
							button.force_next_send()
							note_channel[note_info.index]=note_channel[note_info.index]+1
						else:
							button.set_channel(NON_FEEDBACK_CHANNEL)
							button.force_next_send()
							button.set_light(note_info.color)
							button.set_enabled(True)
						button.turn_off()
							
			self._parent._config_button.send_value(32, force_send=True)
	
	def _get_pattern(self, interval):
		if(self._scales.is_drumrack()):
			pass
		else:	
			notes = self._scales.notes
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
			if interval == None:
				interval = 8
			elif not self._scales.is_diatonic():
				interval = [0,2,4,5,7,9,10,11][interval]
			if self._scales._presets.is_horizontal:
				steps = [1, interval]
				origin = [origin, 0]
			else:
				steps = [interval, 1]
				origin = [0, origin]
			return MelodicPattern(steps=steps, scale=notes, origin=origin, base_note=self._scales._octave_index * 12, chromatic_mode=self._scales.is_chromatic())