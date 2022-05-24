from visualization.plotinteractions.baseinteraction import BaseInteraction
from matplotlib.widgets import RectangleSelector
from matplotlib.backend_bases import MouseButton


class ZoomOnBox(BaseInteraction):

    def __init__(self, figure=None):
        super(ZoomOnBox, self).__init__(figure)

        for ax in self.figure.get_axes():
            self.rect = RectangleSelector(ax, self.line_select_callback,
                                          drawtype='box', useblit=True,
                                          button=[1],  # don't use middle button
                                          minspanx=5, minspany=5,
                                          spancoords='pixels',
                                          interactive=False,
                                          rectprops=dict(facecolor="blue", edgecolor="black", alpha=0.2, fill=True))

        self._connect('button_press_event', self.toggle_selector)

    def line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        if eclick.button == MouseButton.LEFT and erelease.button == MouseButton.LEFT:
            for ax in self.figure.get_axes():
                ax.set_xlim(x1, x2)
                ax.set_ylim(y1, y2)
            self._draw()

    def toggle_selector(self, event):
        if event.key in ['Q', 'q'] and self.rect.active:
            self.rect.set_active(False)
        if event.key in ['A', 'a'] and not self.rect.active:
            self.rect.set_active(True)
