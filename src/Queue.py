class Queue:
    class FullQueue(Exception):
        def __str__(self):
            return "You cannot add an item to a full queue.\nTry a queue with no limit"

    class EmptyQueue(Exception):
        def __str__(self):
            return "Queue is empty"

    def __init__(self, max_size=-1):
        self.size = max_size
        self._data = []

    def __str__(self):
        return str(self._data)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data

    def en_queue(self, item):
        if not self.size == len(self._data):
            self._data.append(item)
        else:
            raise self.FullQueue

    def de_queue(self):
        if not len(self._data) == 0:
            item = self._data[0]
            self._data.remove(item)
            return item
        else:
            raise self.EmptyQueue

    def is_full(self):
        if self.size == -1:
            return False
        else:
            return True if self.size == len(self._data) else False

    def is_empty(self):
        return True if self._data == [] else False


class Stack:
    class FullStack(Exception):
        def __str__(self):
            return "You cannot add an item to a full stack.\nTry a stack with no limit"

    class EmptyStack(Exception):
        def __str__(self):
            return "Queue is empty"

    def __init__(self, max_size=-1):
        self.size = max_size
        self._data = []

    def __str__(self):
        return str(self._data)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def push(self, item):
        if not self.size == len(self._data):
            self._data.append(item)
        else:
            raise self.FullStack

    def pop(self):
        if not len(self._data) == 0:
            return self._data.pop(-1)
        else:
            raise self.EmptyStack

    def peek(self):
        return self._data[-1]

    def is_full(self):
        return True if self.size == len(self._data) and not self.size == -1 else False

    def is_empty(self):
        return True if len(self._data) == 0 else False
