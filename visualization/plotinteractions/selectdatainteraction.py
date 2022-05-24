from visualization.plotinteractions.baseinteraction import BaseInteraction
from matplotlib.widgets import RectangleSelector
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject


class SelectOnBox(BaseInteraction, QObject):
    resultIsReady = pyqtSignal(int, int)

    def __init__(self, figure=None):
        super(SelectOnBox, self).__init__(figure)
        super(QObject, self).__init__()

        for ax in self.figure.get_axes():
            self.rect = RectangleSelector(ax, self.line_select_callback,
                                          drawtype='box', useblit=True,
                                          button=[3],  # don't use middle button
                                          minspanx=5, minspany=5,
                                          spancoords='pixels',
                                          interactive=False,
                                          rectprops=dict(facecolor="red", edgecolor="black", alpha=0.2, fill=True))

        self._connect('button_press_event', self.toggle_selector)

    def line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.resultIsReady.emit(x1, x2)

    def toggle_selector(self, event):
        if event.key in ['Q', 'q'] and self.rect.active:
            self.rect.set_active(False)
        if event.key in ['A', 'a'] and not self.rect.active:
            self.rect.set_active(True)
