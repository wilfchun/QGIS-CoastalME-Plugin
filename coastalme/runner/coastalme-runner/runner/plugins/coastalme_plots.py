import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

preferred_style = 'seaborn-v0_8-whitegrid'
if preferred_style in plt.style.available:
    plt.style.use(preferred_style)


class PlotWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)

        self.figure = Figure(figsize=(5, 3))
        try:
            self.figure.set_layout_engine('tight')
        except AttributeError:
            # This can happen depending on version
            pass
        self.canvas = FigureCanvas(self.figure)
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        layout.addWidget(NavigationToolbar(self.canvas, self))
        layout.addWidget(self.canvas)


class StaticPlot(PlotWindow):
    def __init__(self):
        super(StaticPlot, self).__init__()

        self._static_ax = self.canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self._static_ax.plot(t, np.tan(t), ".")


class VolumePlot(PlotWindow):
    def __init__(self):
        super(VolumePlot, self).__init__()

        self.rs_times = []
        self.rs_volIn = []
        self.rs_volOut = []

        self.ax = self.canvas.figure.subplots()
        self.ln = self.ax.plot(self.rs_times,
                               self.rs_volIn)

    def update(self, rs_times, rs_volIn, rs_volOut):
        self.rs_times = rs_times
        self.rs_volIn = rs_volIn
        self.rs_volOut = rs_volOut
        # This sometimes generates a blank plot
        # self.canvas.figure.clear()
        self.ax.cla()
        self.ax.plot(self.rs_times,
                     self.rs_volIn,
                     'g',
                     label='Vol-In',
                     )
        self.ax.plot(self.rs_times,
                     self.rs_volOut,
                     'b',
                     label='Vol-Out',
                     )
        self.ax.relim()
        self.ax.legend()
        self.canvas.draw()
