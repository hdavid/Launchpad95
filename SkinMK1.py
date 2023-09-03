from _Framework.Skin import Skin
from .ColorsMK1 import Rgb


class Colors:
    class DefaultButton:
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD
        Disabled = Rgb.BLACK

    class Mode:  # mode buttons colour
        class Session:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class ProSession:
            On = Rgb.RED
            Off = Rgb.RED_HALF

        class Note:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Drum:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Device:
            On = Rgb.RED
            Off = Rgb.RED_THIRD

        class StepSequencer:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class StepSequencer2:
            On = Rgb.RED
            Off = Rgb.RED_THIRD

        class User:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class User2:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class Mixer:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Track:
            On = Rgb.ORANGE
            Off = Rgb.ORANGE_HALF

    class Session:
        # scene
        SceneTriggered = Rgb.GREEN_BLINK
        Scene = Rgb.AMBER_THIRD
        NoScene = Rgb.BLACK
        # clip states
        ClipStarted = Rgb.GREEN
        ClipStopped = Rgb.AMBER
        ClipRecording = Rgb.RED
        ClipEmpty = Rgb.BLACK
        # trigs
        ClipTriggeredPlay = Rgb.GREEN_BLINK
        ClipTriggeredRecord = Rgb.RED_BLINK
        RecordButton = Rgb.RED_THIRD
        # stop button
        StopClip = Rgb.ORANGE_HALF
        StopClipTriggered = Rgb.ORANGE_BLINK_HALF
    # Enabled = Rgb.GREEN
    # Off = Rgb.GREEN_THIRD

    class ProSession:  # session zoomin
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD
        ClipStarted = Rgb.GREEN
        ClipTriggeredPlay = Rgb.GREEN_BLINK
        ClipStopped = Rgb.AMBER
        ClipFoldedTrack = Rgb.AMBER
        ClipUnFoldedTrack = Rgb.AMBER_HALF

        class Shift:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class Click:
            On = Rgb.AMBER_BLINK
            Off = Rgb.AMBER

        class Undo:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class Delete:
            On = Rgb.RED_THIRD
            Off = Rgb.RED_HALF

        class Duplicate:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class Double:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class Quantize:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class SessionRec:
            On = Rgb.RED_FULL
            Off = Rgb.RED_THIRD

        class SessionRecMode:
            On = Rgb.RED_BLINK
            Off = Rgb.RED_BLINK_THIRD

    class LaunchQuant:
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD

        class PlusMinus:
            On = Rgb.AMBER
            Idle = Rgb.AMBER_HALF
            Off = Rgb.AMBER_THIRD

        class Value:
            On = Rgb.MANDARIN_BLINK
            Idle = Rgb.MANDARIN
            Off = Rgb.ORANGE_HALF

    class FixedLength:
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD

        class PlusMinus:
            On = Rgb.AMBER
            Idle = Rgb.AMBER_HALF
            Off = Rgb.AMBER_THIRD

        class Value:
            On = Rgb.AMBER
            Idle = Rgb.AMBER_HALF
            Off = Rgb.AMBER_THIRD

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
            On = Rgb.ORANGE_BLINK
            Idle = Rgb.ORANGE
            Off = Rgb.ORANGE_HALF

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
            On = Rgb.RED
            Off = Rgb.RED_THIRD

        class Mute:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Stop:
            On = Rgb.RED
            Off = Rgb.RED_THIRD

        class Selected:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Volume:
            On = Rgb.GREEN_THIRD
            Off = Rgb.GREEN

        class VolumeSlider:
            On = Rgb.GREEN
            Off = Rgb.BLACK

        class Pan:
            On = Rgb.GREEN_THIRD
            Off = Rgb.GREEN

        class PanSlider:
            On = Rgb.AMBER
            Off = Rgb.BLACK

        class Sends:
            On = Rgb.GREEN_THIRD
            Off = Rgb.GREEN

        class SendsSlider:
            On = Rgb.GREEN_THIRD
            Off = Rgb.GREEN
        class SendsSlider_1:
            On = Rgb.GREEN_THIRD
            Off = Rgb.GREEN

        class SendsSlider_2:
            On = Rgb.GREEN_THIRD
            Off = Rgb.GREEN

    class Sends:  # not used yet on legacy launchpad
        A = Rgb.RED
        AAvail = Rgb.RED_THIRD
        B = Rgb.RED
        BAvail = Rgb.RED_THIRD
        C = Rgb.RED
        CAvail = Rgb.RED_THIRD
        D = Rgb.RED
        DAvail = Rgb.RED_THIRD
        E = Rgb.RED
        EAvail = Rgb.RED_THIRD
        F = Rgb.RED
        FAvail = Rgb.RED_THIRD
        G = Rgb.RED
        GAvail = Rgb.RED_THIRD
        H = Rgb.RED
        HAvail = Rgb.RED_THIRD

    class Device:  # device mode colours
        class Bank:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class Lock:
            Empty = Rgb.BLACK
            Set = Rgb.RED_THIRD
            Locked = Rgb.RED

        class DefaultSlider:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class CustomSlider0:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class CustomSlider1:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class CustomSlider2:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class CustomSlider3:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class CustomSlider4:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class CustomSlider5:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class CustomSlider6:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class CustomSlider7:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class PrecisionSlider:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class ModeToggle:
            Precision = Rgb.AMBER
            Normal = Rgb.AMBER_THIRD
            Stepless = Rgb.GREEN
        class Enum:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class BigEnum:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

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
                Off = Rgb.RED_THIRD

            class ToClip:
                On = Rgb.AMBER
                Off = Rgb.AMBER_THIRD

        class LoopSelector:
            SelectedPlaying = Rgb.RED
            Playing = Rgb.RED_THIRD
            Selected = Rgb.GREEN
            InLoop = Rgb.AMBER_THIRD

        class Quantization:
            One = Rgb.GREEN_THIRD
            Two = Rgb.GREEN_FULL
            Three = Rgb.AMBER_FULL
            Four = Rgb.RED_FULL

        class QuantizationLow:
            One = Rgb.GREEN_THIRD
            Two = Rgb.GREEN_FULL
            Three = Rgb.AMBER_HALF
            Four = Rgb.RED_HALF

        class NoteSelector:
            class Octave:
                On = Rgb.GREEN
                Off = Rgb.GREEN_THIRD

            Selected = Rgb.AMBER
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
            Muted = Rgb.RED_THIRD
            Playing = Rgb.RED
            Metronome = Rgb.RED
            NoteMarker = Rgb.AMBER
            PageMarker = Rgb.AMBER_THIRD
            CurrentPageMarker = Rgb.RED_THIRD
            CurrentPageMarkerPlay = Rgb.GREEN_THIRD

    class StepSequencer2:
        class Pitch:
            On = Rgb.GREEN
            Dim = Rgb.GREEN_THIRD
            Off = Rgb.BLACK

        class Octave:
            On = Rgb.RED
            Dim = Rgb.RED_THIRD
            Off = Rgb.BLACK

        class Velocity:
            On = Rgb.AMBER
            Dim = Rgb.AMBER_THIRD
            Off = Rgb.BLACK

        class Length:
            On = Rgb.AMBER
            Dim = Rgb.AMBER_THIRD
            Off = Rgb.BLACK

        class Random:
            On = Rgb.RED
            Off = Rgb.RED

        class NoteEditor:
            MetronomeInPage = Rgb.AMBER
            MetronomeInOtherPage = Rgb.AMBER_THIRD
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
            On = Rgb.ORANGE
            Off = Rgb.ORANGE_HALF

        class Mute:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Undo:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Solo:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

    class DrumGroup:
        PadEmpty = Rgb.BLACK
        PadFilled = Rgb.RED_THIRD
        PadFilled1 = Rgb.RED_THIRD
        PadFilled2 = Rgb.RED_THIRD
        PadFilled3 = Rgb.RED_THIRD
        PadFilled4 = Rgb.RED_THIRD
        PadFilled5 = Rgb.RED_THIRD
        PadSelected = Rgb.GREEN
        PadSelectedNotSoloed = Rgb.AMBER
        PadMuted = Rgb.AMBER
        PadMutedSelected = Rgb.AMBER
        PadSoloed = Rgb.AMBER
        PadSoloedSelected = Rgb.AMBER
        PadInvisible = Rgb.BLACK
        PadAction = Rgb.RED

        class Mute:
            On = Rgb.RED
            Off = Rgb.RED_THIRD

        class Solo:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

    class Note:
        FeedbackRecord = Rgb.RED
        Feedback = Rgb.AMBER

        class Octave:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class Scale:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Pads:
            Root = Rgb.AMBER_THIRD
            InScale = Rgb.GREEN_THIRD
            Highlight = Rgb.GREEN
            OutOfScale = Rgb.BLACK
            Invalid = Rgb.BLACK

    class Scale:  # scale edition
        class Horizontal:
            On = Rgb.LIME
            Off = Rgb.MANDARIN

        class AbsoluteRoot:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        class Mode:
            On = Rgb.RED
            Off = Rgb.RED_THIRD

        class Key:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

        CircleOfFifths = Rgb.RED
        RelativeScale = Rgb.RED

        class Octave:
            On = Rgb.RED
            Off = Rgb.RED_THIRD

        class Modus:
            On = Rgb.GREEN
            Off = Rgb.GREEN_THIRD

        class QuickScale:
            On = Rgb.AMBER
            Off = Rgb.AMBER_THIRD

    class QuickScale:  # quick scale on top of instrument mode
        class Modus:
            On = Rgb.MANDARIN
            Off = Rgb.ORANGE

        class Major:  # quick scale while in major mode
            class Key:
                On = Rgb.AMBER
                Off = Rgb.AMBER_THIRD

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
                On = Rgb.GREEN
                Off = Rgb.GREEN_THIRD

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
            Straight = Rgb.GREEN_THIRD
            Swing = Rgb.GREEN_THIRD
            Dotted = Rgb.GREEN_THIRD
            Flam = Rgb.GREEN_THIRD
            Selected = Rgb.RED
            Note = Rgb.RED_HALF
            Tripplet = Rgb.RED_THIRD


def make_skin():
    return Skin(Colors)
