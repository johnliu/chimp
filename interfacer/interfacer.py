"""
Interface to communicate with the device using uiautomator.
"""

import time
from uiautomator import device
from state import State


class Interface(object):
    @classmethod
    def drag(cls, start, end, duration):
        step_size = 25.0 / 1000
        device.drag(start[0], start[1], end[0], end[1], int(duration / step_size))

    @classmethod
    def touch(cls, x, y):
        device.click(x, y)

    @classmethod
    def back(cls):
        device.press.back()


class Communicator(object):
    def __init__(self):
        self.events = None

    def init(self, events):
        self.events = events
        return self

    def communicate(self):
        if self.events is None:
            print 'Uninitalized events.'
            return

        last_event = None
        while not self.events.empty():
            event = self.events.get()
            # time.sleep(min(3, event.delay(last_event)))
            print event

            event.call()
            last_event = event

    def automate(self, decider):
        last_action = None
        try:
            print 'Begin automation.'
            while True:
                state = State()
                state.xml = device.dump()
                action = decider.predict(state)
                print 'Predicted action: %s' % action
                action.call()
        except KeyboardInterrupt:
            print 'Finished automation.'
