"""
A class representing the UI state of an event.
"""

from xml.etree import ElementTree as ET
from parse import parse
from utils import Rect


class State(object):
    class Node(object):
        def __init__(self, element):
            attr = element.attrib
            self.id = '%s/%s' % (attr.get('class'), attr.get('resource-id'))
            self.bounds = Rect(*parse('[{:d},{:d}][{:d},{:d}]', attr.get('bounds')))

        def __repr__(self):
            return '<Element(%s)>' % self.id

    def __init__(self):
        self.start = None
        self.start_chain = []
        self.end = None
        self.end_chain = []

    def process(self, string, chain, point):
        # TODO(johnliu): Check for touches outside of boundary.
        root = ET.fromstring(string.encode('utf-8'))
        children = list(root)

        while children:
            for child in children:
                node = State.Node(child)
                if point in node.bounds:
                    children = list(child)
                    chain.append(node)
                    break

    def process_start(self, point):
        self.process(self.start, self.start_chain, point)

    def process_end(self, point):
        self.process(self.end, self.end_chain, point)


