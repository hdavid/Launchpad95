import time
from .Test import log


class SliderQueueProcessor(object):
    """
    This class is responsible for processing the queue of slider events
    and updating the slider values accordingly.
    """

    def __init__(self, slider, queue, parameter):
        self.slider = slider
        self.queue = queue
        self.parameter = parameter
        log(f"SliderQueueProcessor {self.parameter.name} created")
        self.process_loop()

    def process_loop(self):
        new_target_value = None
        current_value = None
        current_target_value = None
        current_velocity = None
        new_velocity = None
        while True:
            time.sleep(0.01)
            current_value = self.parameter.value
            if not self.queue.empty():
                while not self.queue.empty():
                    new_target_value, new_velocity = self.queue.get()
                    if new_velocity == 'shutdown':
                        log(f"SliderQueueProcessor {new_target_value} shutdown")
                        return
                if current_target_value != new_target_value or current_velocity != new_velocity:
                    current_target_value = new_target_value
                    current_velocity = new_velocity
                    #log(f"SliderQueueProcessor {current_target_value} {current_velocity}")

            if current_velocity == 0:
                log(f"SliderQueueProcessor Got velocity 0")

            velocity_factor = current_velocity / 127.0
            new_value = current_value + (current_target_value - current_value) * velocity_factor #TODO: check if this is correct
            log(f"SliderQueueProcessor setting {self.parameter.name} to {new_value} from {current_value} with velocity {current_velocity} and factor {velocity_factor} with target {current_target_value}")
            self.parameter.value = new_value
            #self.slider.notify_value(current_velocity)
def process_loop(queue, parameter):
    new_target_value = None
    current_value = None
    current_target_value = None
    current_velocity = None
    new_velocity = None
    log(f"SliderQueueProcessor {parameter.name} created")
    while True:
        time.sleep(0.01)
        current_value = parameter.value
        if not queue.empty():
            while not queue.empty():
                new_target_value, new_velocity = queue.get()
                if new_velocity == 'shutdown':
                    log(f"SliderQueueProcessor {new_target_value} shutdown")
                    return
            if current_target_value != new_target_value or current_velocity != new_velocity:
                current_target_value = new_target_value
                current_velocity = new_velocity
                #log(f"SliderQueueProcessor {current_target_value} {current_velocity}")

        if current_velocity == 0:
            log(f"SliderQueueProcessor Got velocity 0")

        velocity_factor = current_velocity / 127.0
        new_value = current_value + (current_target_value - current_value) * velocity_factor #TODO: check if this is correct
        log(f"SliderQueueProcessor setting {parameter.name} to {new_value} from {current_value} with velocity {current_velocity} and factor {velocity_factor} with target {current_target_value}")
        parameter.value = new_value
        #self.slider.notify_value(current_velocity)
