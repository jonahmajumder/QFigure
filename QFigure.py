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

        self.make_pickable(None)

        self.canvas.mpl_connect('draw_event', self.make_pickable)
        self.canvas.mpl_connect('resize_event', self.make_pickable)

        self.canvas.mpl_connect('pick_event', self.pickFilter)

    def make_pickable(self, event):
        self.clear_pickable()

        xticks = self.axes.get_xaxis().get_major_ticks()
        yticks = self.axes.get_yaxis().get_major_ticks()

        for (i, tick) in enumerate([xticks[0], xticks[-1], yticks[0], yticks[-1]]):
            tick.label.set_picker(True)
            tick.label.set_gid(i)

    def clear_pickable(self):
        for t in self.axes.findobj(lambda a: a.pickable()):
            t.set_picker(None)
            t.set_gid(None)

    def pickFilter(self, event):
        # print('Artist: {}'.format(event.artist))
        # print('GID: {}'.format(event.artist.get_gid()))
        # print(event.mouseevent)

        if event.mouseevent.dblclick:
            self.editLimit(event.artist)

    def editLimit(self, label):
        if not label.get_gid() in range(4):
            return

        # print(label.get_fontsize())
        # print(label.get_fontname())

        self.makeLineEdit(label)

        self.drawnow()

    def makeLineEdit(self, label):

        bbox = label.get_window_extent()
        label.set_visible(False)

        self.limEditor = QtWidgets.QLineEdit(self.parent())
        # self.limEditor.setGeometry(bbox.x0, bbox.y0, bbox.x1, bbox.y1)

        # self.limEditor.setTextMargins(bbox.x0)


    # def mousePressEvent(self, event):
    #     print('Mouse Event')
    #     if event.button() == QtCore.Qt.LeftButton:
    #         print("Left Button Clicked")
    #     elif event.button() == QtCore.Qt.RightButton:
    #         print("Right Button Clicked")

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


