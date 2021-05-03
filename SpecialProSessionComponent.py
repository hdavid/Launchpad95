import Live
#import traceback
from .ClipSlotMK2 import ClipSlotMK2
from _Framework.SceneComponent import SceneComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.SubjectSlot import subject_slot
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework import Task
from _Framework.Util import in_range
from _Framework.SubjectSlot import subject_slot_group
import time
from .SpecialProSessionRecordingComponent import SpecialProSessionRecordingComponent
from .SpecialSessionComponent import SpecialSessionComponent
from .TargetTrackComponent import TargetTrackComponent
_Q = Live.Song.Quantization
Rec_Q = Live.Song.RecordingQuantization
try:
	xrange
except NameError:
	xrange = range
	

REC_QNTZ_RATES = [
Rec_Q.rec_q_quarter,
Rec_Q.rec_q_eight,
Rec_Q.rec_q_eight_triplet,
Rec_Q.rec_q_eight_eight_triplet,
Rec_Q.rec_q_sixtenth,
Rec_Q.rec_q_sixtenth_triplet,
Rec_Q.rec_q_sixtenth_sixtenth_triplet,
Rec_Q.rec_q_thirtysecond]

REC_QNTZ_FIXED_RATES = [
Rec_Q.rec_q_quarter,
Rec_Q.rec_q_eight,
Rec_Q.rec_q_eight_triplet,
Rec_Q.rec_q_sixtenth,
Rec_Q.rec_q_sixtenth_triplet]

REC_QNTZ_NAMES = ('1/4', '1/8', '1/8t', '1/8+t', '1/16', '1/16t', '1/16+t', '1/32')
REC_QNTZ_RATES_LEN = len(REC_QNTZ_RATES)


LAUNCH_QNTZ_RATES = [
_Q.q_8_bars,
_Q.q_4_bars,
_Q.q_2_bars,
_Q.q_bar,
_Q.q_half,
_Q.q_half_triplet,
_Q.q_quarter,
_Q.q_quarter_triplet,
_Q.q_eight,
_Q.q_eight_triplet,
_Q.q_sixtenth,
_Q.q_sixtenth_triplet,
_Q.q_thirtytwoth
]

LAUNCH_QNTZ_FIXED_RATES = [
_Q.q_2_bars,
_Q.q_bar,
_Q.q_quarter,
_Q.q_eight,
_Q.q_sixtenth
]
LAUNCH_QNTZ_NAMES = ('8 Bars', '4 Bars', '2 Bars', '1 Bar', '1/2', '1/2t', '1/4', '1/4t', '1/8', '1/8t', '1/16', '1/16t', '1/32')
LAUNCH_QNTZ_RATES_LEN = len(LAUNCH_QNTZ_RATES)



LENGTH_OPTION_NAMES = ('1 Beat', '1 Bar', '2 Bars', '4 Bars', '8 Bars')

FIXED_LENGTH_VALUES = [0.25, 1, 2, 4, 8]
MAX_FIXED_LENGTH = 31

#SHIFT_COLORS = ('TapSet.One', 'TapSet.Two', 'TapSet.Three', 'TapSet.Four', 'TapSet.Five', 'TapSet.Six', 'TapSet.Seven',
#				'TapSet.Six', 'TapSet.Five', 'TapSet.Four', 'TapSet.Three', 'TapSet.Two')
#SHIFT_COLORS_LEN = len(SHIFT_COLORS)

#TAP_COLORS = ('ShiftSet.One', 'ShiftSet.Two', 'ShiftSet.Three', 'ShiftSet.Two')
#TAP_COLORS_LEN = len(TAP_COLORS)

LONG_PRESS = 0.5
SHORT_PRESS = 0.25
class SpecialClipSlotComponent(ClipSlotComponent):
	quantization_component = None
	device = True
	
	def __init__(self, should_arm = None, *a, **k):
		super(SpecialClipSlotComponent, self).__init__(*a, **k)
		
	def _set_parent(self, parent):		
		self._parent = parent
	
	def _do_select_clip(self, clip_slot):
		super(SpecialClipSlotComponent, self)._do_select_clip(clip_slot)
		if self._clip_slot is not None:
			clip = clip_slot.clip
			
			if not self.application().view.is_view_visible('Detail'):
				self.application().view.show_view('Detail')
				self.device = True
			
			if clip:
				if not self.application().view.is_view_visible('Detail/Clip') and self.device and self._isSelecting():
					self.application().view.show_view('Detail/Clip')
			else:
				self.device = False
					
			if not self.application().view.is_view_visible('Detail/DeviceChain') and not self.device and self._isSelecting():
				self.application().view.show_view('Detail/DeviceChain')			
			
			self.device = not self.device	

	def _isSelecting(self):
		if not self._is_shifting():
			return False
		
		if self._is_copypasting():
			return False

		if self._is_quantizing():
			return False
		
		if self._is_doubling():
			return False
	
		if self._is_deleting():
			return False
	
		if self._is_duplicating():
			return False

		return True

	def _do_duplicate_clip(self):
		if self._clip_slot:
			slot = self._clip_slot
			should_launch = True
			song = self._get_song()
			try:
				clip = slot.clip if slot is not None else None
				if clip is not None:
					track = slot.canonical_parent
					view = song.view
					try:
						start_duplicate = should_launch and clip.is_playing
						target_index = list(track.clip_slots).index(slot)
						destination_index = track.duplicate_clip_slot(target_index)
						view.highlighted_clip_slot = track.clip_slots[destination_index]
						view.detail_clip = view.highlighted_clip_slot.clip
						if start_duplicate:
							view.highlighted_clip_slot.fire(force_legato=True, launch_quantization=_Q.q_no_q)
						self._print('Clip duplicated')
					except Live.Base.LimitationError:
						pass
					except RuntimeError:
						pass
			except (AttributeError, TypeError):
				pass
			
	def _do_copypaste_clip(self, clip_slot):
		if self._should_copy() and clip_slot.has_clip:
			self._set_slot_copy_buffer(clip_slot)
		else:
			if (not self._should_copy()):
				try:
					self._get_slot_copy_buffer().duplicate_clip_to(clip_slot)
				except RuntimeError:
					pass
			
	def _do_double_loop(self, clip_slot):
		self._do_select_clip(clip_slot)
		clip = self.song().view.detail_clip
		if self._can_duplicate_loop(clip):
			try:
				self._get_song().view.detail_clip.duplicate_loop()
				self._print('Clip length doubled to ' + str(clip.length))
			except (AttributeError, TypeError):
				pass
			except RuntimeError:
				pass

	def _can_duplicate_loop(self, clip):
		return clip and clip.is_midi_clip

	def _do_quantize_clip(self, clip_slot):
		if self._clip_slot and self._clip_slot.has_clip:
			clip = clip_slot.clip
			assert isinstance(clip, Live.Clip.Clip)
			clip.quantize(self._get_record_quantization(), 1.0) 
			
			self._print('Clip quantized to ' + str(REC_QNTZ_NAMES[REC_QNTZ_RATES.index(self._get_record_quantization())]))
			
	def _do_delete_clip(self):
		if self._clip_slot and self._clip_slot.has_clip:
			self._clip_slot.delete_clip()
			self._print('Clip deleted')
			
	def _do_track_arm(self):
		if self._clip_slot:
			track = self._clip_slot.canonical_parent
			if track.can_be_armed and not track.arm:
				if self._get_song().exclusive_arm:
					for t in self._get_song().tracks:
						if t.can_be_armed and t.arm:
							t.arm = False

				track.arm = True
				if self._get_song().view.selected_track != track:
					self._get_song().view.selected_track = track
			if self._clip_slot.has_clip:
				self._get_song().session_record = not self._get_song().session_record
	 
	def _do_launch_clip(self, value):
		if(not self._is_fixed_length_on()):
			super(SpecialClipSlotComponent, self)._do_launch_clip(value)
		else:	 
			button = self._launch_button_value.subject # MATRIX BUTTON
			launch_pressed = value or not button.is_momentary() # LAUNCH MSG
			quant = self._get_launch_quant()		
			if not self.has_clip(): #Have CLIP
				self._has_fired_slot = True
			
			if button.is_momentary():
				if(not self.has_clip()):
					self._clip_slot.fire(record_length=self._get_fixed_length(), launch_quantization=quant)
				else:
					self._clip_slot.clip.set_fire_button_state(value != 0)
			elif launch_pressed:
				if(not self.has_clip()):
					self._clip_slot.fire(record_length=self._get_fixed_length(), launch_quantization=quant)
				else:
					self._clip_slot.fire()
			if launch_pressed and self.song().select_on_launch:
				self.song().view.highlighted_clip_slot = self._clip_slot
				self.application().view.show_view('Detail/Clip')

	def _feedback_value(self):
		ret = super(SpecialClipSlotComponent, self)._feedback_value()
		if self._clip_slot and ret == 'ProSession.ClipStopped':
			track = self._clip_slot.canonical_parent
			if track.is_foldable:
				if track.fold_state == 0:
					return 'ProSession.ClipUnFoldedTrack'
				else:
					return 'ProSession.ClipFoldedTrack'
		return ret

	def _is_shifting(self):
		return self._parent._is_shifting()

	def _is_copypasting(self):
		return self._parent._is_copypasting()

	def _is_quantizing(self):
		return self._parent._is_quantizing()
		
	def _is_doubling(self):
		return self._parent._is_doubling()  
	
	def _is_deleting(self):
		return self._parent._is_deleting()
	
	def _is_duplicating(self):
		return self._parent._is_duplicating()
		
	def _get_song(self):
		return self._parent._get_song()
	
	def _get_record_quantization(self):
		return self._parent._get_record_quantization()
	
	def _is_fixed_length_on(self):
		return self._parent._is_fixed_length_on()

	def _get_launch_quant(self):
		return self._parent._get_launch_quant()
		
	def _get_fixed_length(self):
		return self._parent._get_fixed_length()
	
	def _is_pro_mode_on(self):
		return self._parent._is_pro_mode_on()
	
	def _should_arm(self):
		return self._parent._should_arm()

	def _should_copy(self):
		return self._parent._should_copy()
	
	def _set_slot_copy_buffer(self, slot):
		self._parent._set_slot_copy_buffer(slot)
	
	def _get_slot_copy_buffer(self):
		return self._parent._get_slot_copy_buffer()  
	
	def _print(self, msg):
		self._parent._print(str(msg)) 

	@subject_slot('value')
	def _launch_button_value(self, value):
		if self._is_pro_mode_on():
		
			if self.is_enabled():
				if self._is_deleting() and value:
					if self._is_shifting():
						self._parent._do_delete_scene(self._parent)
					else:
						self._do_delete_clip()
				elif self._is_duplicating() and value:
					if self._is_shifting():
						self._parent._do_duplicate_scene()
					else:
						self._do_duplicate_clip()	
				elif self._is_copypasting() and value:
					if self._is_shifting():
						self._parent._do_launch_scene(value)
					else:					
						self._do_copypaste_clip(self._clip_slot)							  
				elif self._is_doubling() and value:
					if self._is_shifting():
						self._parent._do_capture_and_insert_scene()
					else:							
						self._do_double_loop(self._clip_slot)
				elif self._is_quantizing() and value:
					if self._is_shifting():
						self._parent._do_create_scene()
					else:					
						self._do_quantize_clip(self._clip_slot)
				elif self._is_shifting() and value:
					self._do_select_clip(self._clip_slot)			
				else:
					if value:
						if self._should_arm():
							self._do_track_arm()
						self._do_launch_clip(value)
		else:
			super(SpecialClipSlotComponent, self)._launch_button_value(value)

class SpecialSceneComponent(SceneComponent):
	clip_slot_component_type = SpecialClipSlotComponent

	def __init__(self, *a, **k):
		super(SpecialSceneComponent, self).__init__(*a, **k)
			
	def _set_parent(self, parent):		
		self._parent = parent
		
	def _is_shifting(self):
		return self._parent._is_shifting()

	def _is_copypasting(self):
		return self._parent._is_copypasting()

	def _is_deleting(self):
		return self._parent._is_deleting()
	
	def _is_duplicating(self):
		return self._parent._is_duplicating()
	
	def _is_doubling(self):
		return self._parent._is_doubling()	
	
	def _is_quantizing(self):
		return self._parent._is_quantizing()  
	
	def _get_song(self):
		return self._parent._get_song()
	
	def _get_record_quantization(self):
		return self._parent._get_record_quantization()
	
	def _should_arm(self):
		return self._parent._should_arm()
	
	def _is_fixed_length_on(self):
		return self._parent._is_fixed_length_on()
		
	def _get_fixed_length(self):
		return self._parent._get_fixed_length()
	
	def _get_launch_quant(self):
		return self._parent._get_launch_quant()	
	
	def _is_pro_mode_on(self):
		return self._parent._is_pro_mode_on()
	
	def _set_slot_copy_buffer(self, slot):
		self._parent._set_slot_copy_buffer(slot)
	
	def _get_slot_copy_buffer(self):
		return self._parent._get_slot_copy_buffer()  

	def _should_copy(self):
		return self._parent._should_copy()
	
	def _do_delete_scene(self, scene_for_overrides):
		try:
			if self._scene:
				song = self.song()
				song.delete_scene(list(song.scenes).index(self._scene))
				self._print('Scene deleted')
		except RuntimeError:
			pass
	
	def _do_duplicate_scene(self):
		try:
			song = self._get_song()
			song.duplicate_scene(list(song.scenes).index(self._scene))
			self._print('Scene duplicated')
		except Live.Base.LimitationError:
			pass
		except RuntimeError:
			pass
		except IndexError:
			pass
		
	def _do_launch_scene(self, value):
		launched = False
		if value != 0:
			self._scene.fire()
			launched = True
		if launched and self.song().select_on_launch:
			self.song().view.selected_scene = self._scene

	def _do_create_scene(self):
		try:
			song = self._get_song()
			new_scene_index = list(song.scenes).index(self._scene) + 1
			song.view.selected_scene = song.create_scene(new_scene_index)
			self._print('Create scene ' + self.song().view.selected_scene.name)
		except Live.Base.LimitationError:
			pass
		except RuntimeError:
			pass
		except IndexError:
			pass
		
	def _do_capture_and_insert_scene(self):
		try:
			song = self.song()
			song.view.selected_scene = self._scene
			song.capture_and_insert_scene(Live.Song.CaptureMode.all)
			self._print('Captured to scene ' + self.song().view.selected_scene.name)
		except Live.Base.LimitationError:
			pass
		except RuntimeError:
			pass
		except IndexError:
			pass
		
	def _print(self, msg):
		self._parent._print(str(msg))		   
		
class SpecialProSessionComponent(SpecialSessionComponent):
	scene_component_type = SpecialSceneComponent
	""" Special session subclass that handles ConfigurableButtons """

	def __init__(self, num_tracks, num_scenes, stop_clip_buttons, side_buttons, control_surface, main_selector, livesong = None):
		self._pro_mode_on = False
		if control_surface._mk2_rgb:
			#use custom clip colour coding : blink and pulse for trig and play 
			SceneComponent.clip_slot_component_type = ClipSlotMK2
		SpecialSessionComponent.__init__(self, num_tracks = num_tracks, num_scenes = num_scenes, stop_clip_buttons = stop_clip_buttons, control_surface= control_surface, main_selector= main_selector)
		
		self._side_buttons = side_buttons
		self._osd = None
		self._song = livesong
		
		self._slot_copy_buffer = None
		
		self._shift_button = None
		self._click_button = None
		self._undo_button = None
		self._delete_button = None
		self._duplicate_button = None
		self._double_button = None
		self._quantize_button = None
		self._record_button = None
		
		self._shift_pressed = False
		self._delete_pressed = False
		self._duplicate_pressed = False
		self._double_pressed = False
		self._quantize_pressed = False
		self._click_pressed = False
		self._record_pressed = False
		self._record_mode_on = False
		self._is_arming = False
		self._armed_track_count=0
		
		self._last_undo_time = time.time()
		self._last_shift_time = time.time()
		self._last_quantize_time = time.time()
		self._last_click_time = time.time()
		self._last_fixed_time = time.time()
		self._last_solo_time = time.time()
		self._last_mute_time = time.time()
		self._last_record_time = time.time()
				
		self._end_undo_step_task = self._tasks.add(Task.sequence(Task.wait(1.5), Task.run(self.song().end_undo_step)))
		self._end_undo_step_task.kill()
		
		self._launch_quantization = self._get_song().clip_trigger_quantization
		self._launch_quantization_on = self._launch_quantization !=_Q.q_no_q
		self._song.add_clip_trigger_quantization_listener(self._on_clip_trigger_quantization_changed_in_live)
		
		if(self._get_song().midi_recording_quantization== Rec_Q.rec_q_no_q):
			self._record_quantization = Rec_Q.rec_q_sixtenth
		else:
			self._record_quantization = self._get_song().midi_recording_quantization
			
			
		self._record_quantization_on = self._get_song().midi_recording_quantization != Rec_Q.rec_q_no_q
			
			
		self._song.add_midi_recording_quantization_listener(self._on_record_quantization_changed_in_live)
		
		self.song().add_session_record_listener(self._on_session_record_changed_in_live)
		
		self._fixed_length = 1
		self._fixed_length_on = False
		
		self._tap_color_index = 0
		self._shift_color_index = 0
		
		self._tap_button = None
		self._song.add_metronome_listener(self._on_metronome_status_changed)
		
		self._session_record = SpecialProSessionRecordingComponent(target_track_component = TargetTrackComponent(), control_surface = self._control_surface)
		self._session_record._set_parent(self)
		
		if self._control_surface._mk2_rgb:
			from .ColorsMK2 import CLIP_COLOR_TABLE, RGB_COLOR_TABLE
			self.set_rgb_mode(CLIP_COLOR_TABLE, RGB_COLOR_TABLE)
			
		self._setup_actions_buttons()	
		self._set_undo_button(self._side_buttons[0]) 
		#INSTANT: UNDO - LONG: REDO
		
		self._set_shift_button(self._side_buttons[1]) 
		#SHIFT BTN
		# PAD: SEL/VIEW - DOUBLE: CLEAR VIEW - LROW: LAUNCH QUANT
		
		self._set_click_button(self._side_buttons[2]) 
		# +PAD: COPY/PASTE CLIP +SHIFT PAD: LAUNCH SCN??? - DOUBLE: CLIC ON/OFF - LROW: TEMPO FUNCTIONS
		
		self._set_quantize_button(self._side_buttons[3]) 
		# +PAD: QUANT +SHIFT PAD: CREATE SCN???  - DOUBLE: REC QUANT ON/OFF - LROW: REC QUANT
		
		self._set_double_button(self._side_buttons[4]) 
		# +PAD: DOUBLE_MIDI +SHIFT PAD: CAPTURE_INS SCN??? - DOUBLE: FIX LENGTH QUANT ON/OFF - LROW: FIX LENGTH QUANT
		
		self._set_delete_button(self._side_buttons[5]) 
		# +PAD: DELETE CLIP - +SHIFT PAD: DELETE SCN - DOUBLE: UNMUTE - LROW: MUTE TRACK
		
		self._set_duplicate_button(self._side_buttons[6])
		# +PAD: DUPLICATE - +SHIFT PAD: DUPLICATE SCN - DOUBLE: UNSOLO - LROW: SOLO TRACK
		
		self._set_record_button(self._side_buttons[7]) 
		# +PAD: ARM+FIRE CLIP - SHIFT PAD: N/A - INSTANT: SES REC ON/OFF - DOUBLE: N/A - LROW: ARM TRACK
		
		self.update()
		
	def disconnect(self):
		self._song.remove_clip_trigger_quantization_listener(self._on_clip_trigger_quantization_changed_in_live)
		self._song.remove_midi_recording_quantization_listener(self._on_record_quantization_changed_in_live)
		self.song().remove_session_record_listener(self._on_session_record_changed_in_live)
		self._end_undo_step_task.kill()
		self._end_undo_step_task = None
		self._record_quantization_on = False
		self._shift_pressed = False
		self._delete_pressed = False
		self._duplicate_pressed = False
		self._double_pressed = False
		self._quantize_pressed = False
		self._slot_copy_buffer = None
		
		self._click_button = None
		self._undo_button = None
		self._shift_button = None
		self._delete_button = None
		self._duplicate_button = None
		self._double_button = None
		self._quantize_button = None
		self._record_button = None
		self._tap_button = None
		
	def _is_shifting(self):
		return self._shift_pressed

	def _is_copypasting(self):
		return self._click_pressed
	
	def _is_deleting(self):
		return self._delete_pressed
	
	def _is_duplicating(self):
		return self._duplicate_pressed
	
	def _is_doubling(self):
		return self._double_pressed
	
	def _is_quantizing(self):
		return self._quantize_pressed 
	
	def _is_fixed_length_on(self):
		return self._fixed_length_on

	def _should_arm(self):
		return self._record_pressed or self._record_mode_on
	
	def _is_enabled(self):
		return self.is_enabled()
	
	def _is_pro_mode_on(self):
		return self._pro_mode_on
	
	def _set_pro_mode_on(self, pro_mode_on):
		self._pro_mode_on = pro_mode_on
	
	def _set_slot_copy_buffer(self, slot):
		self._slot_copy_buffer = slot
	
	def _get_slot_copy_buffer(self):
		return self._slot_copy_buffer	 
	
	def _should_copy(self):
		return self._slot_copy_buffer is None  
	
	def _get_song(self):
		return self._song
	
	def _get_record_quantization(self):
		return self._record_quantization

	def _setup_actions_buttons(self):
		for scene_index in xrange(self._num_scenes):
			scene = self.scene(scene_index)
			scene._set_parent(self)
			for track_index in xrange(self._num_tracks):
				slot = scene.clip_slot(track_index)
				slot._set_parent(scene)

# UNDO button and its listener
	def _set_undo_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if (self._undo_button != None):
			self._undo_button.remove_value_listener(self._undo_button_value)
		self._undo_button = button
		if (self._undo_button != None):
			self._undo_button.add_value_listener(self._undo_button_value, identify_sender=True)
			self._undo_button.turn_off()

	def _undo_button_value(self, value, sender):
		assert (value in range(128))		
		if self.is_enabled() and self._is_pro_mode_on() and self._undo_button != None:
			now = time.time()
			if ((value is not 0) or (not sender.is_momentary())):
				self._last_undo_time = now
			else:
				if now - self._last_undo_time < LONG_PRESS:
					if self.song().can_undo:
						self.song().undo()
						self._print("Undo")
					else:
						self._print("Can't Undo!") 

				else:
					if self.song().can_redo:
						self.song().redo()
						self._print("Redo")
					else:
						self._print("Can`t Redo!") 
			self._update_undo_button()					

	def _update_undo_button(self):
		if self.is_enabled() and self._is_pro_mode_on() and self._undo_button != None:
			self._undo_button.set_on_off_values("ProSession.Undo")
			if self.song().can_undo:
				self._undo_button.turn_on()
			else:
				self._undo_button.turn_off()	   
				

# SHIFT Button
	def _set_shift_button(self, button=None):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._shift_button != button):
			if (self._shift_button != None):
				self._shift_button.remove_value_listener(self._shift_button_value)
			self._shift_button = button
			if (self._shift_button != None):
				assert isinstance(button, ButtonElement)
				self._shift_button.add_value_listener(self._shift_button_value, identify_sender=True)
				self._shift_button.turn_off()

	def _shift_button_value(self, value, sender):
		assert (value in range(128))
		if self.is_enabled() and self._is_pro_mode_on() and self._shift_button != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._print("Select clip - [ Set launch quantization -> now: "+ self._get_launch_quant_msg() +" ]")
				self._shift_pressed = True
			else:
				self._shift_pressed = False
				if (time.time() - self._last_shift_time) < SHORT_PRESS:
					self.application().view.hide_view('Detail')	
				self._last_shift_time = time.time()
			self.update()
			
	def _update_shift_button(self):
		if self.is_enabled() and self._is_pro_mode_on() and self._shift_button != None:
			self._shift_button.set_on_off_values("ProSession.Shift")
			if self._shift_pressed or self._launch_quantization_on:
				self._shift_button.turn_on()
			else:
				self._shift_button.turn_off()
				
	def _increment_launch_qntz_value(self):
		if(self._launch_quantization_on):
			quant_idx = LAUNCH_QNTZ_RATES.index(self._launch_quantization)
			if(quant_idx<LAUNCH_QNTZ_RATES_LEN-1):
				self.song().clip_trigger_quantization = LAUNCH_QNTZ_RATES[quant_idx+1]
			
	def _decrement_launch_qntz_value(self):
		if(self._launch_quantization_on):
			quant_idx = LAUNCH_QNTZ_RATES.index(self._launch_quantization)
			if(quant_idx>0):
				self.song().clip_trigger_quantization = LAUNCH_QNTZ_RATES[quant_idx-1]			  
	   

# CLICK button and its listener
	def _set_click_button(self, button=None):
		assert isinstance(button, (ButtonElement, type(None)))
		if self._click_button != None:
			self._click_button.remove_value_listener(self._click_value)
		self._click_button = button
		if self._click_button != None:
			self._click_button.add_value_listener(self._click_value, identify_sender=True)
			self._click_button.turn_off()

	def _click_value(self, value, sender):
		assert (value in range(128))
		if self.is_enabled() and self._is_pro_mode_on() and self._click_button != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._click_pressed = True
				if self._shift_pressed:
					self._print("Launch scene - [ Tempo ]")
				else:
					self._print("Copy/paste clip - [ Tempo ]")
			else:
				self._click_pressed = False
				self._tap_button = None
				self._slot_copy_buffer = None
				if (time.time() - self._last_click_time) < SHORT_PRESS:
					self.song().metronome = not self.song().metronome
					if self.song().metronome :
						self._print("Metronome On")
					else:
						self._print("Metronome Off")				
				self._last_click_time = time.time()	 
			self.update()			  
			
	def _tap_tempo_value(self, value):
		if self.is_enabled() and self._is_pro_mode_on():
			if not self._end_undo_step_task.is_running:
				self.song().begin_undo_step()
			self._end_undo_step_task.restart()
			self.song().tap_tempo()
		 
	def _update_click_button(self):
		if self.is_enabled() and self._is_pro_mode_on() and self._click_button != None:
			self._click_button.set_on_off_values("ProSession.Click")
			if self.song().metronome:
				self._click_button.turn_on()
			else:
				self._click_button.turn_off()   
				
	def _on_metronome_status_changed(self):
		if self.is_enabled() and self._is_pro_mode_on():
			self._update_click_button()			

	def _nudge_down(self, value):
		if self.is_enabled() and self._is_pro_mode_on():
			self.song().nudge_down = value > 0
	
	def _nudge_up(self, value):
		if self.is_enabled() and self._is_pro_mode_on():
			self.song().nudge_up = value > 0

	def _change_tempo(self, tempo_delta):
		if self.is_enabled() and self._is_pro_mode_on():
			new_tempo = int(self.song().tempo  + tempo_delta)
			if(new_tempo >=1 and new_tempo <999 ):
				self.song().tempo = new_tempo

# QUANTIZE button and its listener
	def _set_quantize_button(self, button=None):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._quantize_button != button):
			if (self._quantize_button != None):
				self._quantize_button.remove_value_listener(self._quantize_button_value)
			self._quantize_button = button
			if (self._quantize_button != None):
				assert isinstance(button, ButtonElement)
				self._quantize_button.add_value_listener(self._quantize_button_value, identify_sender=True)
				self._quantize_button.turn_off()

	def _quantize_button_value(self, value, sender):
		assert (value in range(128))
		if self.is_enabled() and self._is_pro_mode_on() and self._quantize_button != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._quantize_pressed = True
				if self._shift_pressed:
					self._print("Create Scene - [ Record quantization -> now: "+ self._get_record_quant_msg() +" ]")
				else:
					self._print("Quantize clip - [ Record quantization -> now: "+ self._get_record_quant_msg() +" ]")
			else:
				self._quantize_pressed = False
				if (time.time() - self._last_quantize_time) < SHORT_PRESS:
					self._record_quantization_on = not self._record_quantization_on
					self.song().midi_recording_quantization = self._record_quantization if self._record_quantization_on else Rec_Q.rec_q_no_q					
				self._last_quantize_time = time.time()	 
			self.update()  
			
	def _update_quantize_button(self):
		if self.is_enabled() and self._is_pro_mode_on() and self._quantize_button != None:
			self._quantize_button.set_on_off_values("ProSession.Quantize")
			if self._record_quantization_on:
				self._quantize_button.turn_on()
			else:
				self._quantize_button.turn_off()
			
	def _increment_rec_qntz_value(self):
		rec_quant_value = self._get_song().midi_recording_quantization
		quant_on = rec_quant_value !=Rec_Q.rec_q_no_q
		if(quant_on):
			quant_idx = REC_QNTZ_RATES.index(rec_quant_value)
			if(quant_idx<REC_QNTZ_RATES_LEN-1):
				self.song().midi_recording_quantization = REC_QNTZ_RATES[quant_idx+1]

	def _decrement_rec_qntz_value(self):
		rec_quant_value = self._get_song().midi_recording_quantization
		quant_on = rec_quant_value !=Rec_Q.rec_q_no_q
		if(quant_on):
			quant_idx = REC_QNTZ_RATES.index(rec_quant_value)
			if(quant_idx>0):
				self.song().midi_recording_quantization = REC_QNTZ_RATES[quant_idx-1]
	
	def _on_record_quantization_changed_in_live(self):
		rec_quant_value = self._get_song().midi_recording_quantization
		quant_on = rec_quant_value !=Rec_Q.rec_q_no_q
		if quant_on:
			self._record_quantization = rec_quant_value
		self._record_quantization_on = quant_on

		self._print("Record quantization: " + self._get_record_quant_msg())
		self.update()
   
	def _get_record_quant_msg(self):
		if(self._record_quantization_on):
			return ("ON: " + str(REC_QNTZ_NAMES[REC_QNTZ_RATES.index(self._record_quantization)]))
		else: 
			return "OFF"
   
	def _on_clip_trigger_quantization_changed_in_live(self):
		launch_quant_value = self._get_song().clip_trigger_quantization
		quant_on = launch_quant_value !=_Q.q_no_q
		if quant_on:
			self._launch_quantization = launch_quant_value
		self._launch_quantization_on = quant_on		

		self._print("Launch quantization: " + self._get_launch_quant_msg()) 
		self.update() 
		
	def _on_session_record_changed_in_live(self):
		self.update() 
	
	def _get_launch_quant_msg(self):
		if(self._launch_quantization_on):
			return ("ON: " + str(LAUNCH_QNTZ_NAMES[LAUNCH_QNTZ_RATES.index(self._launch_quantization)]))
		else: 
			return "OFF"
	
# DOUBLE button and its listener
	def _set_double_button(self, button=None):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._double_button != button):
			if (self._double_button != None):
				self._double_button.remove_value_listener(self._double_button_value)
			self._double_button = button
			if (self._double_button != None):
				assert isinstance(button, ButtonElement)
				self._double_button.add_value_listener(self._double_button_value, identify_sender=True)
				self._double_button.turn_off()

	def _double_button_value(self, value, sender):
		assert (value in range(128))
		if self.is_enabled() and self._is_pro_mode_on() and self._double_button != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._double_pressed = True
				if self._shift_pressed:
					self._print("Capture scene - [ Clip fixed length recording -> now: "+ self._get_fixed_length_msg() +" ]")
				else:
					self._print("Double midi clip - [ Clip fixed length recording -> now: "+ self._get_fixed_length_msg() +" ]")
			else:
				self._double_pressed = False
				if (time.time() - self._last_fixed_time) < SHORT_PRESS:
					self._fixed_length_on = not self._fixed_length_on
					self._display_fixed_length_info()
				self._last_fixed_time = time.time()	 
			self.update()  
	
	def _update_double_button(self):
		if self.is_enabled() and self._is_pro_mode_on() and self._double_button != None:
			self._double_button.set_on_off_values("ProSession.Double")
			if self._fixed_length_on:
				self._double_button.turn_on()
			else:
				self._double_button.turn_off()
				
	def _increment_fixed_length_value(self):
		if(self._fixed_length_on):
			if(self._fixed_length<MAX_FIXED_LENGTH):
				if(self._fixed_length==0.25):
					self._fixed_length = 0.5
				elif(self._fixed_length==0.5):
					self._fixed_length = 1 
				else: 
					self._fixed_length += 1

	def _decrement_fixed_length_value(self):
		if(self._fixed_length_on):
			if(self._fixed_length>0.25):
				if(self._fixed_length==0.5):
					self._fixed_length = 0.25 
				elif(self._fixed_length==1):
					self._fixed_length = 0.5
				else: 
					self._fixed_length -= 1			   
				
# DELETE button and its listener
	def _set_delete_button(self, button=None):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._delete_button != button):
			if (self._delete_button != None):
				self._delete_button.remove_value_listener(self._delete_button_value)
			self._delete_button = button
			if (self._delete_button != None):
				assert isinstance(button, ButtonElement)
				self._delete_button.add_value_listener(self._delete_button_value, identify_sender=True)
				self._delete_button.turn_off()

	def _delete_button_value(self, value, sender):
		assert (value in range(128))
		if self.is_enabled() and self._is_pro_mode_on() and self._delete_button != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._delete_pressed = True
				if self._shift_pressed:
					self._print("Delete scene")
				else:
					self._print("Delete clip  - [ Mute Tracks ]")
			else:
				self._delete_pressed = False
				if (time.time() - self._last_mute_time) < SHORT_PRESS:
					for track in tuple(self.song().tracks) + tuple(self.song().return_tracks):
						if track.mute:
							track.mute = False
				self._last_mute_time = time.time()				   
			self.update()
	
	def _update_delete_button(self):
		if self.is_enabled() and self._is_pro_mode_on() and self._delete_button != None:
			self._delete_button.set_on_off_values("ProSession.Delete")
			if self._delete_pressed:
				self._delete_button.turn_on()
			else:
				self._delete_button.turn_off()

# DUPLICATE button and its listener
	def _set_duplicate_button(self, button=None):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._duplicate_button != button):
			if (self._duplicate_button != None):
				self._duplicate_button.remove_value_listener(self._duplicate_button_value)
			self._duplicate_button = button
			if (self._duplicate_button != None):
				assert isinstance(button, ButtonElement)
				self._duplicate_button.add_value_listener(self._duplicate_button_value, identify_sender=True)
				self._duplicate_button.turn_off()

	def _duplicate_button_value(self, value, sender):
		assert (value in range(128))
		if self.is_enabled() and self._is_pro_mode_on() and self._duplicate_button != None:
			if ((value is not 0) or (not sender.is_momentary())):
				self._duplicate_pressed = True
				if self._shift_pressed:
					self._print("Duplicate scene")
				else:
					self._print("Duplicate clip - [ Solo track ]")
			else:
				self._duplicate_pressed = False
				if (time.time() - self._last_solo_time) < SHORT_PRESS:
					for track in tuple(self.song().tracks) + tuple(self.song().return_tracks):
						if track.solo:
							track.solo = False
				self._last_solo_time = time.time()				
			self.update()
	
	def _update_duplicate_button(self):
		if self.is_enabled() and self._is_pro_mode_on() and self._duplicate_button != None:
			self._duplicate_button.set_on_off_values("ProSession.Duplicate")
			if self._duplicate_pressed:
				self._duplicate_button.turn_on()
			else:
				self._duplicate_button.turn_off()

# RECORD button and its listener
	def _set_record_button(self, button=None):
		assert (isinstance(button, (ButtonElement, type(None))))
		if (self._record_button != button):
			if (self._record_button != None):
				self._record_button.remove_value_listener(self._record_button_value)
			self._record_button = button
			if (self._record_button != None):
				assert isinstance(button, ButtonElement)
				self._record_button.add_value_listener(self._record_button_value, identify_sender=True)
				self._record_button.turn_off()

	def _record_button_value(self, value, sender):
		assert (value in range(128))
		if self.is_enabled() and self._is_pro_mode_on() and self._record_button != None:
			if self._shift_pressed:
				if value != 0 or not self._record_button.is_momentary():
					self._record_mode_on = not self._record_mode_on
					self._session_record.set_record_mode(self._record_mode_on)
					if(self._record_mode_on):
						self._print("Autorecord: On")
					else:
						self._print("Autorecord: Off")
			else:
				if ((value is not 0) or (not sender.is_momentary())):
					self._record_pressed = True
					self._last_record_time = time.time()
					self._print("Record clip -  [ Arm track ]")
				else:
					self._record_pressed = False
					if (time.time() - self._last_record_time) < LONG_PRESS and not self._is_arming:
						self._session_record._on_record_button_value()
					self._armed_track_count=0
					self._is_arming = False
			self.update()

	def _update_record_button(self):
		if self.is_enabled() and self._is_pro_mode_on() and self._record_button != None:
			if self._record_mode_on:
				self._record_button.set_on_off_values("ProSession.SessionRecMode")
			else:
				self._record_button.set_on_off_values("ProSession.SessionRec")
			song = self.song()
			status = song.session_record_status
			if status == Live.Song.SessionRecordStatus.on or song.session_record:
				self._record_button.turn_on()
			else:
				self._record_button.turn_off()

# STOP TRACK button and its listener
	#for line in traceback.format_stack():
	#Live.Base.l og(line.strip())
	#Live.Base.l og("SpecialProSessionComponent _update_stop_track_clip_buttons: " + str(self.is_enabled()))

	def _update_stop_track_clip_buttons(self):
		self._tap_button = None
		if self.is_enabled():
			for index in xrange(self._num_tracks):
				self._update_stop_clips_led(index)
			for index in xrange(8):
				self._update_select_leds(index)  

	def _update_stop_clips_led(self, index):
		if not self._is_pro_mode_on():
			super(SpecialSessionComponent, self)._update_stop_clips_led(index) 
		elif (self._stop_track_clip_buttons != None) and (index < len(self._stop_track_clip_buttons)):
			button = self._stop_track_clip_buttons[index]
			tracks_to_use = self.tracks_to_use()
			track_index = index + self.track_offset()
			if 0 <= track_index < len(tracks_to_use):
				track = tracks_to_use[track_index]
				if(self._record_pressed):
					if track.can_be_armed:
						if track.arm:
							button.send_value("Recording.On")
						else:
							button.send_value("Recording.Off")
					elif track.is_foldable:
						if track.fold_state == 0:
							button.send_value("ProSession.ClipUnFoldedTrack")
						else:
							button.send_value("ProSession.ClipFoldedTrack")  
				elif(self._duplicate_pressed):
					if track.solo:
						button.send_value("Mixer.Solo.On")
					else:
						button.send_value("Mixer.Solo.Off")	
				elif(self._delete_pressed):
					if track.mute:
						button.send_value("TrackController.Mute.Off")
					else:
						button.send_value("TrackController.Mute.On")  
				else:
					if not (self._quantize_pressed or self._click_pressed or self._double_pressed or self._shift_pressed):
						if track.fired_slot_index == -2:
							button.send_value(self._stop_clip_triggered_value)
						elif track.playing_slot_index >= 0:
							button.send_value(self._stop_clip_value)
						else:
							button.turn_off()
			else:
				button.send_value("DefaultButton.Disabled")
				#button.send_value(4)
				
	def _update_select_leds(self, index):
		if self._is_pro_mode_on() and (self._stop_track_clip_buttons != None) and (index < len(self._stop_track_clip_buttons)):
			if(self._quantize_pressed):
				self._update_rec_qntz_leds(index)
			elif(self._click_pressed):
				self._update_tempo_leds(index)					   
			elif(self._double_pressed):
				self._update_fixed_length_leds(index)			
			elif(self._shift_pressed):
				self._update_clip_trigger_leds(index)			
		 
	def _update_clip_trigger_leds(self, index):
		button = self._stop_track_clip_buttons[index]
		if(index==0):
			if(self._launch_quantization_on):
				button.send_value("LaunchQuant.On")
			else:
				button.send_value("LaunchQuant.Off")  
		elif(index==1):
			if((self._get_song().clip_trigger_quantization != _Q.q_8_bars)and self._launch_quantization_on):
				button.send_value("LaunchQuant.PlusMinus.On")
			else:
				button.send_value("LaunchQuant.PlusMinus.Off")
		elif(index==2):
			if((self._get_song().clip_trigger_quantization != _Q.q_thirtytwoth) and self._launch_quantization_on):
				button.send_value("LaunchQuant.PlusMinus.On")
			else:
				button.send_value("LaunchQuant.PlusMinus.Off")
		else:
			if(self._launch_quantization_on):
				launch_quant_value = self._get_song().clip_trigger_quantization
				sendValue = "LaunchQuant.Value.On"
			else:
				launch_quant_value = self._launch_quantization   
				sendValue = "LaunchQuant.Value.Idle" 
			
			if(launch_quant_value in LAUNCH_QNTZ_FIXED_RATES):
				quant_idx = LAUNCH_QNTZ_FIXED_RATES.index(launch_quant_value)
				#LaunchQuant values 8 Bars, 4 Bars, 2 Bars, 1 Bar, 1/2, 1/2t, 1/4, 1/4t, 1/8, 1/8t, 1/16, 1/16t, 1/32
				if((index-3) == quant_idx):
					button.send_value(sendValue)
				else:
					button.send_value("LaunchQuant.Value.Off")
			else:
				button.send_value("LaunchQuant.Value.Off")	
				
	def _update_rec_qntz_leds(self, index):
		button = self._stop_track_clip_buttons[index]
		if(index==0):
			if(self._record_quantization_on):
				button.send_value("RecQuant.On") 
			else:
				button.send_value("RecQuant.Off")  
		elif(index==1):
			if((self._get_song().midi_recording_quantization != Rec_Q.rec_q_quarter) and self._record_quantization_on):
				button.send_value("RecQuant.PlusMinus.On")
			else:
				button.send_value("RecQuant.PlusMinus.Off")
		elif(index==2):
			if ((self._get_song().midi_recording_quantization!= Rec_Q.rec_q_thirtysecond) and self._record_quantization_on):
				button.send_value("RecQuant.PlusMinus.On")
			else:
				button.send_value("RecQuant.PlusMinus.Off")
		else:
			if(self._record_quantization_on):
				rec_quant_value = self._get_song().midi_recording_quantization
				sendValue = "RecQuant.Value.On"
			else:
				rec_quant_value = self._record_quantization	
				sendValue = "RecQuant.Value.Idle"
				
			if(rec_quant_value in REC_QNTZ_FIXED_RATES):
				quant_idx = REC_QNTZ_FIXED_RATES.index(rec_quant_value)
				#RecQuant values 1/4, 1/8, 1/8+t, 1/16, 1/16+t
				if((index-3) == quant_idx):
					button.send_value(sendValue)
				else:
					button.send_value("RecQuant.Value.Off")
			else:
				button.send_value("RecQuant.Value.Off")				

	def _update_tempo_leds(self, index):
		button = self._stop_track_clip_buttons[index]
		if(index==0):
			if(self.song().metronome):
				button.send_value("Metronome.On")
			else:
				button.send_value("Metronome.Off")  
		elif(index==1 or index==2):
			button.send_value("Metronome.Nudge")
		elif(index==3 or index==6):
			button.send_value("Metronome.DeltaFive")
		elif(index==4 or index==5):
			button.send_value("Metronome.DeltaOne")			  
		elif(index==7):
			self._tap_button = button	  
			button.send_value("Metronome.DeltaOne")		
			
	def _update_fixed_length_leds(self, index):
		button = self._stop_track_clip_buttons[index]
		if(index==0):
			if(self._fixed_length_on):
				button.send_value("FixedLength.On")
			else:
				button.send_value("FixedLength.Off")  
		elif(index==1):
			if(self._fixed_length > 0.25 and self._fixed_length_on):
				button.send_value("FixedLength.PlusMinus.On")
			else:
				button.send_value("FixedLength.PlusMinus.Off")
		elif(index==2):
			if(self._fixed_length <= 31 and self._fixed_length_on):
				button.send_value("FixedLength.PlusMinus.On")
			else:
				button.send_value("FixedLength.PlusMinus.Off")
		else:
			if(self._fixed_length in FIXED_LENGTH_VALUES):
				fl_idx = FIXED_LENGTH_VALUES.index(self._fixed_length)
				#Fixed Length values 0.25, 1, 2, 4, 8
				if((index-3) == fl_idx):
					if(self._fixed_length_on):
						button.send_value("FixedLength.Value.On")
					else:
						button.send_value("FixedLength.Value.Idle")
				else:
					button.send_value("FixedLength.Value.Off")	
			else:
				button.send_value("FixedLength.Value.Off")						  

	@subject_slot_group('value')
	def _on_stop_track_value(self, value, button):
		if self._is_pro_mode_on():
			if self.is_enabled():
				if(self._quantize_pressed):
					self._set_rec_qntz_value(value, button)
				elif(self._double_pressed):
					self._set_fixed_length_value(value, button)
				elif(self._click_pressed):
					self._set_tempo_value(value, button)					
				elif(self._shift_pressed):
					self._set_launch_qntz_value(value, button)			   
				elif self._record_pressed:
					self._do_arm_track(value, button)				
				elif self._duplicate_pressed:
					self._do_solo_track(value, button)
				elif self._delete_pressed:
					self._do_mute_track(value, button)
				else:
					super(SpecialProSessionComponent, self)._on_stop_track_value(value, button)
				self.update()
		else:  
			super(SpecialProSessionComponent, self)._on_stop_track_value(value, button)
			
	def _set_tempo_value(self, value, button):		
		index = list(self._stop_track_clip_buttons).index(button)
		if(index==0 and (value is not 0 or not button.is_momentary())):
			self.song().metronome = not self.song().metronome
		elif(index==1):
			self._nudge_down(value)
		elif(index==2):
			self._nudge_up(value)
		elif(index==3 and (value is not 0 or not button.is_momentary())):
			self._change_tempo(-5)
		elif(index==4 and (value is not 0 or not button.is_momentary())):
			self._change_tempo(-1)
		elif(index==5 and (value is not 0 or not button.is_momentary())):
			self._change_tempo(1)		
		elif(index==6 and (value is not 0 or not button.is_momentary())):
			self._change_tempo(5)														 
		elif(index==7 and (value is not 0 or not button.is_momentary())):
			self._tap_tempo_value(value)
						
	def _set_fixed_length_value(self, value, button):		
		if value is not 0 or not button.is_momentary():
			index = list(self._stop_track_clip_buttons).index(button)
			if(index==0):
				self._fixed_length_on = not self._fixed_length_on
			elif(index==1):
				self._decrement_fixed_length_value()
			elif(index==2):
				self._increment_fixed_length_value()
			else:
				if(self._fixed_length != FIXED_LENGTH_VALUES[index-3]):
					self._fixed_length = FIXED_LENGTH_VALUES[index-3]
					self._fixed_length_on = True
				else:
					self._fixed_length_on = not self._fixed_length_on	
			self._display_fixed_length_info()					   
				
	def _set_rec_qntz_value(self, value, button):		
		if value is not 0 or not button.is_momentary():
			index = list(self._stop_track_clip_buttons).index(button)
			if(index==0):
				self._record_quantization_on = not self._record_quantization_on
				self.song().midi_recording_quantization = self._record_quantization if self._record_quantization_on else Rec_Q.rec_q_no_q	
			elif(index==1):
				self._decrement_rec_qntz_value()
			elif(index==2):
				self._increment_rec_qntz_value()
			else:
				if(self.song().midi_recording_quantization != REC_QNTZ_FIXED_RATES[index-3]):
					self.song().midi_recording_quantization = REC_QNTZ_FIXED_RATES[index-3]  
				else:
					self._record_quantization_on = not self._record_quantization_on
					self.song().midi_recording_quantization = self._record_quantization if self._record_quantization_on else Rec_Q.rec_q_no_q
				
	def _set_launch_qntz_value(self, value, button):		
		if value is not 0 or not button.is_momentary():
			index = list(self._stop_track_clip_buttons).index(button)
			if(index==0):
				self._launch_quantization_on = not self._launch_quantization_on
				self.song().clip_trigger_quantization = self._launch_quantization if self._launch_quantization_on else _Q.q_no_q	
			elif(index==1):
				self._decrement_launch_qntz_value()
			elif(index==2):
				self._increment_launch_qntz_value()
			else:
				if(self.song().clip_trigger_quantization != LAUNCH_QNTZ_FIXED_RATES[index-3]):
					self.song().clip_trigger_quantization = LAUNCH_QNTZ_FIXED_RATES[index-3]
				else:
					self._launch_quantization_on = not self._launch_quantization_on
					self.song().clip_trigger_quantization = self._launch_quantization if self._launch_quantization_on else _Q.q_no_q

	def _do_arm_track(self, value, button):		
		if value is not 0 or not button.is_momentary():
			tracks = self.tracks_to_use()
			track_index = list(self._stop_track_clip_buttons).index(button) + self.track_offset()
			if in_range(track_index, 0, len(tracks)) and tracks[track_index] in self.song().tracks:
				self._is_arming = True
				track = tracks[track_index]					
				if track.can_be_armed:
					if track.arm:
						track.arm = False
					else:
						if (not self._record_mode_on and self._get_song().exclusive_arm) or (self._record_mode_on and self._armed_track_count == 0): 
							for t in self._get_song().tracks:
								if t.can_be_armed and t.arm:
									t.arm = False
		
						track.arm = True
						self._armed_track_count += 1
						if self._get_song().view.selected_track != track:
							self._get_song().view.selected_track = track		 
				elif track.is_foldable:
					if track.fold_state == 0:
						track.fold_state = 1
					else:
						track.fold_state = 0
								
	def _do_mute_track(self, value, button):		
		if value is not 0 or not button.is_momentary():
			tracks = self.tracks_to_use()
			track_index = list(self._stop_track_clip_buttons).index(button) + self.track_offset()
			
			if in_range(track_index, 0, len(tracks)) and tracks[track_index] in self.song().tracks:
				track = tracks[track_index]					
				track.mute = not track.mute  
				
	def _do_solo_track(self, value, button):		
		if value is not 0 or not button.is_momentary():
			tracks = self.tracks_to_use()
			track_index = list(self._stop_track_clip_buttons).index(button) + self.track_offset()
			if in_range(track_index, 0, len(tracks)) and tracks[track_index] in self.song().tracks:
				track = tracks[track_index]					
				track.solo = not track.solo			  

	def update(self):
		SpecialSessionComponent.update(self)
		if self._is_pro_mode_on():
			self._update_shift_button()
			self._update_undo_button()
			self._update_click_button()
			self._update_delete_button()
			self._update_quantize_button()
			self._update_duplicate_button()
			self._update_double_button()
			self._update_record_button()
			self._update_stop_track_clip_buttons()
			
		if self._main_selector._main_mode_index == 0:
			self._update_OSD()

	def set_enabled(self, enabled):
		SpecialSessionComponent.set_enabled(self, enabled)
		self._session_record.set_enabled(enabled and self._is_pro_mode_on())
		if self._main_selector._main_mode_index == 0:
			self._update_OSD()

	def _display_fixed_length_info(self):
		""" Displays the current fixed recording length/state in the status bar. """
		if self.is_enabled() and self._is_pro_mode_on():
			self._print("Fixed length: " + self._get_fixed_length_msg())
				
	def _get_fixed_length_msg(self):
		if(self._fixed_length_on):
			if self._fixed_length == 0.25:
				return ("ON: 1 Beat")
			elif self._fixed_length == 0.5:
				return ("ON: 2 Beats")   
			elif self._fixed_length == 1:
				return ("ON: 1 Bar")  
			else:
				return ("ON: " + str(int((self._get_fixed_length()*(self.song().signature_denominator/4.0)) / self.song().signature_numerator)) + ' Bars')
		else: 
			return "OFF"				

	def _get_fixed_length(self):
		""" Returns the fixed length to use for recording or creating clips. """
		if(self._fixed_length== 0.25):
			return 1.0
		return 4.0 / self.song().signature_denominator * self.song().signature_numerator * (self._fixed_length)

	def _get_launch_quant(self):
		return self.song().clip_trigger_quantization

	def set_stop_track_clip_buttons(self, buttons):
		if (not self._is_pro_mode_on()) or buttons!=None:
			super(SpecialSessionComponent, self).set_stop_track_clip_buttons(buttons)
			
	def _print(self, msg):
		if self._control_surface!=None:
			self._control_surface.show_message(str(msg))
			
	#def _update_session_tempo_button(self):
	#	if self.is_enabled() and self._is_pro_mode_on():
	#		if self._tap_button != None and self._click_pressed:
	#			self._tap_button.send_value(TAP_COLORS[self._tap_color_index])
	#			self._tap_color_index = ((self._tap_color_index+1)%TAP_COLORS_LEN)
	#		if self._shift_button != None and not self._shift_pressed:
	#			self._shift_button.send_value(SHIFT_COLORS[self._shift_color_index])
	#			self._shift_color_index = ((self._shift_color_index+1)%SHIFT_COLORS_LEN)
