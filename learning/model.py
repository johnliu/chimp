"""
Model creation, generation and saving.
"""

import numpy as np
from sklearn.tree.tree import DecisionTreeClassifier, DecisionTreeRegressor
from event import Action, ACTION_DRAG, ACTION_TOUCH, ACTION_BACK
from uiautomator import device
from utils import Point
from random import random


DRAG = 0
TOUCH = 1
BACK = 2


class Model(object):
    """
    The machine learning component of the tester.

    This component stores four different models:
    1) A model to decide between different types of events (drags and touches).
    2) A model to decide on the starting position for drags.
    3) A model to decide on the ending position for drags.
    4) A model to decide on the position of the touch.

    The input data are all the different known UI elements on the screen from
    the training data and whether or not they are visible on the screen.

    To acquire this, we first get the stored XML model and record the resource-id
    and class. We concatenate them into an array and mark as (1) for visible and (0)
    for not visible.
    """

    def __init__(self):
        self.symbols = {}
        self.action_data = None
        self.action_labels = None
        self.action_classifier = None
        self.drag_data = None
        self.drag_end_labels = None
        self.drag_end_classifier = None
        self.drag_start_labels = None
        self.drag_start_classifier = None
        self.touch_data = None
        self.touch_labels = None
        self.touch_classifier = None
        self.device_info = device.info

    def parse_events(self, queue):
        symbols = {'randomizer': 0}
        events = []

        all_data = []
        all_results = []
        drag_data = []
        drag_start_results = []
        drag_end_results = []
        touch_data = []
        touch_results = []

        while not queue.empty():
            event = queue.get()
            events.append(event)

            lst = event.state.start.as_list(symbols)
            lst[0] = random()
            all_data.append(lst)

            if event.action.is_drag():
                drag_data.append(lst)
                all_results.append(DRAG)

                start = event.changes.start()
                end = event.changes.end()
                drag_start_results.append(start.x * start.y)
                drag_end_results.append(end.x * end.y)

            if event.action.is_touch():
                touch_data.append(lst)
                all_results.append(TOUCH)

                start = event.changes.start()
                touch_results.append(start.x * start.y)

            if event.action.is_back():
                all_results.append(BACK)

        data = np.zeros((len(all_data), len(symbols)))
        for i, item in enumerate(all_data):
            data[i, :len(item)] = item[:]

        drags = np.zeros((len(drag_data), len(symbols)))
        for i, item in enumerate(drag_data):
            drags[i, :len(item)] = item[:]

        touches = np.zeros((len(touch_data), len(symbols)))
        for i, item in enumerate(touch_data):
            touches[i, :len(item)] = item[:]

        self.symbols = symbols

        self.action_data = data
        self.action_labels = np.array(all_results)

        self.drag_data = drags
        self.drag_start_labels = np.array(drag_start_results)
        self.drag_end_labels = np.array(drag_end_results)

        self.touch_data = touches
        self.touch_labels = np.array(touch_results)

    def train(self):
        self.action_classifier = DecisionTreeClassifier()
        self.action_classifier.fit(self.action_data, self.action_labels)

        self.drag_start_classifier = DecisionTreeRegressor()
        self.drag_start_classifier.fit(self.drag_data, self.drag_start_labels)

        self.drag_end_classifier = DecisionTreeRegressor()
        self.drag_end_classifier.fit(self.drag_data, self.drag_end_labels)

        self.touch_classifier = DecisionTreeRegressor()
        self.touch_classifier.fit(self.touch_data, self.touch_labels)

    def predict(self, state):
        input = state.as_list(self.symbols, False)
        input[0] = random()
        action = Action()

        type = self.action_classifier.predict(input)
        width = self.device_info['displayWidth']
        if type == DRAG:
            start = self.drag_start_classifier.predict(input)[0]
            end = self.drag_end_classifier.predict(input)[0]
            start = Point(start % width, start / width)
            end = Point(end % width, end / width)

            action.init(ACTION_DRAG, start, end, 0.5)
        elif type == TOUCH:
            point = self.touch_classifier.predict(input)[0]
            point = Point(point % width, point / width)

            action.init(ACTION_TOUCH, point.x, point.y)
        elif type == BACK:
            action.init(ACTION_BACK)

        return action

    def save(self):
        pass

