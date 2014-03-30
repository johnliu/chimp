"""
Classes representing the UI state of an event.
"""

from xml.etree import ElementTree as ET
from parse import parse
from utils import Rect


class StateChange(object):
    def __init__(self):
        self.start = State()
        self.end = State()


class Node(object):
    def __init__(self, element):
        attr = element.attrib
        self.id = '%s/%s' % (attr.get('class'), attr.get('resource-id'))
        self.cls = attr.get('class')
        self.rid = attr.get('resource-id')
        self.bounds = Rect(*parse('[{:d},{:d}][{:d},{:d}]', attr.get('bounds')))

    def __repr__(self):
        return '<Element(%s)>' % self.id


class State(object):

    def __init__(self):
        self.xml = None
        self.chain = []

    def process(self, point):
        # TODO(johnliu): Check for touches outside of boundary.
        root = ET.fromstring(self.xml.encode('utf-8'))
        children = list(root)

        while children:
            for child in children:
                node = Node(child)
                if point in node.bounds:
                    children = list(child)
                    self.chain.append(node)
                    break
