import sys, os
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

import matplotlib
matplotlib.rcParams['axes.autolimit_mode'] = 'round_numbers'

from math import log10, floor
from time import sleep

class QFigure(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        super(QFigure, self).__init__()

        self.canvas = FigureCanvas(Figure())

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.canvas)

        self.Figure = self.canvas.figure
        self.axes = self.Figure.add_subplot(111)

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

    def clear_pickable(self):
        for t in self.axes.findobj(lambda a: a.pickable()):
            t.set_picker(None)
            t.set_gid(None)

        self.pickableTicks = []

    def pickFilter(self, event):
        # print('Artist: {}'.format(event.artist))
        # print('GID: {}'.format(event.artist.get_gid()))
        # print(event.mouseevent)

        if event.artist.get_gid() in range(4):
            if event.mouseevent.dblclick:
                self.editLimit(event.artist)

    def editLimit(self, label):
        self.showLineEdit(label)
        self.drawnow()

    def showLineEdit(self, label):
        [t.label.set_visible(True) for t in self.pickableTicks]

        tickbbox = label.get_window_extent()
        # print(tickbbox)
        canvas_geometry = self.canvas.geometry()

        editbbox = [
            canvas_geometry.left() + tickbbox.x0,
            canvas_geometry.bottom() - tickbbox.y1,
            tickbbox.x1 - tickbbox.x0,
            tickbbox.y1 - tickbbox.y0
        ]

        current = label.get_text()
        label.set_visible(False)

        if not hasattr(self, 'limEditor'):
            self.makeLineEdit()

        self.limEditor.setText(current)
        self.limEditor.setCursorPosition(len(current))
        self.limEditor.selectAll()
        self.limEditor.setGeometry(*editbbox)
        self.limEditor.editingFinished.connect(self.hideLineEditor)
        self.limEditor.show()
        # self.limEditor.hide() # can later hide it

    def hideLineEditor(self):
        self.limEditor.hide()
        [t.label.set_visible(True) for t in self.pickableTicks]
        self.drawnow()

    def makeLineEdit(self):
        # things to do only first time
        fontname = matplotlib.rcParams['font.family'][0]
        fontsize = matplotlib.rcParams['font.size']
        bold = QtGui.QFont.Bold
        qfont = QtGui.QFont(fontname, fontsize) # can use bold as 3rd arg
        self.limEditor = QtWidgets.QLineEdit(self)
        self.limEditor.hide()
        self.limEditor.setFont(qfont)
        self.limEditor.setFrame(False)

        # set up callback?

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


