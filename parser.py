"""
Android event real-time parser. Based on getevent data for Nexus 5's.

This class will attempt to read event data via Android's getevent command.
We then parse and store the event data.
"""

import sys
from event import AndroidEvent, TYPE_START_OR_END
from subprocess import PIPE, Popen, call
from threading import Thread
from Queue import Queue, Empty


class Parser(object):
    def __init__(self):
        self.raw_data_queue = Queue()
        self.events = Queue()

    def _process_line(self, line, current_event):
        # Ignore empty lines
        if not line:
            return current_event

        # Ignore device add events.
        if line.startswith('add device') or line.startswith('name'):
            return current_event

        # Parse the events now in the correct form.
        # Specifically, the output should be in the form:
        # [%time] %device: %event_type %event_property %value

        line_parts = line.split()
        time = float(line_parts[1][:-1])  # '54000.123132]'
        device = line_parts[2][:-1]  # '/dev/input/event1:'
        event_type = line_parts[3]
        event_property = line_parts[4]
        value = int(line_parts[5], 16)

        # Ignore separator events
        if event_type == 'EV_SYN':
            return current_event

        if current_event is None and event_property == TYPE_START_OR_END:
            current_event = AndroidEvent(time)
        elif current_event and event_property == TYPE_START_OR_END:
            current_event.process()
            self.events.put(current_event)
            current_event = None
        elif current_event and AndroidEvent.recognized(event_property):
            current_event.changed(event_property, time, value)
        else:
            # Unrecognized event type.
            pass

        return current_event

    def collect_events(self):
        on_posix = 'posix' in sys.builtin_module_names

        # Helper function for quickly reading raw output.
        def enqueue_output(out, queue):
            for l in iter(out.readline, ''):
                queue.put(l)

        p = Popen(['adb', 'shell', 'getevent', '-lt'], stdout=PIPE, bufsize=1, close_fds=on_posix)
        t = Thread(target=enqueue_output, args=(p.stdout, self.raw_data_queue))
        t.daemon = True
        t.start()

        try:
            # Process the events in this thread.
            print 'Processing android events from device:'
            current_event = None
            while True:
                try:
                    line = self.raw_data_queue.get_nowait().strip()
                    current_event = self._process_line(line, current_event)
                except Empty:
                    # Ignore empty events, we're simply reading too quickly.
                    pass
        except KeyboardInterrupt:
            print 'Finished processing events from device.'
            p.terminate()
