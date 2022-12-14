#!/usr/bin/env python


##
# A general first in last out stack
#
# This is a general stack. One can push Items
# on the stack and pop them of the stack.
# If someone creates a stack of items he must take into
# account that creating a stack means that the last item
# in that will be the first to be removed.
class Stack(object):

    ##
    # Thrown when popping from an empty stack
    class StackEmpty(Exception):
        ##
        # init exception
        #
        # @param size integer with stacksize
        def __init__(self, size):
            ## message to the user
            self.msg = "Popping from stack with size {}".format(size)

        ## return a string from self
        def __str__(self):
            return self.msg

    ##
    # Init a new stack
    #
    # \param items an iterable, the last item will be the first to be popped.
    # \param maxitems the maximum size of the stack.
    #
    def __init__(self, items=None, maxitems=-1):
        ## A list that holds the items for the stack
        self._s = []
        ## The maximum number of items or infinite if maxitems < 0
        self._maxitems = maxitems
        if items:
            self._s = list(reversed(items))

        # Throw away the abundant items.
        if self._maxitems >= 0:
            self._s = self._s[len(self._s) - self._maxitems:]

    ##
    # pop the last item from the stack
    #
    # \throw  StackEmpty
    # \return the last push item
    def pop(self):
        if len(self._s) <= 0:
            raise Stack.StackEmpty(len(self._s))
        return self._s.pop()

    ##
    # push a new item to the stack
    #
    # Pushes a new item to the stack, if the stack becomes greater than the
    # maximum the items that were added firstly will be removed silently.
    #
    # \param item a new item for on the stack
    #
    def push(self, item):
        self._s.append(item)
        if self._maxitems >= 0 and len(self._s) > self._maxitems:
            self._s.pop(0)

    ##
    # Get a reference to the item at the top op the stack without popping
    # it from the stack.
    #
    # \returns the top item from the stack.
    # \throw Stack.StackEmpty if the stack is empty.
    #
    def top(self):
        if len(self._s) == 0:
            raise Stack.StackEmpty(len(self._s))
        return self._s[len(self._s) - 1]

    ##
    # set the maximum allowed size of a Stack
    def setMaxSize(self, length):
        length = int(length)
        self._maxitems = length
        if self._maxitems >= 0:
            self._s = self._s[len(self._s) - self._maxitems:]

    ##
    # create a string of itself
    def __str__(self):
        return "Stack " + repr(self._s)

    ##
    # create a string of itself
    def __repr__(self):
        return self.__str__()

    ##
    # return size of the stack
    def __len__(self):
        return len(self._s)

    ##
    # return iterator
    def __iter__(self):
        return iter(reversed(self._s))

    ##
    # shrinks the stack
    #
    # Shrinks the stack by removing the newest indices first
    # \param index
    def shrink(self, index):
        if index > len(self):
            self._s = []
        else:
            self._s = self._s[0:len(self._s) - index]

    ##
    # returns the nth item on the stack
    #
    # return the nth item on the stack and where 0 is the last pushed item
    # and len(Stack) - 1 is the first item.
    def __getitem__(self, index):
        index = len(self) - (index + 1)
        assert index >= 0 and index < len(self)
        return self._s[index]


if __name__ == "__main__":
    s = Stack([1, 2, 3], 2)
    print(s)
    s.push(1)
    try:
        while len(s) >= 0:
            print(s.pop(), " ")
    except Stack.StackEmpty as e:
        print(str(e))
    print()

    s = Stack(["Amateur", "Does", "Get", "Better", "Eventually"])
    print(s)
    s.push("Every")
    print(s)
    for i in s:
        print(i, " ")
    print()

    s.pop()
    while len(s) > 0:
        print(s.pop())

    s = Stack(range(6))
    print(s)
    s.setMaxSize(3)
    print(s)

    assert s.top() is s.pop()
    assert not (s.pop() is s.top())
