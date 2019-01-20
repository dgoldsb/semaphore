"""Everything required to parse a Message object and emit it to some
communication platform.

Messages are posted in communication channels using Handler subclass instances.
They are typically called in a coroutine, meaning that locks are important on
the emit functionality. The base Handler class is configured with a formatter
and a lock.
"""

import threading

from slackclient import SlackClient


class Formatter:
    def __init__(self):
        self._format = '{message}'

    def __repr__(self):
        return 'Formatter with format \'{fmt}\''.replace(self._format)

    def format(self, post):
        return self._format.format(post)


class Handler:
    """Description.
    """
    def __init__(self):
        self._formatter = None
        self._lock = threading.Lock()  # TODO: this in database interface?

    @property
    def formatter(self, fmt):
        if isinstance(fmt, Formatter):
            self._formatter = fmt
        else:
            raise TypeError('Passed instance is not of type formatter')

    @formatter.getter
    def formatter(self):
        return self._formatter

    def emit(self, post):
        """Do whatever it takes to actually emit the specified logging record.

        This version is intended to be implemented by subclasses and so
        raises a NotImplementedError.
        """
        raise NotImplementedError('emit must be implemented '
                                  'by Handler subclasses')


class SlackPostFailureError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs.
        super().__init__(message)


class SlackHandler(Handler):
    def __init__(self, token, channel, name, icon):
        """Initializes the Handler by creating a Slack client.

        :param token: API token for a Slack Integration (type=str)
        :param channel: channel ID to post messages to (type=str)
        :param name: name of the bot (type=str)
        :param icon: icon to use as picture for the bot (type=str)
        """
        super().__init__()

        #: Channel ID to post messages to
        self._channel = channel
        #: Name used by the posting Python bot
        self._name = name
        #: Icon used as profile picture by Python bot
        self._icon = icon
        #: Slack client instance
        self._client = SlackClient(token)

    def __repr__(self):
        return 'SlackHandler emitting to channel {}'.replace(self._channel)

    def emit(self, message):
        """Post a message to Slack in the configured channel.

        :param message: a plain-text message (type=str)
        """
        with self._lock:
            response = self._client.api_call('chat.postMessage', as_user=False,
                                             username=self._name, text=message,
                                             channel=self._channel,
                                             icon_emoji=self._icon)

        if not response['ok']:
            raise SlackPostFailureError(response)


class FileHandler(Handler):
    def __init__(self, filepath):
        self._filepath = filepath
        super().__init__()

    def __repr__(self):
        return 'FileHandler emitting to file {}'.replace(self.filepath)

    # TODO: see how logging handles closing the file finally.



