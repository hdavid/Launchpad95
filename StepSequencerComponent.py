import Live
from consts import * 
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.Util import find_if
from itertools import imap
from NoteEditorComponent import NoteEditorComponent
from ScaleComponent import * 
from TrackControllerComponent import TrackControllerComponent
import time
import Settings

# quantization button colours. this must remain of length 4.
QUANTIZATION_MAP = [1, 0.5, 0.25, 0.125]  # 1/4 1/8 1/16 1/32
QUANTIZATION_NAMES = ["1/4", "1/8", "1/16", "1/32"]

STEPSEQ_MODE_NORMAL = 1
STEPSEQ_MODE_MULTINOTE = 2
STEPSEQ_MODE_SCALE_EDIT = 10

LONG_BUTTON_PRESS = 1.0

class NoteSelectorComponent(ControlSurfaceComponent):

	def __init__(self, step_sequencer, offset_buttons, control_surface):
		self._step_sequencer = step_sequencer
		self._control_surface = control_surface
		ControlSurfaceComponent.__init__(self)
		self.set_enabled(False)

		self._clip = None
		self._track = None
		self._notes = None
		self._playhead = None

		self._root_note = 36
		self._offset = 0
		self._key = 0
		self._scale = [0, 2, 4, 5, 7, 9, 11, 12]
		self._force = True

		self._up_button = None
		self._down_button = None

		self._offset_buttons = offset_buttons
		self._enable_offset_button = True
		# cache to optimise display for offset buttons minimizing midi traffic
		self._cache = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
		self._was_velocity_shifted = False
		for button in self._offset_buttons:
			assert isinstance(button, ButtonElement)
			button.remove_value_listener(self.note_offset_button_value)
			button.add_value_listener(self.note_offset_button_value, identify_sender=True)

	def set_clip(self, clip):
		self._clip = clip

	def set_note_cache(self, note_cache):
		self._note_cache = note_cache

	def set_playhead(self, playhead):
		self._playhead = playhead
		self._update_matrix()

	@property
	def _is_mute_shifted(self):
		return self._step_sequencer._is_mute_shifted

	@property
	def _is_velocity_shifted(self):
		return self._step_sequencer._is_velocity_shifted

	@property
	def _drum_group_device(self):
		return self._step_sequencer._drum_group_device

	@property
	def is_drumrack(self):
		return self._step_sequencer._scale_selector.is_drumrack and self._drum_group_device != None

	@property
	def is_chromatic(self):
		return self._step_sequencer._scale_selector.is_chromatic

	@property
	def is_diatonic(self):
		return self._step_sequencer._scale_selector.is_diatonic
	
	
	# DOWN Button
	def _update_down_button(self):
		if self.is_enabled():
			if self._down_button != None:
				if self._clip == None:
					self._down_button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")
					self._down_button.turn_off()
				else:
					self._down_button.set_on_off_values("StepSequencer.Octave.On", "StepSequencer.Octave.Off")
					if not self._is_mute_shifted and not self._enable_offset_button or self._is_mute_shifted and self._enable_offset_button:
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
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._down_button != button):
			if (self._down_button != None):
				self._down_button.remove_value_listener(self._down_button_value)
			self._down_button = button
			if (self._down_button != None):
				assert isinstance(button, ButtonElement)
				self._down_button.add_value_listener(self._down_button_value, identify_sender=True)
			self._update_down_button()

	def _down_button_value(self, value, sender):
		assert (self._down_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if value is not 0 or not sender.is_momentary():
				if not self._is_mute_shifted and not self._enable_offset_button or self._is_mute_shifted and self._enable_offset_button:
					self.scroll_down()
				else:
					self.page_down()
				self._step_sequencer.update()

	# UP button
	def _update_up_button(self):
		if self.is_enabled():
			if self._up_button != None:
				if self._clip == None:
					self._up_button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")
					self._up_button.turn_off()
				else:
					self._up_button.set_on_off_values("StepSequencer.Octave.On", "StepSequencer.Octave.Off")
					if not self._is_mute_shifted and not self._enable_offset_button or self._is_mute_shifted and self._enable_offset_button:
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
		assert (isinstance(button, (ButtonElement, type(None))))
		if self._up_button != button:
			if self._up_button != None:
				self._up_button.remove_value_listener(self._up_button_value)
			self._up_button = button
			if self._up_button != None:
				assert isinstance(button, ButtonElement)
				self._up_button.add_value_listener(self._up_button_value, identify_sender=True)
			self._update_up_button()

	def _up_button_value(self, value, sender):
		assert (self._up_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if value is not 0 or not sender.is_momentary():
				if not self._is_mute_shifted and not self._enable_offset_button or self._is_mute_shifted and self._enable_offset_button:
					self.scroll_up()
				else:
					self.page_up()
				self._step_sequencer.update()

	# Note Offeset Buttons
	def note_offset_button_value(self, value, sender):
		if self.is_enabled() and value > 0 and self._enable_offset_button:
			if self._is_mute_shifted:
				try:
					index = self._offset_buttons.index(sender)
				except ValueError:
					index = -1
				self._step_sequencer._note_editor.mute_lane(self._root_note + index)
			else:
				try:
					self._offset = self._offset_buttons.index(sender)
				except ValueError:
					self._offset = -1
				if self.is_drumrack:
					self._drum_group_device.view.selected_drum_pad = self._drum_group_device.drum_pads[self.selected_note]
				self.update()
				self._step_sequencer._scale_updated()

	def update(self):
		if self.is_enabled():
			self._step_sequencer._track_controller._do_implicit_arm(self._is_velocity_shifted and not self._step_sequencer._is_locked)
			if self._is_velocity_shifted and not self._step_sequencer._is_locked:
				self._control_surface.set_feedback_channels([11])
				self._control_surface._c_instance.set_feedback_velocity(int(self._control_surface._skin['Note.Feedback']))
				self._was_velocity_shifted = True
			elif self.is_drumrack and self._was_velocity_shifted:
				self._was_velocity_shifted = False
				self._offset = self._drum_group_device.view.selected_drum_pad.note - self._root_note
				self._step_sequencer._scale_updated()
			self._update_up_button()
			self._update_down_button()
			self._update_matrix()

	def _update_matrix(self):
		if self._enable_offset_button and self.is_enabled():
			for i in range(len(self._offset_buttons)):
				if self._clip == None:
					self._offset_buttons[i].set_light("DefaultButton.Disabled")
				else:
					note = self._root_note + i

					if self.is_drumrack:
						if self._drum_group_device.drum_pads[note].chains:
							self._offset_buttons[i].set_on_off_values("DrumGroup.PadSelected","DrumGroup.PadFilled")
						else:
							self._offset_buttons[i].set_on_off_values("DrumGroup.PadEmpty", "DrumGroup.PadEmpty")
					else:
						if self._scale != None and i % 12 in self._scale:
							self._offset_buttons[i].set_on_off_values("StepSequencer.NoteSelector.Selected", "Note.Pads.Root")
						else:
							self._offset_buttons[i].set_on_off_values("StepSequencer.NoteSelector.Selected", "Note.Pads.InScale")

					if self._is_velocity_shifted and not self._step_sequencer._is_locked:
						self._offset_buttons[i].force_next_send()
						# self._offset_buttons[i].turn_off()
						self._offset_buttons[i].set_enabled(False)
						self._offset_buttons[i].set_channel(11)
						self._offset_buttons[i].set_identifier(note)
					else:
						self._offset_buttons[i].set_enabled(True)
						self._offset_buttons[i].use_default_message()

						if self._playhead != None and self.note_is_playing(self._clip, self._note_cache, note, self._playhead):
							self._offset_buttons[i].set_on_off_values("StepSequencer.NoteSelector.Playing","StepSequencer.NoteSelector.Playing")

					if self.selected_note == note:
						if self._cache[i] != self._offset_buttons[i]._on_value or self._force:
							self._offset_buttons[i].turn_on()
							self._cache[i] = self._offset_buttons[i]._on_value
					else:
						if self._cache[i] != self._offset_buttons[i]._off_value or self._force:
							self._offset_buttons[i].turn_off()
							self._cache[i] = self._offset_buttons[i]._off_value
			self._force = False

	def set_enabled(self, enabled):
		if enabled:
			self._cache = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
		ControlSurfaceComponent.set_enabled(self, enabled)

	def set_scale(self, scale, key=-1):
		if key != -1:
			self._key = key
		self._scale = scale
		# relativise scale
		for i in range(len(self._scale)):
			self._scale[i] = self._scale[i] - self._key

	def note_is_playing(self, clip, note_cache, midi_note, playhead):
		if clip != None and clip.is_playing and note_cache != None:
			for note in note_cache:
				note_key = note[0]
				note_position = note[1]
				note_length = note[2]
				# note_velocity = note[3]
				note_muted = note[4]
				if midi_note == note_key and note_position <= playhead and note_position + note_length >= playhead and not note_muted:
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
		return self.selected_note + steps >= 0 and self.selected_note + steps < 128

	def move(self, steps):
		if self.can_move(steps):
			if self.is_diatonic:
				# self._control_surface.log_message("can move dia "+ str(steps))

				# find the next note in scale in that direction
				oct = 0
				if steps > 0:
					while self._offset + steps >= 12:
						steps = steps - 12
						oct = oct + 1
					while steps != 0 and self._offset + steps not in self._scale:
						steps = steps + 1
						while self._offset + steps > 12:
							steps = steps - 12
							oct = oct + 1
				elif steps < 0:
					while self._offset + steps < 0:
						steps = steps + 12
						oct = oct - 1
					while steps != 0 and self._offset + steps not in self._scale:
						steps = steps - 1
						if self._offset + steps < 0:
							steps = steps + 12
							oct = oct - 1
				try:
					idx = self._scale.index(self._offset + steps)
				except ValueError:
					idx = -1
				self.set_selected_note(self._root_note + oct * 12 + self._scale[idx])
			else:
				# self._control_surface.log_message("can move drum/chrom "+ str(steps) + " root:"+str(self._root_note)+" offset:"+str(self._offset))
				self.set_selected_note(self._root_note + self._offset + steps)

	def set_selected_note(self, selected_note):
		if self.is_drumrack:
			self._root_note = ((selected_note + 12) / 16 - 1) * 16 + 4
			self._offset = (selected_note - self._root_note + 16) % 16
			# self._control_surface.log_message("DR selected_note:"+str(selected_note)+" self._root_note: "+ str(self._root_note)+" offset: "+ str(self._offset))
		else:
			self._root_note = ((selected_note - self._key) / 12) * 12 + self._key
			self._offset = (selected_note + 12 - self._root_note) % 12
			# self._control_surface.log_message("CHR selected_note:"+str(selected_note)+" self._root_note: "+ str(self._root_note)+" offset: "+ str(self._offset))

		self.update()
		self._step_sequencer._scale_updated()

	def set_key(self, key):
		self._key = key

	def note_is_available(self, key):
		if self.is_drumrack:
			if self._drum_group_device.drum_pads[key].chains:
				return True
			else:
				return False
		else:
			for note in scale:
				if key % 12 == (self.root_note + note) % 12:
					return True
				else:
					return False

	def note_is_used(self, key):
		if clip != None:
			for note in self._clip_notes:
				if note[0] == key:  # key: 0-127 MIDI note #
					return True
		return False

	@property
	def selected_note(self):
		return self._root_note + self._offset


class LoopSelectorComponent(ControlSurfaceComponent):

	def __init__(self, step_sequencer, buttons, control_surface):
		ControlSurfaceComponent.__init__(self)
		self._control_surface = control_surface
		self.set_enabled(False)
		self._step_sequencer = step_sequencer

		self._clip = None
		self._notes = None
		self._playhead = None

		self._loop_end = 0
		self._loop_start = 0

		self._blocksize = 8  # number of note per block
		self._block = 0  # current block
		self._force = True

		# used for loop selection
		self._last_button = -1
		self._last_button_time = time.time()
		self._loop_point1 = -1
		self._loop_point2 = -1

		self._cache = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

		self._buttons = buttons
		for button in self._buttons:
			assert isinstance(button, ButtonElement)
			button.remove_value_listener(self._loop_button_value)
			button.add_value_listener(self._loop_button_value, identify_sender=True)

	def disconnect(self):
		self._top_buttons = None

	@property
	def _number_of_lines_per_note(self):
		if self._mode == STEPSEQ_MODE_MULTINOTE:
			return self._step_sequencer._number_of_lines_per_note
		else:
			return 1

	def set_clip(self, clip):
		self._clip = clip

	@property
	def _mode(self):
		return self._step_sequencer._mode

	def set_note_cache(self, note_cache):
		self._note_cache = note_cache

	def set_playhead(self, playhead):
		self._playhead = playhead
		self.update()

	@property
	def _is_mute_shifted(self):
		return self._step_sequencer._is_mute_shifted

	@property
	def _is_velocity_shifted(self):
		return self._step_sequencer._note_editor._is_velocity_shifted

	@property
	def _quantization(self):
		return self._step_sequencer._quantization

	@property
	def block(self):
		return self._block

	def set_blocksize(self, blocksize):
		self._blocksize = blocksize

	def set_enabled(self, enabled):
		self._force = True
		ControlSurfaceComponent.set_enabled(self, enabled)

	def _get_clip_loop(self):
		if self._clip != None:
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
			x = self._buttons.index(sender)
			if value > 0:
				if self._loop_point1 == -1:
					self._loop_point1 = x
				elif self._loop_point2 == -1:
					self._loop_point2 = x

			elif self._loop_point1 != -1:
				setloop = self._loop_point2 != -1
				if self._loop_point2 == -1:
					self._loop_point2 = x
					if self._last_button == x and time.time() - self.last_button_time < 0.25:
						setloop = True
						self.last_button_time = time.time()
						self._last_button = -1

				if self._loop_point1 != -1 and self._loop_point2 != -1:
					if self._loop_point1 > self._loop_point2:
						start = self._loop_point2
						end = self._loop_point1
					else:
						start = self._loop_point1
						end = self._loop_point2
					end = end + 1
					self._block = start
					if setloop:
						if self._is_mute_shifted:
							if self._is_velocity_shifted:
								self._mute_notes_in_range(start * self._blocksize * self._quantization, end * self._blocksize * self._quantization)
							else:
								self._delete_notes_in_range(start * self._blocksize * self._quantization, end * self._blocksize * self._quantization)
						else:
							if self._is_velocity_shifted:
								self._extend_clip_content(start * self._blocksize * self._quantization, self._loop_end, end * self._blocksize * self._quantization)
							self.set_clip_loop(start * self._blocksize * self._quantization, end * self._blocksize * self._quantization)

					self._step_sequencer.set_page(self._block)
					self._loop_point1 = -1
					self._loop_point2 = -1
					self.update()
				self.last_button_time = time.time()
				self._last_button = x

	def can_scroll(self, blocks):
		if self._clip != None:
			if (blocks + self._block) < 0:
				return False
			if (blocks + self._block) * 8 * self._quantization * self._number_of_lines_per_note < self._clip.loop_start:
				return False
			if (blocks + self._block + 1) * 8 * self._quantization * self._number_of_lines_per_note > self._clip.loop_end:
				return False
			return True
		return False

	def scroll(self, blocks):
		if self._clip != None and self.can_scroll(blocks):
			self._block = blocks + self._block
			self._step_sequencer.set_page(self._block)

	def update(self):
		if self.is_enabled():
			self._get_clip_loop()
			i = 0
			for button in self._buttons:
				if self._clip == None:
					button.set_on_off_values("DefaultButton.Disabled","DefaultButton.Disabled")
					if self._cache[i] != button._off_value:
						button.turn_off()
						self._cache[i] = button._off_value
				else:
					in_loop = (i * self._blocksize * self._quantization < self._loop_end) and (i * self._blocksize * self._quantization >= self._loop_start)
					playing = self._playhead >= i * self._blocksize * self._quantization and self._playhead < (i + 1) * self._blocksize * self._quantization
					selected = i == self.block
					if in_loop:
						if playing:
							if selected:
								self._cache[i] = "StepSequencer.LoopSelector.SelectedPlaying"
							else:
								self._cache[i] = "StepSequencer.NoteSelector.Playing"
						else:
							if selected:
								self._cache[i] = "StepSequencer.LoopSelector.Selected"
							else:
								self._cache[i] = "StepSequencer.LoopSelector.InLoop"	
					else:
						if playing:
							if selected:
								self._cache[i] = "StepSequencer.LoopSelector.SelectedPlaying"
							else:
								self._cache[i] = "StepSequencer.NoteSelector.Playing"
						else:
							if selected:
								self._cache[i] = "StepSequencer.LoopSelector.Selected"
							else:
								self._cache[i] = "DefaultButton.Disabled"

					if self._cache[i] != button._on_value or self._force:
						button.set_on_off_values(self._cache[i], self._cache[i])
						button.turn_on()
				i = i + 1
			self._force = False

	def _extend_clip_content(self, loop_start, old_loop_end, new_loop_end):
		if(self._no_notes_in_range(old_loop_end, new_loop_end, True)):
			clip_looping_length = 0
			if(old_loop_end > 1):
				power = 1
				while(power * 2 < old_loop_end):
					power *= 2
				clip_looping_length = (power)
			clone_length = new_loop_end - old_loop_end
			if(clip_looping_length > 0):
				clone_start_point = (old_loop_end % clip_looping_length)
			else:
				clone_start_point = 0
			self._copy_notes_in_range(clone_start_point, clone_start_point + clone_length, old_loop_end)

	def _no_notes_in_range(self, start, end, or_after):
		for note in list(self._note_cache):
			if note[1] >= start and (note[1] < end or or_after):
				return(False)
		return(True)

	def _delete_notes_in_range(self, start, end):
		new_notes = list()
		for note in list(self._note_cache):
			if note[1] < start or note[1] >= end:
				new_notes.append(note)
		self._clip.select_all_notes()
		self._clip.replace_selected_notes(tuple(new_notes))

	def _mute_notes_in_range(self, start, end):
		new_notes = list()
		for note in list(self._note_cache):
			if note[1] < start or note[1] >= end:
				new_notes.append(note)
			else:
				new_notes.append([note[0], note[1], note[2], note[3], not note[4]])
		self._clip.select_all_notes()
		self._clip.replace_selected_notes(tuple(new_notes))

	def _copy_notes_in_range(self, start, end, new_start):
		new_notes = list(self._note_cache)
		# for i in range()
		for note in new_notes:
			if note[1] >= start and note[1] < end:
				new_notes.append([note[0], note[1] + new_start - start, note[2], note[3], note[4]])
		self._clip.select_all_notes()
		self._clip.replace_selected_notes(tuple(new_notes))


class StepSequencerComponent(CompoundComponent):

	def __init__(self, matrix, side_buttons, top_buttons, control_surface):
		self._osd = None
		self._control_surface = control_surface
		super(StepSequencerComponent, self).__init__()
		self.QUANTIZATION_COLOR_MAP = ["StepSequencer.Quantization.One", "StepSequencer.Quantization.Two", "StepSequencer.Quantization.Three", "StepSequencer.Quantization.Four"]
		self._name = "drum step sequencer"
		# clip
		self._clip = None
		self._clip_slot = None
		self._note_cache = []
		self._playhead = 0
		self._new_clip_pages = 4
		# mode
		self._mode = -1
		self._mode_backup = self._mode
		# buttons
		self._height = matrix.height()
		self._width = matrix.width()
		self._matrix = matrix
		self._top_buttons = top_buttons
		self._side_buttons = side_buttons
		self._left_button = None
		self._right_button = None
		# scale
		self._root_note = 36
		self._chromatic_scale = []
		self._diatonic_scale = []
		# setup
		self._set_loop_selector()
		self._set_note_editor()
		self._set_note_selector()
		self._set_note_selector()
		self._set_track_controller()
		self._set_scale_selector()
		self._set_quantization_function()
		self._set_mute_shift_function()
		self._set_lock_function()
		self._set_mode_function()
		self._scale_updated()

		# TODO: maybe clean this... this should be done on enable.
		# self.on_clip_slot_changed()

	def disconnect(self):
		self._clip = None

		self._lock_button = None
		self._shift_button = None
		self._quantization_button = None
		self._top_buttons = None
		self._side_buttons = None
		self._matrix = None

		self._loop_selector = None
		self._note_editor = None
		self._note_selector = None
		self._scale_selector = None
		self._track_controller = None

# SET FUNCTIONS
	def _set_mode_function(self):
		self._mode_button = None
		self.set_mode_button(self._side_buttons[3])
		self._last_mode_button_press = time.time()
		self._number_of_lines_per_note = 1

	def _set_lock_function(self):
		self._is_locked = False
		self._lock_to_track = False
		self._last_lock_button_press = time.time()
		self._long_press = 0.5
		self._lock_button = None
		self.set_lock_button(self._side_buttons[1])
		self._selected_track = None

	def _set_mute_shift_function(self):
		self._mute_shift_button = None
		self._last_mute_shift_button_press = time.time()
		self.set_mute_shift_button(self._side_buttons[7])
		self._is_mute_shifted = False

	def _set_quantization_function(self):
		self._quantization_index = 2
		self.set_quantization(QUANTIZATION_MAP[self._quantization_index])
		self._quantization_button = None
		self._last_quantize_button_press = time.time()
		self.set_quantization_button(self._side_buttons[2])

	def _set_loop_selector(self):
		self._loop_selector = self.register_component(LoopSelectorComponent(self, [
			self._matrix.get_button(4, 4), self._matrix.get_button(5, 4), self._matrix.get_button(6, 4), self._matrix.get_button(7, 4),
			self._matrix.get_button(4, 5), self._matrix.get_button(5, 5), self._matrix.get_button(6, 5), self._matrix.get_button(7, 5),
			self._matrix.get_button(4, 6), self._matrix.get_button(5, 6), self._matrix.get_button(6, 6), self._matrix.get_button(7, 6),
			self._matrix.get_button(4, 7), self._matrix.get_button(5, 7), self._matrix.get_button(6, 7), self._matrix.get_button(7, 7)],
			self._control_surface)
			)

	def _set_note_editor(self):
		self._note_editor = self.register_component(NoteEditorComponent(self, self._matrix, self._control_surface))
		self._note_editor.set_velocity_button(self._side_buttons[6])

	def _set_note_selector(self):
		self._note_selector = self.register_component(NoteSelectorComponent(self, [
			self._matrix.get_button(0, 7), self._matrix.get_button(1, 7), self._matrix.get_button(2, 7), self._matrix.get_button(3, 7),
			self._matrix.get_button(0, 6), self._matrix.get_button(1, 6), self._matrix.get_button(2, 6), self._matrix.get_button(3, 6),
			self._matrix.get_button(0, 5), self._matrix.get_button(1, 5), self._matrix.get_button(2, 5), self._matrix.get_button(3, 5),
			self._matrix.get_button(0, 4), self._matrix.get_button(1, 4), self._matrix.get_button(2, 4), self._matrix.get_button(3, 4)],
			self._control_surface)
			)
		self._note_selector.set_up_button(self._side_buttons[4])
		self._note_selector.set_down_button(self._side_buttons[5])

	def _set_track_controller(self):
		self._track_controller = self.register_component(TrackControllerComponent(self._control_surface))
		self._track_controller.set_prev_scene_button(self._top_buttons[0])
		self._track_controller.set_next_scene_button(self._top_buttons[1])
		self._track_controller.set_prev_track_button(self._top_buttons[2])
		self._track_controller.set_next_track_button(self._top_buttons[3])
		self._track_controller._implicit_arm = False

	def _set_scale_selector(self):
		self._scale_selector = self.register_component(ScaleComponent(self._control_surface))
		self._scale_selector.set_osd(self._osd)
		self._scale_selector.set_enabled(False)
		self._scale_selector.set_matrix(self._matrix)
		self._scale_selector._mode = "chromatic"
		self._scale_selector._drumrack = False
		self._scale_selector_button = None
		self.set_scale_selector_button(self._side_buttons[0])

	def set_osd(self, osd):
		self._osd = osd
		self._scale_selector.set_osd(osd)

	def _update_OSD(self):
		if self._osd != None:
			if self._mode == STEPSEQ_MODE_MULTINOTE:
				self._osd.set_mode('Drum Step Sequencer (multinote)')
			else:
				self._osd.set_mode('Drum Step Sequencer')

			if self._clip != None:
				self._osd.attributes[0] = MUSICAL_MODES[self._scale_selector._modus * 2]
				self._osd.attribute_names[0] = "Scale"
				self._osd.attributes[1] = KEY_NAMES[self._scale_selector._key % 12]
				self._osd.attribute_names[1] = "Root Note"
				self._osd.attributes[2] = self._scale_selector._octave
				self._osd.attribute_names[2] = "Octave"
				self._osd.attributes[3] = QUANTIZATION_NAMES[self._quantization_index]
				self._osd.attribute_names[3] = "Quantisation"
				self._osd.attributes[4] = " "
				self._osd.attribute_names[4] = " "
				self._osd.attributes[5] = " "
				self._osd.attribute_names[5] = " "
				self._osd.attributes[6] = " "
				self._osd.attribute_names[6] = " "
				self._osd.attributes[7] = " "
				self._osd.attribute_names[7] = " "
			else:
				self._osd.attributes[0] = " "
				self._osd.attribute_names[0] = " "
				self._osd.attributes[1] = " "
				self._osd.attribute_names[1] = " "
				self._osd.attributes[2] = " "
				self._osd.attribute_names[2] = " "
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

			if self._selected_track != None:
				if self._lock_to_track and self._is_locked:
					self._osd.info[0] = "track : " + self._selected_track.name + " (locked)"
				else:
					self._osd.info[0] = "track : " + self._selected_track.name
			else:
				self._osd.info[0] = " "
			if self._clip != None:
				name = self._clip.name
				if name == "":
					name = "(unamed clip)"
				if not self._lock_to_track and self._is_locked:
					self._osd.info[1] = "clip : " + name + " (locked)"
				else:
					self._osd.info[1] = "clip : " + name
			else:
				self._osd.info[1] = "no clip selected"
			self._osd.update()

	@property
	def _is_velocity_shifted(self):
		return self._note_editor._is_velocity_shifted

	def index_of(self, list, elt):
		for i in range(0, len(list)):
			if (list[i] == elt):
				return i
		return(-1)

# enabled
	def set_enabled(self, enabled):
		#self._control_surface.log_message("stepseq.set_mode:"+str(enabled))
		if enabled:
			if self._mode == STEPSEQ_MODE_SCALE_EDIT:
				self.set_mode(self._mode_backup)
			# clear note editor cache
			self._note_editor._force_update = True

			# todo: find a better way to init?
			if self._mode == -1:
				self._mode = STEPSEQ_MODE_NORMAL
				self._detect_scale_mode()

			# sync to selected pad
			self._update_drum_group_device()
			if(self._drum_group_device):
				self._note_selector.set_selected_note(self.index_of(self._drum_group_device.drum_pads,self._drum_group_device.view.selected_drum_pad))

			#load scale settings from clip
			if Settings.STEPSEQ__SAVE_SCALE != None and Settings.STEPSEQ__SAVE_SCALE == "clip":  
				self._scale_selector.from_object(self._clip)
				self._note_selector.set_scale(self._scale_selector.notes, self._scale_selector._key)
				self._note_selector.set_selected_note(self._scale_selector._octave * 12 + self._scale_selector._key)

			self._track_controller.set_enabled(enabled)	
			self._loop_selector.set_enabled(enabled)
			self._note_selector.set_enabled(enabled)
			self._note_editor.set_enabled(enabled)
			# update clip notes as they might have changed while we were sleeping
			self.on_clip_slot_changed()
			# call super.set_enabled()
			CompoundComponent.set_enabled(self, enabled)
			if self._clip != None and self._is_locked:
				self._control_surface.show_message("stepseq : clip '"+str(self._clip.name)+"'")
			self._on_notes_changed()
			self._update_OSD()

		else:
			self._track_controller.set_enabled(enabled)
			self._loop_selector.set_enabled(enabled)
			self._note_selector.set_enabled(enabled)
			self._note_editor.set_enabled(enabled)
			CompoundComponent.set_enabled(self, enabled)

	def set_mode(self, mode, number_of_lines_per_note=1):
		#self._control_surface.log_message("stepseq.set_mode:"+str(mode))
		if self._mode != mode or number_of_lines_per_note != self._number_of_lines_per_note:
			self._number_of_lines_per_note = number_of_lines_per_note
			self._note_editor.set_multinote(mode == STEPSEQ_MODE_MULTINOTE, number_of_lines_per_note)
			if mode == STEPSEQ_MODE_NORMAL:
				if self._mode != mode:
					# self._loop_selector._block = self._loop_selector._block * self._number_of_lines_per_note
					self._note_editor.set_page(self._loop_selector._block)
				self.set_left_button(None)
				self.set_right_button(None)
				self._track_controller.set_prev_track_button(self._top_buttons[2])
				self._track_controller.set_next_track_button(self._top_buttons[3])
			else:
				if self._mode != mode:
					# self._loop_selector._block = self._loop_selector._block / self._number_of_lines_per_note
					self._note_editor.set_page(self._loop_selector._block)
				self._track_controller.set_prev_track_button(None)
				self._track_controller.set_next_track_button(None)
				self.set_left_button(self._top_buttons[2])
				self.set_right_button(self._top_buttons[3])
			self._mode = mode
			self._note_editor._force_update = True
			self.update()

	def set_page(self, block):
		self._note_editor.set_page(block)
		self._note_editor.update()

# SCALE
	def _scale_updated(self):
		# self.log_message("scale updated")
		# self.log_message(str(self._note_selector.selected_note))
		keys = [0, 0, 0, 0, 0, 0, 0, 0]
		key_is_root_note = [False, False, False, False, False, False, False, False]
		key_is_in_scale = [False, False, False, False, False, False, False, False]
		if self._note_selector.is_drumrack:
			for i in range(8):
				keys[i] = self._note_selector.selected_note + i
				key_is_root_note[i] = (keys[i] + 12 + 16) % 16 == 0
				key_is_in_scale[i] = (keys[i] + 12 + 16) % 4 == 0
		elif self._note_selector.is_diatonic:
			self._note_selector._scale_length = len(self._note_selector._scale)
			try:
				idx = self._note_selector._scale.index(self._note_selector._offset)
			except ValueError:
				idx = -1
			if(idx == -1):
				self.log_message("not found : " + str(self._note_selector._offset) + " in " + str(self._note_selector._scale))
				for i in range(8):
					keys[i] = self._note_selector._root_note + self._note_selector._offset + i
			else:
				for i in range(8):
					keys[i] = self._note_selector._root_note + self._note_selector._scale[(i + idx) % self._note_selector._scale_length] + ((i + idx) / self._note_selector._scale_length) * 12
					key_is_root_note[i] = (keys[i] + 12) % 12 == self._note_selector._key
					key_is_in_scale[i] = True
		else:
			for i in range(8):
				keys[i] = self._note_selector.selected_note + i
				key_is_root_note[i] = (keys[i] + 12) % 12 == self._note_selector._key
				key_is_in_scale[i] = (keys[i] - self._note_selector._key + 12) % 12 in self._note_selector._scale

		self._note_editor.set_key_indexes(keys)
		self._note_editor.set_key_index_is_in_scale(key_is_in_scale)
		self._note_editor.set_key_index_is_root_note(key_is_root_note)
		self._note_editor.update()

# UPDATE
	def update(self):
		if self.is_enabled():
			#self._control_surface.log_message("stepseq.update:")
			self._update_track_controller()
			self._update_scale_selector()
			self._update_loop_selector()
			self._update_note_selector()
			self._update_buttons()
			self._update_note_editor()
			self._update_OSD()
			# show clip !
			if not self._is_locked and self._clip != None:
				if ((not self.application().view.is_view_visible('Detail')) or (not self.application().view.is_view_visible('Detail/Clip'))):
					self.application().view.show_view('Detail')
					self.application().view.show_view('Detail/Clip')

	def _update_track_controller(self):
		self._track_controller.set_enabled(self.is_enabled())
		self._track_controller.update()

	def _update_scale_selector(self):
		self._scale_selector.set_enabled(self._mode == STEPSEQ_MODE_SCALE_EDIT)
		self._scale_selector.update()

	def _update_loop_selector(self):
		self._loop_selector.set_enabled(self._mode == STEPSEQ_MODE_NORMAL)
		self._loop_selector.update()

	def _update_note_selector(self):
		self._note_selector._enable_offset_button = self._mode == STEPSEQ_MODE_NORMAL
		self._note_selector.set_enabled(self._mode != STEPSEQ_MODE_SCALE_EDIT)
		self._note_selector.update()

	def _update_note_editor(self):
		self._note_editor.set_multinote(self._mode == STEPSEQ_MODE_MULTINOTE, self._number_of_lines_per_note)
		if self._mode == STEPSEQ_MODE_NORMAL:
			self._note_editor.set_height(self._height - 4)
		else:
			self._note_editor.set_height(self._height)
		self._note_editor.set_enabled(self._mode != STEPSEQ_MODE_SCALE_EDIT)
		self._note_editor.update()

	def _update_buttons(self):
		self._update_quantization_button()
		self._update_lock_button()
		self._update_mode_button()
		self._update_mute_shift_button()
		self._update_scale_selector_button()
		self._update_left_button()
		self._update_right_button()


# CLIP CALLBACKS

	def on_track_list_changed(self):
		self.on_selected_track_changed()

	def on_scene_list_changed(self):
		self.on_selected_scene_changed()

	def on_selected_scene_changed(self):
		self.on_clip_slot_changed()
		self.update()

	def on_selected_track_changed(self):
		if not self._is_locked or self._clip == None:
			self._detect_scale_mode()
			self.on_clip_slot_changed()
			self.update()

	def _on_loop_changed(self):
		if self.is_enabled() and self._clip != None:
			self._loop_selector._get_clip_loop()

	def on_clip_slot_has_clip_changed(self):
		# the clip was deleted. unlock.
		if not self._clip_slot.has_clip:
			self._is_locked = False
		self.on_clip_slot_changed()
		self.update()

	def on_clip_slot_changed(self, scheduled=False):

		# get old reference to clipslot
		clip_slot = self._clip_slot

		# update track if not track locked
		if not self._is_locked or self._selected_track == None:
			self._selected_track = self.song().view.selected_track

		# update scene
		if self._selected_track != None:
			idx = -1
			if self._lock_to_track and self._is_locked:
				# track locked mode

				# schedule a refresh as scene fire happens after scene selection
				# so that we can catch the clip scheduled for playing
				if not scheduled:
					self._control_surface.schedule_message(5, self.on_clip_slot_changed, (True))

				# locate with clip pending fire
				for i in range(len(self.song().scenes)):
					if self._selected_track.clip_slots[i].has_clip and self._selected_track.clip_slots[i].clip.is_triggered:
						idx = i
				# no tirggered clip, locate with playing clip
				if idx == -1:
					for i in range(len(self.song().scenes)):
						if self._selected_track.clip_slots[i].has_clip and self._selected_track.clip_slots[i].clip.is_playing:
							idx = i
				# fallback: use scene selection
				if idx == -1:
					try:
						idx = list(self.song().scenes).index(self.song().view.selected_scene)
					except ValueError: 
						idx = -1

			# unlocked mode
			if not self._is_locked:
				try:
					idx = list(self.song().scenes).index(self.song().view.selected_scene)
				except ValueError:
					idx = -1
			if(idx != -1 and idx < len(list(self._selected_track.clip_slots))):
				clip_slot = self._selected_track.clip_slots[idx]

		# update clip slot
		if clip_slot != self._clip_slot or self._clip_slot == None:
			# self._control_surface.log_message("update clip_slot")
			if clip_slot != None and clip_slot.has_clip_has_listener(self.on_clip_slot_has_clip_changed):
				clip_slot.remove_has_clip_listener(self.on_clip_slot_has_clip_changed)
			self._clip_slot = clip_slot
			if self._clip_slot != None:
				if self._clip_slot.has_clip_has_listener(self.on_clip_slot_has_clip_changed):
					self._clip_slot.remove_has_clip_listener(self.on_clip_slot_has_clip_changed)
				self._clip_slot.add_has_clip_listener(self.on_clip_slot_has_clip_changed)

		if self._clip_slot != None and self._clip_slot.has_clip and self._clip_slot.clip != None and self._clip_slot.clip.is_midi_clip:
			if self._clip == None or self._clip != self._clip_slot.clip:
				# self._control_surface.log_message("link clip_slot")
				# unlink
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
				
				#load scale settings from clip
				if Settings.STEPSEQ__SAVE_SCALE != None and Settings.STEPSEQ__SAVE_SCALE == "clip":  
					self._scale_selector.from_object(self._clip_slot.clip)
					#must set clip to None otherwise it trigger a clip note update which we dont want.
					self._clip = None
					self._note_editor._clip = None
					self._note_selector.set_scale(self._scale_selector.notes, self._scale_selector._key)
					#self._control_surface.schedule_message(1, self._note_selector.set_selected_note,(self._scale_selector,self._scale_selector._octave * 12 + self._scale_selector._key))
					self._note_selector.set_selected_note(self._scale_selector._octave * 12 + self._scale_selector._key)
				
				# link new clip
				self._clip_slot.clip.add_notes_listener(self._on_notes_changed)
				self._clip_slot.clip.add_playing_status_listener(self._on_playing_status_changed)
				self._clip_slot.clip.add_playing_position_listener(self._on_playing_position_changed)
				self._clip_slot.clip.add_loop_start_listener(self._on_loop_changed)
				self._clip_slot.clip.add_loop_end_listener(self._on_loop_changed)
				
				# publish
				self._clip = self._clip_slot.clip
						
				# update
				#if scheduled:
				self._clip_changed()
				#else:
				#self._control_surface.schedule_message(1, self._clip_changed)
			else:
				# same clip...
				pass
				# self._control_surface.log_message("same clip. pass.")

		else:
			# self._control_surface.log_message("empty clip_slot or no clip_slot. cleanup")
			# unlink
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

			# publish
			self._clip = None
			self._clip_changed()

	def _clip_changed(self):  # triggered by _on_clip_slot_changed() or manually on enable.
		self._note_editor.set_clip(self._clip)
		self._note_selector.set_clip(self._clip)
		self._loop_selector.set_clip(self._clip)
		self._note_editor.set_playhead(None)
		self._note_selector.set_playhead(None)
		self._loop_selector.set_playhead(None)
		# reload notes
		self._on_notes_changed()

	def _on_notes_changed(self):  # trigger by callback on clip or via _clip_changed.
		if self.is_enabled():
			# get notes
			if self._clip == None:
				note_cache = []
			else:
				self._clip.select_all_notes()
				note_cache = self._clip.get_selected_notes()
				self._clip.deselect_all_notes()

			# update if needed
			if note_cache != self._note_cache:
				self._note_cache = note_cache
				self._note_editor.set_note_cache(self._note_cache)
				self._note_selector.set_note_cache(self._note_cache)
				self._loop_selector.set_note_cache(self._note_cache)
				self._note_editor.update()

# PLAY POSITION
	def _on_playing_status_changed(self):  # playing status changed listener
		if self.is_enabled():
			self._on_playing_position_changed()

	def _on_playing_position_changed(self):  # playing position changed listener
		if self.is_enabled():
			if self._clip != None and self._clip.is_playing and self.song().is_playing:
				self._playhead = self._clip.playing_position
			else:
				self._playhead = None
			self._loop_selector.set_playhead(self._playhead)
			self._note_selector.set_playhead(self._playhead)
			self._note_editor.set_playhead(self._playhead)

# DRUM_GROUP_DEVICE
	def _update_drum_group_device(self):
		if self.song().view.selected_track != None:
			track = self.song().view.selected_track
			if(track.devices != None and len(track.devices) > 0):
				#device = track.devices[0]
				device = self.find_drum_group_device(track)
				if(device!= None and device.can_have_drum_pads and device.has_drum_pads):
					self._drum_group_device = device
				else:
					self._drum_group_device = None
			else:
				self._drum_group_device = None
		else:
			self._drum_group_device = None

	def _detect_scale_mode(self):
		if not self._is_locked:
			self._update_drum_group_device()
			self._scale_selector.set_drumrack(self._drum_group_device != None)
	
	def find_drum_group_device(self, track):
		device = find_if(lambda d: d.type == Live.Device.DeviceType.instrument, track.devices)
		if device:
			if device.can_have_drum_pads:
				return device
			elif device.can_have_chains:
				return find_if(bool, imap(self.find_drum_group_device, device.chains))
		else:
			return None

# SCALE Selector Button
	def _update_scale_selector_button(self):
		if self.is_enabled():
			if (self._scale_selector_button != None):
				if self._clip != None:
					self._scale_selector_button.set_on_off_values("StepSequencer.Scale")
				else:
					self._scale_selector_button.set_on_off_values("DefaultButton.Disabled","DefaultButton.Disabled")
				if self._mode == STEPSEQ_MODE_SCALE_EDIT:
					self._scale_selector_button.turn_on()
					self._osd.set_mode('Scale')
				else:
					self._scale_selector_button.turn_off()

	def set_scale_selector_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._scale_selector_button != button):
			if (self._scale_selector_button != None):
				self._scale_selector_button.remove_value_listener(self._scale_selector_button_value)
			self._scale_selector_button = button
			if (self._scale_selector_button != None):
				assert isinstance(button, ButtonElement)
				self._scale_selector_button.add_value_listener(self._scale_selector_button_value)

	def _scale_selector_button_value(self, value):
		assert (value in range(128))
		if self.is_enabled():

			if value > 0:
				self._mode_backup = self._mode
				if self._scale_selector != None and self._note_selector != None:
					self._scale_selector.set_octave(self._note_selector._root_note / 12)
					self._scale_selector.set_key(self._note_selector._key)
					self.set_mode(STEPSEQ_MODE_SCALE_EDIT)
			else:
				if self._scale_selector != None and self._note_selector != None:
					self._note_selector.set_scale(self._scale_selector.notes, self._scale_selector._key)
					self._note_selector.set_selected_note(self._scale_selector._octave * 12 + self._scale_selector._key)
					self._scale_updated()
					#update clip name
					if Settings.STEPSEQ__SAVE_SCALE != None and Settings.STEPSEQ__SAVE_SCALE == "clip":  
						self._scale_selector.update_object_name(self._clip)
				self.set_mode(self._mode_backup)


# MUTE SHIFT Button
	def set_mute_shift_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._mute_shift_button != button):
			if (self._mute_shift_button != None):
				self._mute_shift_button.remove_value_listener(self._mute_shift_button_value)
			self._mute_shift_button = button
			if (self._mute_shift_button != None):
				assert isinstance(button, ButtonElement)
				self._mute_shift_button.add_value_listener(self._mute_shift_button_value, identify_sender=True)

	
	def _update_mute_shift_button(self):
	 		if self.is_enabled() and self._mute_shift_button != None:
	 			if self._clip != None and self._clip.is_midi_clip:
	 				self._mute_shift_button.set_on_off_values("StepSequencer.Mute")
	 				if self._is_mute_shifted:
	 					self._mute_shift_button.turn_on()
	 				else:
	 					self._mute_shift_button.turn_off()
	 			else:
	 				self._mute_shift_button.set_light("DefaultButton.Disabled")
	
	def _mute_shift_button_value(self, value, sender):
		assert (self._mute_shift_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			now = time.time()
			if ((value is not 0) or (not sender.is_momentary())):
				self._is_mute_shifted = not self._is_mute_shifted
			else:
				if now - self._last_mute_shift_button_press> 0.25:
					self._is_mute_shifted = not self._is_mute_shifted
				self._last_mute_shift_button_press = now
				
			self._note_editor._is_mute_shifted = self._is_mute_shifted
			self._update_mute_shift_button()
			


# MODE
	def _update_mode_button(self):
		if self.is_enabled():
			if (self._mode_button != None):
				if self._clip != None:
					self._mode_button.set_on_off_values("StepSequencer.Mode")
					if self._mode == STEPSEQ_MODE_MULTINOTE:
						self._mode_button.turn_on()
						self._osd.update()
					else:
						self._mode_button.turn_off()
						self._osd.update()
				else:
					self._mode_button.set_light("DefaultButton.Disabled")

	def set_mode_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._mode_button != button):
			if (self._mode_button != None):
				self._mode_button.remove_value_listener(self._mode_button_value)
			self._mode_button = button
			if (self._mode_button != None):
				assert isinstance(button, ButtonElement)
				self._mode_button.add_value_listener(self._mode_button_value, identify_sender=True)

	def _mode_button_value(self, value, sender):
		assert (self._mode_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._last_mode_button_press = time.time()
			else:
				if self._mode == STEPSEQ_MODE_MULTINOTE and time.time() - self._last_mode_button_press > 0.25:
					if(self._number_of_lines_per_note == 1):
						number_of_lines_per_note = 2
					else:
						number_of_lines_per_note = 1
					self.set_mode(STEPSEQ_MODE_MULTINOTE, number_of_lines_per_note)

				elif self._mode != STEPSEQ_MODE_MULTINOTE:
					self.set_mode(STEPSEQ_MODE_MULTINOTE, self._number_of_lines_per_note)

				else:
					self.set_mode(STEPSEQ_MODE_NORMAL, self._number_of_lines_per_note)

# QUANTIZE
	def _update_quantization_button(self):
		if self.is_enabled():
			if (self._quantization_button != None):
				if self._clip != None:
					self._quantization_button.set_light(self.QUANTIZATION_COLOR_MAP[self._quantization_index])
					self._quantization_button.turn_on()
				else:
					self._quantization_button.set_light("DefaultButton.Disabled")
					self._quantization_button.turn_off()

	def set_quantization_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._quantization_button != button):
			if (self._quantization_button != None):
				self._quantization_button.remove_value_listener(self._quantization_button_value)
			self._quantization_button = button
			if (self._quantization_button != None):
				assert isinstance(button, ButtonElement)
				self._quantization_button.add_value_listener(self._quantization_button_value, identify_sender=True)

	def _quantization_button_value(self, value, sender):
		assert (self._quantization_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			now = time.time()
			if ((value is not 0) or (not sender.is_momentary())):
				self._last_quantize_button_press = now
			else:
				if now - self._last_quantize_button_press > 0.5:
					self._control_surface.show_message("stepseq : duplicate clip")
					self.duplicate_clip()
				else:
					if(self._mode == STEPSEQ_MODE_SCALE_EDIT):
						self._quantization_index = (self._quantization_index - 1+len(QUANTIZATION_MAP)) % len(QUANTIZATION_MAP)
					else:
						self._quantization_index = (self._quantization_index + 1) % len(QUANTIZATION_MAP)
					self.set_quantization(QUANTIZATION_MAP[self._quantization_index])
					self._control_surface.show_message("quantisation : "+QUANTIZATION_NAMES[self._quantization_index])
					self._update_quantization_button()

	def set_quantization(self, quantization):
		self._quantization = quantization
		if self._note_editor != None:
			self._note_editor.set_quantization(self._quantization)
		if self._loop_selector != None:
			self._loop_selector.update()
		if self._note_selector != None:
			self._note_selector.update()
		if self._note_editor != None:
			self._note_editor.update()
		self._update_OSD()

# LOCK Button
	def _update_lock_button(self):
		if self.is_enabled():
			if self._lock_button != None:
				if self._clip != None:
					if self._lock_to_track:
						self._lock_button.set_on_off_values("StepSequencer.Lock.ToTrack")
					else:
						self._lock_button.set_on_off_values("StepSequencer.Lock.ToClip")
					if self._is_locked:
						self._lock_button.turn_on()
					else:
						self._lock_button.turn_off()
				else:
					self._lock_button.set_light("DefaultButton.Disable")

	def set_lock_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (button != self._lock_button):
			if (self._lock_button != None):
				self._lock_button.remove_value_listener(self._lock_value)
			self._lock_button = button
			if (self._lock_button != None):
				self._lock_button.add_value_listener(self._lock_value, identify_sender=True)

	def _lock_value(self, value, sender):
		assert (self._lock_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			now = time.time() 
			if ((value != 0) or (not self._lock_button.is_momentary())):
				self._last_lock_button_press = now
			else:
				if now - self._last_lock_button_press > self._long_press:
					self._lock_to_track = (not self._lock_to_track)
					if not self._is_locked:
						self._control_surface.show_message("stepseq : locked to clip '"+str(self._clip.name)+"'")
						self._is_locked = True
					self._update_lock_button()
				else:
					self._is_locked = (not self._is_locked)
					if self._is_locked:
						self._control_surface.show_message("stepseq : locked to clip '"+str(self._clip.name)+"'")
					self._update_lock_button()
					self._update_OSD()


# RIGHT Button
	def _update_right_button(self):
		if self.is_enabled():
			if self._right_button != None:
				if self._clip != None:
					self._right_button.set_on_off_values("DefaultButton")
					if self._loop_selector.can_scroll(1):
						self._right_button.turn_on()
					else:
						self._right_button.turn_off()
				else:
					self._right_button.set_light("DefaultButton.Disabled")

	def set_right_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (button != self._right_button):
			if (self._right_button != None):
				self._right_button.remove_value_listener(self._right_value)
			self._right_button = button
			if (self._right_button != None):
				self._right_button.add_value_listener(self._right_value, identify_sender=True)

	def _right_value(self, value, sender):
		assert (self._right_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._loop_selector.scroll(1)
				self._note_editor.request_display_page()
				self.update()

# LEFT Button
	def _update_left_button(self):
		if self.is_enabled():
			if self._left_button != None:
				if self._clip != None:
					self._left_button.set_on_off_values("DefaultButton")
					if self._loop_selector.can_scroll(-1):
						self._left_button.turn_on()
					else:
						self._left_button.turn_off()
				else:
					self._left_button.set_light("DefaultButton.Disabled")

	def set_left_button(self, button):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (button != self._left_button):
			if (self._left_button != None):
				self._left_button.remove_value_listener(self._left_value)
			self._left_button = button
			if (self._left_button != None):
				self._left_button.add_value_listener(self._left_value, identify_sender=True)

	def _left_value(self, value, sender):
		assert (self._right_button != None)
		assert (value in range(128))
		if self.is_enabled() and self._clip != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._loop_selector.scroll(-1)
				self._note_editor.request_display_page()
				self.update()


# UTILS

	def create_clip(self):
		if self.song().view.highlighted_clip_slot != None:
			clip_slot = self.song().view.highlighted_clip_slot
			if not clip_slot.has_clip:
				if self._mode == STEPSEQ_MODE_NORMAL:
					clip_slot.create_clip(QUANTIZATION_MAP[self._quantization_index] * 8 * 4)
				else:
					clip_slot.create_clip(QUANTIZATION_MAP[self._quantization_index] * 8)
				self._detect_scale_mode()
				clip_slot.fire()
				self.on_clip_slot_changed()
				self.update()

	def duplicate_clip(self):
		if self._clip_slot and self._clip_slot.has_clip:
			try:
				if not self._is_locked or self._lock_to_track:
					track = self._clip_slot.canonical_parent
					newIdx = track.duplicate_clip_slot(list(track.clip_slots).index(self._clip_slot))
					self.song().view.selected_scene = self.song().scenes[newIdx]
					if track.clip_slots[newIdx] != None:
						track.clip_slots[newIdx].fire()
					self.on_clip_slot_changed()
					self.update()
			except Live.Base.LimitationError:
				pass
			except RuntimeError:
				pass
