"""
Interface to communicate with monkeyrunner.
"""

import sys
import time
from subprocess import Popen, PIPE
from threading import Thread
from Queue import Queue, Empty
from interfacer import Interface, Communicator


def try_call(func):
    def wrapped(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except TypeError:
            print 'Process is not set'
    return wrapped


class MonkeyInterface(Interface):
    write = None

    @classmethod
    @try_call
    def drag(cls, start, end, duration, steps=4):
        cls.write('drag(%s, %s, %f, %d)' % (start, end, duration, steps))

    @classmethod
    @try_call
    def touch(cls, x, y, type='MonkeyDevice.DOWN_AND_UP'):
        cls.write('touch(%d, %d, %s)' % (x, y, type))


class MonkeyCommunicator(Communicator):
    def __init__(self):
        super(MonkeyCommunicator, self).__init__()
        self.output = Queue()

    def init(self, events):
        return super(MonkeyCommunicator, self).init(events)

    def communicate(self):
        on_posix = 'posix' in sys.builtin_module_names

        def enqueue_output(out, queue):
            for l in iter(lambda: out.read(1), ''):
                # sys.stdout.write(l)
                queue.put(l)

        p = Popen(['monkeyrunner'], stdin=PIPE, stdout=PIPE, bufsize=1, close_fds=on_posix)
        t = Thread(target=enqueue_output, args=(p.stdout, self.output))
        t.daemon = True
        t.start()

        def get():
            line = self.output.get()
            while not line.endswith('\n'):
                line += self.output.get()
            return line

        def wait():
            while self.output.empty():
                pass

        def write(string):
            command = '%s\n' % string
            print command
            p.stdin.write(command)
            try:
                get()
                wait()
            except Empty:
                pass

        # Set up the interpreter.
        write('from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice')
        write('device = MonkeyRunner.waitForConnection()')

        # TODO(johnliu): set up activity/package access.
        # write("run_component = package + '/' + package + '.' + activity")
        # write('device.startActivity(component=run_component)')

        MonkeyInterface.write = staticmethod(lambda command: write('device.%s' % command))
        last_event = None
        while True:
            try:
                event = self.events.get_nowait()
                time.sleep(min(3, event.delay(last_event)))
                print event

                event.call()
                last_event = event
            except Empty:
                break
            except KeyboardInterrupt:
                break

        p.terminate()

