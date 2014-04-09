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
        self.args = None

    def init(self, type, *args):
        self.type = type
        self.args = args

        if type == ACTION_TOUCH:
            self.call = partial(interface.touch, *args)
        elif type == ACTION_DRAG:
            self.call = partial(interface.drag, *args)
        elif type == ACTION_BACK:
            self.call = partial(interface.back)
        else:
            print 'Unknown action type.'
        return self

    def is_drag(self):
        return self.type == ACTION_DRAG

    def is_touch(self):
        return self.type == ACTION_TOUCH

    def is_back(self):
        return self.type == ACTION_BACK

    def __repr__(self):
        if self.is_drag():
            return "<Action>: drag(%s)" % str(self.args)
        if self.is_touch():
            return "<Action>: touch(%s)" % str(self.args)
        return "<Action>: back()"
