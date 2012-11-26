from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ButtonSliderElement import ButtonSliderElement
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from ConfigurableButtonElement import ConfigurableButtonElement
from DeviceControllerComponent import DeviceControllerComponent
from QuickMixerComponent import QuickMixerComponent
from SpecialSessionComponent import SpecialSessionComponent
from SubSelectorComponent import *
from StepSequencerComponent import StepSequencerComponent
from _Framework.MomentaryModeObserver import MomentaryModeObserver

class MainSelectorComponent(ModeSelectorComponent):
	""" Class that reassigns the button on the launchpad to different functions """

	def __init__(self, matrix, top_buttons, side_buttons, config_button, parent):
		assert isinstance(matrix, ButtonMatrixElement)
		assert ((matrix.width() == 8) and (matrix.height() == 8))
		assert isinstance(top_buttons, tuple)
		assert (len(top_buttons) == 8)
		assert isinstance(side_buttons, tuple)
		assert (len(side_buttons) == 8)
		assert isinstance(config_button, ButtonElement)
		ModeSelectorComponent.__init__(self)
		self._parent = parent
		self._session = SpecialSessionComponent(matrix.width(), matrix.height())
		self._zooming = SessionZoomingComponent(self._session)
		self._session.name = 'Session_Control'
		self._zooming.name = 'Session_Overview'
		self._matrix = matrix
		self._side_buttons = side_buttons
		self._nav_buttons = top_buttons[:4]
		self._config_button = config_button
		self._zooming.set_empty_value(LED_OFF)
		self._all_buttons = []
		for button in self._side_buttons + self._nav_buttons:
			self._all_buttons.append(button)

		self._sub_modes = SubSelectorComponent(matrix, side_buttons, self._session)
		self._sub_modes.name = 'Mixer_Modes'
		self._sub_modes.set_update_callback(self._update_control_channels)
		self._stepseq = StepSequencerComponent(self, self._matrix,self._side_buttons,self._nav_buttons)
		self._quick_mix = None#QuickMixerComponent(self._nav_buttons,self._side_buttons,self)
		self._device_controller = DeviceControllerComponent(self._matrix, self._side_buttons, self._nav_buttons, self)
		self._init_session()
		self._all_buttons = tuple(self._all_buttons)
		self._mode_index=0
		self._previous_mode_index=-1
		self._sub_mode_index=[0,0,0,0]
		for index in range(4):
			self._sub_mode_index[index]=0
		self.set_mode_buttons(top_buttons[4:])

	def disconnect(self):
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)

		self._session = None
		self._zooming = None
		for button in self._all_buttons:
			button.set_on_off_values(127, LED_OFF)

		self._config_button.turn_off()
		self._matrix = None
		self._side_buttons = None
		self._nav_buttons = None
		self._config_button = None
		ModeSelectorComponent.disconnect(self)

	def session_component(self):
		return self._session

	def _update_mode(self):
		mode = self._modes_heap[-1][0]
		assert mode in range(self.number_of_modes())
		#self.log_message(str(mode))
		if self._mode_index==mode:
			if self._mode_index==1:
				#user mode 1 and device controller
				self._sub_mode_index[self._mode_index] = (self._sub_mode_index[self._mode_index]+1)%2
				self.update()
			elif self._mode_index==2:
				#user mode 2  and step sequencer
				self._sub_mode_index[self._mode_index] = (self._sub_mode_index[self._mode_index]+1)%3
				self.update()
			elif self._mode_index==3:
				self.update()
			else:
				self._sub_mode_index[self._mode_index] = 0
			self._previous_mode_index=self._mode_index	
		else:
			self._mode_index = mode
			self.update()
	
	def set_mode(self, mode):
		self._clean_heap()
		self._modes_heap = [(mode, None, None)]
		#if ((self._mode_index != mode) or (mode == 3) or True):
		#self._mode_index = mode
			#self._update_mode()
		#	self.update()
	
	def number_of_modes(self):
		return 4

	def on_enabled_changed(self):
		self.update()

	def _update_mode_buttons(self):
		for index in range(4):
			if(self._sub_mode_index[index]==0):
				self._modes_buttons[index].set_on_off_values(AMBER_FULL,AMBER_THIRD)
			if(self._sub_mode_index[index]==1):
				self._modes_buttons[index].set_on_off_values(GREEN_FULL,GREEN_THIRD)
			if(self._sub_mode_index[index]==2):
				self._modes_buttons[index].set_on_off_values(RED_FULL,RED_THIRD)
				
			if (index == self._mode_index):	
				self._modes_buttons[index].turn_on()
			else:
				self._modes_buttons[index].turn_off()

	def channel_for_current_mode(self):
		#trying to keep 
		if self._mode_index==0:
			return 0
		elif self._mode_index==1:
			if self._sub_mode_index[self._mode_index]==0:
				new_channel=4#user 1
			else : 
				new_channel = 1#device ctrl
		elif self._mode_index==2:
			if self._sub_mode_index[self._mode_index]==0:	
				new_channel=5#user 2
			else:
				new_channel = 1 + self._sub_mode_index[self._mode_index]#step seq
		elif self._mode_index==3:#mixer modes
			new_channel = 6 + self._sub_modes.mode()
		#if (new_channel > 0):
		#	new_channel += 3
		return new_channel

	def update(self):
		assert (self._modes_buttons != None)
		if self.is_enabled():
			#for index in range(len(self._modes_buttons)):
			#	self._modes_buttons[index].set_force_next_value()
			#	if index == self._mode_index:
			#		self._modes_buttons[index].turn_on()
			#	else:
			#		self._modes_buttons[index].turn_off()
		
			self._update_mode_buttons()
		
			#update matrix and side buttons
			for scene_index in range(8):
				#update scene button
				self._side_buttons[scene_index].set_enabled(True)
				for track_index in range(8):
					#update matrix
					self._matrix.get_button(track_index, scene_index).set_enabled(True)
			for button in self._nav_buttons:
				button.set_enabled(True)

			as_active = True
			as_enabled = True
			self._session.set_allow_update(False)
			self._zooming.set_allow_update(False)
			self._config_button.send_value(40)
			self._config_button.send_value(1)
			release_buttons = (self._mode_index == 1)
			if (self._mode_index == 0):
				#session
				self._setup_mixer((not as_active))
				self._setup_device_controller((not as_active))
				self._setup_step_sequencer((not as_active),0)
				self._setup_device_controller((not as_active))
				self._setup_session(as_active, as_enabled)
			elif (self._mode_index == 1):
				#user mode + device controller
				self._setup_mixer((not as_active))
				if (self._sub_mode_index[self._mode_index]==0):
					self._setup_step_sequencer((not as_active),0)
					self._setup_device_controller((not as_active))
					self._setup_session((not as_active), (as_enabled))
					self._setup_user1(True,True,True)
				else:
					self._setup_session(not as_active, not as_enabled)
					self._setup_step_sequencer(not as_active,0)
					self._setup_device_controller(as_active)
					
			elif (self._mode_index == 2):
				self._setup_session((not as_active), (not as_enabled))
				self._setup_mixer((not as_active))
				self._setup_device_controller((not as_active))
				if (self._sub_mode_index[self._mode_index]==0):
					self._setup_device_controller((not as_active))
					self._setup_step_sequencer((not as_active),0)
					self._setup_user2(release_buttons)
				else:
					self._setup_device_controller((not as_active))
					self._setup_step_sequencer(as_active,self._sub_mode_index[self._mode_index])
					
			elif (self._mode_index == 3):
				self._setup_step_sequencer((not as_active),0)
				self._setup_device_controller((not as_active))
				self._setup_session((not as_active), as_enabled)
				self._setup_mixer(as_active)
			else:
				assert False
			
			self._previous_mode_index=self._mode_index
			
			self._session.set_allow_update(True)
			self._zooming.set_allow_update(True)
			self._update_control_channels()


	
	#Update the channels of the buttons in the user modes..
	def _update_control_channels(self):
		new_channel = self.channel_for_current_mode()
		for button in self._all_buttons:
			button.set_channel(new_channel)
			button.set_force_next_value()

	def _setup_session(self, as_active, as_enabled):
		assert isinstance(as_active, type(False))
		for button in self._nav_buttons:
			if as_enabled:
				button.set_on_off_values(GREEN_FULL, GREEN_THIRD)
			else:
				button.set_on_off_values(127, LED_OFF)

		#matrix
		for scene_index in range(8):
			scene = self._session.scene(scene_index)
			if as_active:
				scene_button = self._side_buttons[scene_index]
				scene_button.set_on_off_values(127, LED_OFF)
				scene.set_launch_button(scene_button)
			else:
				scene.set_launch_button(None)
			for track_index in range(8):
				if as_active:
					button = self._matrix.get_button(track_index, scene_index)
					button.set_on_off_values(127, LED_OFF)
					scene.clip_slot(track_index).set_launch_button(button)
				else:
					scene.clip_slot(track_index).set_launch_button(None)

		#zoom
		if as_active:
			self._zooming.set_zoom_button(self._modes_buttons[0])
			self._zooming.set_button_matrix(self._matrix)
			self._zooming.set_scene_bank_buttons(self._side_buttons)
			self._zooming.set_nav_buttons(self._nav_buttons[0], self._nav_buttons[1], self._nav_buttons[2], self._nav_buttons[3])
			self._zooming.update()
		else:
			self._zooming.set_zoom_button(None)
			self._zooming.set_button_matrix(None)
			self._zooming.set_scene_bank_buttons(None)
			self._zooming.set_nav_buttons(None, None, None, None)

		#nav buttons
		if as_enabled:
			self._session.set_track_bank_buttons(self._nav_buttons[3], self._nav_buttons[2])
			self._session.set_scene_bank_buttons(self._nav_buttons[1], self._nav_buttons[0])
		else:
			self._session.set_track_bank_buttons(None, None)
			self._session.set_scene_bank_buttons(None, None)


	def _setup_quick_mix(self, as_active):
		if self._quick_mix!=None:
			if as_active:
				for button in range(8):
					self._side_buttons[button].set_enabled(True)
 				self._quick_mix._is_active = True
				self._quick_mix.set_enabled(True)
 			else:
				self._quick_mix._is_active = False
				self._quick_mix.set_enabled(False)


	def _setup_step_sequencer(self, as_active, mode):
		if(self._stepseq!=None):
			if(self._stepseq._is_active!=as_active or self._stepseq._mode!=mode ):
				if as_active: 
					self._stepseq._mode=mode
					self._stepseq._force_update = True
					self._stepseq._is_active = True
					self._stepseq.set_enabled(True)
					self._stepseq._on_notes_changed()
					self._stepseq.update_buttons()
					self._config_button.send_value(32)
				else:
					self._stepseq._mode=1
					self._stepseq._is_active = False
					self._stepseq.set_enabled(False)


	def _setup_device_controller(self, as_active):
		if self._device_controller!=None:
			if as_active:
				#for button in range(8):
				#	self._side_buttons[button].set_enabled(True)
 				self._device_controller._is_active = True
				self._device_controller.set_enabled(True)
				self._device_controller.update()
				self._config_button.send_value(32)
 			else:
				self._device_controller._is_active = False
				self._device_controller.set_enabled(False)

	def _setup_mixer(self, as_active):
		assert isinstance(as_active, type(False))
		if(as_active and self._sub_modes.is_enabled()):
			self._sub_modes.set_mode(-1)
		self._sub_modes.set_enabled(as_active)


	def _setup_user1(self, release_matrix=True,release_side_buttons =True,release_nav_buttons = True):
	
		for scene_index in range(8):
			if(release_side_buttons):
				scene_button = self._side_buttons[scene_index]
				scene_button.set_on_off_values(127, LED_OFF)
				scene_button.turn_off()
				scene_button.set_enabled((not release_side_buttons))
				
			for track_index in range(8):
				button = self._matrix.get_button(track_index, scene_index)
				button.set_on_off_values(127, LED_OFF)
				button.turn_off()
				button.set_enabled((not release_matrix))

		for button in self._nav_buttons:
			if(release_nav_buttons):
				button.set_on_off_values(127, LED_OFF)
				button.turn_off()
				button.set_enabled((not release_nav_buttons))

		if release_matrix:
			self._config_button.send_value(2)
		self._config_button.send_value(32, force_send=True)

	def _setup_user2(self, release_buttons):
		for scene_index in range(8):
			scene_button = self._side_buttons[scene_index]
			scene_button.set_on_off_values(127, LED_OFF)
			scene_button.turn_off()
			scene_button.set_enabled(not release_buttons)
			for track_index in range(8):
				button = self._matrix.get_button(track_index, scene_index)
				button.set_on_off_values(127, LED_OFF)
				button.turn_off()
				button.set_enabled(not release_buttons)

		for button in self._nav_buttons:
			button.set_on_off_values(127, LED_OFF)
			button.turn_off()
			button.set_enabled(not release_buttons)

		if release_buttons:
			self._config_button.send_value(2)
		self._config_button.send_value(32, force_send=True)

	def _init_session(self):
		self._session.set_stop_track_clip_value(AMBER_BLINK)
		for scene_index in range(self._matrix.height()):
			scene = self._session.scene(scene_index)
			scene.set_triggered_value(GREEN_BLINK)
			scene.name = 'Scene_' + str(scene_index)
			for track_index in range(self._matrix.width()):
				clip_slot = scene.clip_slot(track_index)
				clip_slot.set_triggered_to_play_value(GREEN_BLINK)
				clip_slot.set_triggered_to_record_value(RED_BLINK)
				clip_slot.set_stopped_value(AMBER_FULL)
				clip_slot.set_started_value(GREEN_FULL)
				clip_slot.set_recording_value(RED_FULL)
				clip_slot.name = str(track_index) + '_Clip_Slot_' + str(scene_index)
				self._all_buttons.append(self._matrix.get_button(track_index, scene_index))

		self._zooming.set_stopped_value(RED_FULL)
		self._zooming.set_selected_value(AMBER_FULL)
		self._zooming.set_playing_value(GREEN_FULL)

	def log_message(self, message):
		self._parent.log_message(message)