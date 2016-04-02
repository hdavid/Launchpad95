from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.Util import in_range

class ClipSlotMK2(ClipSlotComponent):
	
	def update(self):
		super(ClipSlotComponent, self).update()
		self._has_fired_slot = False
		button = self._launch_button_value.subject
		if self._allow_updates:
			if self.is_enabled() and button != None:
				value_to_send = self._feedback_value()
				if value_to_send in (None, -1) or value_to_send["value"] in (None, -1):
					button.turn_off()
				elif in_range(value_to_send["value"], 0, 128):
					button.force_next_send()
					button.send_value(value_to_send["value"], channel = value_to_send["channel"])
				else:
					button.force_next_send()
					button.set_light(value_to_send["value"])
		else:
			self._update_requests += 1
			
	
	def _feedback_value(self):
		if self._clip_slot != None:
			ret = {}
			ret["value"] = 0
			ret["channel"] = 0
			track = self._clip_slot.canonical_parent
			slot_or_clip = self._clip_slot.clip if self.has_clip() else self._clip_slot
	
			if getattr(slot_or_clip, 'controls_other_clips', True) and self._stopped_value != None:
				ret["value"] = self._stopped_value
			if self._track_is_armed(track) and self._clip_slot.has_stop_button and self._record_button_value != None:
				ret["value"] = self._record_button_value
				
			if slot_or_clip.color != None:
				ret["value"] = self._color_value(slot_or_clip.color)
				if slot_or_clip.is_triggered:
					#ret["channel"] = 1 # blink me
					if slot_or_clip.will_record_on_start:
						ret["value"] = self._triggered_to_record_value
					else:
						ret["value"]= self._triggered_to_play_value
						#ret["channel"] = 1 # blink me
				elif slot_or_clip.is_playing:
					if slot_or_clip.is_recording:
						ret["value"] = self._recording_value
					else:	
						ret["value"] = self._started_value
						#ret["channel"] = 2 # pulse me
			else:
				if slot_or_clip.is_triggered:
					if slot_or_clip.will_record_on_start:
						ret["value"] = self._triggered_to_record_value
					else:
						ret["value"]= self._triggered_to_play_value	
				elif slot_or_clip.is_playing:
					if slot_or_clip.is_recording:
						ret["value"] = self._recording_value
					else:	
						ret["value"] = self._started_value
					
			return ret