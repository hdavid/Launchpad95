from _Framework.Skin import Skin
from .ColorsMK2 import Rgb

class Colors:
	
	class DefaultButton:
		On = Rgb.GREEN
		Off = Rgb.GREEN_THIRD
		Disabled = Rgb.BLACK

	class Mode: #mode buttons colour
		class Session:
			On = Rgb.GREEN
			Off = Rgb.GREEN_THIRD
		class Note:
			On = Rgb.LIGHT_BLUE
			Off = Rgb.LIGHT_BLUE_THIRD
		class Drum:
			On = Rgb.YELLOW
			Off = Rgb.YELLOW_HALF
		class Device:
			On = Rgb.PURPLE
			Off = Rgb.PURPLE_THIRD
		class StepSequencer:
			On = Rgb.PINK
			Off = Rgb.PINK_THIRD
		class StepSequencer2:
			On = Rgb.AMBER
			Off = Rgb.AMBER_THIRD
		class User:
			On = Rgb.BLUE
			Off = Rgb.BLUE_THIRD
		class User2:
			On = Rgb.BLUE
			Off = Rgb.BLUE_THIRD
		class Mixer:
			On = Rgb.MINT
			Off = Rgb.MINT_THIRD
	
	class Session:
		#scene
		SceneTriggered = Rgb.GREEN_BLINK
		Scene = Rgb.GREEN
		NoScene = Rgb.BLACK
		#clip states
		ClipStarted = Rgb.GREEN_PULSE
		ClipStopped = Rgb.RED_THIRD
		ClipRecording = Rgb.RED_PULSE
		ClipEmpty = Rgb.BLACK
		#trigs
		ClipTriggeredPlay = Rgb.GREEN_BLINK
		ClipTriggeredRecord = Rgb.RED_BLINK
		RecordButton = Rgb.RED_THIRD
		#stop button
		StopClip = Rgb.RED
		StopClipTriggered = Rgb.RED_BLINK
		#Enabled = Rgb.GREEN
		#Off = Rgb.GREEN_THIRD

	class Zooming:#session zoomin
		Selected = Rgb.AMBER
		Stopped = Rgb.RED
		Playing = Rgb.GREEN
		Empty = Rgb.BLACK

	class Mixer:
		class Arm:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Solo:
			On = Rgb.BLUE
			Off = Rgb.BLUE_THIRD
		class Mute:
			On = Rgb.YELLOW_THIRD
			Off = Rgb.YELLOW
		class Stop:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Selected:
			On = Rgb.LIGHT_BLUE
			Off = Rgb.LIGHT_BLUE_THIRD
		class Volume:
			On = Rgb.MINT
			Off = Rgb.MINT_THIRD
		class VolumeSlider:
			On = Rgb.MINT
			Off = Rgb.BLACK
		class Pan:
			On = Rgb.MINT
			Off = Rgb.MINT_THIRD
		class PanSlider:
			On = Rgb.MINT
			Off = Rgb.BLACK
		class Sends:
			On = Rgb.MINT
			Off = Rgb.MINT_THIRD
		class SendsSlider:
			On = Rgb.MINT
			Off = Rgb.BLACK
		class SendsSlider_1:
			On = Rgb.MINT
			Off = Rgb.BLACK
		class SendsSlider_2:
			On = Rgb.MINT
			Off = Rgb.BLACK

	class Sends:#not used yet on legacy launchpad
		A = Rgb.BLUE
		AAvail = Rgb.BLUE_THIRD
		B = Rgb.BLUE
		BAvail = Rgb.BLUE_THIRD
		C = Rgb.LIGHT_BLUE
		CAvail = Rgb.LIGHT_BLUE_THIRD
		D = Rgb.MINT
		DAvail = Rgb.MINT_THIRD
		E = Rgb.AMBER
		EAvail = Rgb.AMBER_THIRD
		F = Rgb.YELLOW
		FAvail = Rgb.YELLOW_THIRD
		G = Rgb.AMBER
		GAvail = Rgb.AMBER_THIRD
		H = Rgb.RED
		HAvail = Rgb.RED_THIRD

	class Device:#device mode colours
		class Bank:
			On = Rgb.BLUE
			Off = Rgb.BLUE_THIRD
		class Lock:
			Empty = Rgb.PURPLE
			Set = Rgb.RED_THIRD
			Locked = Rgb.RED
		class Slider:
			On = Rgb.PURPLE
			Off = Rgb.PURPLE_THIRD
		class PrecisionSlider:
			On = Rgb.LIGHT_BLUE
			Off = Rgb.LIGHT_BLUE_THIRD
		class Enum:
			On = Rgb.MINT
			Off = Rgb.MINT_THIRD
		class BigEnum:
			On = Rgb.YELLOW
			Off = Rgb.YELLOW_THIRD
		class Toggle:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
	
	class StepSequencer:
		class Scale:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Octave:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Mute:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Mode:
			On = Rgb.AMBER
			Off = Rgb.AMBER_THIRD
		class Lock:
			class ToTrack:
				On = Rgb.RED
				Off =  Rgb.RED_THIRD
			class ToClip:
				On =  Rgb.PURPLE
				Off = Rgb.PURPLE_THIRD
		class LoopSelector:
			SelectedPlaying = Rgb.PURPLE
			Playing = Rgb.PURPLE_HALF
			Selected = Rgb.BLUE
			InLoop = Rgb.BLUE_THIRD
		class Quantization:
			One=Rgb.BLACK
			Two=Rgb.GREEN_THIRD
			Three=Rgb.GREEN
			Four=Rgb.GREEN
		class NoteSelector:
			class Octave:
				On = Rgb.GREEN
				Off = Rgb.GREEN_THIRD
			Selected = Rgb.GREEN
			Playing = Rgb.RED
		class NoteEditor:
			class VelocityShifted:
				On = Rgb.AMBER
				Off = Rgb.AMBER_THIRD
			Velocity0 = Rgb.GREEN_THIRD
			Velocity1 = Rgb.GREEN_HALF
			Velocity2 = Rgb.GREEN
			Velocity3 = Rgb.GREEN_THIRD
			Muted = Rgb.DARK_GREY
			Playing = Rgb.RED
			Metronome = Rgb.BLUE
			NoteMarker = Rgb.AMBER
			PageMarker = Rgb.YELLOW
				
	class StepSequencer2:
		class Pitch:
			On = Rgb.BLUE
			Dim = Rgb.BLUE_THIRD
			Off = Rgb.BLACK
		class Octave:
			On = Rgb.PURPLE
			Dim = Rgb.PURPLE_THIRD
			Off = Rgb.BLACK
		class Velocity:
			On = Rgb.LIGHT_BLUE
			Dim = Rgb.LIGHT_BLUE_THIRD
			Off = Rgb.BLACK
		class Length:
			On = Rgb.MINT
			Dim = Rgb.MINT_THIRD
			Off = Rgb.BLACK
		class Random:
			On = Rgb.RED
			Off = Rgb.RED
		class NoteEditor:
			MetronomeInPage = Rgb.BLUE
			MetronomeInOtherPage = Rgb.BLUE_THIRD
			PlayInPage = Rgb.RED
			PlayInOtherPage = Rgb.RED_THIRD
			
	class Recording:
		On = Rgb.RED
		Off = Rgb.RED_THIRD
		Transition = Rgb.RED_BLINK
		
	class TrackController:
		class Recording:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class ImplicitRecording:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Play:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Stop:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Mute:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Undo:
			On = Rgb.AMBER
			Off = Rgb.AMBER_THIRD
		class Solo:
			On = Rgb.AMBER
			Off = Rgb.AMBER_THIRD
				
	class DrumGroup:
		PadEmpty = Rgb.BLACK
		PadFilled = Rgb.YELLOW
		PadSelected = Rgb.LIGHT_BLUE
		PadSelectedNotSoloed = Rgb.LIGHT_BLUE
		PadMuted = Rgb.AMBER_THIRD
		PadMutedSelected = Rgb.LIGHT_BLUE
		PadSoloed = Rgb.BLUE_THIRD
		PadSoloedSelected = Rgb.LIGHT_BLUE
		PadInvisible = Rgb.BLACK
		PadAction = Rgb.RED
		class Mute:
			On = Rgb.AMBER
			Off = Rgb.AMBER_THIRD
		class Solo:
			On = Rgb.BLUE
			Off = Rgb.BLUE_THIRD
			
	class Note:
		FeedbackRecord = Rgb.RED
		Feedback = Rgb.GREEN
		class Octave:
			On = Rgb.GREEN
			Off = Rgb.GREEN_THIRD
		class Scale:
			On = Rgb.AMBER
			Off = Rgb.AMBER_THIRD
		class Pads:
			Root = Rgb.BLUE
			InScale = Rgb.LIGHT_BLUE_HALF
			Highlight = Rgb.LIGHT_BLUE
			OutOfScale = Rgb.DARK_GREY
			Invalid = Rgb.BLACK
					
	class Scale:#scale edition
		class AbsoluteRoot:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Mode:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Key:		
			On = Rgb.GREEN
			Off = Rgb.GREEN_THIRD
		CircleOfFifths = Rgb.BLUE
		RelativeScale = Rgb.BLUE
		class Octave:
			On = Rgb.RED
			Off = Rgb.RED_THIRD
		class Modus:
			On = Rgb.BLUE
			Off = Rgb.BLUE_THIRD
		class QuickScale:
			On = Rgb.AMBER
			Off = Rgb.AMBER_THIRD
		
	class QuickScale:#quick scale on top of instrument mode
		class Modus:
			On = Rgb.AMBER
			Off = Rgb.AMBER_THIRD
		class Major: # quick scale while in major mode
			class Key:
				On = Rgb.GREEN
				Off = Rgb.GREEN_THIRD
			CircleOfFifths = Rgb.RED
			RelativeScale = Rgb.RED
			Mode = Rgb.GREEN
		class Minor:
			class Key:
				On = Rgb.RED
				Off = Rgb.RED_THIRD
			CircleOfFifths = Rgb.AMBER
			RelativeScale = Rgb.AMBER
			Mode = Rgb.GREEN
		class Other:
			class Key:
				On = Rgb.AMBER
				Off = Rgb.AMBER_THIRD
			CircleOfFifths = Rgb.RED
			RelativeScale = Rgb.RED
			Mode = Rgb.GREEN
		class NoteRepeater:
			On = Rgb.RED_BLINK
			Off = Rgb.BLACK
		class Quant:
			On = Rgb.GREEN
			Off = Rgb.GREEN_THIRD
			Mode = Rgb.GREEN
			Straight = Rgb.BLUE_THIRD
			Swing = Rgb.LIGHT_BLUE
			Dotted = Rgb.PURPLE_THIRD
			Flam = Rgb.PURPLE
			Selected = Rgb.RED
			Note = Rgb.RED_HALF	
			Tripplet = Rgb.RED_THIRD			

def make_skin():
	return Skin(Colors)