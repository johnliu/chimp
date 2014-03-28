from parser import Parser
from interfacer import Communicator
from uiautomator import device


def main(package, activity):
    """
    package - the name of the package, e.g. 'com.twitter.android'
    activity - the name of the activity to start, e.g. 'StartActivity'
    """

    # Ensure the device is connected.
    print "Connecting.."
    info = device.info
    print "Connected." if info else "Unable to connect."

    parser = Parser()
    parser.collect_events()
    communicator = Communicator(parser.events)
    communicator.communicate()


if __name__ == '__main__':
    main('com.twitter.android', 'StartActivity')
