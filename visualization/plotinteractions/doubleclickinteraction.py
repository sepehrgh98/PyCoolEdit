from visualization.plotinteractions.baseinteraction import BaseInteraction


class DoubleClick(BaseInteraction):
    def __init__(self, figure=None):
        super(DoubleClick, self).__init__(figure)
        self._connect('button_press_event', self._on_mouse_press)

    def _on_mouse_press(self, event):
        if event.dblclick:
            pass
