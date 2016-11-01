#!/usr/bin/env python

##
# \file actionthread.py
#

import threading as t

##
# Action runner runs a task inside a thread.
#
# In order to implement a usefull action runner One needs to
# inherit from this class. The method a action is a callable
# that will be called when starting the thread. The argument
# will be passed to the callable. When the Callable needs more
# parameters, make argument a tuple the tuple will be presented
# to the callable, thus the length of the tuple should match the
# function signature.
# Finally if a thread finishes it calls ActionRunner.finish. Defaultly
# it does noting, however if you want to do something when the thread
# finishes overwrite the function in a derived class.
#
class ActionRunner(t.Thread):
    
    ##
    # Make a new ActionRunner
    # \param action a callable (function or object)
    # \param argument can be a single object or a tuple this will
    # be used when starting the thread.
    # \param thread_name a name for the thread, possibly handy for debugging.
    def __init__(self, action, argument, thread_name=None):
        ## a callable that will be called when the thread is started
        self._action     = action
        ## argument passed to the action or tuple that will be given unpacked
        # to the action
        self._argument   = argument
    
    ##
    # called when running the thread.
    def run (self):
        if type(self.argument) == tuple:
            self.action(*self.argument)
        else:
            self.action(argument)
        self.finish()
    
    ##
    # This function is called when the action is completed
    # overwrite in child class to call something useful
    # otherwise finish does nothing.
    def finish(self):
        pass
        
