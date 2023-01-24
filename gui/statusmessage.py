#!/usr/bin/env python

##
# \file statusmessage.py
# Contains a message wich can be displayed in the main gui status window.


##
# Is a message on the queue this object should not
# be instantiated it self. Rather use the derived classes
class StatusMessage(object):
    ## this message is an error
    error = 2
    ## this message is a warning
    warning = 1
    ## this message is ok, not an error
    ok = 0

    ##
    # initialize a statusmessage
    #
    # \param status one of StatusMessage.error, StatusMessage.warning or
    #               StatusMessage.ok
    # \param message a string of the message to show to the users
    def __init__(self, status, message):
        ## the message to be displayed
        self.message = message
        ## the severity status
        self.status = status

    ## return the status
    def get_status(self):
        return self.status

    ## retrieve the message
    def get_message(self):
        return self.message

    ## stringfy the message
    def __str__(self):
        return self.message
