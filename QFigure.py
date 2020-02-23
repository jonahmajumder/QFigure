import sys, os
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

import matplotlib
matplotlib.rcParams['axes.autolimit_mode'] = 'round_numbers'

import os
from math import log10, floor
from time import sleep

FLOAT_RE = "[-+]?(\\d+(\\.\\d*)?|\\.\\d+)([eE][-+]?\\d+)?"

class QFigure(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        super(QFigure, self).__init__()

        self.canvas = FigureCanvas(Figure())

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.canvas)

        self.Figure = self.canvas.figure
        self.dpiscaling = 100.0 / self.Figure.dpi
        self.axes = self.Figure.add_subplot(111)
        self.axes_class = type(self.axes)

        self.xlabel = kwargs.get('xlabel', '')
        self.ylabel = kwargs.get('ylabel', '')

        self.makeLineEdit()
        self.make_pickable(None)

        self.canvas.mpl_connect('draw_event', self.make_pickable)
        self.canvas.mpl_connect('resize_event', self.make_pickable)

        self.canvas.mpl_connect('pick_event', self.pickFilter)

    def make_pickable(self, event):
        self.clear_pickable()

        xticks = self.axes.get_xaxis().get_major_ticks()
        yticks = self.axes.get_yaxis().get_major_ticks()

        self.pickableTicks = [xticks[0], xticks[-1], yticks[0], yticks[-1]]

        for (i, tick) in enumerate(self.pickableTicks):
            tick.label.set_picker(True)
            tick.label.set_gid(i)

        self.axes.set_picker(True)


    def clear_pickable(self):
        for t in self.axes.findobj(lambda a: a.pickable()):
            t.set_picker(None)
            t.set_gid(None)

        self.pickableTicks = []

    def pickFilter(self, event):
        # print('Artist: {}'.format(type(event.artist)))
        # print('GID: {}'.format(event.artist.get_gid()))

        if isinstance(event.artist, matplotlib.text.Text) and event.mouseevent.dblclick:
                self.editLimit(event.artist)
        if isinstance(event.artist, self.axes_class):
            if hasattr(self, 'limEditor'):
                self.doneEditing()

    def editLimit(self, label):
        self.showLineEdit(label)
        self.drawnow()

    def showLineEdit(self, label):
        [t.label.set_visible(True) for t in self.pickableTicks]

        tickbbox = label.get_window_extent()
        # print(tickbbox)
        canvas_geometry = self.canvas.geometry()

        editbbox = [
            canvas_geometry.left() + round(tickbbox.xmin * self.dpiscaling),
            canvas_geometry.bottom() - round(tickbbox.ymax * self.dpiscaling),
            round(tickbbox.width * self.dpiscaling),
            round(tickbbox.height * self.dpiscaling)
        ]
        
        # hardcoded 
        editbbox[0] -= 1
        editbbox[2] += 4

        # print(editbbox)

        self.editing = label
        self.old_lim = self.editing.get_text().replace(chr(8722), '-')
        self.editing.set_visible(False)

        if not hasattr(self, 'limEditor'):
            self.makeLineEdit()

        self.limEditor.setText(self.old_lim)
        self.limEditor.setCursorPosition(len(self.old_lim))
        # self.limEditor.selectAll()
        self.limEditor.setGeometry(*editbbox)
        self.limEditor.editingFinished.connect(self.doneEditing)
        self.limEditor.show()
        # self.limEditor.hide() # can later hide it

    def makeLineEdit(self):
        # things to do only first time

        bold = QtGui.QFont.Bold
        qfont = QtGui.QFont("DejaVu Sans", 13) # can use bold as 3rd arg

        self.limEditor = QtWidgets.QLineEdit(self)
        self.limEditor.hide()
        self.limEditor.setAlignment(QtCore.Qt.AlignCenter)
        self.limEditor.setFont(qfont)
        self.limEditor.setFrame(False)
        reval = QtGui.QRegExpValidator(QtCore.QRegExp(FLOAT_RE))
        self.limEditor.setValidator(reval)

    def doneEditing(self):
        if hasattr(self, 'editing'):
            newval = float(self.limEditor.text())
            changed = float(self.old_lim) != newval
            if changed:
                self.changeLimit(self.editing.get_gid(), newval)

        self.limEditor.hide()
        [t.label.set_visible(True) for t in self.pickableTicks]
        self.drawnow()

    def changeLimit(self, gid, newval):
        fcnDict = [
            lambda val: self.axes.set_xlim(val, self.axes.get_xlim()[1]),
            lambda val: self.axes.set_xlim(self.axes.get_xlim()[0], val),
            lambda val: self.axes.set_ylim(val, self.axes.get_ylim()[1]),
            lambda val: self.axes.set_ylim(self.axes.get_ylim()[0], val),
        ]
        fcnDict[gid](newval)
        self.drawnow()


    def plot(self, *args, **kwargs):
        self.axes.plot(*args, **kwargs)
        self.axes.margins(0, tight=False)
        self.drawnow()

    def cleardata(self):
        self.axes.clear()

    @property
    def xlabel(self):
        return self.__xlabel

    @xlabel.setter
    def xlabel(self, newlabel):
        self.axes.set_xlabel(newlabel)
        self.__xlabel = self.axes.get_xlabel()
        self.drawnow()

    @property
    def ylabel(self):
        return self.__ylabel

    @ylabel.setter
    def ylabel(self, newlabel):
        self.axes.set_ylabel(newlabel)
        self.__ylabel = self.axes.get_ylabel()
        self.drawnow()

    def drawnow(self):
        self.canvas.draw()


