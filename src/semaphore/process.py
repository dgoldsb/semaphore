"""Description.

Usage paragraph.
"""

import asyncio
import threading
import time


class Process:
    """Blank process class, implemented in three distinct subclasses.

    This Process class is the base for the input-, middleware- and
    output process classes implemented in these module. It is
    recommended to build any implementation you desire on these
    three classes.
    """
    def __init__(self, logger):
        """Provide a lock for concurrent access to queues.
        """
        self._lock = threading.RLock()
        self._logger = logger

    async def execution_loop(self):
        """To be implemented by subclasses.
        """
        raise NotImplementedError('To be implemented by subclasses')


# TODO: input process, to be expanded further.
class InputProcess(Process):
    """
    """
    def __init__(self, name, queue, logger):
        """
        """
        super().__init__(logger)

        #:
        self._name = name
        #:
        self._queue = queue
        #:
        self._topic_filter = None  # TODO: check if this is right class.

    def _put_message(self, message):
        """
        """
        if self._topic_filter is None:
            raise ValueError('Topic filter has not been supplied')

        if self._topic_filter(message):
            self._logger.debug(f'Putting message {message.body}')
            with self._lock:
                self._queue.put(message)
                # TODO: Catch full exception.

    @property
    def name(self):
        return self._name

    @property
    def topic_filter(self):
        return self._topic_filter

    @topic_filter.setter
    def topic_filter(self, topic_filter):
        # TODO: test if it is valid, if not remove this boilerplate.
        self._topic_filter = topic_filter

    async def execution_loop(self):
        """The main execution loop for an input process, to be 
        implemented by a subclass.
        
        Each subclass of the InputProcess should implement their own
        execution loop, which receives a Topic object and adds Message
        objects to the queue until interrupted.
        """
        raise NotImplementedError('To be implemented by subclasses')

# TODO: twitter input process.


# TODO: reddit process.


# TODO: blank middle-process.
class MiddlewareProcess(Process):
    """

    We only support one middleware layer as we do not do multi-core
    concurrency, meaning that splitting up a process without blocking
    API calls will not result any significant speedup.
    """
    def __init__(self, input_queue, output_queue, logger):
        """
        """
        super().__init__(logger)
        self._input_queue = input_queue
        self._output_queue = output_queue

    def _get_message(self):
        """
        """
        with self._lock:
            try:
                message = self._input_queue.get(False)
                self._logger.debug(f'Got message {message.body}')
                return message
            except self._input_queue.Empty:
                raise self._input_queue.Empty

    def _put_message(self, message):
        """
        """
        with self._lock:
            self._logger.debug(f'Putting message {message.body}')
            self._output_queue.put(message)
            # TODO: Catch full exception.

    def process_message(self, message):
        """
        """
        return message

    async def execution_loop(self):
        """
        """
        while True:
            try:
                message = self._get_message()
                message = self.process_message(message)
                self._put_message(message)
            except self._input_queue.Empty:
                await time.sleep(1)


# TODO: sentiment middle-process.


def output_message(handler):
    """Coroutine to emit messages using handlers without creating threads.
    """
    while True:
        message = (yield)
        handler.emit(message)


class OutputProcess(Process):
    """
    """
    def __init__(self, queue, logger):
        """
        """
        super().__init__(logger)
        self._queue = queue
        self._output_handlers = set()  # TODO: name : instance dict?

    def _get_message(self):
        """
        """
        with self._lock:
            try:
                return self._queue.get(False)
            except self._queue.Empty:
                raise  self._queue.Empty

    @property
    def handlers(self):
        return list(self._output_handlers)

    def add_handler(self, handler):
        if handler in self._output_handlers:
            pass
        else:
            self._output_handlers.add(handler)

    def delete_handler(self, handler):
        self._output_handlers.remove(handler)

    async def execution_loop(self):
        """
        """
        # Set up coroutines for all handlers.
        handler_coroutines = [output_message(x) for x in self._output_handlers]

        # Get messages from the queue.
        while True:
            try:
                message = self._get_message()
                self._logger.debug(f'Posting {message.body}')
                for coroutine in handler_coroutines:
                    coroutine.send(message)
            except self._queue.Empty:
                await time.sleep(1)


class SemaphoreTimeLimitInterrupt(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs.
        super().__init__(message)


class TimeLimitProcess(Process):
    """
    """
    def __init__(self, time_limit, logger):
        """
        """
        super().__init__(logger)
        self._time_limit = time_limit

    async def execution_loop(self):
        """
        """
        start_time = time.time()
        while True:
            time_left = self._time_limit - (time.time() - start_time)
            if time_left >= 0:
                raise SemaphoreTimeLimitInterrupt('Finished after {}s'.format(
                    self._time_limit))
            else:
                self._logger.debug(f'Still {time_left}s left')

            await time.sleep(1)
