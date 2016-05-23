# -*- coding: utf-8 -*-

import Live
from DeviceComponent import DeviceComponent
from InstrumentControllerComponent import InstrumentControllerComponent
import Settings
from SpecialSessionComponent import SpecialSessionComponent
from StepSequencerComponent import StepSequencerComponent
from StepSequencerComponent2 import StepSequencerComponent2
from SubSelectorComponent import SubSelectorComponent  # noqa
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.SessionZoomingComponent import DeprecatedSessionZoomingComponent# noqa

log_enabled = False
setup_log_enabled = False
class MainSelectorComponent(ModeSelectorComponent):

	""" Class that reassigns the button on the launchpad to different functions """

	#def log(self, message):
	#	self._control_surface.log_message((' ' + message + ' ').center(50, '='))

	def __init__(self, matrix, top_buttons, side_buttons, config_button, osd, control_surface):
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent.__init__ start")
		#verify matrix dimentions
		assert isinstance(matrix, ButtonMatrixElement)
		assert ((matrix.width() == 8) and (matrix.height() == 8))
		assert isinstance(top_buttons, tuple)
		assert (len(top_buttons) == 8)
		assert isinstance(side_buttons, tuple)
		assert (len(side_buttons) == 8)
		assert isinstance(config_button, ButtonElement)
		ModeSelectorComponent.__init__(self) #super constructor
		
		#inject ControlSurface and OSD components (M4L)
		self._osd = osd
		self._control_surface = control_surface

		#initialize index variables
		self._mode_index = 0 #Inherited from parent
		self._previous_mode_index = -1 #Unused
		self._main_mode_index = 0 #LP original modes
		self._sub_mode_list = [0, 0, 0, 0]
		for index in range(4):
			self._sub_mode_list[index] = 0
		self.set_mode_buttons(top_buttons[4:])
			
		if Settings.SESSION__STOP_BUTTONS:#session with bottom stop buttons
			clip_stop_buttons = [] 
			for column in range(8):
				clip_stop_buttons.append(matrix.get_button(column,matrix.height()-1))
			self._session = SpecialSessionComponent(matrix.width(), matrix.height()-1, clip_stop_buttons, self._control_surface, self)
		else:#no stop buttons
			self._session = SpecialSessionComponent(matrix.width(), matrix.height(), None, self._control_surface, self)
		
		#initialize _session variables	
		self._session.set_osd(self._osd)
		self._session.name = 'Session_Control'
		
		#initialize _zooming variables	
		self._zooming = DeprecatedSessionZoomingComponent(self._session, enable_skinning = True)
		self._zooming.name = 'Session_Overview'
		self._zooming.set_empty_value("Default.Button.Off")
		
		self._matrix = matrix
		self._side_buttons = side_buttons#launch buttons
		self._nav_buttons = top_buttons[:4]#arrow buttons
		self._config_button = config_button#used to reset launchpad
		
		self._all_buttons = []
		for button in self._side_buttons + self._nav_buttons:
			self._all_buttons.append(button)

		#SubSelector changes the Mode using side buttons (ie. Pan, Volume, Send1, Send2, Stop, Solo, Activate, Arm)
		self._sub_modes = SubSelectorComponent(matrix, side_buttons, self._session, self._control_surface)
		self._sub_modes.name = 'Mixer_Modes'
		self._sub_modes._mixer.set_osd(self._osd)
		self._sub_modes.set_update_callback(self._update_control_channels)

		#User2 stepSequencer (Drum)
		self._stepseq = StepSequencerComponent(self._matrix, self._side_buttons, self._nav_buttons, self._control_surface)
		self._stepseq.set_osd(self._osd)
		
		#User2 stepSequencer (Melodic)
		self._stepseq2 = StepSequencerComponent2(self._matrix, self._side_buttons, self._nav_buttons, self._control_surface)
		self._stepseq2.set_osd(self._osd)
		
		#User1 Instrument controller (Scale)
		self._instrument_controller = InstrumentControllerComponent(self._matrix, self._side_buttons, self._nav_buttons, self._control_surface)
		self._instrument_controller.set_osd(self._osd)
		#self._instrument_controller = None
		
		#User1 Device controller (Fx or Instrument parameters)
		self._device_controller = DeviceComponent(control_surface = self._control_surface, matrix = self._matrix, side_buttons = self._side_buttons, top_buttons =  self._nav_buttons)
		self._device_controller.set_osd(self._osd)

		self._init_session()
		self._all_buttons = tuple(self._all_buttons)

	def disconnect(self):
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent.disconnect start")
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)

		self._session = None
		self._zooming = None
		for button in self._all_buttons:
			button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")

		self._config_button.turn_off()
		self._matrix = None
		self._side_buttons = None
		self._nav_buttons = None
		self._config_button = None
		ModeSelectorComponent.disconnect(self)
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent.disconnect end")
			
	def session_component(self):
		return self._session

	def _update_mode(self):
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._update_mode start")
		mode = self._modes_heap[-1][0] #get first value of last _modes_heap tuple. _modes_heap tuple structure is (mode, sender, observer) 

		assert mode in range(self.number_of_modes()) # 8 for this script
		if self._main_mode_index == mode:
			if self._main_mode_index == 1: #user mode 1 and device controller and instrument mode
				self._sub_mode_list[self._main_mode_index] = (self._sub_mode_list[self._main_mode_index] + 1) % 3
				self.update()
			elif self._main_mode_index == 2: #user mode 2  and step sequencer
				self._sub_mode_list[self._main_mode_index] = (self._sub_mode_list[self._main_mode_index] + 1) % 3
				self.update()
			elif self._main_mode_index == 3: #Mixer mode
				self.update()
			else: #Session mode
				self._sub_mode_list[self._main_mode_index] = 0
				self._mode_index = 0

		else:
			self._previous_mode_index = self._main_mode_index
			self._main_mode_index = mode
			self.update()
			
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._update_mode end")

	def set_mode(self, mode):
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent.set_mode start mode=" + str(mode))
		self._clean_heap()
		self._modes_heap = [(mode, None, None)]
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent.set_mode end")
		# if ((self.__main_mode_index != mode) or (mode == 3) or True):
		# 	self._main_mode_index = mode
		# 	self._update_mode()
		# 	self.update()

	def number_of_modes(self):
		return 1 + 3 + 3 + 1

	def on_enabled_changed(self):
		self.update()

	def _update_mode_buttons(self):
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._update_mode_buttons start")
		self._modes_buttons[0].set_on_off_values("Mode.Session.On","Mode.Session.Off")
		self._modes_buttons[3].set_on_off_values("Mode.Mixer.On","Mode.Mixer.Off")
		mode1 = self.getSkinName(Settings.USER_MODES[self._sub_mode_list[1]])
		mode2 = self.getSkinName(Settings.USER_MODES[3 + self._sub_mode_list[2]])
		self._modes_buttons[1].set_on_off_values("Mode."+mode1+".On","Mode."+mode1+".Off")
		self._modes_buttons[2].set_on_off_values("Mode."+mode2+".On","Mode."+mode2+".Off")
		
		for index in range(4):
			if (index == self._main_mode_index):
				self._modes_buttons[index].turn_on()
			else:
				self._modes_buttons[index].turn_off()
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._update_mode_buttons end")
			
	def getSkinName(self, user2Mode):
		if user2Mode=="instrument":
			user2Mode = "Note"
		if user2Mode=="device":
			user2Mode = "Device"
		if user2Mode=="user 1":
			user2Mode = "User"
		if user2Mode=="user 2":
			user2Mode = "User2"
		if user2Mode=="drum stepseq":
			user2Mode = "StepSequencer"
		if user2Mode=="melodic stepseq":
			user2Mode = "StepSequencer2"
		return user2Mode
		
	def channel_for_current_mode(self):
		# in this code, midi channels start at 0.
		# so channels range from 0 - 15.
		# mapping to 1-16 in the real world

		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent.channel_for_current_mode start")

		if self._main_mode_index == 0:
			new_channel = 0  # session

		elif self._main_mode_index == 1:
			if self._sub_mode_list[self._main_mode_index] == 0:
				new_channel = 11  # instrument controller
				# instrument controller uses base channel plus the 4 next ones. 11,12,13,14,15
				if self._instrument_controller != None:
					self._instrument_controller.base_channel = new_channel
			elif self._sub_mode_list[self._main_mode_index] == 1:
				new_channel = 3  # device controller
			elif self._sub_mode_list[self._main_mode_index] == 2:
				new_channel = 4  # plain user mode 1

		elif self._main_mode_index == 2:
			if self._sub_mode_list[self._main_mode_index] == 0:
				new_channel = 1  # step seq
			elif self._sub_mode_list[self._main_mode_index] == 1:
				new_channel = 2  # melodic step seq
			elif self._sub_mode_list[self._main_mode_index] == 2:
				new_channel = 5  # plain user mode 2

		elif self._main_mode_index == 3:  # mixer modes
			# mixer uses base channel 7 and the 4 next ones.
			new_channel = 6 + self._sub_modes.mode()  # 6,7,8,9,10

		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent.channel_for_current_mode end returning=" + str(new_channel))

		return new_channel

				
	
	def update(self):
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent.update start")
		assert (self._modes_buttons != None)
		if self.is_enabled():

			self._update_mode_buttons()
			self._session.set_allow_update(False)
			self._zooming.set_allow_update(False)
			self._config_button.send_value(40) #Set LP double buffering mode (investigate this)
			self._config_button.send_value(1) #Set LP X-Y layout grid mapping mode

			if self._main_mode_index == 0:
				self._setup_usermode("session")
			elif self._main_mode_index == 1 or self._main_mode_index == 2:#User1 or User2 modes
				self._setup_usermode(Settings.USER_MODES[ (self._main_mode_index-1) * 3 + self._sub_mode_list[self._main_mode_index] ] )
			elif self._main_mode_index == 3:
				self._setup_usermode("mixer")
			else:
				assert False
				
			self._previous_mode_index = self._main_mode_index

			self._session.set_allow_update(True)
			self._zooming.set_allow_update(True)
			#self.log_message("main selector update")
			#for line in traceback.format_stack():
			#	self.log_message(line.strip())
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent.update end")
		
	def _setup_usermode(self, mode):
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_usermode start mode=" + str(mode))
		self._disable_all_modes()
		
		if mode == "session":
			self._control_surface.show_message("SESSION MODE" )
			self._setup_session(True, True)
			self._mode_index = 0
		elif mode == "instrument":
			self._control_surface.show_message("INSTRUMENT MODE")
			self._setup_instrument_controller(True) 
			self._mode_index = 4
		elif mode == "device":
			self._control_surface.show_message("DEVICE CONTROLLER MODE")
			self._setup_device_controller(True)
			self._mode_index = 5
		elif mode == "user 1":
			self._control_surface.show_message("USER 1 MODE" )
			self._setup_user_mode(True, True, False, True)
			self._update_control_channels()
			self._mode_index = 1
		elif mode == "melodic stepseq":
			self._control_surface.show_message("MELODIC SEQUENCER MODE")
			self._setup_step_sequencers(True, self._stepseq2)
			self._mode_index = 7
		elif mode == "drum stepseq":
			self._control_surface.show_message("DRUM SEQUENCER MODE")
			self._setup_step_sequencers(True, self._stepseq)
			self._mode_index = 6
		elif mode == "user 2":
			self._control_surface.show_message("USER 2 MODE" )
			self._setup_user_mode(False, False, False, False)
			self._mode_index = 2
		elif mode == "mixer":
			self._control_surface.show_message("MIXER MODE")
			self._setup_session(False, True)
			self._setup_mixer(True)
			self._mode_index = 3
		
		self._update_control_channels()#change channel for all buttons according to mode
		
		if(self._mode_index in range(1,3)):
			self._osd.clear()
			self._osd.mode = mode.capitalize()
			self._osd.update()
			
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_usermode end")
		
	def _setup_session(self, as_active, as_navigation_enabled):
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_session start as_active=" + str(as_active) + 
						"  as_navigation_enabled=" + str(as_navigation_enabled))
		assert isinstance(as_active, type(False))#assert is boolean
		for button in self._nav_buttons:
			if as_navigation_enabled:
				button.set_on_off_values("Mode.Session.On", "Mode.Session.Off")
			else:
				button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")

		self._activate_matrix(True)
		for scene_index in range(self._session._num_scenes):#iterate over scenes
			scene = self._session.scene(scene_index)
			if as_active:#set scene launch buttons
				scene_button = self._side_buttons[scene_index]
				scene_button.set_enabled(as_active)
				scene_button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")
				scene.set_launch_button(scene_button)
			else:
				scene.set_launch_button(None)  
				
			for track_index in range(self._session._num_tracks):#iterate over tracks of a scene -> clip slots
				if as_active:#set clip slot launch button
					button = self._matrix.get_button(track_index, scene_index)
					button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")
					button.set_enabled(as_active)
					scene.clip_slot(track_index).set_launch_button(button)
				else:
					scene.clip_slot(track_index).set_launch_button(None)

		if as_active:#Set up stop clip buttons and stop all clips button
			if self._session._stop_clip_buttons != None:
				for button in self._session._stop_clip_buttons:
					button.set_enabled(as_active)
				#	button.set_on_off_values("Session.StopClip", "DefaultButton.Disabled")
				self._session.set_stop_track_clip_buttons(self._session._stop_clip_buttons)
				
				#last side button is stop all clip buttons ???
				self._side_buttons[self._session._num_scenes].set_enabled(as_active)
				self._side_buttons[self._session._num_scenes].set_on_off_values("Session.StopClip", "DefaultButton.Disabled")
				self._session.set_stop_all_clips_button(self._side_buttons[self._session._num_scenes])
			else:
				self._session.set_stop_track_clip_buttons(None)
				self._session.set_stop_all_clips_button(None)
		else:
			self._session.set_stop_track_clip_buttons(None)
			self._session.set_stop_all_clips_button(None)
				
		if as_active:# zoom
			self._zooming.set_zoom_button(self._modes_buttons[0])# Set Session button as zoom button, wrong behavior???
			self._zooming.set_button_matrix(self._matrix)
			self._zooming.set_scene_bank_buttons(self._side_buttons)
			self._zooming.set_nav_buttons(self._nav_buttons[0], self._nav_buttons[1], self._nav_buttons[2], self._nav_buttons[3])
			self._zooming.update()
		else:
			self._zooming.set_zoom_button(None)
			self._zooming.set_button_matrix(None)
			self._zooming.set_scene_bank_buttons(None)
			self._zooming.set_nav_buttons(None, None, None, None)

		if as_navigation_enabled: # nav buttons -> Why set up clip slot navigation AND matrix control buttons???
			self._session.set_track_bank_buttons(self._nav_buttons[3], self._nav_buttons[2])
			self._session.set_scene_bank_buttons(self._nav_buttons[1], self._nav_buttons[0])
		else:
			self._session.set_track_bank_buttons(None, None)
			self._session.set_scene_bank_buttons(None, None)
			
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_session end")

	def _setup_instrument_controller(self, as_active):
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_instrument_controller start as_active=" + str(as_active))
		if self._instrument_controller != None:
			if as_active:
				self._activate_matrix(False) #Disable matrix buttons (clip slots)
				self._activate_scene_buttons(True)#Enable side buttons
				self._activate_navigation_buttons(True)#Enable nav buttons
			else:
				for scene_index in range(8):#Restore all matrix buttons and scene launch buttons
					scene_button = self._side_buttons[scene_index]
					scene_button.use_default_message() # Reset to original channel
					scene_button.force_next_send() #Flush
					for track_index in range(8):
						button = self._matrix.get_button(track_index, scene_index)
						button.use_default_message()# Reset to original channel
						button.force_next_send()#Flush
			self._instrument_controller.set_enabled(as_active)#Enable/disable instrument controller
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_instrument_controller end")
			
	def _setup_device_controller(self, as_active):
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_device_controller start as_active=" + str(as_active))		
		if self._device_controller != None:
			if as_active:
				self._activate_scene_buttons(True)
				self._activate_matrix(True)
				self._activate_navigation_buttons(True)
				self._device_controller._is_active = True
				self._config_button.send_value(32)
				self._device_controller.set_enabled(True)
				self._device_controller.update()
			else:
				self._device_controller._is_active = False
				self._device_controller.set_enabled(False)
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_device_controller end")				

	def _setup_user_mode(self, release_matrix=True, release_side_buttons=True, release_nav_buttons=True, drum_rack_mode=True):
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_user_mode start release_matrix=" + str(release_matrix) 
						+ ", release_side_buttons=" + str(release_side_buttons) 
						+ ", release_nav_buttons=" + str(release_nav_buttons) 
						+ ", drum_rack_mode=" + str(drum_rack_mode))	
		# user1 -> All True but release_nav_buttons / user2 -> All false 
		for scene_index in range(8):
			scene_button = self._side_buttons[scene_index]
			scene_button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")
			scene_button.force_next_send()
			scene_button.turn_off()
			scene_button.set_enabled((not release_side_buttons))#User2 enabled

			for track_index in range(8):
				button = self._matrix.get_button(track_index, scene_index)
				button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")
				button.turn_off()
				button.set_enabled((not release_matrix))#User2 enabled

		for button in self._nav_buttons:
			button.set_on_off_values("DefaultButton.Disabled", "DefaultButton.Disabled")
			button.turn_off()
			button.set_enabled((not release_nav_buttons)) #User1 & User2 enabled

		if drum_rack_mode:#User1 enabled
			self._config_button.send_value(2)#Set LP drum rack layout grid mapping mode
		self._config_button.send_value(32)#Send enable flashing led config message to LP
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_user_mode end")	

	def _disable_all_modes(self):
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._disable_all_modes start")	
		self._setup_session(False, False)
		self._setup_instrument_controller(False) 			
		self._setup_device_controller(False)
		self._setup_step_sequencers(False, self._stepseq)
		self._setup_step_sequencers(False, self._stepseq2)
		self._setup_mixer(False)
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._disable_all_modes end")	
				
	def _setup_step_sequencers(self, as_active, sequencer):
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_step_sequencers start as_active=" + str(as_active) 
						+ ", sequencer=" + str(sequencer))		
		if(sequencer != None):
			#if(sequencer.is_enabled() != as_active):
			if as_active:
				self._activate_scene_buttons(True)#Enable side buttons
				self._activate_matrix(True) # Enable matrix buttons (clip slots)
				self._activate_navigation_buttons(True)#Enable nav buttons
				self._config_button.send_value(32)#Send enable flashing led config message to LP
				sequencer.set_enabled(True)
			else:
				sequencer.set_enabled(False)
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_step_sequencers end")					

	def _setup_mixer(self, as_active):
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_mixer start as_active=" + str(as_active))			
		assert isinstance(as_active, type(False))
		if as_active:
			self._activate_navigation_buttons(True)
			self._activate_scene_buttons(True)
			self._activate_matrix(True)
			if(self._sub_modes.is_enabled()):# go back to default mode
				self._sub_modes.set_mode(-1)
		else:
			self._sub_modes.release_controls()

		self._sub_modes.set_enabled(as_active)
		if(setup_log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._setup_mixer end")	

	def _init_session(self):
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._init_session start")		
		#self._session.set_stop_clip_value("Session.StopClip")
		#self._session.set_stop_clip_triggered_value("Session.ClipTriggeredStop")
		
		session_height = self._matrix.height()
		if self._session._stop_clip_buttons != None:
			session_height = self._matrix.height()-1
	
		for scene_index in range(session_height):
		#	scene = self._session.scene(scene_index)
		#	scene.set_triggered_value("Session.SceneTriggered")
		#	scene.name = 'Scene_' + str(scene_index)
			for track_index in range(self._matrix.width()):
		#		clip_slot = scene.clip_slot(track_index)
		#		clip_slot.set_triggered_to_play_value("Session.ClipTriggeredPlay")
		#		clip_slot.set_triggered_to_record_value("Session.ClipTriggeredRecord")
		#		clip_slot.set_stopped_value("Session.ClipStopped")
		#		clip_slot.set_started_value("Session.ClipStarted")
		#		clip_slot.set_recording_value("Session.ClipRecording")
		#		clip_slot.set_record_button_value("Session.RecordButton")
		#		clip_slot.name = str(track_index) + '_Clip_Slot_' + str(scene_index)
				self._all_buttons.append(self._matrix.get_button(track_index, scene_index))

		#self._zooming.set_stopped_value("Zooming.Stopped")
		#self._zooming.set_selected_value("Zooming.Selected")
		#self._zooming.set_playing_value("Zooming.Playing")
		if(log_enabled):
			Live.Base.log("LOG: MainSelectorComponent._init_session end")

	def _activate_navigation_buttons(self, active):
		for button in self._nav_buttons:
			button.set_enabled(active)

	def _activate_scene_buttons(self, active):
		for button in self._side_buttons:
			button.set_enabled(active)

	def _activate_matrix(self, active):
		for scene_index in range(8):
			for track_index in range(8):
				self._matrix.get_button(track_index, scene_index).set_enabled(active)

	def log_message(self, msg):
		self._control_surface.log_message(msg)

	# Update the channels of the buttons in the user modes..
	def _update_control_channels(self):
		new_channel = self.channel_for_current_mode()
		for button in self._all_buttons:
			button.set_channel(new_channel)
			button.force_next_send()

