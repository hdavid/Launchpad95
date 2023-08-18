from _Framework.Skin import Skin
from .ColorsMK2 import Rgb


class Colors:
    class DefaultButton:
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD
        Disabled = Rgb.BLACK

    class Mode:  # mode buttons colour
        class Session:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class ProSession:
            On = Rgb.MINT
            Off = Rgb.MINT_THIRD

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

        class Track:  # used in device component
            On = Rgb.MINT
            Off = Rgb.MINT_THIRD

    class Session:
        # scene
        SceneTriggered = Rgb.GREEN_BLINK
        Scene = Rgb.GREEN
        NoScene = Rgb.BLACK
        # clip states
        ClipStarted = Rgb.GREEN_PULSE
        ClipStopped = Rgb.RED_THIRD
        ClipRecording = Rgb.RED_PULSE
        ClipEmpty = Rgb.BLACK
        # trigs
        ClipTriggeredPlay = Rgb.GREEN_BLINK
        ClipTriggeredRecord = Rgb.RED_BLINK
        RecordButton = Rgb.RED_THIRD
        # stop button
        StopClip = Rgb.GREY
        StopClipTriggered = Rgb.GREY_BLINK
    # Enabled = Rgb.GREEN
    # Off = Rgb.GREEN_THIRD

    class ProSession:  # session zoomin
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD
        ClipStarted = Rgb.GREEN_PULSE
        ClipTriggeredPlay = Rgb.GREEN_BLINK
        ClipStopped = Rgb.RED_THIRD
        ClipFoldedTrack = Rgb.AMBER
        ClipUnFoldedTrack = Rgb.AMBER_HALF

        class Shift:
            On = Rgb.WHITE
            Off = Rgb.DARK_GREY

        class Click:
            On = Rgb.BLUE
            Off = Rgb.BLUE_THIRD

        class Undo:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class Delete:
            On = Rgb.RED_THIRD
            Off = Rgb.RED_HALF

        class Duplicate:
            On = Rgb.BLUE_HALF
            Off = Rgb.BLUE

        class Double:
            On = Rgb.PURPLE
            Off = Rgb.PURPLE_THIRD

        class Quantize:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class SessionRec:
            On = Rgb.RED
            Off = Rgb.RED_THIRD

        class SessionRecMode:
            On = Rgb.RED_BLINK
            Off = Rgb.RED_THIRD_BLINK

    class LaunchQuant:
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD

        class PlusMinus:
            On = Rgb.AMBER
            Idle = Rgb.AMBER_HALF
            Off = Rgb.AMBER_THIRD

        class Value:
            On = Rgb.YELLOW
            Idle = Rgb.YELLOW_HALF
            Off = Rgb.YELLOW_THIRD

    class FixedLength:
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD

        class PlusMinus:
            On = Rgb.AMBER
            Idle = Rgb.AMBER_HALF
            Off = Rgb.AMBER_THIRD

        class Value:
            On = Rgb.YELLOW
            Idle = Rgb.YELLOW_HALF
            Off = Rgb.YELLOW_THIRD

    class Metronome:
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD
        Nudge = Rgb.AMBER
        DeltaOne = Rgb.RED_THIRD
        DeltaFive = Rgb.RED

    class RecQuant:
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD

        class PlusMinus:
            On = Rgb.AMBER
            Idle = Rgb.AMBER_HALF
            Off = Rgb.AMBER_THIRD

        class Value:
            On = Rgb.YELLOW
            Idle = Rgb.YELLOW_HALF
            Off = Rgb.YELLOW_THIRD

    class Zooming:  # session zoomin
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

    class Sends:  # not used yet on legacy launchpad
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

    class Device:  # device mode colours
        class Bank:
            On = Rgb.BLUE
            Off = Rgb.BLUE_THIRD

        class Lock:
            Empty = Rgb.PURPLE
            Set = Rgb.RED_THIRD
            Locked = Rgb.RED

        class Slider0:
            On = Rgb.PURPLE
            Off = Rgb.BLACK
        class Slider1:
            On = Rgb.PURPLE
            Off = Rgb.BLACK
        class Slider2:
            On = Rgb.LIGHT_BLUE
            Off = Rgb.BLACK
        class Slider3:
            On = Rgb.LIGHT_BLUE
            Off = Rgb.BLACK
        class Slider4:
            On = Rgb.MINT
            Off = Rgb.BLACK
        class Slider5:
            On = Rgb.MINT
            Off = Rgb.BLACK
        class Slider6:
            On = Rgb.BLUE
            Off = Rgb.BLACK
        class Slider7:
            On = Rgb.BLUE
            Off = Rgb.BLACK
        class PrecisionSlider:
            On = Rgb.LIGHT_BLUE
            Off = Rgb.LIGHT_BLUE_THIRD

        class ModeToggle:
            Precision = Rgb.LIGHT_BLUE
            Normal = Rgb.LIGHT_BLUE_THIRD
            Stepless = Rgb.MINT_THIRD

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
            On = Rgb.YELLOW
            Off = Rgb.YELLOW_THIRD

        class Mode:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Lock:
            class ToTrack:
                On = Rgb.RED
                Off = Rgb.RED_THIRD

            class ToClip:
                On = Rgb.PURPLE
                Off = Rgb.PURPLE_THIRD

        class LoopSelector:
            SelectedPlaying = Rgb.PURPLE
            Playing = Rgb.PURPLE_HALF
            Selected = Rgb.BLUE
            InLoop = Rgb.BLUE_THIRD

        class Quantization:
            One = Rgb.GREEN
            Two = Rgb.YELLOW
            Three = Rgb.AMBER
            Four = Rgb.RED

        class QuantizationLow:
            One = Rgb.GREEN_HALF
            Two = Rgb.YELLOW_HALF
            Three = Rgb.AMBER_HALF
            Four = Rgb.RED_HALF

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
            Velocity3 = Rgb.AMBER_HALF
            Velocity4 = Rgb.AMBER
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
            On = Rgb.YELLOW
            Off = Rgb.YELLOW_THIRD

        class Undo:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Solo:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

    class DrumGroup:
        PadEmpty = Rgb.BLACK
        PadFilled = Rgb.YELLOW
        PadFilled1 = Rgb.PURPLE_THIRD
        PadFilled2 = Rgb.MINT_THIRD
        PadFilled3 = Rgb.PINK_THIRD
        PadFilled4 = Rgb.YELLOW
        PadFilled5 = Rgb.GREY
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

    class Scale:  # scale edition
        class Horizontal:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

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

    class QuickScale:  # quick scale on top of instrument mode
        class Modus:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Major:  # quick scale while in major mode
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
            Off = Rgb.RED_THIRD

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
