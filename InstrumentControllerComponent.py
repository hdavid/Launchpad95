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
from ScaleComponent import *
from consts import *

NOTE_NAMES = ('C', 'D\x1b', 'D', 'E\x1b', 'E', 'F', 'G\x1b', 'G', 'A\x1b', 'A', 'B\x1b', 'B')
#CIRCLE_OF_FIFTHS = [ 7 * k % 12 for k in range(12) ]
#KEY_CENTERS = CIRCLE_OF_FIFTHS[0:6] + CIRCLE_OF_FIFTHS[-1:5:-1]

class InstrumentControllerComponent(CompoundComponent):
	
	def __init__(self, matrix, side_buttons, top_buttons, parent):
		super(InstrumentControllerComponent, self).__init__()
		self._parent = parent
		self._matrix = None
		self._side_buttons=side_buttons
		self._remaining_buttons = []
		self._track_controller = None
		
		self._drum_group_device  = None
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

	def set_enabled(self, enabled):
		CompoundComponent.set_enabled(self,enabled)
		self._track_controller.set_enabled(enabled)
		if not enabled:
			self._parent._parent.set_feedback_channels([])
			
		if self._track_controller!=None:
			self._track_controller._do_auto_arm(enabled)
			self._track_controller.set_enabled(enabled)
		#self.update()

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
			if self._track_controller != None:
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
			#self._parent._parent.set_feedback_channels([])
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
							button.set_light(note_info.color)
							button.set_enabled(True)
							button.force_next_send()
						button.turn_off()
							
			self._parent._config_button.send_value(32)
	
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