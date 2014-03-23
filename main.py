from parser import Parser
from interfacer import Communicator
from monkey_interfacer import MonkeyCommunicator


def main(package, activity):
    """
    package - the name of the package, e.g. 'com.twitter.android'
    activity - the name of the activity to start, e.g. 'StartActivity'
    """

    parser = Parser()
    parser.collect_events()

    # monkey = MonkeyCommunicator(parser.events)
    # monkey.communicate()
    communicator = Communicator(parser.events)
    communicator.communicate()


if __name__ == '__main__':
    main('com.twitter.android', 'StartActivity')
