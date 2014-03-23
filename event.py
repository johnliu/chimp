"""
A class to represent an Android event.
"""

from functools import partial
from interfacer import Interface
from monkey_interfacer import MonkeyInterface


TYPE_START_OR_END = 'ABS_MT_TRACKING_ID'
TYPE_POSITION_X = 'ABS_MT_POSITION_X'
TYPE_POSITION_Y = 'ABS_MT_POSITION_Y'
_EVENT_TYPES = [TYPE_POSITION_X, TYPE_POSITION_Y]

ACTION_TOUCH = 'touch'
ACTION_DRAG = 'drag'


class AndroidEvent(object):
    class Change:
        def __init__(self, event_type, duration, time, value):
            self.event_type = event_type
            self.duration = duration
            self.time = time
            self.value = value
            self.action = None

    @classmethod
    def recognized(cls, event_type):
        return event_type in _EVENT_TYPES

    def __init__(self, start_time):
        self.processed = False
        self.start_time = start_time
        self.changes = {}
        self.action = None
        self.action_type = ''

    def changed(self, event_type, time, value):
        delta_time = time - self.start_time
        self.changes.setdefault(event_type, [])
        self.changes[event_type].append(AndroidEvent.Change(event_type, delta_time, time, value))

    def process(self):
        # TODO(johnliu): interpolate a curve, for now just use start and end points.
        start_x, start_y = self.changes[TYPE_POSITION_X][0], self.changes[TYPE_POSITION_Y][0]
        end_x, end_y = self.changes[TYPE_POSITION_X][-1], self.changes[TYPE_POSITION_Y][-1]

        if abs(start_x.value - end_x.value) <= 25 and abs(start_y.value - end_y.value) <= 25:
            self.action = partial(Interface.touch, start_x.value, start_y.value)
            # self.action = partial(MonkeyInterface.touch, start_x.value, start_y.value, 'MonkeyDevice.DOWN_AND_UP')
            self.action_type = ACTION_TOUCH
        else:
            start = (start_x.value, start_y.value)
            end = (end_x.value, end_y.value)
            duration = max(end_x.duration, end_y.duration)
            steps = 4
            # self.action = partial(MonkeyInterface.drag, start, end, duration, steps)
            self.action = partial(Interface.drag, start, end, duration)
            self.action_type = ACTION_DRAG

        self.processed = True
        print 'Got event: %s' % self

    def delay(self, two):
        if two is None:
            return 0
        start_time = max([self.changes[change_type][-1].time for change_type in self.changes])
        end_time = min([two.changes[change_type][0].time for change_type in two.changes])
        return abs(end_time - start_time)

    def call(self):
        if self.processed:
            self.action()
        else:
            print 'Event not processed.'

    def __repr__(self):
        start_x, start_y = self.changes[TYPE_POSITION_X][0], self.changes[TYPE_POSITION_Y][0]
        end_x, end_y = self.changes[TYPE_POSITION_X][-1], self.changes[TYPE_POSITION_Y][-1]

        # Determine the arguments
        start = (start_x.value, start_y.value)
        end = (end_x.value, end_y.value)
        duration = max(end_x.duration, end_y.duration)

        message = 'unprocessed'
        if self.processed:
            if self.action_type == ACTION_DRAG:
                message = '%s -> %s in %f' % (start, end, duration)
            elif self.action_type == ACTION_TOUCH:
                message = '%s' % (start,)

        return '<AndroidEvent(%s): %s>.' % (self.action_type, message)