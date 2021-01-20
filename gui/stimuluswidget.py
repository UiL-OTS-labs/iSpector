#!/usr/bin/env python

from PyQt4 import QtGui

DEBUG = False

##
# A widget that displays a stimulus
#
# The stimulus is the background of this widget
# The stimulus is rendered in such way that the
# ratio between the width and height of the stimulus
# are maintained. The StimulusWidget takes care
# that all image transformations are done from
# this widget. Thus if the clients in this
# class call their custompaint handler,
# they don't have to make new transformations
# to align the eyemovement data with the stimulus.
#
# \note the client must implement the onCustomPaint() function
class StimulusWidget(QtGui.QWidget):
    
    ##
    # initializes a StimulusWidget
    # 
    # To initialize specify a width and height or a stimulus image or both
    #
    # \param width, the width of the eyetracker window/screen
    # \param height the height of the eyetracking window
    # \param bgcolor the default background color
    def __init__(self,
                 width=-1,
                 height=-1,
                 bgcolor=QtGui.QColor(0,0,0),
                 parent=None
                 ):
        super(StimulusWidget,self).__init__(parent=None)
        
        ## the width of the screen of the eyetracker
        self.screen_width = width
        ## the heightof the screen of the eyetracker
        self.screen_height= height
        
        self.bgcol = bgcolor

    ##
    # reset the background color
    #
    # the reset background color takes effect after new painteven, so
    # you might want to force a redraw of the entire widget.
    def setBackgroundColor(self, color):
        self.bgcol = QtGui.QColor(color)

    ##
    # gets the model 
    def getModel(self):
        raise NotImplementedError()
        
    ##
    # gets the model 
    def getController(self):
        raise NotImplementedError()

    ##
    # Applies the default transformations
    #
    def _default_img_transform(self, painter):
        winheight   = float(self.height())
        winwidth    = float(self.width())
        # scr width and height refer to the size of the screen
        scrheight   = float(self.screen_height)
        scrwidth    = float(self.screen_width)
        MODEL       = self.getModel()
        assert(painter.transform().isIdentity())
        if scrheight <= 0 or scrwidth <= 0:
            # use dimensions of the stimulus
            try:
                scrheight = float(MODEL.getPixmap().height())
                scrwidth  = float(MODEL.getPixmap().width())
            except Exception as e:
                pass
                
        try:
            if scrheight <= 0 or scrwidth <= 0:
                raise RuntimeError(repr(self) + "Unable to determine Screensize")

            widthr  = winwidth / scrwidth
            heightr = winheight / scrheight

            if widthr > heightr:
                translate = (winwidth - heightr * scrwidth) /2
                painter.translate(translate, 0)
                painter.scale(heightr, heightr)
            else:
                translate = (winheight - widthr * scrheight) / 2
                painter.translate(0, translate)
                painter.scale(widthr, widthr)
        
        except RuntimeError as e:
            if DEBUG:
                mainwin = MODEL.getMainWindow()
                mainwin.reportStatus(StatusMessage.warning,
                                    "Unable to deduce image dimension\n"
                                    "is the stimulus correctly specified?")

        self.getController().setTransformationMatrix(painter.transform())

    ##
    # Paints the background and calls onCustomPaint
    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)

        # TODO examine whether the hint makes everything better.
        hint = QtGui.QPainter.RenderHint(painter.SmoothPixmapTransform)
        painter.setRenderHint(hint, True)
        painter.setClipRegion(event.region())
        
        #draw the background
        painter.fillRect(self.rect(), self.bgcol)
        
        # Apply transformations that center the stimulus nicely and completely in the 
        # center of the widget.
        self._default_img_transform(painter)

        #draw the stimulus
        pixmap = self.getModel().getPixmap()
        if pixmap:
            painter.drawPixmap(pixmap.rect(), pixmap, pixmap.rect())
        else:
            print("No pixmap loaded")
        
        # Let the derived widget do the other painting
        self.onCustomPaint(painter)

        painter.end()
    
    ##
    # The on custom paint is a painting handler that must be overloaded in
    # the derived class
    #
    # each time the paint event of this widget is called, the StimulusWidget
    # will call this function. Derived classes should not overload the paintEvent,
    # but this method. Then the StimulusWidget will draw the background
    # while the derived class paints the relevant foreground
    def onCustomPaint(self, painter):
        raise NotImplementedError("Overload this function in derived class.")

