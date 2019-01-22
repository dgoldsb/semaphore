"""Description.

Usage paragraph.
"""

import asyncio
import logging
import queue
import sys

from .handler import FileHandler, SlackHandler, StreamHandler
from .process import InputProcess, MiddlewareProcess, OutputProcess, TimeLimitProcess


class Message:
    def __init__(self, author, body, platform, url, timestamp, **kwargs):
        #: Author of the message
        self.author = author
        #: Body of the message
        self.body = body
        #: Platform the message was posted on
        self.platform = platform
        #: URL where the message was fetched from
        self.url = url
        #: Timestamp the message was posted
        self.timestamp = timestamp

        #: Additional fields can be set later by another process, or are supplied
        self.additions = kwargs  # TODO: access in the DotDict way.

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


async def run_process(processes):
    tasks = []
    for process in processes:
        task = asyncio.ensure_future(process.execution_loop())
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)


class Semaphore:
    def __init__(self, time_limit=None):
        #:
        self.time_limit = time_limit
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

    def add_input_process(self, input_process):
        """
        INSTANCE

        :param input_process:
        :return:
        """
        if input_process.name in self._input_processes.keys():
            self._logger.warning(f'Process {input_process.name} '
                                 f'has been defined')
        else:
            self._input_processes[input_process.name] = input_process

    def add_output_handler(self, handler):
        # TODO: check if this is a subclass of the correct object.

        self._output_process.add_handler(handler)

    def delete_output_handler(self, handler):
        # TODO: check if this is a subclass of the correct object.

        self._output_process.delete_handler(handler)

    def replace_middleware_process(self, middleware_process):
        """
        CLASS OBJECT

        :param middleware_process:
        :return:
        """
        # TODO: check if this is a subclass of the correct object.

        self._middleware = middleware_process(self._input_queue,
                                              self._output_queue,
                                              self._logger)

    def run(self):
        if not self._input_processes:
            raise SemaphoreConfigurationError('No input processes '
                                              'have been defined')

        if not self._output_process.handlers:
            raise SemaphoreConfigurationError('No output handlers '
                                              'have been defined')

        all_processes = list(self._input_processes.values()) + \
                        [self._middleware, self._output_process]
        if self.time_limit is not None:
            all_processes.append(TimeLimitProcess(self.time_limit, self._logger))
        try:
            # Kick off concurrent processes.
            asyncio.get_event_loop().run_until_complete(run_process(all_processes))
        except KeyboardInterrupt:
            sys.exit(0)
