# -*- coding: utf-8 -*-

class Skin():

	def __init__(self, model):
		if model=='launchpad mk2':
			self.off = 0
			self.RED_FULL = 5
			self.RED_HALF = 6
			self.RED_THIRD = 9
			self.RED_BLINK = 5
			self.GREEN_FULL = 21
			self.GREEN_HALF = 27
			self.GREEN_THIRD = 29
			self.GREEN_BLINK = 21
			self.AMBER_FULL = 13
			self.AMBER_HALF = 15
			self.AMBER_THIRD = 19
			self.AMBER_BLINK = 14
			
		else:
			self.off = 4
			self.RED_FULL = 7
			self.RED_HALF = 6
			self.RED_THIRD = 5
			self.RED_BLINK = 11
			self.GREEN_FULL = 52
			self.GREEN_HALF = 36
			self.GREEN_THIRD = 20
			self.GREEN_BLINK = 56
			self.AMBER_FULL = ((self.RED_FULL + self.GREEN_FULL) - 4)
			self.AMBER_HALF = ((self.RED_HALF + self.GREEN_HALF) - 4)
			self.AMBER_THIRD = ((self.RED_THIRD + self.GREEN_THIRD) - 4)
			self.AMBER_BLINK = ((self.AMBER_FULL - 4) + 8)
		
		self.session = Session(model, self)
		#self.mixer = Mixer(model, self) # todo
		self.device = Device(model, self)
		self.scale = Scale(model, self)
		self.loop_selector = LoopSelector(model, self)
		self.note_editor = NoteEditor(model, self)
			
class Session():
	
		def __init__(self, model, skin):
			self.scene_triggered = skin.GREEN_BLINK
			self.clip_triggered_to_play = skin.GREEN_BLINK
			self.clip_triggered_to_stop = skin.AMBER_BLINK
			self.clip_triggered_to_record = skin.RED_BLINK
			self.clip_stopped = skin.AMBER_FULL
			self.clip_playing = skin.GREEN_FULL
			self.clip_recording = skin.RED_FULL
			self.clip_record = skin.RED_THIRD
			self.track_stop = skin.AMBER_THIRD

class Mixer():

		def __init__(self, model, skin):
			pass

class NoteEditor():
	
		def __init__(self, model, skin):
			
			self.velocity_1 = skin.GREEN_THIRD
			self.velocity_2 = skin.GREEN_HALF
			self.velocity_3 = skin.GREEN_FULL
			self.muted = skin.RED_THIRD
			self.playing = skin.RED_FULL
			self.note_marker = skin.AMBER_FULL
			self.page_marker = skin.AMBER_FULL
			self.metronome = skin.AMBER_FULL
			
class Scale():
	
		def __init__(self, model, skin):
			
			self.note_scale_root = skin.AMBER_THIRD
			self.note_in_scale = skin.GREEN_THIRD
			self.note_in_scale_highlight = skin.GREEN_HALF
			self.note_out_of_scale = skin.off
			
			self.note_selected_scale_root = skin.AMBER_HALF
			self.note_selected_in_scale = skin.GREEN_FULL
			self.note_selected_in_scale_highlight = skin.GREEN_FULL
			self.note_selected_out_of_scale = skin.AMBER_THIRD
			
			self.note_playing = skin.AMBER_FULL
			self.note_recording = skin.RED_FULL 
			
			self.pad = skin.GREEN_THIRD
			self.pad_selected = skin.GREEN_FULL
			self.pad_empty = skin.off 

class LoopSelector():

		def __init__(self, model, skin):
			self.in_loop = skin.AMBER_THIRD
			self.playing = skin.RED_HALF
			self.selected = skin.AMBER_FULL
			self.selected_playing = skin.RED_FULL
			self.out = skin.off 
			
class Device():

		def __init__(self, model, skin):
			self.slider_on = skin.GREEN_FULL
			self.slider_off = skin.GREEN_THIRD
			self.list_on = skin.AMBER_FULL
			self.list_off = skin.AMBER_THIRD
			self.toggle_on = skin.RED_FULL
			self.toggle_off = skin.RED_THIRD
			