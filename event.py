"""
A class to represent an Android event.
"""

from collections import namedtuple
from functools import partial
from enum import IntEnum
from interfacer import Interface
from monkey_interfacer import MonkeyInterface


# Event Properties
TYPE_START_OR_END = 'ABS_MT_TRACKING_ID'
TYPE_POSITION_X = 'ABS_MT_POSITION_X'
TYPE_POSITION_Y = 'ABS_MT_POSITION_Y'
EVENT_TYPES = [TYPE_POSITION_X, TYPE_POSITION_Y]

# Event Types
ACTION_TOUCH = 'touch'
ACTION_DRAG = 'drag'


Point = namedtuple('Point', ['x', 'y'])
State = namedtuple('State', ['start', 'end'])


class Status(IntEnum):
    uninitialized = 1
    initialized = 2
    preprocessed = 3
    processed = 4


class Action(object):
    def __init__(self):
        self.type = None
        self.call = None

    def init(self, type, *args):
        self.type = type
        if type == ACTION_TOUCH:
            self.call = partial(AndroidEvent.interfacer.touch, *args)
        elif type == ACTION_DRAG:
            self.call = partial(AndroidEvent.interfacer.drag, *args)
        else:
            print 'Unknown action type.'
        return self

    def is_drag(self):
        return self.type == ACTION_DRAG

    def is_touch(self):
        return self.type == ACTION_TOUCH


class Change(object):
    def __init__(self, type, duration, time, value):
        self.type = type
        self.duration = duration
        self.time = time
        self.value = value


class ChangeStore(object):
    def __init__(self):
        self.changes = {}

    def append(self, change):
        self.changes.setdefault(change.type, [])
        self.changes[change.type].append(change)

    def x(self, index):
        return self.changes[TYPE_POSITION_X][index]

    def y(self, index):
        return self.changes[TYPE_POSITION_Y][index]

    def duration(self):
        return max(self.x(-1).duration, self.y(-1).duration)

    def max_time(self):
        return max([self.changes[change_type][-1].time for change_type in self.changes])

    def min_time(self):
        return min([self.changes[change_type][0].time for change_type in self.changes])


class AndroidEvent(object):
    # Set the interfacer
    interfacer = Interface

    def __init__(self):
        self.status = Status.uninitialized
        self.start_time = None
        self.state = State(None, None)
        self.changes = ChangeStore()
        self.action = Action()
        self.element_chain = []

    def init(self, start_time, start_state):
        self.status = Status.initialized
        self.start_time = start_time
        self.state = State(start_state, None)
        return self

    def is_start(self, event_property):
        return self.status is Status.uninitialized and event_property == TYPE_START_OR_END

    def is_end(self, event_property):
        return self.status is Status.initialized and event_property == TYPE_START_OR_END

    @classmethod
    def recognized(cls, type):
        return type in EVENT_TYPES

    def changed(self, type, time, value):
        delta_time = time - self.start_time
        self.changes.append(Change(type, delta_time, time, value))

    def preprocess(self, end_event):
        self.state = State(self.state.start, end_event)

        # TODO(johnliu): interpolate a curve, for now just use start and end points.
        start = Point(self.changes.x(0).value, self.changes.y(0).value)
        end = Point(self.changes.x(-1).value, self.changes.y(-1).value)

        if abs(start.x - end.x) <= 25 and abs(start.y - end.y) <= 25:
            self.action.init(ACTION_TOUCH, start.x, start.y)
        else:
            self.action.init(ACTION_DRAG, start, end, self.changes.duration())

        self.status = Status.preprocessed
        print 'Got event: %s' % self

    def process(self):
        self.status = Status.processed

    def delay(self, other):
        if other is None:
            return 0
        start_time = self.changes.max_time()
        end_time = other.changes.min_time()
        return abs(end_time - start_time)

    def call(self):
        if self.status >= Status.preprocessed:
            self.action.call()
        else:
            print 'Event not processed.'

    def __repr__(self):
        text_start = '<AndroidEvent(%s)>'
        text_end = ':\n %s'
        t, m = (None, None)

        if self.status is Status.uninitialized:
            t = 'null'
        if self.status is Status.initialized:
            t = 'unprocessed'

        start = Point(self.changes.x(0).value, self.changes.y(0).value)
        end = Point(self.changes.x(-1).value, self.changes.y(-1).value)
        duration = self.changes.duration()

        if self.status >= Status.preprocessed:
            t = self.action.type
            if self.action.is_drag():
                m = '\t%s ->\n\t%s \n\tin %f' % (start, end, duration)
            elif self.action.is_touch():
                m = '\t%s' % (start,)
        if self.status is Status.processed:
            if self.action.is_drag():
                m += ', \n\tfrom: %s ->\n\t%s' % (self.element_chain[0], self.element_chain[-1])
            elif self.action.is_touch():
                m += ', \n\tin: %s' % self.element_chain[0]

        text = text_start
        if m: text += text_end
        return text % (t, m)