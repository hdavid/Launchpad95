class Live(object):
    pass

class RackDevice(object):
    pass
    
    class RackDevice(object):
            pass

class DeviceParameter(object):
    pass
    
    @classmethod
    def DeviceParameter(cls):
        pass

class Song(object):
    pass
    
    class Quantization(object):
            
            
            def __init__(self):
                self.q_no_q = None

    
    class  SessionRecordStatus(object):
        
        
        def __init__(self):
            self.transition = None
            self.on = None
            self.off = None
        
    class CaptureMode(object):   
        
        
        def __init__(self):
            self.all_except_selected = None

class Track(object):
    pass
    
    class Track(object):
        pass

class MidiMap(object):
    pass
    
    class MapMode(object):
        
        def __init__(self):
            self.absolute = None

    
    @classmethod
    def NoteFeedbackRule(cls):
        pass
    
    @classmethod
    def CCFeedbackRule(cls):
        pass
    
    @classmethod
    def PitchBendFeedbackRule(cls):
        pass

    
    @classmethod
    def map_midi_note_with_feedback_map(cls, midi_map_handle, parameter, message_channel, message_identifier, feedback_rule):
        pass

    
    @classmethod
    def map_midi_cc_with_feedback_map(cls, midi_map_handle, parameter, message_channel, message_identifier, message_map_mode, feedback_rule, needs_takeover, mapping_sensitivity):
        pass

    
    @classmethod
    def map_midi_pitchbend_with_feedback_map(cls, midi_map_handle, parameter, message_channel, feedback_rule, needs_takeover):
        pass

    
    @classmethod
    def send_feedback_for_parameter(cls, midi_map_handle, parameter):
        pass

    
    @classmethod
    def forward_midi_note(cls, handle, midi_map_handle, message_channel, message_identifier):
        pass

    
    @classmethod
    def forward_midi_cc(cls, handle, midi_map_handle, message_channel, message_identifier):
        pass

    
    @classmethod
    def forward_midi_pitchbend(cls, handle, midi_map_handle, message_channel):
        pass
            
class Device(object):
    pass
    
    class DeviceType(object):
        
        def __init__(self):
            self.instrument = None            

class Application(object):
    
    class Application(object):
        pass
    
        class View(object):
            pass 
             
            class NavDirection(object):
                pass  
        
    @classmethod
    def combine_apcs(cls):
        return False
    
    @classmethod
    def get_application(cls):
        pass
    
    @classmethod
    def get_random_int(cls, param1, param2):
        pass
    
    @classmethod
    def encrypt_challenge2(cls, _challenge):
        pass
    
class Base(object):
    
    @classmethod
    def log(cls, _combine_active_instances):
        pass

    class LimitationError(object):
        pass
