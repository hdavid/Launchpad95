import Live
from consts import *
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from StepSequencerComponent import *
from ScaleComponent import *
from TrackControllerComponent import TrackControllerComponent
from random import randrange
import time

STEPSEQ_MODE_NOTES=1
STEPSEQ_MODE_NOTES_OCTAVES=2
STEPSEQ_MODE_NOTES_VELOCITIES=3
STEPSEQ_MODE_NOTES_LENGTHS=4

LONG_BUTTON_PRESS=1.0

# TODO :
# top scene buttons not updating on load

class MelodicNoteEditorComponent(ControlSurfaceComponent):

	def __init__(self, parent, matrix, side_buttons):
	
		ControlSurfaceComponent.__init__(self)
		self.set_enabled(False)
		self._is_velocity_shifted = False
		self._parent = parent
		
		self._clip = None
		self._notes = None
		self._playhead = None
		
		self._matrix = matrix
		self._side_buttons = side_buttons
		
		#metronome
		self.metronome_color = AMBER_FULL
		
		#other colors
		self.playing_note_color = RED_FULL
		
		#buttons
		self._matrix = None
		
		#matrix
		self.set_button_matrix(matrix)
		self._grid_buffer = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
		self._grid_back_buffer = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
		
		#clip
		self._clip = None
		self._note_cache = []
		self._force_update = True
		self._init_data()
		
		self._velocity_map = [0,30,60,80,100,115,127]
		self._length_map = [1,2,3,4,8,16,32]
		
		#time
		self._playhead = 0
		self._page = 0
		
		#notes
		self._key_indexes=[36,37,38,39,40,41,42,43]
		self._key_index_is_in_scale  = [True,False,True,True,False,True,False,True]
		self._key_index_is_root_note  = [True,False,False,False,False,False,False,False]
		
		#quantization
		self._quantization = 16
		
		#MODE
		self._mode = STEPSEQ_MODE_NOTES
		self._mode_notes_button = None
		self._mode_notes_octaves_button = None
		self._mode_notes_velocities_button = None
		self._mode_notes_lengths_button = None
		self._random_button = None
		self.set_random_button(self._side_buttons[3])
		self.set_mode_notes_lengths_button(self._side_buttons[4])
		self.set_mode_notes_octaves_button(self._side_buttons[5])
		self.set_mode_notes_velocities_button(self._side_buttons[6])
		self.set_mode_notes_button(self._side_buttons[7])
		
	def disconnect(self):
		self._parent = None
		self._matrix = None
		self._velocity_button = None
		self._mute_shift_button = None
		self._clip = None

	def _init_data(self):
		pages = 128
		self._notes = [0]*(7*pages)
		self._notes_velocities = [4]*pages
		self._notes_octaves = [2]*pages
		self._notes_lengths = [3]*pages
		
	def set_mode(self, mode):
		self._mode = mode
		self.update()
	
	def set_clip(self,clip):
		if(self._clip!=clip):
			self._init_data()
			self._clip = clip
	
	def set_note_cache(self,note_cache):
		if(self._note_cache!=note_cache):
			self._note_cache = note_cache
			#self._init_data()
			self._parse_notes()
	
	def set_playhead(self, playhead):
		self._playhead = playhead
		self._update_matrix()
		
	def set_multinote(self,x=0,y=0):
		pass
			
	@property
	def quantization(self):
		return self._quantization
		
	def set_quantization(self,quantization):
		old_quantize = self._quantization
		self._quantization = quantization
		#update loop point
		if(self._clip!=None and old_quantize != self._quantization):
			
			self._clip.loop_start = self._clip.loop_start *self._quantization /  old_quantize
			self._clip.loop_end = self._clip.loop_end * self._quantization/ old_quantize
			
		self._update_clip_notes()

	def set_diatonic(self,diatonic):
		self._diatonic = diatonic

	def set_key_indexes(self, key_indexes):
		if(self._key_indexes != key_indexes):
			self._key_indexes = key_indexes
			self._update_clip_notes()
			
			
	def set_key_index_is_in_scale(self, key_index_is_in_scale):
		self._key_index_is_in_scale = key_index_is_in_scale

	def set_key_index_is_root_note(self, key_index_is_root_note):
		self._key_index_is_root_note = key_index_is_root_note
	
	def set_playhead(self,playhead):
		self._playhead = playhead
		self._update_matrix()

	def set_page(self, page):
		self._page = page

	def _parse_notes(self):
		#clear notes
		for i in range(len(self._notes)):
			self._notes[i] = 0
		
		first_note = [True]*128
							
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
					
					#velocity
					for x in range(7):
						if note_velocity>=self._velocity_map[x]:
							self._notes_velocities[i] = x
					
					#length
					for x in range(7):
						if note_length >= self._length_map[x] *self._quantization / 4:
							self._notes_lengths[i] = x
					
					#note and octave
					found = False
					for j in range(max(7,len(self._key_indexes))):
						for octave in range(7):
							if note_key == self._key_indexes[j] + 12 * (octave-2) and not found:
								found = True
								self._notes_octaves[i] = octave
								self._notes[i*7 + j] = 1
				else:
					#note
					found = False
					for j in range(max(7,len(self._key_indexes))):
						if note_key == self._key_indexes[j] + 12 * (self._notes_octaves[i]-2) and not found:
							found = True
							self._notes[i*7 + j] = 1

		self._update_matrix()
	
	def _update_clip_notes(self):
		if self._clip != None:
			note_cache = list()
			for x in range(len(self._notes_velocities)):
				for note_index in range(7):
					if self._notes[x*7 + note_index] == 1:
						time = x * self._quantization
						velocity = self._velocity_map[self._notes_velocities[x]]
						length = self._length_map[self._notes_lengths[x]] * self._quantization / 4
						pitch = self._key_indexes[note_index] + 12 * (self._notes_octaves[x]-2)
						if(pitch>=0 and pitch<128 and velocity>=0 and velocity<128 and length>=0):
							note_cache.append( [pitch, time, length, velocity, False] )
			self._clip.select_all_notes()
			self._clip.replace_selected_notes(tuple(note_cache))
		

	def update(self, force = False):
		if force:
			self._force_update = True
		if self.is_enabled():
			self._update_mode_notes_octaves_button()
			self._update_mode_notes_lengths_button()
			self._update_mode_notes_velocities_button()
			self._update_mode_notes_button()
			self._update_random_button()
			self._update_matrix()	
	

	def request_display_page(self):
		pass
		
	def set_height(self,height):
		pass
	
#MATRIX

	def set_button_matrix(self, matrix):
		assert isinstance(matrix, (ButtonMatrixElement, type(None)))
		if (matrix != self._matrix):
			if (self._matrix != None):
				self._matrix.remove_value_listener(self._matrix_value)
			self._matrix = matrix
			if (self._matrix != None):
				self._matrix.add_value_listener(self._matrix_value)

	def _update_matrix(self): #step grid LEDs are updated here
		if self.is_enabled():
			#clear back buffer
			for x in range(8):
				for y in range(8):
					self._grid_back_buffer[x][y] = 0
			
			#update back buffer
			if self._clip != None:
				
				for x in range(8):
					has_note = False
					for y in range(7):
						if self._notes[(x+8*self._page)*7 + 6-y] == 1:
							has_note = True

					for y in range(7):
						if self._mode == STEPSEQ_MODE_NOTES:
							if self._notes[(x+8*self._page)*7 + 6-y] == 1:
								self._grid_back_buffer[x][y]=GREEN_FULL
							else:
								self._grid_back_buffer[x][y]=LED_OFF

						elif self._mode == STEPSEQ_MODE_NOTES_OCTAVES:
							if(has_note):
								if self._notes_octaves[x+8*self._page] == 6-y:
									self._grid_back_buffer[x][y]=RED_HALF
								else:
									self._grid_back_buffer[x][y]=LED_OFF
							else:
								if self._notes_octaves[x+8*self._page] == 6-y:
									self._grid_back_buffer[x][y]=RED_THIRD
								else:
									self._grid_back_buffer[x][y]=LED_OFF
									
						elif self._mode == STEPSEQ_MODE_NOTES_VELOCITIES:
							if(has_note):
								if self._notes_velocities[x+8*self._page] >= 6-y:
									self._grid_back_buffer[x][y]=RED_HALF
								else:
									self._grid_back_buffer[x][y]=LED_OFF
							else:
								if self._notes_velocities[x+8*self._page] >= 6-y:
									self._grid_back_buffer[x][y]=RED_THIRD
								else:
									self._grid_back_buffer[x][y]=LED_OFF
					
						elif self._mode == STEPSEQ_MODE_NOTES_LENGTHS:
							if(has_note):
								if self._notes_lengths[x+8*self._page] >= 6-y:
									self._grid_back_buffer[x][y]=AMBER_FULL
								else:
									self._grid_back_buffer[x][y]=LED_OFF
							else:
								if self._notes_lengths[x+8*self._page] >= 6-y:
									self._grid_back_buffer[x][y]=AMBER_THIRD
								else:
									self._grid_back_buffer[x][y]=LED_OFF
				#metronome
				if self._playhead != None:
					play_position = int(self._playhead / self.quantization)
					play_x_position = int(self._playhead / self.quantization)%8
					page = int(self._playhead / self.quantization /8)
					if self._mode == STEPSEQ_MODE_NOTES_LENGTHS:
						if page == self._page:
							self.metronome_color = RED_FULL
						else:
							self.metronome_color = RED_THIRD
					else:
						if page == self._page:
							self.metronome_color = AMBER_FULL
						else:
							self.metronome_color = AMBER_THIRD		
					self._grid_back_buffer[play_x_position][6] = self.metronome_color
				
					#playing notes
					if self._mode == STEPSEQ_MODE_NOTES:
						for y in range(7):
							if self._notes[play_position*7 + 6-y] == 1:
								if page == self._page:
									self._grid_back_buffer[play_x_position][y] = RED_FULL
								else:
									self._grid_back_buffer[play_x_position][y] = RED_THIRD
							
					
			else:
				for x in range(8):
					for y in range(7):
						self._grid_back_buffer[x][y]=LED_OFF

	
			#caching : compare back buffer to buffer and update grid. this should minimize midi traffic quite a bit.
			for x in range(8):
				for y in range(7):
					if(self._grid_back_buffer[x][y]!=self._grid_buffer[x][y] or self._force_update):
						self._grid_buffer[x][y] = self._grid_back_buffer[x][y]
						self._matrix.send_value(x, y, self._grid_buffer[x][y])
			self._force_update=False
	
	def _matrix_value(self, value, x, y, is_momentary): #matrix buttons listener
		if self.is_enabled():
			if self._clip == None:
				self._parent.create_clip()
			else:
				if ((value != 0) or (not is_momentary)) and y<7:
					#self._parent.log_message("matrix value bro !")
					if self._mode == STEPSEQ_MODE_NOTES:
						if self._notes[(x+8*self._page)*7 +6-y] == 1:
							self._notes[(x+8*self._page)*7 + 6-y] = 0
						else:
							self._notes[(x+8*self._page)*7 + 6-y] = 1
					elif self._mode == STEPSEQ_MODE_NOTES_OCTAVES:
						self._notes_octaves[x+8*self._page] = 6-y
					elif self._mode == STEPSEQ_MODE_NOTES_VELOCITIES:
						self._notes_velocities[x+8*self._page] = 6-y
					elif self._mode == STEPSEQ_MODE_NOTES_LENGTHS:
						self._notes_lengths[x+8*self._page] = 6-y
					self._update_matrix()
					self._update_clip_notes()
				

#RANDOM
	def _update_random_button(self):
		if self.is_enabled():
			if (self._random_button != None):
				if self._clip != None:
					self._random_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
					self._random_button.turn_off()
				else:
					self._random_button.set_on_off_values(LED_OFF,LED_OFF)
					self._random_button.turn_off()

	def set_random_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._random_button != button):
			if (self._random_button != None):
				self._random_button.remove_value_listener(self._random_button_value)
			self._random_button = button
			if (self._random_button != None):
				assert isinstance(button, ButtonElement)
				self._random_button.add_value_listener(self._random_button_value, identify_sender=True)
		
	def _random_button_value(self, value, sender):
		assert (self._mode_notes_button != None)
		assert (value in range(128))
		if self.is_enabled()  and self._clip != None:
			
			loop_start = int(self._clip.loop_start / self._quantization)
			loop_end = int(self._clip.loop_end / self._quantization)
			
			self._random_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
			if ((value is 0) and (sender.is_momentary())):
				self._random_button.turn_on()
				for x in range(loop_start, loop_end):
					if self._mode == STEPSEQ_MODE_NOTES:
						val2 = randrange(0,9)
						for y in range(7):
							self._notes[x*7 + 6-y] = val2 == y
					elif self._mode == STEPSEQ_MODE_NOTES_OCTAVES:
						val = randrange(2,6)
						self._notes_octaves[x] = val
					elif self._mode == STEPSEQ_MODE_NOTES_VELOCITIES:
						val = randrange(0,7)
						self._notes_velocities[x] = val
					elif self._mode == STEPSEQ_MODE_NOTES_LENGTHS:
						val = randrange(0,4)
						self._notes_lengths[x] = val
					self._update_clip_notes()
			else:
				self._random_button.turn_off()
		
# MODE
	def _update_mode_notes_button(self):
		if self.is_enabled():
			if (self._mode_notes_button != None):
				if self._clip != None:
					self._mode_notes_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
					if self._mode == STEPSEQ_MODE_NOTES:
						self._mode_notes_button.turn_on()
					else:
						self._mode_notes_button.turn_off()
				else:
					self._mode_notes_button.set_on_off_values(LED_OFF,LED_OFF)
					self._mode_notes_button.turn_off()

	def set_mode_notes_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._mode_notes_button != button):
			if (self._mode_notes_button  != None):
				self._mode_notes_button.remove_value_listener(self._mode_button_notes_value)
			self._mode_notes_button = button
			if (self._mode_notes_button  != None):
				assert isinstance(button, ButtonElement)
				self._mode_notes_button.add_value_listener(self._mode_button_notes_value, identify_sender=True)
		
	def _mode_button_notes_value(self, value, sender):
		assert (self._mode_notes_button != None)
		assert (value in range(128))
		if self.is_enabled()  and self._clip != None:
			if ((value is 0) and (sender.is_momentary())):
				self.set_mode(STEPSEQ_MODE_NOTES)
				self.update()
	
	
	
	def _update_mode_notes_octaves_button(self):
		if self.is_enabled():
			if (self._mode_notes_octaves_button != None):
				if self._clip != None:
					self._mode_notes_octaves_button.set_on_off_values(RED_FULL,RED_THIRD)
					if self._mode == STEPSEQ_MODE_NOTES_OCTAVES:
						self._mode_notes_octaves_button.turn_on()
					else:
						self._mode_notes_octaves_button.turn_off()
				else:
					self._mode_notes_octaves_button.set_on_off_values(LED_OFF,LED_OFF)
					self._mode_notes_octaves_button.turn_off()

	def set_mode_notes_octaves_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._mode_notes_octaves_button != button):
			if (self._mode_notes_octaves_button  != None):
				self._mode_notes_octaves_button.remove_value_listener(self._mode_button_notes_octaves_value)
			self._mode_notes_octaves_button = button
			if (self._mode_notes_octaves_button  != None):
				assert isinstance(button, ButtonElement)
				self._mode_notes_octaves_button.add_value_listener(self._mode_button_notes_octaves_value, identify_sender=True)
		
	def _mode_button_notes_octaves_value(self, value, sender):
		assert (self._mode_notes_octaves_button != None)
		assert (value in range(128))
		if self.is_enabled()  and self._clip != None:
			if ((value is 0) and (sender.is_momentary())):
				self.set_mode(STEPSEQ_MODE_NOTES_OCTAVES)
				self.update()

	
	
	def _update_mode_notes_velocities_button(self):
		if self.is_enabled():
			if (self._mode_notes_velocities_button != None):
				if self._clip != None:
					self._mode_notes_velocities_button.set_on_off_values(RED_FULL,RED_THIRD)
					if self._mode == STEPSEQ_MODE_NOTES_VELOCITIES:
						self._mode_notes_velocities_button.turn_on()
					else:
						self._mode_notes_velocities_button.turn_off()
				else:
					self._mode_notes_velocities_button.set_on_off_values(LED_OFF,LED_OFF)
					self._mode_notes_velocities_button.turn_off()

	def set_mode_notes_velocities_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._mode_notes_velocities_button != button):
			if (self._mode_notes_velocities_button  != None):
				self._mode_notes_velocities_button.remove_value_listener(self._mode_button_notes_velocities_value)
			self._mode_notes_velocities_button = button
			if (self._mode_notes_velocities_button  != None):
				assert isinstance(button, ButtonElement)
				self._mode_notes_velocities_button.add_value_listener(self._mode_button_notes_velocities_value, identify_sender=True)
		
	def _mode_button_notes_velocities_value(self, value, sender):
		assert (self._mode_notes_velocities_button != None)
		assert (value in range(128))
		if self.is_enabled()  and self._clip != None:
			if ((value is 0) and (sender.is_momentary())):
				self.set_mode(STEPSEQ_MODE_NOTES_VELOCITIES)
				self.update()
				
	
	
	def _update_mode_notes_lengths_button(self):
		if self.is_enabled():
			if (self._mode_notes_lengths_button != None):
				if self._clip != None:
					self._mode_notes_lengths_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
					if self._mode == STEPSEQ_MODE_NOTES_LENGTHS:
						self._mode_notes_lengths_button.turn_on()
					else:
						self._mode_notes_lengths_button.turn_off()
				else:
					self._mode_notes_lengths_button.set_on_off_values(LED_OFF,LED_OFF)
					self._mode_notes_lengths_button.turn_off()

	def set_mode_notes_lengths_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._mode_notes_lengths_button != button):
			if (self._mode_notes_lengths_button  != None):
				self._mode_notes_lengths_button.remove_value_listener(self._mode_button_notes_lengths_value)
			self._mode_notes_lengths_button = button
			if (self._mode_notes_lengths_button  != None):
				assert isinstance(button, ButtonElement)
				self._mode_notes_lengths_button.add_value_listener(self._mode_button_notes_lengths_value, identify_sender=True)
		
	def _mode_button_notes_lengths_value(self, value, sender):
		assert (self._mode_notes_lengths_button != None)
		assert (value in range(128))
		if self.is_enabled()  and self._clip != None:
			if ((value is 0) and (sender.is_momentary())):
				self.set_mode(STEPSEQ_MODE_NOTES_LENGTHS)
				self.update()			


class StepSequencerComponent2(StepSequencerComponent):

	def __init__(self, matrix, side_buttons, top_buttons, parent):
		super(StepSequencerComponent2, self).__init__(matrix, side_buttons, top_buttons, parent)
		self._new_clip_pages = 1
		self._scale_selector.set_diatonic()

	
	def _set_track_controller(self):
		self._track_controller = self.register_component(TrackControllerComponent())
		self._track_controller.set_prev_scene_button(self._top_buttons[0])
		self._track_controller.set_next_scene_button(self._top_buttons[1])
		self._track_controller.set_prev_track_button(self._top_buttons[2])
		self._track_controller.set_next_track_button(self._top_buttons[3])
		self._track_controller._parent = self
		self._track_controller._notify_parent = False
		
	def _set_note_editor(self):
		self._note_editor = self.register_component(MelodicNoteEditorComponent(self, self._matrix, self._side_buttons))

	def _set_note_selector(self):
		self._note_selector = self.register_component(NoteSelectorComponent(self,[]))
		
	def _set_loop_selector(self):
		self._loop_selector = self.register_component(LoopSelectorComponent(self, 
		[self._matrix.get_button(0,7),self._matrix.get_button(1,7),self._matrix.get_button(2,7),self._matrix.get_button(3,7),
		self._matrix.get_button(4,7),self._matrix.get_button(5,7),self._matrix.get_button(6,7),self._matrix.get_button(7,7)
		] ) )
		self.set_left_button(self._top_buttons[2])
		self.set_right_button(self._top_buttons[3])

	def update_buttons(self):
		self._update_quantization_button()
		self._update_lock_button()
		self._update_scale_selector_button()
		self._update_left_button()
		self._update_right_button()
		
		
	
	def _update_mode_button(self):
		if self.is_enabled():
			if (self._mode_button != None):
				self._mode_button.set_on_off_values(LED_OFF,LED_OFF)
				self._mode_button.turn_off()

	def _mode_button_value(self, value, sender):
		pass
		

			

		
			




