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
        Live.Base.log("NoteRepeatComponent - Init Start")
        super(NoteRepeatComponent, self).__init__(*a, **k)
        self._last_record_quantization = None
        self._note_repeat = None
        self._freq_index = 2
        self.set_note_repeat(None)
        Live.Base.log("NoteRepeatComponent - Init End")

    def on_enabled_changed(self):
        Live.Base.log("NoteRepeatComponent - on_enabled_changed Start")        
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
        Live.Base.log("NoteRepeatComponent - update Start")         
        super(NoteRepeatComponent, self).update()

    def set_select_buttons(self, buttons):
        Live.Base.log("NoteRepeatComponent - set_select_buttons Start")        
        self._options.select_buttons.set_control_element(buttons)

    def set_note_repeat(self, note_repeat):
        Live.Base.log("NoteRepeatComponent - set_note_repeat Start: " + str(note_repeat))          
        if not note_repeat:
            note_repeat = DummyNoteRepeat()
        if self._note_repeat != None:
            self._note_repeat.enabled = False
        self._note_repeat = note_repeat
        self._update_note_repeat(enabled=self.is_enabled())
        Live.Base.log("NoteRepeatComponent - set_note_repeat End")  

    def set_pad_parameters(self, element):
        Live.Base.log("NoteRepeatComponent - set_pad_parameters Start: " + str(element))           
        if element:
            element.reset()
        Live.Base.log("NoteRepeatComponent - set_pad_parameters End")  
        
    def _enable_note_repeat(self):
        self._last_record_quantization = self.song().midi_recording_quantization
        self._set_recording_quantization(False)
        self._update_note_repeat(enabled=True)
        
    def _disable_note_repeat(self):
        if not self.song().midi_recording_quantization and self._last_record_quantization:
            self._set_recording_quantization(self._last_record_quantization)
        self._update_note_repeat(enabled=False)

    def _set_recording_quantization(self, value):
        Live.Base.log("NoteRepeatComponent - _set_recording_quantization Start: " + str(value))
        def doit():
            self.song().midi_recording_quantization = value

        self._tasks.parent_task.add(Task.run(doit))
        Live.Base.log("NoteRepeatComponent - _set_recording_quantization End")

    def _on_selected_option_changed(self, option):
        Live.Base.log("NoteRepeatComponent - _on_selected_option_changed Start: " + str(option))        
        frequency = NOTE_REPEAT_FREQUENCIES[option]
        self._note_repeat.repeat_rate = 1.0 / frequency * 4.0
        Live.Base.log("NoteRepeatComponent - _on_selected_option_changed End")         

    def _update_note_repeat(self, enabled = False):
        self._on_selected_option_changed(self._freq_index)
        self._note_repeat.enabled = self.is_enabled()
