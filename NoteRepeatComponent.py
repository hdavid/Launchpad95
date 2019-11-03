from _Framework import Task
from _Framework.CompoundComponent import CompoundComponent
import Live

t = 3.0 / 2.0
NOTE_REPEAT_FREQUENCIES = [4, 4*t, 8, 8*t, 16, 16*t, 32, 32*t]
del t
QUANTIZATION_NAMES = ('1/4', '1/4t', '1/8',  '1/8t', '1/16', '1/16t', '1/32', '1/32t')

class DummyNoteRepeat(object):
    repeat_rate = 1.0
    enabled = False


class NoteRepeatComponent(CompoundComponent):
    """
    Component for setting up the note repeat
    """

    def __init__(self, *a, **k):
        super(NoteRepeatComponent, self).__init__(*a, **k)
        self._last_record_quantization = None
        self._note_repeat = None
        self._freq_index = 2
        self.set_note_repeat(None)
        
    def on_enabled_changed(self):
        if self.is_enabled():
            self._enable_note_repeat()
        else:
            self._disable_note_repeat()
 
    def set_freq_index(self, index):
        self._freq_index = index
        self._update_note_repeat(self.is_enabled())            
        
    def freq_index(self):              
        return self._freq_index
    
    def freq_name(self):              
        return QUANTIZATION_NAMES[self._freq_index]
    
    def update(self):
        super(NoteRepeatComponent, self).update()

    def set_select_buttons(self, buttons):
        self._options.select_buttons.set_control_element(buttons)

    def set_note_repeat(self, note_repeat):
        if not note_repeat:
            note_repeat = DummyNoteRepeat()
        if self._note_repeat != None:
            self._note_repeat.enabled = False
        self._note_repeat = note_repeat
        self._update_note_repeat(enabled=self.is_enabled())
        
    def set_pad_parameters(self, element):
        if element:
            element.reset()
        
    def _enable_note_repeat(self):
        self._last_record_quantization = self.song().midi_recording_quantization
        self._set_recording_quantization(False)
        self._update_note_repeat(enabled=True)
        
    def _disable_note_repeat(self):
        if not self.song().midi_recording_quantization and self._last_record_quantization:
            self._set_recording_quantization(self._last_record_quantization)
        self._update_note_repeat(enabled=False)

    def _set_recording_quantization(self, value):
        def doit():
            self.song().midi_recording_quantization = value

        self._tasks.parent_task.add(Task.run(doit))
        
    def _on_selected_option_changed(self, option):
        frequency = NOTE_REPEAT_FREQUENCIES[option]
        self._note_repeat.repeat_rate = 1.0 / frequency * 4.0
        
    def _update_note_repeat(self, enabled = False):
        self._on_selected_option_changed(self._freq_index)
        self._note_repeat.enabled = self.is_enabled()
