"""Description.

Usage paragraph.
"""

import logging
import queue
import sys

from .process import MiddlewareProcess, OutputProcess


class Message:
    def __init__(self, author, body, platform, url, timestamp, **kwargs):
        #: Author of the message
        self._author = author
        #: Body of the message
        self._body = body
        #: Platform the message was posted on
        self._platform = platform
        #: URL where the message was fetched from
        self._url = url
        #: Timestamp the message was posted
        self._timestamp = timestamp

        #: Additional fields can be set later by another process, or are supplied
        self._additions = kwargs

    def __repr__(self):
        description = {
            'author': self._author,
            'body': self._body,
            'platform': self._platform,
            'timestamp': self._timestamp,
            'url': self._url
        }
        return {**self._additions, **description}


class SemaphoreConfigurationError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs.
        super().__init__(message)


class Semaphore:
    def __init__(self):
        #: Input processes
        self._input_processes = dict()
        #: Message queue
        self._input_queue = queue.Queue()
        self._logger = logging.getLogger()
        self._output_queue = queue.Queue()
        #: Processes to kick off
        self._processes = dict()

        # We always have an output process.
        self._output_process = OutputProcess(self._output_queue,
                                             self._logger)

        # As a default we use a plain passing MiddlewareProcess.
        self._middleware = MiddlewareProcess(self._input_queue,
                                             self._output_queue,
                                             self._logger)

    def add_output_handler(self, handler):
        # TODO: check if this is a subclass of the correct object.

        self._output_process.add_handler(handler)

    def delete_output_handler(self, handler):
        # TODO: check if this is a subclass of the correct object.

        self._output_process.delete_handler(handler)

    def replace_middleware_process(self, middleware_process):
        # TODO: check if this is a subclass of the correct object.

        self._middleware = middleware_process

    def run(self):
        if not self._input_processes:
            raise SemaphoreConfigurationError('No input processes '
                                              'have been defined')

        if not self._output_process.handlers:
            raise SemaphoreConfigurationError('No output handlers '
                                              'have been defined')

        all_processes = list(self._input_processes.values()) + \
                        [self._middleware, self._output_process]
        try:
            # Kick off concurrent processes.
            # TODO: Run all sources in different threads to let Python handle CPU time.
            pass
        except KeyboardInterrupt:
            sys.exit(0)
