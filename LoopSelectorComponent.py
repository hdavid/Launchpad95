import time

from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

STEPSEQ_MODE_MULTINOTE = 2
class LoopSelectorComponent(ControlSurfaceComponent):

    def __init__(self, step_sequencer, buttons, control_surface):
        ControlSurfaceComponent.__init__(self)
        self._control_surface = control_surface
        self.set_enabled(False)
        self._step_sequencer = step_sequencer

        self._clip = None  # clip being played
        self._notes = None  # notes of the clip
        self._playhead = None  # contains the clip playing position

        self._loop_end = 0
        self._loop_start = 0

        self._blocksize = 8  # number of notes per block -> how many steps are in a button (depending on quantization for note length variable)
        self._block = 0  # currently selected block (button)
        self._force = True  # used to force a state change / message send

        # used for loop selection
        self._last_button_idx = -1
        self._last_button_time = time.time()
        self._loop_point1 = -1
        self._loop_point2 = -1

        self._cache = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                       -1, -1]  # Length=16

        self._buttons = buttons
        for button in self._buttons:  # iterate 16 buttons of 4x4 lower right matrix section
            assert isinstance(button, ButtonElement)
            button.remove_value_listener(self._loop_button_value)
            button.add_value_listener(self._loop_button_value,
                                      identify_sender=True)

    def disconnect(self):
        self._top_buttons = None

    @property
    def _number_of_lines_per_note(self):
        if self._mode == STEPSEQ_MODE_MULTINOTE:
            return self._step_sequencer._number_of_lines_per_note
        else:
            return 1

    def set_clip(self, clip):
        self._clip = clip

    @property
    def _mode(self):
        return self._step_sequencer._mode

    def set_note_cache(self, note_cache):
        self._note_cache = note_cache

    def set_playhead(self, playhead, updateBlock=False):
        self._playhead = playhead
        if updateBlock and self._playhead is not None:
            self._block = int(self._playhead / self._blocksize / self._quantization)
            self._step_sequencer.set_page(self._block)
        self.update()

    @property
    def _is_mute_shifted(self):
        return self._step_sequencer._is_mute_shifted

    @property
    def _is_velocity_shifted(self):
        return self._step_sequencer._note_editor._is_velocity_shifted

    @property
    def _quantization(self):
        return self._step_sequencer._quantization

    @property
    def block(self):
        return self._block

    def set_blocksize(self, blocksize):
        self._blocksize = blocksize

    def set_enabled(self, enabled):
        self._force = True
        ControlSurfaceComponent.set_enabled(self, enabled)

    # Read Live's Clip loop values to LoopSelector Values OK
    def _get_clip_loop(self):
        if self._clip != None:
            self._loop_start = self._clip.loop_start
            self._loop_end = self._clip.loop_end
        else:
            self._loop_start = 0
            self._loop_end = 0

    # Write LoopSelector Values to Live's Clip loop values (loop and marker) OK
    def set_clip_loop(self, start, end):
        if self._clip != None:
            self._loop_end = end
            self._loop_start = start
            if self._loop_start >= self._clip.loop_end:
                self._clip.loop_end = self._loop_end
                self._clip.loop_start = self._loop_start
                self._clip.end_marker = self._loop_end
                self._clip.start_marker = self._loop_start
            else:
                self._clip.loop_start = self._loop_start
                self._clip.loop_end = self._loop_end
                self._clip.start_marker = self._loop_start
                self._clip.end_marker = self._loop_end
            self.update()

    # LoopSelector listener OK
    def _loop_button_value(self, value, sender):
        # Allows to make selection by hold and pressing marker buttons
        # Selects simple page by double click on region button
        # Allows to mute and delete notes in a range
        # Allows to duplicate a range forwards (to empty regions)
        if self.is_enabled():
            idx = self._buttons.index(sender)
            if value > 0:  # This allow to setup loop range by pressing two buttons at a time [Start,End]
                if self._loop_point1 == -1:
                    self._loop_point1 = idx
                elif self._loop_point2 == -1:
                    self._loop_point2 = idx

            # Button released
            elif self._loop_point1 != -1:
                setloop = self._loop_point2 != -1  # two buttons pressed
                if self._loop_point2 == -1:
                    self._loop_point2 = idx  # _loop_point1 = _loop_point2
                    if self._last_button_idx == idx and (
                        time.time() - self._last_button_time) < 0.25:  # Double clic set loop subsection (depending on quantization)
                        setloop = True
                        self._last_button_time = time.time()
                        self._last_button_idx = -1

                if self._loop_point1 != -1 and self._loop_point2 != -1:

                    start = min(self._loop_point1, self._loop_point2)
                    end = max(self._loop_point1, self._loop_point2) + 1

                    self._block = start
                    if setloop:
                        if self._is_mute_shifted:
                            if self._is_velocity_shifted:
                                self._mute_notes_in_range(
                                    start * self._blocksize * self._quantization,
                                    end * self._blocksize * self._quantization)
                            else:
                                self._delete_notes_in_range(
                                    start * self._blocksize * self._quantization,
                                    end * self._blocksize * self._quantization)
                        else:
                            if self._is_velocity_shifted:  # FIX, see if can copy backwards
                                self._extend_clip_content(
                                    start * self._blocksize * self._quantization,
                                    self._loop_end,
                                    end * self._blocksize * self._quantization)
                            self.set_clip_loop(
                                start * self._blocksize * self._quantization,
                                end * self._blocksize * self._quantization)

                    self._step_sequencer.set_page(
                        self._block)  # set sequencer focus
                    self._loop_point1 = -1
                    self._loop_point2 = -1
                    self.update()
                self._last_button_time = time.time()
                self._last_button_idx = idx

    # Index check for page boundaries scroll OK
    def can_scroll(self, blocks):
        if self._clip != None:
            if (blocks + self._block) < 0:
                return False
            if (
                blocks + self._block) * 8 * self._quantization * self._number_of_lines_per_note < self._clip.loop_start:
                return False
            if (
                blocks + self._block + 1) * 8 * self._quantization * self._number_of_lines_per_note > self._clip.loop_end:
                return False
            return True
        return False

    # Does the actual scroll OK
    def scroll(self, blocks):
        if self._clip != None and self.can_scroll(blocks):
            self._block = blocks + self._block
            self._step_sequencer.set_page(self._block)

    # Iterates refreshing all loop selector buttons (called from playing position listener) OK
    def update(self):
        if self.is_enabled():
            self._get_clip_loop()  # gets the loop start/end values from the clip -> self._loop_start & self._loop_end
            i = 0
            for button in self._buttons:  # iterate 16 buttons of 4x4 lower right matrix section
                if self._clip == None:  # Disable/turn off all buttons
                    button.set_on_off_values("DefaultButton.Disabled",
                                             "DefaultButton.Disabled")
                    if self._cache[i] != button._off_value:
                        button.turn_off()
                        self._cache[i] = button._off_value
                else:
                    # is the button in loop range
                    in_loop = (
                                  i * self._blocksize * self._quantization < self._loop_end) and (
                                  i * self._blocksize * self._quantization >= self._loop_start)
                    # is the playing position is inside the block represented by the button
                    playing = self._playhead != None and self._playhead >= i * self._blocksize * self._quantization and self._playhead < (
                        i + 1) * self._blocksize * self._quantization
                    # is this block selected (green)
                    selected = i == self.block
                    if in_loop:
                        if playing:
                            if selected:
                                self._cache[
                                    i] = "StepSequencer.LoopSelector.SelectedPlaying"
                            else:
                                self._cache[
                                    i] = "StepSequencer.LoopSelector.Playing"
                        else:
                            if selected:
                                self._cache[
                                    i] = "StepSequencer.LoopSelector.Selected"
                            else:
                                self._cache[
                                    i] = "StepSequencer.LoopSelector.InLoop"
                    else:
                        if playing:
                            if selected:
                                self._cache[
                                    i] = "StepSequencer.LoopSelector.SelectedPlaying"
                            else:
                                self._cache[
                                    i] = "StepSequencer.LoopSelector.Playing"
                        else:
                            if selected:
                                self._cache[
                                    i] = "StepSequencer.LoopSelector.Selected"
                            else:
                                self._cache[i] = "DefaultButton.Disabled"

                    if self._cache[
                        i] != button._on_value or self._force:  # Enable/turn on all buttons
                        button.set_on_off_values(self._cache[i], self._cache[i])
                        button.turn_on()
                i = i + 1
            self._force = False

    # Make a copy of the current loop to the next N empty blocks OK
    def _extend_clip_content(self, loop_start, old_loop_end, new_loop_end):
        if (self._no_notes_in_range(old_loop_end, new_loop_end, True)):
            clip_looping_length = 0
            if (old_loop_end > 1):
                power = 1
                while (power * 2 < old_loop_end):
                    power *= 2
                clip_looping_length = (power)
            clone_length = new_loop_end - old_loop_end
            if (clip_looping_length > 0):
                clone_start_point = (old_loop_end % clip_looping_length)
            else:
                clone_start_point = 0
            self._copy_notes_in_range(clone_start_point,
                                      clone_start_point + clone_length,
                                      old_loop_end)

    # Does the note by note copy OK
    def _copy_notes_in_range(self, start, end, new_start):
        new_notes = list(self._note_cache)
        # for i in range()
        for note in new_notes:
            if note[1] >= start and note[1] < end:
                new_notes.append(
                    [note[0], note[1] + new_start - start, note[2], note[3],
                     note[4]])
        self._clip.select_all_notes()
        self._clip.replace_selected_notes(tuple(new_notes))

    # Checks if a range is empty OK
    def _no_notes_in_range(self, start, end, or_after):
        for note in list(self._note_cache):
            if note[1] >= start and (note[1] < end or or_after):
                return (False)
        return (True)

    # Deletes a block of notes OK
    def _delete_notes_in_range(self, start, end):
        new_notes = list()
        for note in list(self._note_cache):
            if note[1] < start or note[1] >= end:
                new_notes.append(note)
        self._clip.select_all_notes()
        self._clip.replace_selected_notes(tuple(new_notes))

    # Mutes a block of notes OK
    def _mute_notes_in_range(self, start, end):
        new_notes = list()
        for note in list(
            self._note_cache):  # Note -> tuple containing pitch, time, duration, velocity, and mute
            if note[1] < start or note[1] >= end:  # Note time
                new_notes.append(note)
            else:
                new_notes.append([note[0], note[1], note[2], note[3],
                                  not note[4]])  # Negate mute state
        self._clip.select_all_notes()
        self._clip.replace_selected_notes(tuple(new_notes))
