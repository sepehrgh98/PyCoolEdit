from plotinteractions.baseinteraction import BaseInteraction
from PyQt5.QtCore import pyqtSignal


class DragMove(BaseInteraction):
    mouse_pressed = pyqtSignal('double', 'double')

    def __init__(self, figure=None):
        super(DragMove, self).__init__(figure)
        self._connect('button_press_event', self._on_mouse_pressed)
        self._connect('button_release_event', self._on_mouse_released)
        self._connect('motion_notify_event', self._on_mouse_move)

    def _on_mouse_pressed(self, event):
        # Go through all axes to enable zoom for multiple axes subplots
        x_axes, y_axes = self._axes_to_update(event)

        for ax in x_axes:
            transform = ax.transData.inverted()
            xdata, ydata = transform.transform_point((event.x, event.y))
            self.mouse_pressed.emit(xdata, ydata)

    def _on_mouse_released(self, event):
        pass

    def _on_mouse_move(self, event):
        pass
