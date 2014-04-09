"""
A class to represent an Android event.
"""

from enum import IntEnum
from state import StateChange
from action import Action
from change import ChangeStore, AndroidEventChange
from uiautomator import device
from constants import *


class Status(IntEnum):
    discarded = 0
    uninitialized = 1
    initialized = 2
    preprocessed = 3
    processed = 4


class AndroidEvent(object):
    def __init__(self):
        self.status = Status.uninitialized
        self.start_time = None
        self.state = StateChange()
        self.changes = ChangeStore()
        self.action = Action()
        self.device_info = device.info

    def init(self, start_time, start_state):
        self.status = Status.initialized
        self.start_time = start_time
        self.state.start.xml = start_state
        return self

    def is_start(self, event_property):
        return self.status is Status.uninitialized and event_property == TYPE_START_OR_END

    def is_end(self, event_property):
        return self.status is Status.initialized and event_property == TYPE_START_OR_END

    @classmethod
    def recognized(cls, type):
        return type in EVENT_TYPES

    def changed(self, type, time, value):
        if self.status is Status.initialized:
            delta_time = time - self.start_time
            self.changes.append(AndroidEventChange(type, delta_time, time, value))
        else:
            print 'Ignored uninitialized event.'

    def preprocess(self, end_event):
        try:
            self.status = Status.preprocessed
            self.state.end.xml = end_event

            # TODO(johnliu): interpolate a curve, for now just use start and end points.
            start = self.changes.start()
            end = self.changes.end()

            if abs(start.x - end.x) <= 25 and abs(start.y - end.y) <= 25:
                if start.y >= self.device_info['displayHeight']:
                    self.action.init(ACTION_BACK)
                else:
                    self.action.init(ACTION_TOUCH, start.x, start.y)
            else:
                self.action.init(ACTION_DRAG, start, end, self.changes.duration())
        except Exception as e:
            self.status = Status.discarded
            print e

        print 'Got event: %s' % self

    def process(self):
        try:
            self.status = Status.processed

            if not self.action.is_back():
                self.state.start.process(self.changes.start())
                self.state.end.process(self.changes.end())
                if not len(self.state.start.chain) or not len(self.state.end.chain):
                    self.status = Status.discarded
        except Exception as e:
            self.status = Status.discarded
            print e

        print 'Processed: %s' % self

    def delay(self, other):
        if other is None:
            return 0
        start_time = self.changes.max_time()
        end_time = other.changes.min_time()
        return abs(end_time - start_time)

    def call(self):
        if self.status >= Status.processed:
            self.action.call()
        else:
            print 'Event not processed.'

    def __repr__(self):
        text_start = '<AndroidEvent(%s)>'
        text_end = ':\n %s'
        t, m = (None, None)

        if self.status is Status.uninitialized:
            t = 'null'
        if self.status is Status.discarded:
            t = 'discarded'
        if self.status is Status.initialized:
            t = 'unprocessed'

        if self.status >= Status.preprocessed:
            start = self.changes.start()
            end = self.changes.end()
            duration = self.changes.duration()

            t = self.action.type
            if self.action.is_drag():
                m = '\t%s ->\n\t%s \n\tin %f' % (start, end, duration)
            elif self.action.is_touch():
                m = '\t%s' % (start,)
        if self.status is Status.processed:
            if self.action.is_drag():
                m += ', \n\tfrom: %s ->\n\t%s' % (self.state.start.chain[-1], self.state.end.chain[-1])
            elif self.action.is_touch():
                m += ', \n\tin: %s' % self.state.start.chain[-1]

        text = text_start
        if m: text += text_end % m
        return text % t