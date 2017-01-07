from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.SessionComponent import SessionComponent
from SpecialMixerComponent import SpecialMixerComponent
from PreciseButtonSliderElement import PreciseButtonSliderElement, SLIDER_MODE_VOLUME, SLIDER_MODE_PAN
PAN_VALUE_MAP = (-1.0, -0.634921, -0.31746, 0.0, 0.0, 0.31746, 0.634921, 1.0)
VOL_VALUE_MAP = (0.0, 0.142882, 0.302414, 0.4, 0.55, 0.7, 0.85, 1.0)
SEND_VALUE_MAP = (0.0, 0.103536, 0.164219, 0.238439, 0.343664, 0.55, 0.774942, 1.0)


#SubSelector for Mixer Mode (Allow to select mixing sub modes: Vol, Pan, Snd, Stop, etc)
class SubSelectorComponent(ModeSelectorComponent):

	""" Class that handles different mixer modes """

	def __init__(self, matrix, side_buttons, session, control_surface):
		assert isinstance(matrix, ButtonMatrixElement)
		assert ((matrix.width() == 8) and (matrix.height() == 8))
		assert isinstance(side_buttons, tuple)
		assert (len(side_buttons) == 8)
		assert isinstance(session, SessionComponent)
		ModeSelectorComponent.__init__(self)
		self._control_surface = control_surface
		self._session = session
		self._mixer = SpecialMixerComponent(matrix.width())
		self._matrix = matrix
		self._sliders = []
		self._mixer.name = 'Mixer'
		self._mixer.master_strip().name = 'Master_Channel_strip'
		self._mixer.selected_strip().name = 'Selected_Channel_strip'
		for column in range(matrix.width()):
			self._mixer.channel_strip(column).name = 'Channel_Strip_' + str(column)
			self._sliders.append(PreciseButtonSliderElement(tuple([matrix.get_button(column, 7 - row) for row in range(8)])))
			self._sliders[-1].name = 'Button_Slider_' + str(column)

		self._side_buttons = side_buttons[4:]
		self._update_callback = None
		self._session.set_mixer(self._mixer)
		self.set_modes_buttons(side_buttons[:4])

	def disconnect(self):
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)

		self._session = None
		self._mixer = None
		for slider in self._sliders:
			slider.release_parameter()
			slider.set_disabled(True)

		self._sliders = None
		self._matrix = None
		self._side_buttons = None
		self._update_callback = None
		ModeSelectorComponent.disconnect(self)

	def set_update_callback(self, callback):
		assert (dir(callback).count("im_func") is 1)
		self._update_callback = callback

	def set_modes_buttons(self, buttons):
		assert ((buttons == None) or (isinstance(buttons, tuple)))
		assert (len(buttons) == self.number_of_modes())
		identify_sender = True
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)

		self._modes_buttons = []
		if buttons != None:
			for button in buttons:
				assert isinstance(button, ButtonElement)
				self._modes_buttons.append(button)
				button.add_value_listener(self._mode_value, identify_sender)

	def set_mode(self, mode):
		assert isinstance(mode, int)
		assert (mode in range(-1, self.number_of_modes()))
		if ((self._mode_index != mode) or (mode == -1)):
			self._mode_index = mode
			self.update()

	def mode(self):
		result = 0
		if self.is_enabled():
			result = self._mode_index + 1
		return result

	def number_of_modes(self):
		return 4

	def on_enabled_changed(self):
		enabled = self.is_enabled()
		for index in range(self._matrix.width()):
			self._sliders[index].set_disabled(not enabled)

		self._mixer.set_enabled(enabled)
		self.set_mode(-1)

	def release_controls(self):
		for track in range(self._matrix.width()):
			for row in range(self._matrix.height()):
				self._matrix.get_button(track, row).set_on_off_values(127, "DefaultButton.Disabled")

			strip = self._mixer.channel_strip(track)
			strip.set_default_buttons(None, None, None, None)
			strip.set_mute_button(None)
			strip.set_solo_button(None)
			strip.set_arm_button(None)
			strip.set_send_controls((None, None))
			strip.set_pan_control(None)
			strip.set_volume_control(None)

		self._session.set_stop_track_clip_buttons(None)
		self._mixer.set_global_buttons(None, None, None)
		self._session.set_stop_all_clips_button(None)

	def update(self):
		super(SubSelectorComponent, self).update()
		assert (self._modes_buttons != None)
		if self.is_enabled():
			if (self._modes_buttons != None):
				for index in range(len(self._modes_buttons)):
					button = self._modes_buttons[index]
					if index == 0:
						button.set_on_off_values("Mixer.Volume")
					elif index == 1:
						button.set_on_off_values("Mixer.Pan")
					elif index == 2:
						button.set_on_off_values("Mixer.Sends")
					elif index == 3:
						button.set_on_off_values("Mixer.Sends")
					if (index == self._mode_index):
						button.turn_off()
					else:
						button.turn_on()

			for button in self._side_buttons:
				button.set_on_off_values(127, "DefaultButton.Disabled")
				button.turn_off()

			for index in range(self._matrix.width()):
				self._sliders[index].set_disabled((self._mode_index == -1))

			self._mixer.set_allow_update(False)
			self._session.set_allow_update(False)
			if self._mode_index == -1:
				self._setup_mixer_overview()
			elif self._mode_index == 0:
				self._setup_volume_mode()
			elif self._mode_index == 1:
				self._setup_pan_mode()
			elif self._mode_index == 2:
				self._setup_send1_mode()
			elif self._mode_index == 3:
				self._setup_send2_mode()
			else:
				assert False
			if (self._update_callback != None):
				self._update_callback()
			self._mixer.set_allow_update(True)
			self._session.set_allow_update(True)
		else:
			self.release_controls()

	def _setup_mixer_overview(self):
		stop_buttons = []
		for track in range(self._matrix.width()):
			strip = self._mixer.channel_strip(track)
			strip.set_send_controls((None, None))
			strip.set_pan_control(None)
			strip.set_volume_control(None)
			self._sliders[track].release_parameter()
			for row in range(self._matrix.height()):
				if row == 0:
					self._matrix.get_button(track, row).set_on_off_values("Mixer.Volume")
				elif row == 1:
					self._matrix.get_button(track, row).set_on_off_values("Mixer.Pan")
				elif row == 2:
					self._matrix.get_button(track, row).set_on_off_values("Mixer.Sends")
				elif row == 3:
					self._matrix.get_button(track, row).set_on_off_values("Mixer.Sends")
				elif row == 4:
					self._matrix.get_button(track, row).set_on_off_values("Mixer.Stop")
				elif row == 5:
					self._matrix.get_button(track, row).set_on_off_values("Mixer.Mute")
				elif row == 6:
					self._matrix.get_button(track, row).set_on_off_values("Mixer.Solo")
				elif row == 7:
					self._matrix.get_button(track, row).set_on_off_values("Mixer.Arm")

			strip.set_default_buttons(self._matrix.get_button(track, 0), self._matrix.get_button(track, 1), self._matrix.get_button(track, 2), self._matrix.get_button(track, 3))
			stop_buttons.append(self._matrix.get_button(track, 4))
			strip.set_mute_button(self._matrix.get_button(track, 5))
			strip.set_solo_button(self._matrix.get_button(track, 6))
			strip.set_arm_button(self._matrix.get_button(track, 7))

			for button in self._side_buttons:
				if list(self._side_buttons).index(button) == 0:
					button.set_on_off_values("Mixer.Stop")
				elif list(self._side_buttons).index(button) == 1:
					button.set_on_off_values("Mixer.Mute")
				elif list(self._side_buttons).index(button) == 2:
					button.set_on_off_values("Mixer.Solo")
				elif list(self._side_buttons).index(button) == 3:
					button.set_on_off_values("Mixer.Arm") 
				
			button.force_next_send()
			button.turn_off()

		self._session.set_stop_track_clip_buttons(tuple(stop_buttons))
		self._session.set_stop_all_clips_button(self._side_buttons[0])
		self._mixer.set_global_buttons(self._side_buttons[3], self._side_buttons[2], self._side_buttons[1])

	def _setup_volume_mode(self):
		for track in range(self._matrix.width()):
			strip = self._mixer.channel_strip(track)
			strip.set_default_buttons(None, None, None, None)
			strip.set_mute_button(None)
			strip.set_solo_button(None)
			strip.set_arm_button(None)
			strip.set_send_controls((None, None))
			strip.set_pan_control(None)
			for row in range(self._matrix.height()):
				self._matrix.get_button(track, row).set_on_off_values("Mixer.VolumeSlider")

			self._sliders[track].set_mode(SLIDER_MODE_VOLUME)
			self._sliders[track].set_value_map(VOL_VALUE_MAP)
			strip.set_volume_control(self._sliders[track])

		self._session.set_stop_track_clip_buttons(None)
		self._session.set_stop_all_clips_button(None)
		self._mixer.set_global_buttons(None, None, None)

	def _setup_pan_mode(self):
		for track in range(self._matrix.width()):
			strip = self._mixer.channel_strip(track)
			strip.set_default_buttons(None, None, None, None)
			strip.set_mute_button(None)
			strip.set_solo_button(None)
			strip.set_arm_button(None)
			strip.set_send_controls((None, None))
			strip.set_volume_control(None)
			for row in range(self._matrix.height()):
				self._matrix.get_button(track, row).set_on_off_values("Mixer.PanSlider")

			self._sliders[track].set_mode(SLIDER_MODE_PAN)
			self._sliders[track].set_value_map(PAN_VALUE_MAP)
			strip.set_pan_control(self._sliders[track])

		self._session.set_stop_track_clip_buttons(None)
		self._session.set_stop_all_clips_button(None)
		self._mixer.set_global_buttons(None, None, None)

	def _setup_send1_mode(self):
		for track in range(self._matrix.width()):
			strip = self._mixer.channel_strip(track)
			strip.set_default_buttons(None, None, None, None)
			strip.set_mute_button(None)
			strip.set_solo_button(None)
			strip.set_arm_button(None)
			strip.set_volume_control(None)
			strip.set_pan_control(None)
			for row in range(self._matrix.height()):
				self._matrix.get_button(track, row).set_on_off_values("Mixer.SendsSlider_1")

			self._sliders[track].set_mode(SLIDER_MODE_VOLUME)
			self._sliders[track].set_value_map(SEND_VALUE_MAP)
			strip.set_send_controls((self._sliders[track], None))

		self._session.set_stop_track_clip_buttons(None)
		self._session.set_stop_all_clips_button(None)
		self._mixer.set_global_buttons(None, None, None)

	def _setup_send2_mode(self):
		for track in range(self._matrix.width()):
			strip = self._mixer.channel_strip(track)
			strip.set_default_buttons(None, None, None, None)
			strip.set_mute_button(None)
			strip.set_solo_button(None)
			strip.set_arm_button(None)
			strip.set_volume_control(None)
			strip.set_pan_control(None)
			for row in range(self._matrix.height()):
				self._matrix.get_button(track, row).set_on_off_values("Mixer.SendsSlider_2")

			self._sliders[track].set_mode(SLIDER_MODE_VOLUME)
			self._sliders[track].set_value_map(SEND_VALUE_MAP)
			strip.set_send_controls((None, self._sliders[track]))

		self._session.set_stop_track_clip_buttons(None)
		self._session.set_stop_all_clips_button(None)
		self._mixer.set_global_buttons(None, None, None)
