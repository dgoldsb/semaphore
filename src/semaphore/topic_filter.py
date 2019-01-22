"""Something functor.

Description.
"""


class TopicFilter:
    def __call__(self, message):
        return self.filter(message)

    def filter(self, message):
        raise NotImplementedError('Implement filter method in a subclass')
