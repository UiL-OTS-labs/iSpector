#!/usr/bin/env python2.7
"""
@packackage statusqueue

"""

from Queue import Queue

class StatusMessage(object):
    '''
    Is a message on the queue this object should not
    be instantiated it self. Rather use the derived classes
    '''

    ## this message is an error
    error   = 1 
    ## this message is ok, not an error
    ok      = 0
    def __init__(self, status, message):
        '''
        @param message the message to display to the user
        @param status is either StatusMessage.error or StatusMessage.ok.
        '''
        self.message = message
        self.status  = status

    def status(self):
        return self.status

    def message(self):
        return self.message

    def __str__(self):
        ret = ""
        if self.status == self.ok:
            ret = "ok   : {}".format()
        else:
            ret = "error: {}".format(self.msg)

class StatusQueue(object):
    '''
    A queue that lives in the gui. If some notable event happens and
    we want to inform the user. We can send a message to this queue.
    The queue is sometimes emptied by the gui and then the gui posts
    the events and thereby updating the user of possible errors that
    have occurred.
    This is a FIFO queue
    '''

    def __init__(self):
        self.queue = Queue(100)

    def __size__():
        return self.queue.qsize()

    def push_message(self, message):
        try :
            self.queue.put(message, False)
        except Queue.Full as e:
            exit("Oops status queue full this should not happen: " + str(e))

    def pop_message(self):
        ''' get a message from the queue or return None'''
        ret = None
        try :
            ret = self.queue.get(False)
        except Queue.Empty:
            pass
        return ret
