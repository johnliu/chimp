"""
Classes representing the UI state of an event.
"""

from xml.etree import ElementTree as ET
from parse import parse
from utils import Rect
from collections import deque


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
            else:
                print 'Could not find an element.'
                break

    def as_list(self, symbols, append=True):
        root = ET.fromstring(self.xml.encode('utf-8'))
        queue = deque(list(root))

        data = [0] * len(symbols)
        while queue:
            child = queue.popleft()
            node = Node(child)

            if node.cls:
                if node.cls not in symbols and append:
                    symbols[node.cls] = len(symbols)
                    data.append(0)

                try:
                    index = symbols[node.cls]
                    data[index] = 1
                except KeyError:
                    pass

            if node.rid:
                if node.rid not in symbols and append:
                    symbols[node.rid] = len(symbols)
                    data.append(0)

                try:
                    index = symbols[node.rid]
                    data[index] = 1
                except KeyError:
                    pass

            queue.extend(list(child))

        return data
