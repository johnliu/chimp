"""
A class to represent an event action.
"""

from functools import partial
from interfacer import Interface
from constants import *


interface = Interface


class Action(object):
    def __init__(self):
        self.type = None
        self.call = None

    def init(self, type, *args):
        self.type = type
        if type == ACTION_TOUCH:
            self.call = partial(interface.touch, *args)
        elif type == ACTION_DRAG:
            self.call = partial(interface.drag, *args)
        else:
            print 'Unknown action type.'
        return self

    def is_drag(self):
        return self.type == ACTION_DRAG

    def is_touch(self):
        return self.type == ACTION_TOUCH
