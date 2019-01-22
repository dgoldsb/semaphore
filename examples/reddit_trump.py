# TODO: read Trump posts from several subreddits, post them to a CSV for analysis with sentiment and timestamp, as well as a simple markdown dump with a silly separator.
# TODO: ask credentials in CMD, then create credentials file in ignore.

import datetime
import time
import logging
import os
import sys

from semaphore import Semaphore, FileHandler, InputProcess, Message, MiddlewareProcess
from semaphore.topic_filter import TopicFilter


class DummyInputProcess(InputProcess):
    async def execution_loop(self):
        counter = 0
        while True:
            message = Message('me', f'test {counter}', 'dummy', 'https://www.foo.com', datetime.datetime.utcnow())
            self._put_message(message)
            counter += 1
            await time.sleep(1)


class DummyMiddleProcess(MiddlewareProcess):
    def process_message(self, message):
        message.body += ' bar'
        return message


class DummyTopicFilter(TopicFilter):
    def filter(self, message):
        return '1' in message.body


def test_semaphore():
    filename = 'foo.txt'
    try:
        semaphore = Semaphore(time_limit=10)

        log_handler = logging.StreamHandler(sys.stderr)
        log_handler.setLevel(logging.DEBUG)
        semaphore._logger.addHandler(log_handler)

        input_process = DummyInputProcess('foo', semaphore._input_queue, semaphore._logger)
        input_process.topic_filter = DummyTopicFilter()
        file_handler = FileHandler('barhandler', filename)

        semaphore.add_input_process(input_process)
        semaphore.replace_middleware_process(DummyMiddleProcess)
        semaphore.add_output_handler(file_handler)

        semaphore.run()
    finally:
        if os.path.isfile(filename):
            os.remove(filename)


if __name__ == '__main__':
    test_semaphore()
