import Live
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SubjectSlot import subject_slot
from _Framework.ButtonElement import ButtonElement
from _Framework.Util import find_if, clamp
from itertools import imap
from TrackControllerComponent import TrackControllerComponent
from ScaleComponent import ScaleComponent,CIRCLE_OF_FIFTHS,MUSICAL_MODES,KEY_NAMES
import Settings

class InstrumentControllerComponent(CompoundComponent):

	def __init__(self, matrix, side_buttons, top_buttons, control_surface, note_repeat):
		super(InstrumentControllerComponent, self).__init__()
		self._control_surface = control_surface
		self._note_repeat = note_repeat
		self._osd = None
		self._matrix = None
		self._side_buttons = side_buttons
		self._remaining_buttons = []
		self._track_controller = None
		self.base_channel = 11
		self._quick_scales = [0, 1, 2, 3, 4, 5, 6, 7, 10, 13, 14, 15, 17, 18, 24]
		self._quick_scale_root = 0
		self._normal_feedback_velocity = int(self._control_surface._skin['Note.Feedback'])
		self._recordind_feedback_velocity = int(self._control_surface._skin['Note.FeedbackRecord'])
		self._drum_group_device = None
		self._octave_up_button = None
		self._octave_down_button = None
		self._scales_toggle_button = None
		self.set_scales_toggle_button(side_buttons[0])#Enable scale selecting mode
		self.set_octave_up_button(side_buttons[2])#Shift octave up
		self.set_octave_down_button(side_buttons[3])#Shift octave down

		self._track_controller = self.register_component(TrackControllerComponent(control_surface = control_surface, implicit_arm = True))
		self._track_controller.set_enabled(False)
		
		#Clip navigation buttons
		self._track_controller.set_prev_scene_button(top_buttons[0])
		self._track_controller.set_next_scene_button(top_buttons[1])
		self._track_controller.set_prev_track_button(top_buttons[2])
		self._track_controller.set_next_track_button(top_buttons[3])
		
		#Clip edition buttons
		self._track_controller.set_undo_button(side_buttons[1])
		self._track_controller.set_stop_button(side_buttons[4])
		self._track_controller.set_play_button(side_buttons[5])
		self._track_controller.set_session_record_button(side_buttons[7])
		self._track_controller.set_solo_button(side_buttons[6])

		self._scales = self.register_component(ScaleComponent(self._control_surface))
		#self._scales.set_enabled(False)
		self._scales.set_matrix(matrix)
		self._scales.set_osd(self._osd)
		
		self.set_matrix(matrix)

		self._on_session_record_changed.subject = self.song()
		self._on_swing_amount_changed_in_live.subject = self.song()
		self._note_repeat.set_enabled(False)

	def set_enabled(self, enabled):
		CompoundComponent.set_enabled(self, enabled)
		if self._track_controller != None:
			self._track_controller.set_enabled(enabled)
		feedback_channels = [self.base_channel, self.base_channel + 1, self.base_channel + 2, self.base_channel + 3]
		# non_feedback_channel = self.base_channel + 4
		self._set_feedback_velocity()
		self._control_surface.set_feedback_channels(feedback_channels)
		if not enabled:
			self._control_surface.release_controlled_track()
			self._note_repeat.set_enabled(False)
		else:
			self._control_surface.set_controlled_track(self._track_controller.selected_track)

		if self._track_controller != None:
			self._track_controller._do_implicit_arm(enabled)
			self._track_controller.set_enabled(enabled)
			
		if enabled:
			if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "track":  
				self._scales.from_object(self._track_controller.selected_track)
			if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "clip":  
				self._scales.from_object(self._track_controller.selected_clip)
			self._update_OSD()
					
	def _set_feedback_velocity(self):
		if self.song().session_record:
			self._control_surface._c_instance.set_feedback_velocity(self._recordind_feedback_velocity)
		else:
			self._control_surface._c_instance.set_feedback_velocity(self._normal_feedback_velocity)

	@subject_slot('session_record')
	def _on_session_record_changed(self):
		self._set_feedback_velocity()

	@subject_slot('swing_amount')
	def _on_swing_amount_changed_in_live(self):
		self.update()

	def _change_swing_amount_value(self, value):
		self._set_swing_amount_value(clamp(self.song().swing_amount + value*0.025, 0.0, 0.99))

		
	def _set_swing_amount_value(self, value):
		self.song().swing_amount = value
		self._control_surface.show_message("REPEATER Swing amount: " + str(int(self._swing_amount()*100)) + "%")
				
	def _swing_amount(self):
		return self.song().swing_amount
	
	def _toggle_note_repeater(self):
		self._note_repeat.set_enabled(not self._note_repeat.is_enabled())
		

	# Refresh button and its listener
	def set_scales_toggle_button(self, button):
		assert isinstance(button, (ButtonElement, type(None)))
		if (self._scales_toggle_button != None):
			self._scales_toggle_button.remove_value_listener(self._scales_toggle)
		self._scales_toggle_button = button
		if (self._scales_toggle_button != None):
			self._scales_toggle_button.add_value_listener(self._scales_toggle, identify_sender=True)
			self._scales_toggle_button.turn_off()

	# Refresh button and its listener
	def set_octave_up_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if (self._octave_up_button != None):
			self._octave_up_button.remove_value_listener(self._scroll_octave_up)
		self._octave_up_button = button
		if (self._octave_up_button != None):
			self._octave_up_button.add_value_listener(self._scroll_octave_up, identify_sender=True)
			self._octave_up_button.turn_off()

	# Refresh button and its listener
	def set_octave_down_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if (self._octave_down_button != None):
			self._octave_down_button.remove_value_listener(self._scroll_octave_down)
		self._octave_down_button = button
		if (self._octave_down_button != None):
			self._octave_down_button.add_value_listener(self._scroll_octave_down, identify_sender=True)
			self._octave_down_button.turn_off()

	#Enables scale selection mode
	def _scales_toggle(self, value, sender):
		if self.is_enabled():
			if (value is not 0):
				self._scales.set_enabled(True)
				self._osd_mode_backup = self._osd.mode
				self._osd.mode = self._osd_mode_backup + ' - Scale'
				self._scales_toggle_button.turn_on()
				self._scales.update()
			else:
				self._scales_toggle_button.turn_off()
				self._scales.set_enabled(False)
				#TODO: save scale setting in track or clip. detect if changed
				if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "track":
					self._scales.update_object_name(self._track_controller.selected_track)
				if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "clip":
					self._scales.update_object_name(self._track_controller.selected_clip)
				self._osd.mode = self._osd_mode_backup
				if(not self._scales.is_quick_scale):
					self._note_repeat.set_enabled(False)
				self.update()


	# Transposes key one octave up 
	def _scroll_octave_up(self, value, sender):
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value is not 0)):
				if self._can_scroll_octave_up():
					self._scales._octave += 1
					self.update()

	def _can_scroll_octave_up(self):
		return self._scales._octave < 10

	# Transposes key one octave down 
	def _scroll_octave_down(self, value, sender):
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value is not 0)):
				if self._can_scroll_octave_down():
					self._scales._octave -= 1
					self.update()

	def _can_scroll_octave_down(self):
		return self._scales._octave  > -2

	#Handles scale setting and configuration
	def _matrix_value_quickscale(self, value, x, y, is_momentary):  # matrix buttons listener for advanced mode
		if self.is_enabled() and not self._scales.is_enabled() and self._scales.is_quick_scale:
			keys = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
			if ((value != 0) or (not is_momentary)):
				if self._quick_scale_root==0 and not self._scales.is_drumrack:
					root = -1
					selected_key = self._scales._key
					selected_modus = self._scales._modus
					#Root selection keys
					if y == 1 and x < 7 or y == 0 and x in[0, 1, 3, 4, 5]:
						if y == 1:
							root = [0, 2, 4, 5, 7, 9, 11, 12][x]
							self._control_surface.show_message(keys[root]+" "+str(self._scales._modus_names[selected_modus]))
						if y == 0 and x < 6:
							root = [0, 2, 4, 5, 7, 9, 11, 12][x] + 1
							self._control_surface.show_message(keys[root]+" "+str(self._scales._modus_names[selected_modus]))
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
							self._control_surface.show_message(keys[root]+" "+str(self._scales._modus_names[selected_modus]))
					else:
						
						if y == 0 and x == 7:  # change scale mode
							self.setup_quick_scale_mode()
							self.update()
						if y == 1 and x == 7:  # nav circle of 5th right
							root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) + 1 + 12) % 12]
							self._control_surface.show_message("circle of 5ths -> "+keys[selected_key]+" "+str(self._scales._modus_names[selected_modus])+" => "+keys[root]+" "+str(self._scales._modus_names[selected_modus]))
						if y == 0 and x == 6:  # nav circle of 5th left
							root = CIRCLE_OF_FIFTHS[(self.tuple_idx(CIRCLE_OF_FIFTHS, selected_key) - 1 + 12) % 12]
							self._control_surface.show_message("circle of 5ths <- "+keys[selected_key]+" "+str(self._scales._modus_names[selected_modus])+" => "+keys[root]+" "+str(self._scales._modus_names[selected_modus]))
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
							self._control_surface.show_message("Relative scale : "+keys[root]+" "+str(self._scales._modus_names[selected_modus]))

					if root != -1:
						self._scales.set_modus(selected_modus, False)
						self._scales.set_key(root, False)
						#TODO: save scale in clip or track name
						if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "track":
							if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "track":
								self._scales.update_object_name(self._track_controller.selected_track)
							if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "clip":
								self._scales.update_object_name(self._track_controller.selected_clip)
						self.update()

				elif self._quick_scale_root==1 and not self._scales.is_drumrack:
					if(y == 0):
						if x < 7 and self._quick_scales[x] != -1:
							self._scales.set_modus(self._quick_scales[x])
							#TODO: save scale in clip or track name
							if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "track":
								self._scales.update_object_name(self._track_controller.selected_track)
							if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "clip":
								self._scales.update_object_name(self._track_controller.selected_clip)
							self._control_surface.show_message("mode : "+str(self._scales._modus_names[self._scales._modus]))
							self.update()
						if x == 7:
							self.setup_quick_scale_mode()
							self.update()
					if(y == 1):
						if x < 8 and self._quick_scales[x + 7] != -1:
							self._scales.set_modus(self._quick_scales[x + 7])
							#TODO: save scale in clip or track name
							if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "track":
								self._scales.update_object_name(self._track_controller.selected_track)
							if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "clip":
								self._scales.update_object_name(self._track_controller.selected_clip)
							self._control_surface.show_message("mode : "+str(self._scales._modus_names[self._scales._modus]))
							self.update()
				else:
					if(y == 0):
						if x == 0:
							self._change_swing_amount_value(-1)
						elif x == 1:
							self._change_swing_amount_value(1)
						elif x == 2:
							self._set_swing_amount_value(0.0)
						elif x == 3:
							self._set_swing_amount_value(0.25)
						elif x == 4:
							self._set_swing_amount_value(0.5)	
						elif x == 5:
							self._set_swing_amount_value(0.75)	
						elif x == 6:
							self._toggle_note_repeater()
							self._control_surface.show_message("REPEATER is: " + str("ON" if self._note_repeat.is_enabled() else "OFF"))																							
						elif x == 7:
							self.setup_quick_scale_mode()
							
					if(y == 1):
						if x in range(8):
							
							self._note_repeat.set_freq_index(x)
							self._control_surface.show_message("REPEATER Step: " + str(self._note_repeat.freq_name()))
					self.update()							

	def setup_quick_scale_mode(self):
		
		self._quick_scale_root = ((self._quick_scale_root + 1) % 3)
		
		if self._quick_scale_root==0:
			self._control_surface.show_message("quick scale : root")
		elif self._quick_scale_root==1:
			self._control_surface.show_message("quick scale : modes")
		else:
			self._control_surface.show_message("quick scale : REPEATER")

	def update(self):
		if self.is_enabled():
			if self._track_controller != None:
				self._track_controller.set_enabled(True)

			self._update_matrix()

			for button in self._remaining_buttons:
				button.set_light("DefaultButton.Disabled")

			if self._scales_toggle_button != None:
				self._scales_toggle_button.set_on_off_values("Note.Scale")
				self._scales_toggle_button.turn_off()

			if self._octave_up_button != None:
				self._octave_up_button.set_on_off_values("Note.Octave")
				if(self._can_scroll_octave_up()):
					self._octave_up_button.turn_on()
				else:
					self._octave_up_button.turn_off()

			if self._octave_down_button != None:
				self._octave_down_button.set_on_off_values("Note.Octave")
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
			self._osd.attributes[0] = MUSICAL_MODES[self._scales._modus * 2]
			self._osd.attribute_names[0] = "Scale"
			self._osd.attributes[1] = KEY_NAMES[self._scales._key % 12]
			self._osd.attribute_names[1] = "Root Note"
			self._osd.attributes[2] = self._scales._octave
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

			if self._track_controller.selected_track != None:
				self._osd.info[0] = "track : " + self._track_controller.selected_track.name
			else:
				self._osd.info[0] = " "

			self._osd.info[1] = " "
			self._osd.update()

	# Refresh matrix and its listener
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

	#Listener, setup drumrack scale mode and load the selected scale for Track/Cip (Disabled)
	def on_selected_track_changed(self):
		if self._track_controller._implicit_arm:
			self._get_drumrack_device()
			if self._drum_group_device != None:
				self._scales.set_drumrack(True)
			else:
				self._scales.set_drumrack(False)
				
			#load scale settings from track
			if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "track":  
				self._scales.from_object(self._track_controller.selected_track)
			if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "clip":  
				self._scales.from_object(self._track_controller.selected_clip)
				# must be delayed.... self._scales.update_object_name(track)
					
			self.update()
	
	def on_selected_scene_changed(self):
		if self._track_controller._implicit_arm:
			#load scale settings from track
			if Settings.INSTRUMENT__SAVE_SCALE != None and Settings.INSTRUMENT__SAVE_SCALE == "clip":  
				self._scales.from_object(self._track_controller.selected_clip)
				# must be delayed.... self._scales.update_object_name(track)
					
			self.update()

	#Set the drum rack instrument to _drum_group_device variable, if it exists
	def _get_drumrack_device(self):
		if self._track_controller.selected_track != None:
			track = self._track_controller.selected_track
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
	
	#Return the drum device inside the track devices or inside the track chain or None if device is not a Drum
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
			self._control_surface.release_controlled_track()
			# self._control_surface.set_feedback_channels([])
		else:
			# feedback_channels = [self.base_channel, self.base_channel + 1, self.base_channel + 2, self.base_channel + 3]
			non_feedback_channel = self.base_channel + 4

			# create array to keep last channel used for note.
			note_channel = range(128)
			for i in range(128):
				note_channel[i] = self.base_channel

			# Validate if device is drumrack (assign _drum_group_device)
			self._get_drumrack_device()

			if self._scales.is_drumrack and not self._scales.is_diatonic and not self._scales.is_chromatic:
				if self._drum_group_device != None:
					self._scales.set_drumrack(True) 
				else:
					self._scales.set_drumrack(False)

			for button, (x, y) in self._matrix.iterbuttons():
				button.use_default_message()
				button.set_channel(non_feedback_channel)
				#button.force_next_send()

			if self._scales.is_quick_scale:
				
				selected_modus = self._scales._modus
				selected_key = self._scales._key

				if self._quick_scale_root==0 and not self._scales.is_drumrack:
					if selected_modus == 0 or selected_modus == 12:
						key_color = "QuickScale.Major.Key"
						fifth_button_color = "QuickScale.Major.CircleOfFifths"
						mode_button_color = "QuickScale.Major.Mode"
						relative_scale_button_color = "QuickScale.Major.RelativeScale"
					elif selected_modus == 1 or selected_modus == 11:
						key_color = "QuickScale.Minor.Key"
						fifth_button_color = "QuickScale.Minor.CircleOfFifths"
						mode_button_color = "QuickScale.Minor.Mode"
						relative_scale_button_color = "QuickScale.Minor.RelativeScale"
					else:
						key_color = "QuickScale.Other.Key"
						fifth_button_color = "QuickScale.Other.CircleOfFifths"
						mode_button_color = "QuickScale.Other.Mode"
						relative_scale_button_color = "QuickScale.Other.RelativeScale"

					# circle of 5th nav right
					button = self._matrix.get_button(7, 1)
					button.set_light(fifth_button_color)
					# circle of 5th nav left
					button = self._matrix.get_button(6, 0)
					button.set_light(fifth_button_color)
					# mode button
					button = self._matrix.get_button(7, 0)
					button.set_light(mode_button_color)
					# relative scale button
					button = self._matrix.get_button(2, 0)
					button.set_light(relative_scale_button_color)

					for x in [0, 1, 3, 4, 5]:
						button = self._matrix.get_button(x, 0)
						button.set_enabled(True)
						button.set_on_off_values(key_color)
						#button.force_next_send()
						if [0, 2, 4, 5, 7, 9, 11, 12][x] + 1 == selected_key:
							button.turn_on()
						else:
							button.turn_off()

					for x in [0, 1, 2, 3, 4, 5, 6]:
						button = self._matrix.get_button(x, 1)
						button.set_enabled(True)
						button.set_on_off_values(key_color)
						#button.force_next_send()
						if [0, 2, 4, 5, 7, 9, 11, 12][x] == selected_key:
							button.turn_on()
						else:
							button.turn_off()
				elif self._quick_scale_root==1 and not self._scales.is_drumrack:
					button = self._matrix.get_button(7, 0)
					button.set_light("QuickScale.Major.Mode")
					for x in range(7):
						button = self._matrix.get_button(x, 0)
						button.set_enabled(True)
						if self._quick_scales[x] != -1:
							button.set_on_off_values("QuickScale.Modus")
							if self._quick_scales[x] == selected_modus:
								button.turn_on()
							else:
								button.turn_off()
							
						else:
							button.set_light("DefaultButton.Disabled")
						
					for x in range(8):
						button = self._matrix.get_button(x, 1)
						button.set_enabled(True)
						if self._quick_scales[x + 7] != -1:
							button.set_on_off_values("QuickScale.Modus")
						else:
							button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")
						#button.force_next_send()
						if self._quick_scales[x + 7] == selected_modus:
							button.turn_on()
						else:
							button.turn_off()
				else:
					button = self._matrix.get_button(7, 0)
					button.set_light("QuickScale.Quant.Mode")
					
					
					for x in range(7):
						button = self._matrix.get_button(x, 0)
						button.set_enabled(True)
						
						if(x ==0):
							button.set_on_off_values("QuickScale.Quant.On", "QuickScale.Quant.Off")
							if(not self._swing_amount() ==0.0):
								button.turn_on()
							else:
								button.turn_off()
						elif(x ==1):
							button.set_on_off_values("QuickScale.Quant.On", "QuickScale.Quant.Off")
							if(self._swing_amount() < 0.98):
								button.turn_on()
							else:
								button.turn_off()	
							
						elif(x ==2):
							button.set_on_off_values("QuickScale.Quant.Straight", "DefaultButton.Disabled")
							button.turn_on()
						elif(x ==3):
							button.set_on_off_values("QuickScale.Quant.Swing", "DefaultButton.Disabled")
							button.turn_on()
						elif(x ==4):
							button.set_on_off_values("QuickScale.Quant.Dotted", "DefaultButton.Disabled")
							button.turn_on()
						elif(x ==5):
							button.set_on_off_values("QuickScale.Quant.Flam", "DefaultButton.Disabled")
							button.turn_on()								
						
						elif(x ==6):
							button.set_on_off_values("QuickScale.NoteRepeater.On", "QuickScale.NoteRepeater.Off")
							if(self._note_repeat.is_enabled()):
								button.turn_on()
							else:								
								button.turn_off()
						
					for x in range(8):
						button = self._matrix.get_button(x, 1)
						button.set_enabled(True)
						if(x%2==0):						
							button.set_on_off_values("QuickScale.Quant.Selected", "QuickScale.Quant.Note")
						else:
							button.set_on_off_values("QuickScale.Quant.Selected", "QuickScale.Quant.Tripplet")

						if (x) == self._note_repeat.freq_index():
							button.turn_on()
						else:
							button.turn_off()

			if self._scales.is_drumrack:

				for button, (x, y) in self._matrix.iterbuttons():
					if button and (not self._scales.is_quick_scale or y > 1):
						note = 0
						if(x < 4):
							note = 12 * self._scales._octave + x + 4 * (7 - y)
						else:
							note = 12 * self._scales._octave + 32 + x - 4 + 4 * (7 - y)

						if note < 128 and note >= 0:
							if self._drum_group_device != None and self._drum_group_device.can_have_drum_pads and self._drum_group_device.has_drum_pads and self._drum_group_device.drum_pads[note].chains:
								button.set_light("DrumGroup.PadFilled")
								button.set_enabled(False)
								button.set_channel(self.base_channel)
								button.set_identifier(note)
							else:
								button.set_light("DrumGroup.PadEmpty")
								button.set_enabled(False)
								button.set_channel(self.base_channel)
								button.set_identifier(note)
						else:
							button.set_light("DrumGroup.PadEmpty")
							button.set_enabled(True)
							button.set_channel(non_feedback_channel)
						#button.force_next_send()
						#button.turn_off()

			else:	
				pattern = self._scales.get_pattern()
				max_j = self._matrix.width() - 1
				a = 0
				if self._scales.is_chromatic:
					a= 63
				for button, (i, j) in self._matrix.iterbuttons():
					if button and (not self._scales.is_quick_scale or j > 1):
						a = a +1
						note_info = pattern.note(i, max_j - j)
						if note_info.index != None:
							if note_info.root:
								button.set_light("Note.Pads.Root")
							elif note_info.highlight:
								button.set_light("Note.Pads.Highlight")
							elif note_info.in_scale:
								button.set_light("Note.Pads.InScale")
							elif note_info.valid:
								button.set_light("Note.Pads.OutOfScale")
							else:
								button.set_light("Note.Pads.Invalid")
							button.set_enabled(False)
							button.set_channel(note_channel[note_info.index])
							# comment the line above and use the one below if you want instrument controller to use one channel instead of 3
							# button.set_channel(note_channel[0])
							button.set_identifier(note_info.index)
							if(note_channel[note_info.index]<15):
								note_channel[note_info.index] = note_channel[note_info.index] + 1
						else:
							button.set_channel(non_feedback_channel)
							button.set_identifier(a)
							button.set_light("Note.Pads.Invalid")
							button.set_enabled(True)
						button.force_next_send()
						

			for button in self._side_buttons:
				button.use_default_message()
				button.set_channel(non_feedback_channel)
				button.set_enabled(True)
				button.force_next_send()

			#self._control_surface._config_button.send_value(32)#Send enable flashing led config message to LP

	
	def tuple_idx(self, target_tuple, obj):
			for i in xrange(0, len(target_tuple)):
				if (target_tuple[i] == obj):
					return i
			return(False)
	
