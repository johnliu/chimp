"""
Interface to communicate with the device using uiautomator.
"""
import time

from uiautomator import device


class Interface(object):
    @classmethod
    def drag(cls, start, end, duration):
        step_size = 25.0 / 1000
        device.drag(start[0], start[1], end[0], end[1], int(duration / step_size))

    @classmethod
    def touch(cls, x, y):
        device.click(x, y)


class Communicator(object):
    def __init__(self, events):
        self.events = events

    def communicate(self):
        last_event = None
        while not self.events.empty():
            event = self.events.get()
            time.sleep(event.delay(last_event))
            print event

            event.call()
            last_event = event
