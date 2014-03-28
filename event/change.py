"""
Classes to represent Android Event Changes.
"""

from utils import Point
from constants import *


class AndroidEventChange(object):
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

    def start(self):
        return Point(self.x(0).value, self.y(0).value)

    def end(self):
        return Point(self.x(-1).value, self.y(-1).value)

    def duration(self):
        return max(self.x(-1).duration, self.y(-1).duration)

    def max_time(self):
        return max([self.changes[change_type][-1].time for change_type in self.changes])

    def min_time(self):
        return min([self.changes[change_type][0].time for change_type in self.changes])
