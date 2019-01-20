"""Everything required to parse a Message object and emit it to some
communication platform.

Messages are posted in communication channels using Handler subclass instances.
They are typically called in a coroutine, meaning that locks are important on
the emit functionality. The base Handler class is configured with a formatter
and a lock.
"""

import os
import sys
import threading

from slackclient import SlackClient


class Formatter:
    def __init__(self):
        self._format = '{message}'

    def __repr__(self):
        return 'Formatter with format \'{fmt}\''.replace(self._format)

    def format(self, message):
        return self._format.format(message.__repr__)


class Handler:
    """Description.
    """
    def __init__(self, name):
        self._formatter = Formatter()
        self._lock = threading.Lock()
        self._name = name

    @property
    def formatter(self, fmt):
        if isinstance(fmt, Formatter):
            self._formatter = fmt
        else:
            raise TypeError('Passed instance is not of type formatter')

    @formatter.getter
    def formatter(self):
        return self._formatter

    @property
    def name(self):
        return self._name

    def emit(self, message):
        """Do whatever it takes to actually emit the specified logging record.

        This version is intended to be implemented by subclasses and so
        raises a NotImplementedError.
        """
        raise NotImplementedError('emit must be implemented '
                                  'by Handler subclasses')

    def format(self, message):
        return self._formatter.format(message)


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
            message = self.format(message)
            response = self._client.api_call('chat.postMessage', as_user=False,
                                             username=self._name, text=message,
                                             channel=self._channel,
                                             icon_emoji=self._icon)

        if not response['ok']:
            raise SlackPostFailureError(response)


class StreamHandler(Handler):
    """
    A handler class which writes messages, appropriately formatted,
    to a stream. Note that this class does not close the stream, as
    sys.stdout or sys.stderr may be used.
    """
    def __init__(self, stream=None, terminator='\n'):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        Handler.__init__(self)

        #:
        self.terminator = terminator
        #:
        self.stream = stream or sys.stderr

    def flush(self):
        """
        Flushes the stream.
        """
        with self._lock:
            try:
                if self.stream and hasattr(self.stream, "flush"):
                    self.stream.flush()
            finally:
                pass

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            message = self.format(record)
            stream = self.stream
            stream.write(message)
            stream.write(self.terminator)
            self.flush()
        except Exception as error:
            raise error

    def set_stream(self, stream):
        """Sets the StreamHandler's stream to the specified value,
        if it is different.

        Returns the old stream, if the stream was changed, or None
        if it wasn't.
        """
        if stream is self.stream:
            result = None
        else:
            result = self.stream
            with self._lock:
                self.flush()
                self.stream = stream
        return result

    def __repr__(self):
        return 'StreamHandler emitting to stream {}'.replace(self.stream.__repr__)


class FileHandler(StreamHandler):
    def __init__(self, filename, mode='a', encoding=None):
        """Open the specified file and use it as the stream for logging.
        """
        super().__init__()
        filename = os.fspath(filename)

        #:
        self.filepath = os.path.abspath(filename)
        #:
        self.mode = mode
        #:
        self.encoding = encoding

    def close(self):
        """Closes the stream.
        """
        with self._lock:
            if self.stream:
                try:
                    self.flush()
                finally:
                    stream = self.stream
                    self.stream = None
                    if hasattr(stream, "close"):
                        stream.close()

    def _open(self):
        """Open the current base file with the (original) mode and encoding.

        Return the resulting stream.
        """
        return open(self.filepath, self.mode, encoding=self.encoding)

    def emit(self, record):
        """Emit a record.

        If the stream was not opened because 'delay' was specified in the
        constructor, open it before calling the superclass's emit.
        """
        if self.stream is None:
            self.stream = self._open()
        StreamHandler.emit(self, record)

    def __repr__(self):
        return 'FileHandler emitting to file {}'.replace(self.filepath)
