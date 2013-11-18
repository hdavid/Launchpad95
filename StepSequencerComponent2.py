import Live
from consts import *
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.SessionComponent import SessionComponent
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from NoteEditorComponent import NoteEditorComponent
from ScaleComponent import *
from TrackControllerComponent import TrackControllerComponent
import time

#quantization button colours. this must remain of length 4.
QUANTIZATION_MAP = [1,0.5,0.25,0.125]#1/4 1/8 1/16 1/32
QUANTIZATION_COLOR_MAP = [LED_OFF,AMBER_THIRD,AMBER_HALF,AMBER_FULL]

STEPSEQ_MODE_COMBINED=1
STEPSEQ_MODE_MULTINOTE=2
STEPSEQ_MODE_SCALE_EDIT=3

LONG_BUTTON_PRESS=0.500

class NoteSelectorComponent(ControlSurfaceComponent):

	def __init__(self, parent, offset_buttons):
		ControlSurfaceComponent.__init__(self)	
		self.set_enabled(False)
		self._parent = parent

		self._root_note = 36
		self._offset = 0
		self._key = 0
		self._scale = [0,2,4,5,7,9,11,12]
		
		self._up_button = None
		self._down_button = None

		self._offset_buttons=offset_buttons
		self._enable_offset_button = True
		#cache to optimise display for offset buttons minimizing midi traffic
		self._cache = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
		for button in self._offset_buttons :
			assert isinstance(button, ButtonElement)	
			button.remove_value_listener(self.note_offset_button_value)
			button.add_value_listener(self.note_offset_button_value, identify_sender=True)
	
	@property
	def _clip(self):
		return self._parent._clip

	@property
	def _mode(self):
		return self._parent._mode
	
	@property
	def _is_shifted(self):
		return self._parent._is_shifted
	
	@property
	def _quantization(self):
		return self._parent._quantization

	@property
	def _drum_group_device(self):
		return self._parent._drum_group_device
	
	@property
	def _playhead(self):
		return self._parent._playhead

	@property
	def is_drumrack(self):
		return self._parent._scales.is_drumrack() and self._drum_group_device != None
		
	@property
	def is_chromatic(self):
			return self._parent._scales.is_chromatic()
			
	@property
	def is_diatonic(self):
		return self._parent._scales.is_diatonic()

	#DOWN Button
	def _update_down_button(self):
		if self.is_enabled():
			if (self._down_button != None):
				if self._clip == None:
					self._down_button.set_on_off_values(LED_OFF,LED_OFF)
					self._down_button.turn_off()
				else:
					self._down_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
					if not self._is_shifted and self._mode==STEPSEQ_MODE_MULTINOTE or self._is_shifted and self._mode==STEPSEQ_MODE_COMBINED:
						if self.can_scroll_down():
							self._down_button.turn_on()
						else:
							self._down_button.turn_off()
					else:
						if self.can_page_down():
							self._down_button.turn_on()
						else:
							self._down_button.turn_off()

	def set_down_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._down_button != button):
			if (self._down_button  != None):
				self._down_button.remove_value_listener(self._down_button_value)
			self._down_button = button
			if (self._down_button  != None):
				assert isinstance(button, ButtonElement)
				self._down_button.add_value_listener(self._down_button_value, identify_sender=True)
			self._update_down_button()

	def _down_button_value(self, value, sender):
		assert (self._down_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if ((value is not 0) or (not sender.is_momentary())):
				if not self._is_shifted and self._mode==STEPSEQ_MODE_MULTINOTE or self._is_shifted and self._mode==STEPSEQ_MODE_COMBINED:
					self.scroll_down()
				else:
					self.page_down()
				self._parent.update()
		
	#UP button
	def _update_up_button(self):
		if self.is_enabled():
			if (self._up_button != None):
				if self._clip == None:
					self._up_button.set_on_off_values(LED_OFF,LED_OFF)
					self._up_button.turn_off()
				else:
					self._up_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
					if not self._is_shifted and self._mode==STEPSEQ_MODE_MULTINOTE or self._is_shifted and self._mode==STEPSEQ_MODE_COMBINED:
						if self.can_scroll_up():
							self._up_button.turn_on()
						else:
							self._up_button.turn_off()
					else:
						if self.can_page_up():
							self._up_button.turn_on()
						else:
							self._up_button.turn_off()

	def set_up_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._up_button != button):
			if (self._up_button  != None):
				self._up_button.remove_value_listener(self._up_button_value)
			self._up_button = button
			if (self._up_button  != None):
				assert isinstance(button, ButtonElement)
				self._up_button.add_value_listener(self._up_button_value, identify_sender=True)
			self._update_up_button()

	def _up_button_value(self, value, sender):
		assert (self._up_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if ((value is not 0) or (not sender.is_momentary())):
				if not self._is_shifted and self._mode==STEPSEQ_MODE_MULTINOTE or self._is_shifted and self._mode==STEPSEQ_MODE_COMBINED:
					self.scroll_up()
				else:
					self.page_up()
				self._parent.update()

	#Note Offeset Buttons
	def note_offset_button_value(self, value, sender):
		if self.is_enabled() and value>0 and self._enable_offset_button:
			if self._is_shifted:
				index = index_of(self._offset_buttons,sender)
				self._parent._note_editor.mute_lane(self._root_note+index)
			else:
				self._offset = index_of(self._offset_buttons,sender)
				if self.is_drumrack:
					self._drum_group_device.view.selected_drum_pad=self._drum_group_device.drum_pads[self.selected_note]
				self.update()
				self._set_note_editor_notes()
				self._parent._note_editor.update()
				
	def _set_note_editor_notes(self):
		keys = [0,0,0,0,0,0,0,0]
		key_is_root_note = [False,False,False,False,False,False,False,False]
		key_is_in_scale = [False,False,False,False,False,False,False,False]
		if self.is_drumrack:
			for i in range(8):
				keys[i] = self.selected_note+i
				key_is_root_note[i] = (keys[i]+12+16)%16==0
				key_is_in_scale[i] = (keys[i]+12+16)%4==0
		elif self.is_diatonic:
			self._scale_length=len(self._scale)
			idx = index_of(self._scale,self._offset)
			if(idx == -1):
				self._parent._parent._parent.log_message("not found : "+ str(self._offset) + " in "+str(self._scale))
				for i in range(8):
					keys[i] = self._root_note+self._offset+i
			else:
				for i in range(8):
					keys[i] = self._root_note+self._scale[(i+idx)%self._scale_length] + ((i+idx)/self._scale_length)*12
					key_is_root_note[i] = (keys[i]+12)%12==self._key
					key_is_in_scale[i] = True
		else:
			for i in range(8):
				keys[i] = self.selected_note+i		
				key_is_root_note[i] = (keys[i]+12)%12==self._key
				key_is_in_scale[i] = (keys[i]-self._key+12)%12 in self._scale

		self._parent._note_editor.set_key_indexes(keys)
		self._parent._note_editor.set_key_index_is_in_scale(key_is_in_scale)
		self._parent._note_editor.set_key_index_is_root_note(key_is_root_note)
			
	def update_notes(self):
		self.update()
			
	def update(self):
		if self.is_enabled():
			self._update_up_button()
			self._update_down_button()
			self.update_matrix()
			
	def update_matrix(self):
		if self._enable_offset_button:
			for i in range(16):
				if self._clip == None:
					self._offset_buttons[i].set_on_off_values(AMBER_FULL,LED_OFF)
					self._offset_buttons[i].turn_off()
				else:
					note = self._root_note + i
					#self._parent.log_message(str(self._playhead)+ " "+ str(note))
					if self.note_is_playing(self._playhead, note):
						self._offset_buttons[i].set_on_off_values(RED_FULL,RED_FULL)
					else:
						if self.is_drumrack:
							if self._drum_group_device.drum_pads[note].chains:
								self._offset_buttons[i].set_on_off_values(GREEN_FULL,GREEN_THIRD)
							else:
								self._offset_buttons[i].set_on_off_values(AMBER_FULL,LED_OFF)
						else:
							if self._scale!=None and i%12 in self._scale:
								self._offset_buttons[i].set_on_off_values(AMBER_FULL,AMBER_THIRD)
							else:
								self._offset_buttons[i].set_on_off_values(GREEN_FULL,GREEN_THIRD)

					if self.selected_note==note :
						if self._cache[i]!=self._offset_buttons[i]._on_value:
							self._offset_buttons[i].turn_on()
							self._cache[i]=self._offset_buttons[i]._on_value
					else:
						if self._cache[i]!=self._offset_buttons[i]._off_value:
							self._offset_buttons[i].turn_off()
							self._cache[i]=self._offset_buttons[i]._off_value
							
	def set_enabled(self, enabled):
		if enabled:
			self._cache = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
		ControlSurfaceComponent.set_enabled(self,enabled)
			
	def set_scale(self,scale,key=-1):
		if key != -1:
			self._key = key
		self._scale = scale
		#relativise scale
		for i in range(len(self._scale)):
			self._scale[i]=self._scale[i]-self._key
	
	def note_is_playing(self,clip,midi_note):
		if self._clip != None and self._clip.is_playing:
			for note in self._parent._note_editor._clip_notes:
				note_key = note[0] #key: 0-127 MIDI note #
				note_position = note[1]
				note_length = note[2]
				note_velocity = note[3]
				note_muted = note[4]
				#self._parent._parent.log_message("pos:"+str(note_position)+ " length:"+str(note_length)+ " head:"+str( self._playhead))
				if midi_note == note_key and note_position <= self._playhead and note_position + note_length >= self._playhead and not note_muted:
					return True
		return False

					
	def scroll_down(self):
		self.move(-1)

	def scroll_up(self):
		self.move(1)

	def page_down(self):
		if self.is_drumrack:
			self.move(-16)
		else:
			self.move(-12)

	def page_up(self):
		if self.is_drumrack:
			self.move(16)
		else:
			self.move(12)

	def can_scroll_down(self):
		return self.can_move(-1)

	def can_scroll_up(self):
		return self.can_move(1)

	def can_page_down(self):
		if self.is_drumrack:
			return self.can_move(-16)
		else:
			return self.can_move(-12)

	def can_page_up(self):
		if self.is_drumrack:
			return self.can_move(16)
		else:
			return self.can_move(12)

	def can_move(self, steps):
		return self.selected_note+steps>=0 and self.selected_note+steps<128

	def move(self, steps):
		if self.can_move(steps):
			if self.is_diatonic:
				#find the next note in scale in that direction
				oct = 0
				if steps > 0:
					while self._offset+steps>=12:
						steps = steps - 12
						oct = oct +1
					while steps!=0 and self._offset+steps not in self._scale:
						steps = steps +1
						while self._offset+steps>12:
							steps = steps - 12
							oct = oct +1
				elif steps < 0:
					while self._offset+steps<0:
						steps = steps + 12
						oct = oct -1
					while steps!=0 and self._offset+steps not in self._scale:
						steps = steps - 1	
						if self._offset+steps<0:
							steps = steps + 12
							oct = oct -1
								
				idx = index_of(self._scale, self._offset+steps)
				self.set_selected_note(self._root_note + oct * 12 + self._scale[idx])
			else:
				self.set_selected_note(self.selected_note + steps)
			
	def set_selected_note(self, root):
		if self.is_drumrack:
			self._root_note = ((root-4)/16)*16+4
			self._offset = (root+12)%16
		else:
			self._root_note = ((root-self._key)/12)*12+self._key
			self._offset = (root+12-self._key)%12
		self.update()
		self._set_note_editor_notes()
		
	def set_key(self, key):
		self._key = key
		
	def note_is_available(self,key):
		if self.is_drumrack:
			if self._drum_group_device.drum_pads[key].chains:
				return True
			else: 
				return False
		else:
			for note in scale:
				if key%12 == (self.root_note+note)%12:
					return True
				else:
					return False

	def note_is_used(self,key):
		if clip != None:
			for note in self._clip_notes:
				if note[0]==key: #key: 0-127 MIDI note #
					return True
		return False
	
	@property
	def selected_note(self):
		return self._root_note + self._offset




class LoopSelectorComponent(ControlSurfaceComponent):

	def __init__(self, parent, buttons):
		ControlSurfaceComponent.__init__(self)
		self.set_enabled(False)
		self._parent = parent
		
		self._loop_end = 0
		self._loop_start = 0

		self._blocksize = 8
		self._block = 0
		self._last_button = -1
		self._last_button_time = time.time()
		#
		self._loop_point1 = -1
		self._loop_point2 = -1
		
		self._buttons = buttons
		self._cache = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
		for button in self._buttons :
			assert isinstance(button, ButtonElement)
			button.remove_value_listener(self._loop_button_value)
			button.add_value_listener(self._loop_button_value, identify_sender=True)

	def disconnect(self):
		self._top_buttons = None

	@property
	def _number_of_lines_per_note(self):
		if self._mode == STEPSEQ_MODE_MULTINOTE:
			return self._parent._number_of_lines_per_note
		else: 
			return 1
			
	@property
	def _clip(self):
		return self._parent._clip
		
	@property
	def _mode(self):
		return self._parent._mode
	
	@property
	def _is_shifted(self):
		return self._parent._is_shifted
		
	@property
	def _is_velocity_shifted(self):
		return self._parent._note_editor._is_velocity_shifted
	
	@property
	def _quantization(self):
		return self._parent._quantization

	@property
	def _playhead(self):
		return self._parent._playhead

	@property
	def block(self):
		return self._block
	
	def set_blocksize(self,blocksize):
		self._blocksize=blocksize
			
	def set_enabled(self, enabled):
		if enabled:
			#clear cache
			self._cache = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
		ControlSurfaceComponent.set_enabled(self,enabled)	
	
	def _get_clip_loop(self):
		if self._clip!=None: 
			self._loop_start = self._clip.loop_start
			self._loop_end = self._clip.loop_end
		else:
			self._loop_start = 0
			self._loop_end = 0
		
	def set_clip_loop(self, start, end):
		if self._clip != None:
			self._loop_end = end
			self._loop_start = start
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
			self.update()


	def _loop_button_value(self, value, sender):
		if self.is_enabled():
			x = index_of(self._buttons,sender)
			if value>0:
				if self._loop_point1==-1:
					self._loop_point1 = x
				elif self._loop_point2==-1:
					self._loop_point2 = x
				
			elif self._loop_point1!=-1:
				setloop=self._loop_point2!=-1
				if self._loop_point2==-1:
					self._loop_point2=x
					if self._last_button == x and time.time() - self.last_button_time < 0.25:
						setloop=True
						self.last_button_time=time.time()
						self._last_button = -1
						
				if self._loop_point1 != -1 and self._loop_point2 !=-1:
					if self._loop_point1>self._loop_point2:
						start = self._loop_point2
						end = self._loop_point1
					else:
						start = self._loop_point1
						end = self._loop_point2
					end=end+1
					self._block = start
					if setloop:
						if self._is_shifted:
							if self._is_velocity_shifted:
								self._mute_notes_in_range(start * self._blocksize * self._quantization, end * self._blocksize * self._quantization)
							else:
								self._delete_notes_in_range(start * self._blocksize * self._quantization, end * self._blocksize * self._quantization)
						else:
							if self._is_velocity_shifted:					
								self._extend_clip_content(start * self._blocksize * self._quantization, self._loop_end , end * self._blocksize * self._quantization)
							self.set_clip_loop(start * self._blocksize * self._quantization, end * self._blocksize * self._quantization)

					self._parent._note_editor.set_page(self._block/4)
					self._parent._note_editor.update()
					self._loop_point1=-1
					self._loop_point2=-1
					self.update()
				self.last_button_time=time.time()
				self._last_button = x
					
	def can_scroll(self, blocks):
		if self._clip != None:
			if (blocks+self._block)<0:
				return False
			if (blocks+self._block) * 8  * self._quantization * self._number_of_lines_per_note < self._clip.loop_start:
				return False
			if (blocks+self._block+1) * 8 * self._quantization * self._number_of_lines_per_note > self._clip.loop_end:
				return False
			return True
		return False

	def scroll(self, blocks):
		if self._clip != None and self.can_scroll(blocks):
			self._block = blocks+self._block
			self._parent._note_editor.set_page(self._block)
	
	def update_notes(self):
		self.update()
	
	def update(self):
		if self.is_enabled():
			self._get_clip_loop()
			i = 0
			for button in self._buttons:
				if self._clip == None:
					button.set_on_off_values(RED_THIRD,LED_OFF)
					if self._cache[i]!=button._off_value:
						button.turn_off()
						self._cache[i]=button._off_value
				else:
					button.set_on_off_values(LED_OFF,LED_OFF)
					if (i* self._blocksize * self._quantization < self._loop_end) and (i * self._blocksize * self._quantization >= self._loop_start ):
						button.set_on_off_values(RED_THIRD,RED_THIRD)
						
					if i==self.block:
						button.set_on_off_values(AMBER_FULL,AMBER_FULL)

					if  self._playhead >= i*self._blocksize * self._quantization and self._playhead < (i+1) * self._blocksize * self._quantization:					
						button.set_on_off_values(GREEN_FULL,GREEN_FULL)
	
					if self._cache[i]!=button._on_value:
						button.turn_on()
						self._cache[i]=button._on_value
				i=i+1


	def _extend_clip_content(self, loop_start, old_loop_end, new_loop_end):
		if(self._no_notes_in_range(old_loop_end, new_loop_end, True)):
			clip_looping_length = 0
			if(old_loop_end>1):
				power = 1
				while(power*2 < old_loop_end ):
					power*=2
				clip_looping_length = (power)
			clone_length = new_loop_end-old_loop_end
			if(clip_looping_length>0):
				clone_start_point = (old_loop_end%clip_looping_length)
			else:
				clone_start_point = 0
			self._copy_notes_in_range(clone_start_point, clone_start_point+ clone_length, old_loop_end)
			self._parent._note_editor.update()
	
	def _no_notes_in_range(self, start, end, or_after):
		note_cache = list(self._parent._note_editor._clip_notes)
		for note in note_cache:
			if note[1]>=start and (note[1]<end or or_after):
				return(False)
		return(True)
		
	def _delete_notes_in_range(self, start, end):
		note_cache = list(self._parent._note_editor._clip_notes)
		new_notes = list()
		for note in note_cache:
			if note[1]<start or note[1]>=end:
				new_notes.append(note)
		self._parent._clip.select_all_notes()
		self._parent._clip.replace_selected_notes(tuple(new_notes))
		self._parent._note_editor.update()
		
	def _mute_notes_in_range(self, start, end):
		note_cache = list(self._parent._note_editor._clip_notes)
		new_notes = list()
		for note in note_cache:
			if note[1]<start or note[1]>=end:
				new_notes.append(note)
			else:
				new_notes.append([note[0], note[1], note[2], note[3], not note[4]])
		self._parent._clip.select_all_notes()
		self._parent._clip.replace_selected_notes(tuple(new_notes))
		self._parent._note_editor.update()
		
	def _copy_notes_in_range(self, start, end, new_start):
		note_cache = list(self._parent._note_editor._clip_notes)
		for note in note_cache:
			if note[1]>=start and note[1]<end:
					note_cache.append([note[0], note[1]+new_start-start, note[2], note[3], note[4]])
		self._parent._clip.select_all_notes()
		self._parent._clip.replace_selected_notes(tuple(note_cache))


class StepSequencerComponent(CompoundComponent):

	def __init__(self, matrix, side_buttons, top_buttons, parent):
		super(StepSequencerComponent, self).__init__()
		
		self._parent = parent
		self._clip = None
		self._clip_slot = None
		self._playhead = 0
		self._mode = -1
		self._mode_backup = self._mode
		self._height = matrix.height()
		self._width = matrix.width()
		self._top_buttons = top_buttons
		self._left_button = None
		self._right_button = None
		
		#loop
		self._loop_selector = self.register_component(LoopSelectorComponent(self, 
		[matrix.get_button(4,4),matrix.get_button(5,4),matrix.get_button(6,4),matrix.get_button(7,4),
		matrix.get_button(4,5),matrix.get_button(5,5),matrix.get_button(6,5),matrix.get_button(7,5),
		matrix.get_button(4,6),matrix.get_button(5,6),matrix.get_button(6,6),matrix.get_button(7,6),
		matrix.get_button(4,7),matrix.get_button(5,7),matrix.get_button(6,7),matrix.get_button(7,7)])
		)

		#notes
		self._note_editor = self.register_component(NoteEditorComponent(self, matrix))
		self._note_editor.set_velocity_button(side_buttons[6])
		self._note_editor.set_mute_shift_button(side_buttons[7])
		
		#note selector
		self._note_selector = self.register_component(NoteSelectorComponent(self,
		[matrix.get_button(0,7),matrix.get_button(1,7),matrix.get_button(2,7),matrix.get_button(3,7),
		matrix.get_button(0,6),matrix.get_button(1,6),matrix.get_button(2,6),matrix.get_button(3,6),
		matrix.get_button(0,5),matrix.get_button(1,5),matrix.get_button(2,5),matrix.get_button(3,5),
		matrix.get_button(0,4),matrix.get_button(1,4),matrix.get_button(2,4),matrix.get_button(3,4)])
		)
		self._note_selector.set_up_button(side_buttons[2])
		self._note_selector.set_down_button(side_buttons[3])

		#track nav
		self._track_controller = self.register_component(TrackControllerComponent())
		self._track_controller.set_prev_scene_button(top_buttons[0])
		self._track_controller.set_next_scene_button(top_buttons[1])
		self._track_controller.set_prev_track_button(top_buttons[2])
		self._track_controller.set_next_track_button(top_buttons[3])
		self._track_controller._parent = self
		self._track_controller._notify_parent = False

		#scales
		self._scales = self.register_component(ScalesComponent())
		self._scales.set_enabled(False)
		self._scales.set_matrix(matrix)
		self._scales.set_chromatic()
		self._scales_button = None
		self.set_scales_button(side_buttons[0])
		
		#quantization
		self._quantization_index = 2
		self.set_quantization(QUANTIZATION_MAP[self._quantization_index])
		self._quantization_button = None
		self.set_quantization_button(side_buttons[5])
		
		#mode
		self._mode_button = None
		self.set_mode_button(side_buttons[1])
		self._last_mode_button_press=time.time()
		self._number_of_lines_per_note = 1
		
		#shift
		self._shift_button = None
		self.set_shift_button(side_buttons[7])
		self._is_shifted = False

		#lock
		self._is_locked = False
		self._lock_to_track = False
		self._last_lock_button_press = int(round(time.time() * 1000))
		self._long_press = 500
		self._lock_button = None
		self.set_lock_button(side_buttons[4])
		self._selected_track = None
		
		self.on_clip_slot_changed()

	def disconnect(self):
		self._parent = None
		self._clip = None
		self._mode = None
		
		self._lock_button = None
		self._shift_button = None
		self._mode_button = None
		self._quantization_button = None
		self._top_buttons = None

		self._loop_selector = None
		self._note_editor = None
		self._note_selector = None
		self._scales = None
		self._track_controller = None

		
	#def on_enabled_changed(self):
	#	self.update()

	def set_enabled(self, enabled):
		if enabled:
			#clear cache
			self._note_editor._force_update=True
			#sync to selected pad
			self._update_drum_group_device()
			if(self._drum_group_device):
				self._note_selector.set_selected_note(index_of(self._drum_group_device.drum_pads,self._drum_group_device.view.selected_drum_pad))
			if self._mode == -1:
				self._mode = STEPSEQ_MODE_COMBINED
				self._detect_scale_mode()
			self._track_controller.set_enabled(enabled)
			#update clip
			#self.on_clip_slot_changed()
			CompoundComponent.set_enabled(self,enabled)
			
		else:
			self._track_controller.set_enabled(enabled)
			CompoundComponent.set_enabled(self,enabled)
			
	def set_mode(self,mode , number_of_lines_per_note = 1):
		if self._mode != mode or number_of_lines_per_note != self._number_of_lines_per_note:
			self._number_of_lines_per_note = number_of_lines_per_note
		 	if mode == STEPSEQ_MODE_COMBINED:
				if self._mode != mode:
					self._loop_selector._block = self._loop_selector._block * self._number_of_lines_per_note 
					self._note_editor.set_page(self._loop_selector._block/4)
				self.set_left_button(None)
				self.set_right_button(None)
				self._track_controller.set_prev_track_button(self._top_buttons[2])
				self._track_controller.set_next_track_button(self._top_buttons[3])
			else:
				if self._mode != mode:
					self._loop_selector._block = self._loop_selector._block / self._number_of_lines_per_note
					self._note_editor.set_page(self._loop_selector._block)
				self._track_controller.set_prev_track_button(None)
				self._track_controller.set_next_track_button(None)
				self.set_left_button(self._top_buttons[2])
				self.set_right_button(self._top_buttons[3])
			self._note_editor.set_multinote(mode == STEPSEQ_MODE_MULTINOTE, number_of_lines_per_note)
			self._note_editor._force_update=True
			self._mode = mode
			self.update()

	def update(self):
		if self.is_enabled():
			#self._parent._parent.log_message("update !")
				
			#track controller
			self._track_controller.set_enabled(True)

			#scale
			self._scales.set_enabled(self._mode==STEPSEQ_MODE_SCALE_EDIT)
			self._scales.update()
			
			#loop
			self._loop_selector.set_enabled(self._mode==STEPSEQ_MODE_COMBINED)
			self._loop_selector.update()
			
			#note selector
			self._note_selector._enable_offset_button = self._mode==STEPSEQ_MODE_COMBINED
			self._note_selector.set_enabled(True)			
			self._note_selector.update()
			
			#note editor
			self._note_editor.set_multinote(self._mode==STEPSEQ_MODE_MULTINOTE, self._number_of_lines_per_note)
			if self._mode==STEPSEQ_MODE_COMBINED:
				self._note_editor.set_height(self._height-4)
			else:
				self._note_editor.set_height(self._height)
			self._note_editor.set_enabled(self._mode!=STEPSEQ_MODE_SCALE_EDIT)	
			self._note_selector._set_note_editor_notes()
			self._note_editor.update()
			
			#update my buttons
			self.update_buttons()

			#show clip !
			if not self._is_locked and self._clip !=None:
					if ((not self.application().view.is_view_visible('Detail')) or (not self.application().view.is_view_visible('Detail/Clip'))):
 						self.application().view.show_view('Detail')
 						self.application().view.show_view('Detail/Clip')

	def update_buttons(self):
		self._update_quantization_button()
		self._update_lock_button()
		self._update_mode_button()
		self._update_scales_button()
		self._update_left_button()
		self._update_right_button()
		
#CLIP CALLBACKS

	def on_track_list_changed(self):
		self.on_selected_track_changed()

	def on_scene_list_changed(self):
		self.on_selected_scene_changed()
	
	def on_selected_scene_changed(self):
		self.on_clip_slot_changed()
		self.update()
	
	def on_selected_track_changed(self):
		if not self._lock_to_track or not self._is_locked or self._clip == None:
			self._detect_scale_mode()
			self.on_clip_slot_changed()
			self.update()

	def _on_loop_changed(self): 
		if self.is_enabled() and self._clip != None:
			self.update()

	def on_clip_slot_has_clip_changed(self):
		#the clip was deleted. unlock.
		if not self._clip_slot.has_clip:
			self._is_locked = False
		self.on_clip_slot_changed()
		self.update()
		

	def on_clip_slot_changed(self):
		clip_slot = None
		
		#update track if not track locked
		if not self._lock_to_track or self._selected_track == None:
			self._selected_track = self.song().view.selected_track
			
		#update scene if not locked
		if self._selected_track != None:
			idx = list(self.song().scenes).index(self.song().view.selected_scene)
			if(idx != -1):
				clip_slot = self._selected_track.clip_slots[idx]
				
		#update clip slot
		if clip_slot != self._clip_slot or self._clip_slot == None:			
			#self._parent._parent.log_message("update clip_slot")
			if clip_slot !=None and clip_slot.has_clip_has_listener(self.on_clip_slot_has_clip_changed):
				clip_slot.remove_has_clip_listener(self.on_clip_slot_has_clip_changed)
			self._clip_slot = clip_slot
			if self._clip_slot != None:
				if self._clip_slot.has_clip_has_listener(self.on_clip_slot_has_clip_changed):
					self._clip_slot.remove_has_clip_listener(self.on_clip_slot_has_clip_changed)
				self._clip_slot.add_has_clip_listener(self.on_clip_slot_has_clip_changed)
			
		if self._clip_slot != None and self._clip_slot.has_clip and self._clip_slot.clip != None and self._clip_slot.clip.is_midi_clip:
			if self._clip == None or self._clip != self._clip_slot.clip:
				#self._parent._parent.log_message("link clip_slot")
				#unlink
				if self._clip != None and self._clip.is_midi_clip:
					if self._clip.notes_has_listener(self._on_notes_changed):
						self._clip.remove_notes_listener(self._on_notes_changed)
					if self._clip.playing_status_has_listener(self._on_playing_status_changed):
						self._clip.remove_playing_status_listener(self._on_playing_status_changed) 
					if self._clip.playing_position_has_listener(self._on_playing_position_changed):
						self._clip.remove_playing_position_listener(self._on_playing_position_changed)
					if self._clip.loop_start_has_listener(self._on_loop_changed):
						self._clip.remove_loop_start_listener(self._on_loop_changed) 
					if self._clip.loop_end_has_listener(self._on_loop_changed):
						self._clip.remove_loop_end_listener(self._on_loop_changed)
				#link new clip	
				self._clip_slot.clip.add_notes_listener(self._on_notes_changed)
				self._clip_slot.clip.add_playing_status_listener(self._on_playing_status_changed)
				self._clip_slot.clip.add_playing_position_listener(self._on_playing_position_changed)
				self._clip_slot.clip.add_loop_start_listener(self._on_loop_changed)
				self._clip_slot.clip.add_loop_end_listener(self._on_loop_changed)
				
				#publish
				self._clip = self._clip_slot.clip
			else:
				#same clip...
				pass
				#self._parent._parent.log_message("same clip. pass.")
				
		else:
			#self._parent._parent.log_message("empty clip_slot or no clip_slot. cleanup")
			#unlink
			if self._clip != None:
				if self._clip.notes_has_listener(self._on_notes_changed):
					self._clip.remove_notes_listener(self._on_notes_changed)
				if self._clip.playing_status_has_listener(self._on_playing_status_changed):
					self._clip.remove_playing_status_listener(self._on_playing_status_changed) 
				if self._clip.playing_position_has_listener(self._on_playing_position_changed):
					self._clip.remove_playing_position_listener(self._on_playing_position_changed)
				if self._clip.loop_start_has_listener(self._on_loop_changed):
					self._clip.remove_loop_start_listener(self._on_loop_changed) 
				if self._clip.loop_end_has_listener(self._on_loop_changed):
					self._clip.remove_loop_end_listener(self._on_loop_changed)
				
			#publish
			self._clip = None
			
		#update
		self._note_editor.set_clip(self._clip)			
		
#NOTES CHANGES
	def _on_notes_changed(self):
		if self.is_enabled() and self._clip!= None:
			self._note_editor.update_notes()
			self._note_selector.update_notes()
			self._loop_selector.update_notes()
			
#PLAY POSITION
	def _on_playing_status_changed(self): #playing status changed listener
		#if self._clip != None:
			#if self._clip.is_playing:
		pass

	def _on_playing_position_changed(self): #playing position changed listener
		if self.is_enabled() and self._clip != None and self._clip.is_playing and self.song().is_playing:
			self._playhead = self._clip.playing_position
			self._loop_selector.update()
			self._note_selector.update_matrix()
			self._note_editor.set_playhead(self._playhead)
			self._note_editor.update()

#DRUM_GROUP_DEVICE
	def _update_drum_group_device(self):
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
	
	def _detect_scale_mode(self):
		if not self._is_locked:
			self._update_drum_group_device()
			self._scales.set_drumrack(self._drum_group_device != None)
		
			

# SCALES
	def _update_scales_button(self):
		if self.is_enabled():
			if (self._scales_button != None):
				if self._clip != None:
					self._scales_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
				else:
					self._scales_button.set_on_off_values(LED_OFF,LED_OFF)
				if self._mode==STEPSEQ_MODE_SCALE_EDIT:
					self._scales_button.turn_on()
				else:
					self._scales_button.turn_off()

	def set_scales_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._scales_button != button):
			if (self._scales_button  != None):
				self._scales_button.remove_value_listener(self._scales_button_value)
			self._scales_button = button
			if (self._scales_button  != None):
				assert isinstance(button, ButtonElement)
				self._scales_button.add_value_listener(self._scales_button_value)
			
	def _scales_button_value(self, value):
		assert (value in range(128))
		if self.is_enabled()  and self._clip != None:
			if value>0:
				self._scales.set_octave_index(self._note_selector._root_note/12)
				self._scales.set_key(self._note_selector._key)
				self._mode_backup = self._mode
				self.set_mode(STEPSEQ_MODE_SCALE_EDIT) 
			else:
				#self._note_editor._force_update = True
				self._note_selector.set_scale(self._scales.notes, self._scales._selected_key)
				self._note_selector.set_selected_note(self._scales._octave_index * 12 + self._scales._selected_key)
				self.set_mode(self._mode_backup)


#SHIFT
	def set_shift_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._shift_button != button):
			if (self._shift_button  != None):
				self._shift_button.remove_value_listener(self._shift_button_value)
			self._shift_button = button
			if (self._shift_button  != None):
				assert isinstance(button, ButtonElement)
				self._shift_button.add_value_listener(self._shift_button_value, identify_sender=True)

	def _shift_button_value(self, value, sender):
		assert (self._shift_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._is_shifted = True
			else:
				self._is_shifted = False
			self._note_editor._is_shifted=self._is_shifted


# MODE
	def _update_mode_button(self):
		if self.is_enabled():
			if (self._mode_button != None):
				if self._clip != None:
					self._mode_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
					if self._mode != STEPSEQ_MODE_MULTINOTE:
						self._mode_button.turn_on()
					else:
						self._mode_button.turn_off()
				else:
					self._mode_button.set_on_off_values(LED_OFF,LED_OFF)
					self._mode_button.turn_off()

	def set_mode_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._mode_button != button):
			if (self._mode_button  != None):
				self._mode_button.remove_value_listener(self._mode_button_value)
			self._mode_button = button
			if (self._mode_button  != None):
				assert isinstance(button, ButtonElement)
				self._mode_button.add_value_listener(self._mode_button_value, identify_sender=True)
		
	def _mode_button_value(self, value, sender):
		assert (self._mode_button != None)
		assert (value in range(128))
		if self.is_enabled()  and self._clip != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._last_mode_button_press = time.time()
			else:
				if self._mode == STEPSEQ_MODE_MULTINOTE and time.time() - self._last_mode_button_press > 0.25:
					if(self._number_of_lines_per_note == 1):
						number_of_lines_per_note = 2
					else:
						number_of_lines_per_note = 1
					self.set_mode(STEPSEQ_MODE_MULTINOTE , number_of_lines_per_note)
					
				elif self._mode != STEPSEQ_MODE_MULTINOTE:
					self.set_mode(STEPSEQ_MODE_MULTINOTE , self._number_of_lines_per_note)
	
				else:
					self.set_mode(STEPSEQ_MODE_COMBINED, self._number_of_lines_per_note)

# QUANTIZE
	def _update_quantization_button(self):
		if self.is_enabled():
			if (self._quantization_button != None):
				if self._clip != None:
					self._quantization_button.set_on_off_values(QUANTIZATION_COLOR_MAP[self._quantization_index],LED_OFF)
					self._quantization_button.turn_on()
				else:
					self._quantization_button.set_on_off_values(LED_OFF,LED_OFF)
					self._quantization_button.turn_off()

	def set_quantization_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (self._quantization_button != button):
			if (self._quantization_button  != None):
				self._quantization_button.remove_value_listener(self._quantization_button_value)
			self._quantization_button = button
			if (self._quantization_button  != None):
				assert isinstance(button, ButtonElement)
				self._quantization_button.add_value_listener(self._quantization_button_value, identify_sender=True)
		
	def _quantization_button_value(self, value, sender):
		assert (self._quantization_button != None)
		assert (value in range(128))
		if self.is_enabled()  and self._clip != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._quantization_index = (self._quantization_index+1)%len(QUANTIZATION_MAP)					
				self.set_quantization(QUANTIZATION_MAP[self._quantization_index])
				self._update_quantization_button()	

	def set_quantization(self, quantization):
		self._quantization = quantization
		self._note_editor.set_quantization(self._quantization)
		self._loop_selector.update()
		self._note_selector.update()
		self._note_editor.update()

# LOCK
	def _update_lock_button(self):
		if self.is_enabled():
			if self._lock_button != None:
				if self._clip != None:
					if self._lock_to_track:
						self._lock_button.set_on_off_values(AMBER_FULL,AMBER_THIRD)
					else:
						self._lock_button.set_on_off_values(RED_FULL,RED_THIRD)
					if self._is_locked:
						self._lock_button.turn_on()
					else:
						self._lock_button.turn_off()
				else:
					self._lock_button.set_on_off_values(LED_OFF,LED_OFF)
					self._lock_button.turn_off()
					

	def set_lock_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (button != self._lock_button):
			if (self._lock_button != None):
				self._lock_button.remove_value_listener(self._lock_value)
			self._lock_button = button
			if (self._lock_button != None):
				self._lock_button.add_value_listener(self._lock_value,identify_sender=True)


	def _lock_value(self, value,sender):
		assert (self._lock_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip!=None:
			now = int(round(time.time() * 1000))
			if ((value != 0) or (not self._lock_button.is_momentary())):
				self._last_lock_button_press=now
			else:
				if now-self._last_lock_button_press > self._long_press:
					self._lock_to_track = (not self._lock_to_track)
					if not self._is_locked:
						self._is_locked = True
				else:
					self._is_locked = (not self._is_locked) 
				self._update_lock_button()


# RIGHT
	def _update_right_button(self):
		if self.is_enabled():
			if self._right_button != None:
				if self._clip != None:
					self._right_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
					if self._loop_selector.can_scroll(1):
						self._right_button.turn_on()
					else:
						self._right_button.turn_off()
				else:
					self._right_button.set_on_off_values(LED_OFF,LED_OFF)
					self._right_button.turn_off()
					

	def set_right_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (button != self._right_button):
			if (self._right_button != None):
				self._right_button.remove_value_listener(self._right_value)
			self._right_button = button
			if (self._right_button != None):
				self._right_button.add_value_listener(self._right_value,identify_sender=True)


	def _right_value(self, value,sender):
		assert (self._right_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip!=None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._loop_selector.scroll(1)
				self._note_editor.request_display_page()
				self.update()

# LEFT
	def _update_left_button(self):
		if self.is_enabled():
			if self._left_button != None:
				if self._clip != None:
					self._left_button.set_on_off_values(GREEN_FULL,GREEN_THIRD)
					if self._loop_selector.can_scroll(-1):
						self._left_button.turn_on()
					else:
						self._left_button.turn_off()
				else:
					self._left_button.set_on_off_values(LED_OFF,LED_OFF)
					self._left_button.turn_off()
							

	def set_left_button(self, button):
		assert (isinstance(button,(ButtonElement,type(None))))
		if (button != self._left_button):
			if (self._left_button != None):
				self._left_button.remove_value_listener(self._left_value)
			self._left_button = button
			if (self._left_button != None):
				self._left_button.add_value_listener(self._left_value,identify_sender=True)


	def _left_value(self, value,sender):
		assert (self._right_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip!=None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._loop_selector.scroll(-1)
				self._note_editor.request_display_page()
				self.update()



	def create_clip(self):
		if self.song().view.highlighted_clip_slot != None:
			clip_slot = self.song().view.highlighted_clip_slot
			if not clip_slot.has_clip:
				if self._mode == STEPSEQ_MODE_COMBINED:
					clip_slot.create_clip(QUANTIZATION_MAP[self._quantization_index]*8 *4)
				else:
					clip_slot.create_clip(QUANTIZATION_MAP[self._quantization_index]*8)
				self._detect_scale_mode()
				clip_slot.fire()
				self.on_clip_slot_changed()
				self.update()
		
	def log_message(self, msg):
		self._parent.log_message(msg)
	
