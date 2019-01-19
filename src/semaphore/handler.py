"""Description.

Usage paragraph.
"""

import threading


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
        self.lock = threading.Lock()  # TODO: this in database interface?

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
        """
        Do whatever it takes to actually emit the specified logging record.

        This version is intended to be implemented by subclasses and so
        raises a NotImplementedError.
        """
        raise NotImplementedError('emit must be implemented '
                                  'by Handler subclasses')


class SlackHandler(Handler):
    def __init__(self):
        super().__init__()
        pass
