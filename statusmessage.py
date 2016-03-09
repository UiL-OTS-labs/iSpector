#!/usr/bin/env python2.7
"""
@package StatusMessage

"""

class StatusMessage(object):
    '''
    Is a message on the queue this object should not
    be instantiated it self. Rather use the derived classes
    '''
    ## this message is an error
    error   = 2 
    ## this message is a warning
    warning = 1
    ## this message is ok, not an error
    ok      = 0

    def __init__(self, status, message):
        '''
        @param message the message to display to the user
        @param status is either StatusMessage.error or StatusMessage.ok.
        '''
        self.message = message
        self.status  = status

    def get_status(self):
        return self.status

    def get_message(self):
        return self.message

    def __str__(self):
        return self.message
