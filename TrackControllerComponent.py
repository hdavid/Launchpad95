# -*- coding: utf-8 -*-
import Live
from consts import *  # noqa
from _Framework.MixerComponent import MixerComponent
from _Framework.ButtonElement import ButtonElement
import time
log_enabled = False

class TrackControllerComponent(MixerComponent):

	""" provide a one strip control on the current track  : arm,solo,mute
			navigate in tracks left/right
			navigate in scenes up and down
			fire/stop selected clip.
			enable/disable session_record
	"""

	def __init__(self, control_surface = None, implicit_arm = False, skin_name = "Session", enabled = False):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent __init__ start")
		self._prev_track_button = None
		self._next_track_button = None
		self._prev_scene_button = None
		self._next_scene_button = None
		self._play_button = None
		self._stop_button = None
		self._session_record_button = None
		self._mute_button = None
		self._solo_button = None
		self._undo_button = None
		self._arm_button = None
		self._control_surface = control_surface
		self._implicit_arm = implicit_arm
		self._skin_name = skin_name
		MixerComponent.__init__(self, 1)
		self.set_enabled(enabled)

		now = int(round(time.time() * 1000))
		self._last_arm_button_press = now
		self._last_session_record_button_press = now
		self._last_undo_button_press = now
		self._last_solo_button_press = now
		self._last_stop_button_press = now
		self._long_press = 500
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent __init__ end")
		

	def disconnect(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent disconnect start")
		self.set_prev_scene_button(None)
		self.set_next_scene_button(None)
		self.set_prev_track_button(None)
		self.set_next_track_button(None)
		self.set_mute_button(None)
		self.set_play_button(None)
		self.set_stop_button(None)
		self.set_session_record_button(None)
		self.set_solo_button(None)
		self.set_arm_button(None)

		MixerComponent.disconnect(self)
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent disconnect end")

	def set_enabled(self, enabled):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_enabled start - enabled=" + str(enabled))
		if self.is_enabled and not enabled:
			# disable implicit arm while leaving.
			if self._implicit_arm:
				if self.selected_track.can_be_armed:
					self.selected_track.implicit_arm = False
		MixerComponent.set_enabled(self, enabled)
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_enabled end")
	#def _do_select_scene(self, scene):
	#	view = self.song().view
	#	if view.selected_scene != self.selected_scene:
	#		view.selected_scene = self._scene


	def set_prev_scene_button(self, prev_scene=None):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_prev_scene_button start - prev_scene=" + str(prev_scene))
		assert isinstance(prev_scene, (ButtonElement, type(None)))
		if self._prev_scene_button != None:
			self._prev_scene_button.remove_value_listener(self._prev_scene_value)
		self._prev_scene_button = prev_scene
		if self._prev_scene_button != None:
			self._prev_scene_button.add_value_listener(self._prev_scene_value, identify_sender=True)
			self._prev_scene_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_prev_scene_button end")            

	def set_next_scene_button(self, next_scene=None):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_next_scene_button start - next_scene=" + str(next_scene))   
		assert isinstance(next_scene, (ButtonElement, type(None)))
		if self._next_scene_button != None:
			self._next_scene_button.remove_value_listener(self._next_scene_value)
		self._next_scene_button = next_scene
		if self._next_scene_button != None:
			self._next_scene_button.add_value_listener(self._next_scene_value, identify_sender=True)
			self._next_scene_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_next_scene_button end")   

	def set_session_record_button(self, session_record=None):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_session_record_button start - session_record=" + str(session_record))         
		assert isinstance(session_record, (ButtonElement, type(None)))
		if self._session_record_button != None:
			self._session_record_button.remove_value_listener(self._session_record_value)
		self._session_record_button = session_record
		if self._session_record_button != None:
			self._session_record_button.add_value_listener(self._session_record_value)
			self._session_record_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_session_record_button end")               

	def set_play_button(self, play=None):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_play_button start - play=" + str(play))         
		assert isinstance(play, (ButtonElement, type(None)))
		if self._play_button != None:
			self._play_button.remove_value_listener(self._play_value)
		self._play_button = play
		if self._play_button != None:
			self._play_button.add_value_listener(self._play_value)
			self._play_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_play_button end")           

	def set_stop_button(self, stop=None):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_stop_button start - stop=" + str(stop))      
		assert isinstance(stop, (ButtonElement, type(None)))
		if self._stop_button != None:
			self._stop_button.remove_value_listener(self._stop_value)
		self._stop_button = stop
		if self._stop_button != None:
			self._stop_button.add_value_listener(self._stop_value)
			self._stop_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_stop_button end")             

	def set_mute_button(self, mute=None):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_mute_button start - stop=" + str(mute))      
		assert isinstance(mute, (ButtonElement, type(None)))
		if self._mute_button != None:
			self._mute_button.remove_value_listener(self._mute_value)
		self._mute_button = mute
		if self._mute_button != None:
			self._mute_button.add_value_listener(self._mute_value)
			self._mute_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_mute_button end")            


	def set_solo_button(self, solo=None):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_solo_button start - solo=" + str(solo))        
		assert isinstance(solo, (ButtonElement, type(None)))
		if self._solo_button != None:
			self._solo_button.remove_value_listener(self._solo_value)
		self._solo_button = solo
		if self._solo_button != None:
			self._solo_button.add_value_listener(self._solo_value)
			self._solo_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_solo_button end")                

	def set_arm_button(self, arm=None):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_arm_button start - arm=" + str(arm))      
		assert isinstance(arm, (ButtonElement, type(None)))
		if self._arm_button != None:
			self._arm_button.remove_value_listener(self._arm_value)
		self._arm_button = arm
		if self._arm_button != None:
			self._arm_button.add_value_listener(self._arm_value)
			self._arm_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_arm_button end")

	def set_undo_button(self, button=None):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_undo_button start - button=" + str(button))      
		assert isinstance(button, (ButtonElement, type(None)))
		if self._undo_button != None:
			self._undo_button.remove_value_listener(self._undo_value)
		self._undo_button = button
		if self._undo_button != None:
			self._undo_button.add_value_listener(self._undo_value)
			self._undo_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_undo_button end")

# TRACKS Buttons
	def update_track_buttons(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent update_track_buttons start")    
		# tracks
		if self.is_enabled():
			if self._prev_track_button != None:
				self._prev_track_button.set_on_off_values("Mode."+self._skin_name)
				if self.selected_track_idx > 0:
					self._prev_track_button.turn_on()
				else:
					self._prev_track_button.turn_off()
			if self._next_track_button != None :
				self._next_track_button.set_on_off_values("Mode."+self._skin_name)
				if self.selected_track_idx < len(self.song().tracks) - 1:
					self._next_track_button.turn_on()
				else:
					self._next_track_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent update_track_buttons end")                        

	def set_next_track_button(self, button):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_next_track_button start - button=" + str(button))          
		assert (isinstance(button, (ButtonElement, type(None))))
		if  self._next_track_button != button:
			if self._next_track_button != None:
				self._next_track_button.remove_value_listener(self._next_track_value)
			self._next_track_button = button
			if self._next_track_button != None:
				assert isinstance(button, ButtonElement)
				self._next_track_button.add_value_listener(self._next_track_value, identify_sender=True)
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_next_track_button end")                            

	def _next_track_value(self, value, sender):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _next_track_value start - value=" + str(value) + ",  sender=" + str(sender))           
		assert (self._next_track_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if (not sender.is_momentary()) or (value is not 0):
				if self.selected_track_idx < len(self.song().tracks) - 1:
					self.song().view.selected_track = self.song().tracks[self.selected_track_idx + 1]
					self._do_implicit_arm()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _next_track_value end")                       

	def set_prev_track_button(self, button):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_prev_track_button start - button=" + str(button))          
		assert (isinstance(button, (ButtonElement, type(None))))
		if self._prev_track_button != button:
			if self._prev_track_button != None:
				self._prev_track_button.remove_value_listener(self._prev_track_value)
			self._prev_track_button = button
			if self._prev_track_button != None:
				assert isinstance(button, ButtonElement)
				self._prev_track_button.add_value_listener(self._prev_track_value, identify_sender=True)
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent set_prev_track_button end")                      

	def _prev_track_value(self, value, sender):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _prev_track_value start - value=" + str(value) + ",  sender=" + str(sender))           
		assert (self._next_track_button != None)    
		assert (self._prev_track_button != None)
		assert (value in range(128))
		if (not sender.is_momentary()) or (value is not 0):
			if self.is_enabled():
				if self.selected_track_idx > 0:
					self.song().view.selected_track = self.song().tracks[self.selected_track_idx - 1]
					self._do_implicit_arm()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _prev_track_value end")                      

	def update_scene_buttons(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent update_scene_buttons start")       
		# tracks
		if self.is_enabled():
			if self._prev_scene_button != None:
				self._prev_scene_button.set_on_off_values("Mode."+self._skin_name)
				if self.selected_scene_idx > 0:
					self._prev_scene_button.turn_on()
				else:
					self._prev_scene_button.turn_off()

			if self._next_scene_button != None:
				self._next_scene_button.set_on_off_values("Mode."+self._skin_name)
				if self.selected_scene_idx < len(self.song().scenes) - 1:
					self._next_scene_button.turn_on()
				else:
					self._next_scene_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent update_scene_buttons end")                       

	def _prev_scene_value(self, value, sender):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _prev_scene_value start - value=" + str(value) + ",  sender=" + str(sender))    
		assert (self._prev_scene_button != None)
		assert (value in range(128))
		if not sender.is_momentary() or value is not 0:
			if self.is_enabled():
				if self.selected_scene_idx > 0:
					self.song().view.selected_scene = self.song().scenes[self.selected_scene_idx - 1]
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _prev_scene_value end")                       
				
	def _next_scene_value(self, value, sender):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _next_scene_value start - value=" + str(value) + ",  sender=" + str(sender))       
		assert (self._next_scene_button != None)
		assert (value in range(128))
		if not sender.is_momentary() or value is not 0:
			if self.is_enabled():
				if not sender.is_momentary() or value is not 0:
					if self.selected_scene_idx < len(self.song().scenes) - 1:
						self.song().view.selected_scene = self.song().scenes[self.selected_scene_idx + 1]
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _next_scene_value end")                           

	def _session_record_value(self, value):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _session_record_value start - value=" + str(value))        
		assert (self._session_record_button != None)
		assert (value in range(128))
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if value != 0 or not self._session_record_button.is_momentary():
				self._last_session_record_button_press = now
			else:
				if now - self._last_session_record_button_press > self._long_press * 4:
					self._implicit_arm = not self._implicit_arm
					self._do_implicit_arm()
					if self._implicit_arm:
						self._control_surface.show_message("implicit arm : on")
					else:
						self._control_surface.show_message("implicit arm : off")
					self.update()
				elif now - self._last_session_record_button_press > self._long_press:
					self.song().metronome = not self.song().metronome
					if self.song().metronome :
						self._control_surface.show_message("metronome : on")
					else:
						self._control_surface.show_message("metronome : off")
				else:
					if self._implicit_arm:
						self.song().session_record = not self.song().session_record
						if self.song().session_record :
							self._control_surface.show_message("session record : on")
						else:
							self._control_surface.show_message("session record : off")
					else:
						if self.selected_track.can_be_armed:
							self.selected_track.arm = not self.selected_track.arm
							if self.selected_track.arm :
								self._control_surface.show_message("track "+str(self.selected_track.name)+" armed")
							else:
								self._control_surface.show_message("track "+str(self.selected_track.name)+" unarmed")
					self.update()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _session_record_value end")                      

	def _play_value(self, value):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _play_value start - value=" + str(value))        
		assert (self._play_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if value != 0 or not self._play_button.is_momentary():
				self._play_button.turn_on()
				if self.selected_scene != None:
					slot = self.selected_scene.clip_slots[self.selected_track_idx]
					slot.fire()
					self._control_surface.show_message("fire clip")
			else:
				self._play_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _play_value end")                  

	def _stop_value(self, value):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _stop_value start - value=" + str(value))     
		assert (self._stop_button != None)
		assert (value in range(128))
		assert(self.selected_track != None)
		now = int(round(time.time() * 1000))
		if self.is_enabled():
			if value != 0 or not self._stop_button.is_momentary():
				self._last_stop_button_press = now
				self._stop_button.turn_on()
			else:
				if now - self._last_stop_button_press > self._long_press:
					if self.selected_scene != None:
						slot = self.selected_scene.clip_slots[self.selected_track_idx]
						if slot and slot.has_clip:
							slot.delete_clip()
							self._control_surface.show_message("delete clip")
				else:
					if self.selected_scene != None:
						slot = self.selected_scene.clip_slots[self.selected_track_idx]
						slot.stop()
						self._control_surface.show_message("stop clip")
				self._stop_button.turn_off()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _stop_value end")                   

	def _mute_value(self, value):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _mute_value start - value=" + str(value))         
		assert (self._mute_button != None)
		assert (value in range(128))
		assert(self.selected_track != None)
		if self.is_enabled():
			if value != 0 or not self._mute_button.is_momentary():
				self.selected_track.mute = not self.selected_track.mute
				if self.selected_track.mute :
					self._control_surface.show_message("track "+str(self.selected_track.name)+" muted")
				else:
					self._control_surface.show_message("track "+str(self.selected_track.name)+" unmuted")
			self.update()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _mute_value end")                   

	def _solo_value(self, value):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _solo_value start - value=" + str(value))        
		assert (self._solo_button != None)
		assert (value in range(128))
		assert(self.selected_track != None)
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if value != 0 or not self._session_record_button.is_momentary():
				self._last_solo_button_press = now
				self._solo_button.turn_on()
				if(log_enabled):
					Live.Base.log("LOG: TrackControllerComponent _solo_value start - _solo_button.turn_on() now=" + str(now))   
			else:
				self._solo_button.turn_off()
				if now - self._last_solo_button_press > self._long_press:
					self.selected_track.mute = not self.selected_track.mute
					if self.selected_track.mute:
						self._control_surface.show_message("track "+str(self.selected_track.name)+" mute")
					else:
						self._control_surface.show_message("track "+str(self.selected_track.name)+" unmute")
					if(log_enabled):
						Live.Base.log("LOG: TrackControllerComponent _solo_value start - selected_track.mute time=" + str(now - self._last_solo_button_press))   
				else:
					self.selected_track.solo = not self.selected_track.solo
					if(log_enabled):
						Live.Base.log("LOG: TrackControllerComponent _solo_value start - selected_track.solo time=" + str(now - self._last_solo_button_press))   
					if self.selected_track.solo:
						self._control_surface.show_message("track "+str(self.selected_track.name)+" solo")
					else:
						self._control_surface.show_message("track "+str(self.selected_track.name)+" unsolo")
			self.update()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _solo_value end")

	def _undo_value(self, value):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _undo_value start - value=" + str(value))    
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if value != 0 or not self._session_record_button.is_momentary():
				self._last_undo_button_press = now
			else:
				if now - self._last_undo_button_press < self._long_press:
					if self.song().can_undo:
						self.song().undo()
						self._control_surface.show_message("undo!")
				else:
					if self.song().can_redo:
						self.song().redo()
						self._control_surface.show_message("redo!")
			self.update()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _undo_value end")            

	def _arm_value(self, value):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _arm_value start - value=" + str(value))        
		assert (self._arm_button != None)
		assert (value in range(128))
		assert(self.selected_track != None)
		if self.is_enabled():
			now = int(round(time.time() * 1000))
			if value != 0 or not self._arm_button.is_momentary():
				self._last_arm_button_press = now
			else:
				if now - self._last_arm_button_press > self._long_press:
					self._implicit_arm = not self._implicit_arm
					if self._implicit_arm:
						self._control_surface.show_message("implicit arm : on")
					else:
						self._control_surface.show_message("implicit arm : off")
					self._do_implicit_arm()
				else:
					if self.selected_track.can_be_armed:
						self.selected_track.arm = not self.selected_track.arm
						if self.selected_track.arm :
							self._control_surface.show_message("track "+str(self.selected_track.name)+" armed")
						else:
							self._control_surface.show_message("track "+str(self.selected_track.name)+" unarmed")
			self.update()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _arm_value end")                  

	def update(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent update start")     
		if self.is_enabled():
			self.update_track_buttons()
			self.update_scene_buttons()

			if self._session_record_button != None:
				if self._implicit_arm:
					self._session_record_button.set_on_off_values("TrackController.ImplicitRecording")
				else:
					self._session_record_button.set_on_off_values("TrackController.Recording")
				if(self.song().session_record):
					self._session_record_button.turn_on()
				else:
					self._session_record_button.turn_off()

			if self._play_button != None:
				self._play_button.set_light("TrackController.Play.Off")
				
			if self._stop_button != None:
				self._stop_button.set_light("TrackController.Stop.Off")
		
			if self._mute_button != None:
				self._mute_button.set_on_off_values("TrackController.Mute")
				if(self.selected_track.mute):
					self._mute_button.turn_off()
				else:
					self._mute_button.turn_on()

			if self._undo_button != None:
				self._undo_button.set_on_off_values("TrackController.Undo")
				if self.song().can_undo:
					self._undo_button.turn_on()
				else:
					self._undo_button.turn_off()

			if self._solo_button != None:
				self._solo_button.set_on_off_values("TrackController.Solo")
				if self.selected_track.solo:
					self._solo_button.turn_on()
				else:
					self._solo_button.turn_off()

			if self._arm_button != None:
				if self._implicit_arm:
					self._arm_button.set_on_off_values("TrackController.ImplicitRecording")
				else:
					self._arm_button.set_on_off_values("TrackController.Recording")

				if(self.selected_track.can_be_armed and self.selected_track.arm):
					self._arm_button.turn_on()
				else:
					self._arm_button.turn_off()

		MixerComponent.update(self)
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent update end")             

	def can_implicit_arm_track(self, track):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent can_implicit_arm_track start - track=" + str(track) + "returning track.can_be_armed: " 
						+  str(track.can_be_armed) + " track.has_midi_input: " + str(track.has_midi_input))    
		return track.can_be_armed and track.has_midi_input

	def _do_implicit_arm(self, arm = True):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _do_implicit_arm start - arm=" + str(arm))      
		if self.is_enabled():
			if self._implicit_arm:
				self._control_surface.set_controlled_track(self.selected_track)
			else:
				self._control_surface.release_controlled_track()
			for track in self.song().tracks:
				if self.can_implicit_arm_track(track):
					track.implicit_arm = self._implicit_arm and arm and self.selected_track == track
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent _do_implicit_arm end")                       

		
	def on_selected_track_changed(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent on_selected_track_changed start")
		self._do_implicit_arm()
		self.update()
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent on_selected_track_changed end")        

	def on_selected_scene_changed(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent on_selected_scene_changed start")    
		self.update()
	
	@property
	def selected_track(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent selected_track start")      
		return self.song().view.selected_track

	@property
	def selected_track_idx(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent selected_track_idx start")       
		return list(self.song().tracks).index(self.song().view.selected_track)

	@property
	def selected_scene_idx(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent selected_scene_idx start")         
		return list(self.song().scenes).index(self.song().view.selected_scene)
		
	@property
	def selected_scene(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent selected_scene start")      
		return self.song().view.selected_scene

	@property
	def selected_clip(self):
		if(log_enabled):
			Live.Base.log("LOG: TrackControllerComponent selected_clip start")     
		clip_slot = self.selected_scene.clip_slots[self.selected_track_idx]
		if clip_slot.has_clip:
			return clip_slot.clip
		else:
			return None

