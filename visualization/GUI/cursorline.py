import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt



class CursorLine(QObject):
    """
    A cross hair cursor.
    """
    data_selected = pyqtSignal(np.double)
    def __init__(self, ax, mood):
        super(CursorLine, self).__init__()
        self.ax = ax
        self.fig = ax.figure
        self.mood = mood
        self.line = None
        self.move_ev = None
        self.last_data = None
        if self.mood == "h":
            self.line = ax.axhline(color='g', lw=1.2, ls='-')
        elif self.mood == "v":
            self.line = ax.axvline(color='g', lw=1.2, ls='-')

        self.move_ev = self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)



    def set_cross_hair_visible(self, visible):
        need_redraw = self.line.get_visible() != visible
        self.line.set_visible(visible)
        return need_redraw

    def on_mouse_move(self, event):
        if not event.inaxes:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.draw()
        else:
            self.set_cross_hair_visible(True)
            x, y = event.xdata, event.ydata
            # update the line positions
            if self.mood == "h":
               self.line.set_ydata(y)
            elif self.mood == "v":
                self.line.set_xdata(x)

            self.fig.canvas.draw()

    def on_mouse_pressed(self, event):
        if event.inaxes == self.ax:
            self.move_ev = self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def on_mouse_released(self, event):
        self.fig.canvas.mpl_disconnect(self.move_ev)
        pre_coor = self.ax.transData.inverted().transform((event.x, event.y))
        if self.mood == "h":
            # self.data_selected.emit(event.x)
            self.last_data = round(pre_coor[1],2)
        elif self.mood == "v":
            # self.data_selected.emit(event.y)
            self.last_data = round(pre_coor[0],2)
        self.data_selected.emit(self.last_data)


    def get_last_data(self):
        return self.last_data
        
        

    def set_pos(self, val):
        if self.mood == "h":
            self.line.set_ydata(val)
        elif self.mood == "v":
            self.line.set_xdata(val)


if __name__ == "__main__":
    x = np.arange(0, 1, 0.01)
    y = np.sin(2 * 2 * np.pi * x)

    fig, ax = plt.subplots(2)
    ax[0].set_title('Simple cursor')
    ax[0].plot(x, y, 'o')
    cursor = CursorLine(ax[0], "h")
    fig.canvas.mpl_connect('button_press_event', cursor.on_mouse_pressed)
    fig.canvas.mpl_connect('button_release_event', cursor.on_mouse_released)
    plt.show()
