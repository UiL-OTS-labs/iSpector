#!/usr/bin/env python

##
# \file fixationeditor.py
#
# this file is created to help edit fixations.
# The fixations in this editor are edited in space.
#
# \todo make it possible to edit fixations in space.
#

import time
import copy
from . import datamodel
from . import dataview
from . import stimuluswidget
from .statusmessage import StatusMessage
from log.eyelog import LogEntry, SaccadeEntry
from utils import space
from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
import os.path as path


## show the left eye only
SHOW_LEFT = 1 << 0
## show the right eye only
SHOW_RIGHT = 1 << 1
## show the average eye only
SHOW_AVG = 1 << 2
## show all the eyes
SHOW_ALL = SHOW_LEFT | SHOW_RIGHT | SHOW_AVG


##
# This class helps translating fixations using the map function
#
class _TranslateFix(object):
    ##
    # Inits a _TranslateFix object
    #
    # \param x[in]   translate value for x coordinate
    # \param y[in]   translate value for y coordinate
    # \param ref[in] A reference fixation or None, than all fixations are mapped
    def __init__(self, x, y, ref=None):
        ## Reference fixation
        self._ref = ref
        ## the amount to translate a fixation in the x coordinate
        self._x = x
        ## the amount to translate a fixation in the y coordinate
        self._y = y

    ##
    # if fix is equal to the reference variable it is going to be translated
    #
    # The translation only occurs if fix is equal to the reference fixation
    # or the reference fixation is None.
    #
    # The input fix.x and .y is translated by the x and y value specified
    # by __init__ function
    #
    # \param fix a fixation to be translated
    # \return the original fixation or the translated fixation
    def __call__(self, fix):
        if self._ref is None or fix == self._ref:
            fix.x += self._x
            fix.y += self._y
        return fix


##
# Used internally to sort fixation base on the distance from
# the mouse click
#
# It is a python3 compatible key function, whereas it was a python2
# compare function before.
#
class _SortOnDistanceKey(object):

    ##
    # \param x x-coordinate
    # \param y y-coordinate
    def __init__(self, x, y):
        self.p = space.Point(x, y)

    ##
    # Called to compute key (distance between self.p and p2.
    def __call__(self, p2):
        coordinate = space.Point(p2.x, p2.y)
        return space.Point.distance(self.p, coordinate)


##
# Container for edits in the fixation edit view.
#
class FixationDataEdit(object):

    ##
    # \param [in] lfix an iterable with fixations of the left eye (or None)
    # \param [in] rfix an iterable with fixations of the right eye (or None)
    # \param [in] avgfix an iterable with fixations of the average eye (or None)
    # \param [in] lsac an iterable with saccades of the left eye (or None)
    # \param [in] rsac an iterable with saccades of the right eye (or None)
    # \param [in] avgsac an iterable with saccades of the average eye (or None)
    def __init__(self,
                 lfix,
                 rfix,
                 avgfix,
                 lsac,
                 rsac,
                 avgsac,
                 ):
        
        ## left fixations
        self.lfix = None
        ## right fixations
        self.rfix = None
        ## average eyesignal fixations
        self.avgfix = None
        ## left saccades
        self.lsac = None
        ## right saccades
        self.rsac = None
        ## average eyesignal saccades
        self.avgsac = None

        if lfix:
            self.lfix = copy.deepcopy(lfix)
        if rfix:
            self.rfix = copy.deepcopy(rfix)
        if avgfix:
            self.avgfix = copy.deepcopy(avgfix)
        if lsac:
            self.lsac = copy.deepcopy(lsac)
        if rsac:
            self.rsac = copy.deepcopy(rsac)
        if avgsac:
            self.avgsac = copy.deepcopy(avgsac)

    ##
    # Test for object equality
    def __eq__(self, rhs):
        return type(self) is type(rhs) and self.__dict__ == rhs.__dict__

    ##
    # Test for object difference
    def __ne__(self, rhs):
        return not (self == rhs)


##
# A controller for the editing of fixations.
#
class FixationEditController(datamodel.EditDataController):

    ##
    #  Init a FixationEditController
    #
    def __init__(self, model):
        super(FixationEditController, self).__init__(model)

        ## mouse event of mouse press
        self.press_event = None
        ## pressed time
        self.press_time = 0.0
        ## is the left button pressed
        self.lb_pressed = False

        ## mouse event of mouse release
        self.release_event = None

        ## mouse release time
        self.release_time = 0.0

        ## mouse event of dragging motion
        self.drag_event = None

        ## mouse release time
        self.drag_time = 0.0

        ##
        # number of ms between press and release to treat it
        # as a click
        self.click_time = 250.0

    ##
    # provide the model with the right transformation matrix
    def setTransformationMatrix(self, matrix):
        self.model.setTransformationMatrix(QtGui.QTransform(matrix))

    ##
    # The mouse press is stored and the timestamp is saved
    #
    def mousePress(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.press_time = time.time()
            self.press_event = QtGui.QMouseEvent(event)
            self.lb_pressed = True

    ##
    # The mouse press is stored if a release is triggered in the region
    #
    def mouseRelease(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.release_time = time.time()
            self.release_event = event
            if self.press_event and self.release_time - self.press_time < self.click_time / 1000:
                self._registerClick(event)
            elif self.lb_pressed:
                self.saveEdit(event)
            self.lb_pressed = False

    ##
    # The drag event is used to obtain a vector in wich indicate
    # how far the fixations have been dragged.
    def dragEvent(self, event):
        self.drag_time = time.time()
        self.drag_event = event
        if self.model.getSelected():
            x1, y1 = float(self.press_event.x()), float(self.press_event.y())
            x2, y2 = float(event.x()), float(event.y())
            mx1, my1 = self.model.mapMouseCoordinate(x1, y1)
            mx2, my2 = self.model.mapMouseCoordinate(x2, y2)
            vector = mx2 - mx1, my2 - my1
            self.model.setVector(vector)

    ##
    # checks the mouse event and selects, removes selected or selects multiple
    # fixations.
    # \param event[in] a QMouseEvent
    def _registerClick(self, event):
        x, y = float(event.x()), float(event.y())
        mappedx, mappedy = self.model.mapMouseCoordinate(x, y)

        if mappedx and mappedy:
            mod = event.modifiers()
            if mod == QtCore.Qt.NoModifier:
                self.selectNearest(mappedx, mappedy)
            elif mod == QtCore.Qt.ShiftModifier:
                self.deselectNearest(mappedx, mappedy)
            elif mod == QtCore.Qt.ControlModifier:
                self.addNearest(mappedx, mappedy)

    ##
    # Selects the nearest fixation
    #
    # The other fixations will be deselected
    def selectNearest(self, x, y):
        self.model.clearSelected()
        nearest = copy.deepcopy(self.model.selectFixation(x, y))
        self.model.appendSelected(nearest)

    ##
    # Selects the nearest fixation
    #
    # The other fixations will NOT be deselected
    def addNearest(self, x, y):
        nearest = copy.deepcopy(self.model.selectFixation(x, y))
        if nearest not in self.model.getSelected():
            self.model.appendSelected(nearest)

    ##
    # Deselects the nearest fixation
    #
    # The other fixations will NOT be deselected
    def deselectNearest(self, x, y):
        nearest = copy.deepcopy(self.model.selectFixation(x, y))
        selected = self.model.deselectFixation(nearest)

    ##
    # selects all the visible fixations
    def selectAll(self):
        selected = copy.deepcopy(self.model.getVisible())
        self.model.clearSelected()
        for i in selected:
            self.model.appendSelected(i)

    ##
    # Saves the current edit.
    #
    # \param mevent [in] mevent is a QMouseEvent
    def saveEdit(self, event):
        x1, y1 = float(self.press_event.x()), float(self.press_event.y())
        x2, y2 = float(event.x()), float(event.y())
        mx1, my1 = self.model.mapMouseCoordinate(x1, y1)
        mx2, my2 = self.model.mapMouseCoordinate(x2, y2)
        vector = mx2 - mx1, my2 - my1
        self.model.setVector(vector)
        self.model.saveEdit()
        self.model.setVector((0.0, 0.0))

    ##
    # tries to pop one edit from the stack of edits of the model
    #
    def undoEdit(self):
        super(FixationEditController, self).undoEdit()
        self.model.setSelected([])

    ##
    # tries to pop one edit from the stack of edits of the model
    #
    def redoEdit(self):
        super(FixationEditController, self).redoEdit()
        self.model.setSelected([])


##
# FixationEditModel allows you to remap fixations.
#
#
# FixationEditModel removes all non saccade and fixation
# eyemovement events from a trial. Therefore opening
# a file means editting it. The user can use the mouse to
# select a fixation and move to a place where he/she
# thinks it should be.
#
# \todo The main model has an fix that want to show
#       eyes that doesn't support the avg signal
#       it should be implemented there and
#       _show_eye should be removed here. 
class FixationEditModel(datamodel.EditDataModel):

    ##
    # Init a FixationEditModel
    #
    # \param files [in]     A list of files.
    # \param mainwin [in]   The iSpector main window.
    # \param show_eye [in]  An integer which bits specify which eyes to show.
    def __init__(self, files, mainwin, show_eye=SHOW_ALL):
        super(FixationEditModel, self).__init__(files, mainwin)
        ## an integer which bits dictate which eye should be selected
        self._show_eye = show_eye
        ## a list with references to the selected fixations
        self._selected = []
        ## the transformation matrix for the fixation canvas
        # it is used to map mouse presses to the coordinate system of
        # the stimulus.
        self._matrix = None

        ## The vector that indicate how far the fixations must be translated
        self._vector = 0.0, 0.0

        ## The pixmap of the current stimulus.
        self._pixmap = None

        ## The transparency of the fixations
        self.fixalpha = 50
        ## The transparency of the selection marker
        self.selalpha = 80

    ##
    # Set the transformation matrix.
    def setTransformationMatrix(self, m):
        self._matrix = QtGui.QTransform(m)

    ##
    # Get the transformation matrix.
    def getTransformationMatrix(self):
        return self._matrix

    ##
    # Returns the selected fixations, and only those visible
    # to the user.
    def getSelected(self):
        visible = self.getVisible()
        return [fix for fix in self._selected if fix in visible]

    ##
    # Reset the selected fixations
    def setSelected(self, selected):
        self._selected = selected

    ##
    # append a fixation to the selection
    def appendSelected(self, selection):
        self._selected.append(selection)

    ##
    # Remove a selection from the selected
    def deselectFixation(self, selection):
        self._selected =\
            [fix for fix in self._selected if fix != selection]

    ##
    # Clears the selection
    def clearSelected(self):
        self._selected = []

    ##
    # Sets the vector which indicates the distance the fixations should
    # be translated
    def setVector(self, vector):
        self._vector = vector

    ##
    # Gets the vector
    def getVector(self):
        return self._vector

    ##
    # Additionally to what onNewTrial normally does it also loads the stimulus.
    # and since a new trial means new data we clear the selection
    def onNewTrial(self):
        super(FixationEditModel, self).onNewTrial()
        t = self.getCurrentTrial()
        assert t
        fn = t.stimulus
        MM = self.getMainWindow().getModel()[0]
        stimdir = MM.stimulus_dir()
        abspath = path.join(stimdir, fn)

        # load relative to stimulus directory.
        if path.exists(abspath):
            self._pixmap = QtGui.QPixmap(abspath)
        else:
            self._pixmap = None

        # load relative to working directory.
        if self._pixmap and self._pixmap.isNull():
            self._pixmap = QtGui.QPixmap(fn)

        if self._pixmap and self._pixmap.isNull():
            self._pixmap = None
        if not self._pixmap:
            self.getMainWindow().reportStatus(StatusMessage.warning,
                                              "Unable to load \"" + fn + "\""
                                              )
        # Clear the selection.
        self.clearSelected()

    ##
    # Test whether the left fixations must be shown
    def showLeft(self):
        edit = self.getCurrentEdit()
        if not edit:
            return False

        if edit.lfix and super(FixationEditModel, self).showLeft():
            return True
        else:
            return False

    ##
    # Test whether the right fixations must be shown
    def showRight(self):
        edit = self.getCurrentEdit()
        if not edit:
            return False

        if edit.rfix and super(FixationEditModel, self).showRight():
            return True
        else:
            return False

    ##
    # Test whether the averaged fixations must be shown
    def showAvg(self):
        edit = self.getCurrentEdit()
        if not edit:
            return False

        if edit.avgfix and super(FixationEditModel, self).showAvg():
            return True
        else:
            return False

    ##
    # connect the fixation together to make a list of saccades
    #
    # The input fixations are strung together. Thereby a list of saccades
    # is generated. The Saccades will be formed by taking
    #
    # \param [in] fixations a list with fixations
    # \return     a list with saccades or an empty list if there are not enough
    #             fixations.
    @staticmethod
    def connectFixations(fixations):
        saccades = []
        for i in range(1, len(fixations)):
            first = fixations[i - 1]
            second = fixations[i]

            start = first.getEyeTime() + first.duration
            end = second.getEyeTime()
            x1, y1 = first.x, first.y
            x2, y2 = second.x, second.y
            et = first.getEntryType()
            if et == LogEntry.LFIX:
                et = LogEntry.LSAC
            elif et == LogEntry.RFIX:
                et = LogEntry.RSAC
            else:
                et = LogEntry.AVGSAC

            saccades.append(
                SaccadeEntry(et, start, end - start, x1, y1, x2, y2)
            )

        return saccades

    ##
    # Pushes initial edit to the stack
    def _pushInitialEdit(self):
        trial = self.getCurrentTrial()
        lfix = trial.loglfix
        rfix = trial.logrfix
        avgfix = trial.logavgfix
        lsac = trial.loglsac
        rsac = trial.logrsac
        avgsac = trial.logavgsac
        # if we don't have saccades we create them
        if not lsac and lfix:
            lsac = self.connectFixations(lfix)
        if not rsac and rfix:
            rsac = self.connectFixations(rfix)
        if not avgsac and avgfix:
            avgsac = self.connectFixations(avgfix)

        edit = FixationDataEdit(lfix,
                                rfix,
                                avgfix,
                                lsac,
                                rsac,
                                avgsac
                                )
        self.pushEdit(edit)

    ##
    # adds the current trial to the current experiment if there is a difference
    #
    # If edits were made to the current trial merge it with the current
    # experiment. In practice this means that we replace the fixation and
    # saccades for each eye with the saccades in the current edit.
    def addTrialToCurrentExperiment(self):
        data = self.getCurrentEdit()
        curtrial = self.getCurrentTrial()

        curtrial.loglfix = data.lfix
        curtrial.logrfix = data.rfix
        curtrial.logavgfix = data.avgfix
        curtrial.loglsac = data.lsac
        curtrial.logrsac = data.rsac
        curtrial.logavgsac = data.avgsac
        self._current_experiment.trials[self.trialindex] = curtrial

    ##
    # Tells which fixations should be visible on the screen
    #
    # \returns a list with those fixations or an empty list.
    def getVisible(self):
        visible = []
        if self.showLeft():
            visible += self.getCurrentEdit().lfix
        if self.showRight():
            visible += self.getCurrentEdit().rfix
        if self.showAvg():
            visible += self.getCurrentEdit().avgfix
        return visible

    ##
    # The edits are saved by pushing the edits on the stack
    #
    # Also the current trials is modified.
    #
    def saveEdit(self):
        if not self._selected:
            return  # nothing to save

        edit = copy.deepcopy(self.getCurrentEdit())
        x, y = self.getVector()
        for i in self._selected:
            translater = _TranslateFix(x, y, i)
            if edit.lfix:
                edit.lfix = list(map(translater, edit.lfix))
            if edit.rfix:
                edit.rfix = list(map(translater, edit.rfix))
            if edit.avgfix:
                edit.avgfix = list(map(translater, edit.avgfix))

        # also modify the selected.
        translater = _TranslateFix(x, y)
        list(map(translater, self._selected))
        if edit.lfix:
            edit.lsac = self.connectFixations(edit.lfix)
        if edit.rfix:
            edit.rsac = self.connectFixations(edit.rfix)
        if edit.avgfix:
            edit.avgsac = self.connectFixations(edit.avgfix)

        self.pushEdit(edit)

    ##
    # Selects the nearest fixation.
    #
    # \returns the nearest visible fixation or none
    def selectFixation(self, x, y):
        visible = self.getVisible()
        if not visible:
            return None
        visible.sort(key=_SortOnDistanceKey(x, y))
        return visible[0]

    ##
    # returns the current self._pixmap or None if it failed to load
    def getPixmap(self):
        return self._pixmap

    ##
    # maps a coordinate within the widget to a coordinate in the
    # in the coordinate system of the image.
    #
    # \param x[in] float of x coordinate
    # \param y[in] float of y coordinate
    # \returns tuple with a mapped x and y coordinate
    def mapMouseCoordinate(self, x, y):
        inverted, invertable = self._matrix.inverted()
        if not invertable:
            return None, None
        return inverted.map(x, y)


##
# A widget that draws fixations on a stimulus
#
class FixationUpdateCanvas(
        stimuluswidget.StimulusWidget,
        dataview.CustomDataView):

    ##
    # Inits a FixationUpdateCanvas
    def __init__(self, model, controller, parent=None):
        ## a FixationEditModel
        self.MODEL = model
        ## a FixationEditController
        self.controller = controller
        ## Contains different paths
        super(FixationUpdateCanvas, self).__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    ##
    # return self.MODEL
    #
    # our parent StimulusWidget needs this.
    def getModel(self):
        return self.MODEL

    ##
    # return self.controller
    #
    # our parent StimulusWidget needs this.
    def getController(self):
        return self.controller

    ##
    # onCustomPaint paint the fixations
    # and saccades in the current view
    def onCustomPaint(self, painter):

        red = QtGui.QColor(255, 0, 0, self.MODEL.fixalpha)
        blue = QtGui.QColor(0, 0, 255, self.MODEL.fixalpha)
        green = QtGui.QColor(0, 255, 0, self.MODEL.fixalpha)
        black = QtGui.QColor(0, 0, 0, self.MODEL.selalpha)

        edit = self.MODEL.getCurrentEdit()

        # enable anti aliasing of paths.
        painter.setRenderHint(painter.Antialiasing)
        if edit:
            if self.MODEL.showLeft():
                self._paintFixations(painter, edit.lfix, blue, black, True)
                self._paintSaccades(painter, edit.lsac, blue)
            if self.MODEL.showRight():
                self._paintFixations(painter, edit.rfix, red, black, True)
                self._paintSaccades(painter, edit.rsac, red)
            if self.MODEL.showAvg():
                self._paintFixations(painter, edit.avgfix, green, black, True)
                self._paintSaccades(painter, edit.avgsac, green)
            selected = self.MODEL.getSelected()
            if selected:
                x, y = self.MODEL.getVector()
                translator = _TranslateFix(x, y)
                translatedlist = list(
                    map(translator, copy.deepcopy(self.MODEL.getSelected()))
                )
                self._paintFixations(painter, translatedlist, black, black)
        else:
            pass
            # print self.onCustomPaint, "No edit"

    ##
    # Draws the circles and the letters for the fixations.
    def _paintFixations(
            self,
            painter,
            fixations,
            fill,
            line,
            draw_letter=False):
        n = 0
        RADIUS = min(self.height(), self.width()) / 50
        for i in fixations:
            n += 1
            radius = RADIUS
            x, y = i.x, i.y
            self._paintDot(painter, x, y, radius, fill, line)
            if draw_letter:
                self._writeFixation(painter, x, y, n, i.duration)

    ##
    # Paints the circles of the fixations.
    def _paintDot(self, painter, x, y, radius, fill, line):
        painter.save()
        painter.translate(x, y)
        path = QtGui.QPainterPath()
        path.moveTo(radius, 0)
        path.arcTo(-radius, -radius, radius * 2, radius * 2, 0, 360)
        painter.fillPath(path, fill)
        painter.strokePath(path, line)
        painter.restore()

    ##
    # Writes the number of the fixation
    # and the time of the fixation.
    def _writeFixation(self, painter, x, y, n, duration):
        nth = str(n)
        dur = str(int(round(duration)))
        col = QtGui.QColor(0, 0, 0,)
        painter.save()  # 1
        painter.translate(x, y)

        pathn = QtGui.QPainterPath()
        pathdur = QtGui.QPainterPath()

        font = QtGui.QFont()

        pathn.addText(0, 0, font, nth)
        pathdur.addText(0, 0, font, dur)

        r = pathn.boundingRect()
        painter.save()  # 2
        painter.translate(-r.width() / 2, 0)  # r.height()/2)
        painter.fillPath(pathn, col)
        painter.restore()  # 1

        r = pathdur.boundingRect()
        painter.save()  # 2
        painter.translate(-r.width() / 2, r.height())  # /2)
        painter.fillPath(pathdur, col)
        painter.restore()  # 1
        painter.restore()  # 0

    ##
    # Draws the lines of all saccades
    def _paintSaccades(self, painter, saccades, color):
        if saccades:
            painter.save()
            pen = QtGui.QPen(color)
            painter.setPen(pen)
            for sac in saccades:
                p1 = QtCore.QPoint(sac.xstart, sac.ystart)
                p2 = QtCore.QPoint(sac.xend, sac.yend)
                painter.drawLine(p1, p2)
            painter.restore()

    ##
    # Handles mouse press event
    def mousePressEvent(self, event):
        self.controller.mousePress(event)
        return super(FixationUpdateCanvas, self).mousePressEvent(event)

    ##
    # Handles a mouse release
    def mouseReleaseEvent(self, event):
        self.controller.mouseRelease(event)
        super(FixationUpdateCanvas, self).mouseReleaseEvent(event)
        self.updateFromModel()

    ##
    # Handles a mouse move event.
    def mouseMoveEvent(self, event):
        self.controller.dragEvent(event)
        super(FixationUpdateCanvas, self).mouseMoveEvent(event)
        self.updateFromModel()

    ##
    # Paint the stimulus fixations and edit all shizzle.
    def updateFromModel(self):
        self.repaint()
        # draw fixations and selections here

    def sizeHint(self):
        return QtCore.QSize(int(1920 * .75), int(1080 * .75))


##
# A FixationEditCustomView allows editting of fixations.
#
# The view contains a box with on the left hand side a
# widget that contains the editor view where the user
# can select fixations. The right hand plane contains
# the settings of all fixations and additional information.
#
class FixationEditCustomView(QtWidgets.QWidget, dataview.CustomDataView):

    def __init__(self, model, controller):
        super(FixationEditCustomView, self).__init__()
        ## a FixationEditModel
        self.MODEL = model
        ## a FixationEditController
        self._controller = controller
        self._initGui()

    def _initGui(self):
        box = QtWidgets.QVBoxLayout()
        self.fixationcanvas = FixationUpdateCanvas(
            self.MODEL,
            self._controller
        )
        box.addWidget(self.fixationcanvas)

        self.setLayout(box)

    def updateFromModel(self):
        self.fixationcanvas.updateFromModel()


##
# Simple class that just creates it's own custom_widget
#
# The custom_widget of this DataView allows edditing of fixations.
class FixationEditView(dataview.EditDataView):

    def initCustomWidget(self):
        ## The custom widget a gui.FixationUpdateCanvas
        self.custom_widget = FixationUpdateCanvas(self.MODEL, self.controller)

    ##
    # handles Keypresses
    #
    # Currently the widget accepts:
    # # Ctrl+a  select all (visible) fixations
    # # all other options in dataview.EditDataView
    def keyPressEvent(self, event):
        handled = False
        if event.modifiers() == QtCore.Qt.ControlModifier:
            handled = True
            if event.key() == QtCore.Qt.Key_A:
                self.controller.selectAll()
            else:
                handled = False

        if handled:
            self.updateFromModel()
        else:
            super(FixationEditView, self).keyPressEvent(event)
