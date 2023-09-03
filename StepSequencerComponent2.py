from .MelodicNoteEditorComponent import MelodicNoteEditorComponent, \
	STEPSEQ_MODE_NOTES, STEPSEQ_MODE_NOTES_OCTAVES, \
	STEPSEQ_MODE_NOTES_VELOCITIES, STEPSEQ_MODE_NOTES_LENGTHS
from .StepSequencerComponent import StepSequencerComponent, QUANTIZATION_NAMES
from .LoopSelectorComponent import LoopSelectorComponent
from .NoteSelectorComponent import NoteSelectorComponent
from .ScaleComponent import MUSICAL_MODES, KEY_NAMES
from .TrackControllerComponent import TrackControllerComponent

LONG_BUTTON_PRESS = 1.0

# TODO :
# extend / clear region (possible via drum step seq for now)
# not even clip lengths (using shift notes ?)
# store scale settings per clip or track ?
# display current scale mode in osd


class StepSequencerComponent2(StepSequencerComponent):

	def __init__(self, matrix, side_buttons, top_buttons, control_surface):
		super(StepSequencerComponent2, self).__init__(matrix, side_buttons, top_buttons, control_surface)
		self._new_clip_pages = 1
		self._name = "melodic step sequencer"
		
		
	def _set_scale_selector(self):
		super(StepSequencerComponent2, self)._set_scale_selector()
		self._scale_selector._mode = "diatonic"
		self._scale_selector._drumrack = False

	def _set_track_controller(self):
		self._track_controller = self.register_component(TrackControllerComponent(self._control_surface, implicit_arm = False))
		self._track_controller.set_prev_scene_button(self._top_buttons[0])
		self._track_controller.set_next_scene_button(self._top_buttons[1])
		self._track_controller.set_prev_track_button(self._top_buttons[2])
		self._track_controller.set_next_track_button(self._top_buttons[3])

	def _set_note_editor(self):
		self._note_editor = self.register_component(
			MelodicNoteEditorComponent(self, self._matrix, self._side_buttons, self._control_surface))

	def _set_mute_shift_function(self):
		self._is_mute_shifted = False
			
	def _set_note_selector(self):
		self._note_selector = self.register_component(NoteSelectorComponent(self, [], self._control_surface))

	def _set_loop_selector(self):
		self._loop_selector = self.register_component(LoopSelectorComponent(self, [
			self._matrix.get_button(0, 7), self._matrix.get_button(1, 7), self._matrix.get_button(2, 7), self._matrix.get_button(3, 7),
			self._matrix.get_button(4, 7), self._matrix.get_button(5, 7), self._matrix.get_button(6, 7), self._matrix.get_button(7, 7)
		],self._control_surface))
		self.set_left_button(self._top_buttons[2])
		self.set_right_button(self._top_buttons[3])

	def _update_buttons(self):
		self._update_quantization_button()
		self._update_lock_button()
		self._update_scale_selector_button()
		self._update_left_button()
		self._update_right_button()

	def _update_drum_group_device(self):
		# no drum rack mode for me. i am a melodic step seq.
		self._drum_group_device = None

	def _update_OSD(self):
		if self._osd != None:
			self._osd.set_mode('Melodic Step Sequencer')
			if self._clip != None:
				self._osd.attributes[0] = MUSICAL_MODES[self._scale_selector._modus * 2]
				self._osd.attribute_names[0] = "Scale"
				self._osd.attributes[1] = KEY_NAMES[self._scale_selector._key % 12]
				self._osd.attribute_names[1] = "Root Note"
				self._osd.attributes[2] = self._scale_selector._octave
				self._osd.attribute_names[2] = "Octave"
				self._osd.attributes[3] = QUANTIZATION_NAMES[self._quantization_index]
				self._osd.attribute_names[3] = "Quantisation"
				if self._note_editor._is_monophonic:
					self._osd.attributes[4] = "Mono"
				else:
					self._osd.attributes[4] = "Poly"
				self._osd.attribute_names[4] = "Polyphony"

				self._osd.attribute_names[5] = "Page"
				if self._note_editor._mode == STEPSEQ_MODE_NOTES:
					self._osd.attributes[5] = "Notes"
				elif self._note_editor._mode == STEPSEQ_MODE_NOTES_OCTAVES:
					self._osd.attributes[5] = "Octave"
				elif self._note_editor._mode == STEPSEQ_MODE_NOTES_VELOCITIES:
					self._osd.attributes[5] = "Velocity"
				elif self._note_editor._mode == STEPSEQ_MODE_NOTES_LENGTHS:
					self._osd.attributes[5] = "Length"

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

	def _update_mode_button(self):
		if self.is_enabled():
			if (self._mode_button != None):
				self._mode_button.set_on_off_values("DefaultButton.Disaled")

	def _mode_button_value(self, value, sender):
		pass
