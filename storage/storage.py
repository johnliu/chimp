"""
A class managing storing python objects as pickled objects.
"""

import cPickle as pickle
import os
import time
import types
import copy_reg
from Queue import Queue
from event import Status


class GenericStorage(object):
    def __init__(self, path):
        self.path = path

        try:
            os.makedirs(path)
        except OSError:
            pass

    def read(self, offset=0, limit=0):
        files = os.listdir(self.path)
        files.sort()

        objects = []

        stop = limit if limit else len(files)
        for i in range(offset, stop):
            with open('%s%s' % (self.path, files[i]), 'rb') as f:
                print 'Reading: %s.' % f.name
                objects.append(pickle.load(f))

        return objects

    def write(self, obj, name):
        with open('%s%s' % (self.path, name), 'wb') as f:
            print 'Writing: %s.' % f.name
            pickle.dump(obj, f)


class EventStorage(GenericStorage):
    def __init__(self, package):

        # Ensure that instance methods can be pickled.
        def reduce_method(m):
            return getattr, (m.__self__, m.__func__.__name__)
        copy_reg.pickle(types.MethodType, reduce_method)

        super(EventStorage, self).__init__('data/%s/' % package)

    def write(self, obj, name=None):
        name = name if name else str(int(time.time() * 1000))
        if obj.status is not Status.discarded:
            super(EventStorage, self).write(obj, name)
        else:
            print 'Skipped discarded event.'

    def write_all(self, events):
        for event in events:
            self.write(event)

    def qread(self, offset=0, limit=0):
        events = self.read(offset, limit)
        queue = Queue()

        for event in events:
            queue.put(event)

        return queue

    def qwrite_all(self, queue):
        while not queue.empty():
            self.write(queue.get())
