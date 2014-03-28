"""
Android event real-time parser. Based on getevent data for Nexus 5's.

This class will attempt to read event data via Android's getevent command.
We then parse and store the event data.
"""

import sys
import uiautomator as ui
from event import AndroidEvent, TYPE_START_OR_END
from subprocess import PIPE, Popen
from threading import Thread
from Queue import Queue, Empty


class Parser(object):
    def __init__(self):
        self.raw_data_queue = Queue()
        self.events = Queue()
        self.current_event = AndroidEvent()
        self.previous_state = None

    def preprocess_line(self, line):
        # Ignore empty lines and device add events.
        if not line or line.startswith('add device') or line.startswith('name'):
            return

        # Parse the events now in the correct form.
        # Specifically, the output should be in the form:
        # [%time] %device: %event_code %event_property %value
        line_parts = line.split()
        time = float(line_parts[1][:-1])  # '54000.123132]'
        input_device = line_parts[2][:-1]  # '/dev/input/event1:'
        event_code = line_parts[3]
        event_property = line_parts[4]
        value = int(line_parts[5], 16)

        # Ignore separator events
        if event_code == 'EV_SYN':
            return

        event = self.current_event
        if event.is_start(event_property):
            event.init(time, self.previous_state)
        elif event.is_end(event_property):
            event.preprocess(self.previous_state)
            self.events.put(event)
            event = AndroidEvent()
        elif AndroidEvent.recognized(event_property):
            event.changed(event_property, time, value)

        # Re set the current event.
        self.current_event = event

    def post_process_events(self):
        preprocessed = self.events
        processed = Queue()

        while not preprocessed.empty():
            event = preprocessed.get()
            event.process()
            processed.put(event)

        self.events = processed

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
            self.previous_state = ui.device.dump()
            while True:
                try:
                    line = self.raw_data_queue.get_nowait().strip()
                    self.preprocess_line(line)
                except Empty:
                    # Ignore empty events, we're simply reading too quickly.
                    pass
        except KeyboardInterrupt:
            print 'Finished processing events from device.'
            p.terminate()
