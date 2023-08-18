import threading
import traceback

from .ButtonSliderElement import ButtonSliderElement
from .Settings import Settings
import time, sys
from .Log import log

SLIDER_MODE_OFF = 0
SLIDER_MODE_TOGGLE = 1
SLIDER_MODE_SLIDER = 2
SLIDER_MODE_PRECISION_SLIDER = 3
SLIDER_MODE_SMALL_ENUM = 4
SLIDER_MODE_BIG_ENUM = 5
ROUNDTRIP_TARGET = 0.01


class DeviceControllerStripServer(ButtonSliderElement, threading.Thread):
    def __init__(self, buttons, control_surface, column, request_queue,
        response_queue, parent=None):
        ButtonSliderElement.__init__(self, buttons)
        self._control_surface = control_surface
        self._column = column
        self._request_queue = request_queue
        self._response_queue = response_queue
        self._parent = parent
        self._num_buttons = len(buttons)
        self._value_map = tuple(
            [float(index) / (self._num_buttons - 1) for index in
             range(self._num_buttons)])
        self._precision_mode = False
        self._stepless_mode = False
        self._enabled = True
        self._current_value = None
        self._last_value = None
        self._last_sent_value = -1
        self._target_value = None
        self._current_velocity = 10
        self.roundtrip_start = 0
        self.roundtrip_end = 0
        self.roundtrip_time = 0

    def set_enabled(self, enabled):
        self._enabled = enabled

    def set_precision_mode(self, precision_mode):
        self._precision_mode = precision_mode
        self.update()

    def set_stepless_mode(self, stepless_mode):
        self._stepless_mode = stepless_mode
        self.update()

    def shutdown(self):
        self._control_surface = None
        self._parent = None
        self._column = None
        self._buttons = None

    @property
    def _value(self):
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to.value
        else:
            return 0

    @property
    def _max(self):
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to.max
        else:
            return 0

    @property
    def _min(self):
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to.min
        else:
            return 0

    @property
    def _range(self):
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to.max - self._parameter_to_map_to.min
        else:
            return 0

    @property
    def _default_value(self):
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to._default_value
        else:
            return 0

    @property
    def _is_quantized(self):
        if self._parameter_to_map_to is not None:
            return self._parameter_to_map_to.is_quantized
        else:
            return False

    @property
    def _mode(self):
        if self._parameter_to_map_to is not None:
            if self._is_quantized:
                if self._range == 1:
                    return SLIDER_MODE_TOGGLE
                elif self._range <= self._num_buttons:
                    return SLIDER_MODE_SMALL_ENUM
                else:
                    return SLIDER_MODE_BIG_ENUM
            else:
                if self._precision_mode:
                    return SLIDER_MODE_PRECISION_SLIDER
                else:
                    return SLIDER_MODE_SLIDER
        else:
            return SLIDER_MODE_OFF

    def update(self):
        if self._enabled:
            if self._mode == SLIDER_MODE_TOGGLE:
                self._update_toggle()
            elif self._mode == SLIDER_MODE_SMALL_ENUM:
                self._update_small_enum()
            elif self._mode == SLIDER_MODE_BIG_ENUM:
                self._update_big_enum()
            elif (self._mode == SLIDER_MODE_SLIDER):
                self._update_slider()
            elif (self._mode == SLIDER_MODE_PRECISION_SLIDER):
                self._update_precision_slider()
            else:
                self._update_off()

    def reset(self):
        self._update_off()

    def reset_if_no_parameter(self):
        if self._parameter_to_map_to is None:
            self.reset()

    def _update_off(self):
        v = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        self._update_buttons(tuple(v))

    def _update_toggle(self):
        v = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        if self._value == self._max:
            v[0] = "Device.Toggle.On"
        else:
            v[0] = "Device.Toggle.Off"
        self._update_buttons(tuple(v))

    def _update_small_enum(self):
        v = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        for index in range(int(self._range + 1)):
            if self._value == index + self._min:
                v[index] = "Device.Enum.On"
            else:
                v[index] = "Device.Enum.Off"
        self._update_buttons(tuple(v))

    def _update_big_enum(self):
        v = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        if self._value > self._min:
            v[3] = "Device.BigEnum.On"
        else:
            v[3] = "Device.BigEnum.Off"
        if self._value < self._max:
            v[4] = "Device.BigEnum.On"
        else:
            v[4] = "Device.BigEnum.Off"
        self._update_buttons(tuple(v))

    def _update_slider(self):
        v = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        for index in range(len(self._buttons)):
            if self._value >= self._value_map[index] * self._range + self._min:
                v[index] = f"Device.Slider{self._column}.On"
            else:
                v[index] = f"Device.Slider{self._column}.Off"
        self._update_buttons(tuple(v))

    def _update_precision_slider(self):
        v = ["DefaultButton.Disabled" for index in range(len(self._buttons))]
        if self._value > self._min:
            v[3] = "Device.PrecisionSlider.On"
        else:
            v[3] = "Device.PrecisionSlider.Off"

        if self._value < self._max:
            v[4] = "Device.PrecisionSlider.On"
        else:
            v[4] = "Device.PrecisionSlider.Off"
        self._update_buttons(tuple(v))

    def _update_buttons(self, buttons):
        assert isinstance(buttons, tuple)
        assert (len(buttons) == len(self._buttons))
        for index in range(len(self._buttons)):
            self._buttons[index].set_on_off_values(buttons[index],
                                                   buttons[index])
            if buttons[index].endswith("On"):  # buttons[index]>0:
                self._buttons[index].turn_on()
            else:
                self._buttons[index].turn_off()

    def _button_value(self, value, sender):
        assert isinstance(value, int)
        assert (sender in self._buttons)
        log("button_value: value: " + str(value)) if not value == 0 else None
        self._last_sent_value = -1
        if (self._parameter_to_map_to is not None and self._enabled and (
            (value != 0) or (not sender.is_momentary()))):
            if (value != self._last_sent_value):
                target_value = self._parameter_to_map_to.value

                index_of_sender = list(self._buttons).index(sender)
                if (self._mode == SLIDER_MODE_TOGGLE) and index_of_sender == 0:
                    if self._value == self._max:
                        target_value = self._min
                    else:
                        target_value = self._max

                elif self._mode == SLIDER_MODE_SMALL_ENUM:
                    target_value = index_of_sender + self._min

                elif self._mode == SLIDER_MODE_BIG_ENUM:
                    if index_of_sender >= 4:
                        inc = 2 ** (index_of_sender - 3 - 1)
                        if self._value + inc <= self._max:
                            target_value += inc
                        else:
                            target_value = self._max
                    else:
                        inc = 2 ** (4 - index_of_sender - 1)
                        if self._value - inc >= self._min:
                            target_value -= inc
                        else:
                            target_value = self._min


                elif (self._mode == SLIDER_MODE_SLIDER):
                    target_value = self._value_map[
                                       index_of_sender] * self._range + self._min

                elif (self._mode == SLIDER_MODE_PRECISION_SLIDER):
                    inc = float(self._range) / 128
                    if self._range > 7 and inc < 1:
                        inc = 1
                    if index_of_sender >= 4:
                        inc = inc * 2 ** (index_of_sender - 3 - 1)
                        if self._value + inc <= self._max:
                            target_value += inc
                        else:
                            target_value = self._max
                    else:
                        inc = inc * 2 ** (4 - index_of_sender - 1)
                        if self._value - inc >= self._min:
                            target_value -= inc
                        else:
                            target_value = self._min
                self.update_value(target_value, value)

    def update_value(self, new_target_value=None, new_velocity=None):
        target_value = self._target_value if new_target_value is None else new_target_value
        velocity = self._current_velocity if new_velocity is None else new_velocity
        current_value = self._current_value
        if self._precision_mode or not self._stepless_mode:
            while True:
                try:
                    self._parameter_to_map_to.value = target_value
                    break
                except RuntimeError:
                    continue
            self._current_value = self._parameter_to_map_to.value
            self._target_value = self._current_value
            self._last_value = self._current_value
        else:
            if self._target_value != target_value or self._current_velocity != velocity:
                self._target_value = target_value
                self._current_velocity = velocity
            if target_value != current_value:
                max_diff = abs(target_value - current_value)
                velocity_factor = self.velocity_factor(velocity, max_diff)
                new_value = current_value + velocity_factor if current_value < target_value else current_value - velocity_factor
                new_value = max(min(new_value, self._parameter_to_map_to.max),
                                self._parameter_to_map_to.min)
                while True:
                    try:
                        self._parameter_to_map_to.value = new_value
                        break
                    except RuntimeError:
                        continue
                self._current_value = self._parameter_to_map_to.value
                self._last_value = self._current_value
        self.update()

    def run(self):
        try:
            while True:

                if self._request_queue.empty():
                    time.sleep(ROUNDTRIP_TARGET)
                    self.roundtrip_end = time.time()
                    self.roundtrip_time = self.roundtrip_end - self.roundtrip_start
                    self.roundtrip_start = self.roundtrip_end
                    # TODO: CHANGE VALUE ALWAYS BUT UPDATE GUI OLY WHEN ENABLED
                    if (self._parameter_to_map_to is not None):
                        # if (self._parameter_to_map_to != None and self._enabled):
                        self._current_value = self._parameter_to_map_to.value
                        if self._target_value is None or self._last_value is None:
                            self._target_value = self._current_value
                            self._last_value = self._current_value

                        if self._current_value != self._target_value:
                            if round(self._last_value, 5) == round(
                                self._current_value, 5):
                                self.update_value()
                            else:
                                self._last_value = self._current_value
                                self._target_value = self._current_value
                                self.update()
                    continue
                else:
                    funct_name, args, kwargs = self._request_queue.get()
                    if funct_name == "shutdown":
                        # log(f"Shutting down DCSServer {self._column}")
                        return
                    else:
                        self._request_handler(funct_name, *args, **kwargs)
        except Exception as e:
            log(f"Exception in DCSServer {self._column}:\n {e}")
            log(traceback.print_exc())
            raise e

    def _request_handler(self, funct_name, *args, **kwargs):
        # log(f"DCSServer {self._column} requesting {funct_name} with {args} and {kwargs}")

        if funct_name == "_parameter_to_map_to":
            self._response_queue.put(self._parameter_to_map_to)
        elif False:
            pass
        else:
            result = self._call_dispatcher(funct_name, *args, **kwargs)
            if result is not None:
                self._response_queue.put(result)

    def _call_dispatcher(self, method_name, *args, **kwargs):
        # log(f"DCSServer {self._column} calling {method_name} with {args} and {kwargs}")
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                return method(*args, **kwargs)
            else:
                log(f"DCSServer {self._column} method {method_name} is not callable")
        else:
            log(f"DCSServer {self._column} has no method {method_name}")

    def _on_parameter_changed(self):
        assert (self._parameter_to_map_to is not None)
        if self._parent is not None:
            self._parent._update_OSD()
        self.update()

    def velocity_factor(self, velocity, max_diff):
        if velocity > Settings.VELOCITY_THRESHOLD_MAX:
            return max_diff
        velocity_factor = max(velocity, 10) / (Settings.VELOCITY_FACTOR * 127.0)
        change_per_roundtrip = velocity_factor / ROUNDTRIP_TARGET
        velocity_factor = change_per_roundtrip * self.roundtrip_time
        return min(velocity_factor, max_diff)
