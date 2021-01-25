#!/usr/bin/env python

#import QtGui
from PyQt5 import QtCore

class StatusEvent(QtCore.QEvent):
    
    my_user_event_type = QtCore.QEvent.registerEventType()

    def __init__(self, status):
        super(StatusEvent, self).__init__(StatusEvent.my_user_event_type)
        self.status = status

    def get_status(self):
        return self.status

    def spontaneous(self):
        return False

    def type(self):
        return StatusEvent.my_user_event_type


# probably to be removed or redesigned
class iSpectorUserEvent(QtCore.QEvent):
    
    my_user_event_type = QtCore.QEvent.registerEventType()

    def __init__(self):
        super(iSpectorUserEvent, self).__init__(my_user_event_type)
        


# probably to be removed or redesigned
class ActionThreadEvent (iSpectorUserEvent):
    
    my_user_event_type = QtCore.QEvent.registerEventType()

    def __init__(self):#, something)
        pass 

