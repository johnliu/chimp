from interfacer import Communicator, Parser
from storage import EventStorage
from uiautomator import device


def main(package):
    """
    package - the name of the package, e.g. 'com.twitter.android'
    activity - the name of the activity to start, e.g. 'StartActivity'
    """

    # Ensure the device is connected.
    print "Connecting.."
    info = device.info
    print "Connected." if info else "Unable to connect."

    # First parse and collect events.
    parser = Parser()
    parser.collect_events()
    parser.process_events()

    # Store the events in persistent storage.
    storage = EventStorage(info['currentPackageName'])
    storage.qwrite_all(parser.events)
    events = storage.qread()

    # Generate a model for this.
    communicator = Communicator(events)
    communicator.communicate()


if __name__ == '__main__':
    main('com.twitter.android')
