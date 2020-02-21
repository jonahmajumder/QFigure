from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
import numpy as np

from QFigure import QFigure

import matplotlib

def printmethods(item):
	[print(m) for m in dir(item) if not m.startswith('_')]

app = QApplication([])
window = QWidget()

layout = QVBoxLayout()

figWidget = QFigure()

def genFcn():
	data = np.random.random(10)
	figWidget.cleardata()
	figWidget.plot(np.random.random(10)-.5, np.random.random(10)-.5)

timer = QTimer()
timer.timeout.connect(genFcn)
genFcn()
# timer.start(500)

p = figWidget.axes.findobj(lambda a: a.pickable())

layout.addWidget(figWidget)
window.setLayout(layout)
window.show()

if __name__ == '__main__':
	app.exec_()
