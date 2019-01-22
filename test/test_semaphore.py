# TODO: test the basic functionalities with a dummy logger that emits to a variable, with two simple generators with waits as inputs.

import datetime
import pytest
import time
import os

from semaphore import Semaphore, FileHandler, InputProcess, Message, MiddlewareProcess
from semaphore.process import SemaphoreTimeLimitInterrupt
from semaphore.topic_filter import TopicFilter


class DummyInputProcess(InputProcess):
    def execution_loop(self):
        counter = 0
        while True:
            message = Message('me', f'test {counter}', 'dummy', 'https://www.foo.com', datetime.datetime.utcnow())
            self._put_message(message)
            counter += 1
            time.sleep(2)


class DummyMiddleProcess(MiddlewareProcess):
    def process_message(self, message):
        message.body += ' bar'
        return message


class DummyTopicFilter(TopicFilter):
    def filter(self, message):
        return '1' in message.body


# TODO: split into general test NowhereHandler and test for FileHandler.
def test_semaphore():
    filename = 'foo.txt'
    try:
        semaphore = Semaphore(time_limit=5)

        input_process = DummyInputProcess('foo', semaphore._input_queue, semaphore._logger)
        input_process.topic_filter = DummyTopicFilter()
        file_handler = FileHandler('barhandler', filename)

        semaphore.add_input_process(input_process)
        semaphore.replace_middleware_process(DummyMiddleProcess)
        semaphore.add_output_handler(file_handler)

        with pytest.raises(SemaphoreTimeLimitInterrupt):
            semaphore.run()
    finally:
        if os.path.isfile(filename):
            os.remove(filename)
