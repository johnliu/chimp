from parser import Parser
from monkey_interfacer import MonkeyCommunicator


def main(package, activity):
    """
    package - the name of the package, e.g. 'com.twitter.android'
    activity - the name of the activity to start, e.g. 'StartActivity'
    """

    parser = Parser()
    parser.collect_events()

    monkey = MonkeyCommunicator(parser.events)
    monkey.communicate()


if __name__ == '__main__':
    main('com.twitter.android', 'StartActivity')
