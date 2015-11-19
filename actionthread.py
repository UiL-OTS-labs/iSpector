#!/usr/bin/env python

import threading as t

class ActionRunner(t.Thread):
    
    def __init__(self, action, argument, thread_name=None):
        '''
        Make a new ActionRunner
        @param action a callable function or object
        @param argument can be a single object or a tuple
        '''
        self.my_file    = absfname
        self.errors     = None
        self.action     = action
        self.argument   = argument

    def run (self):
        if type(self.argument) == tuple:
            self.action(*self.argument)
        else
            self.action(argument)
        self.finish()
    
    def finish(self):
        '''
        this function is called when the action is completed
        overwrite in child class to call something usefull
        '''
        pass
        
