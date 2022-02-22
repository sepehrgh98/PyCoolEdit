import matplotlib
from matplotlib.figure import Figure
from plotinteractions.scrollzoominteraction import ZoomOnWheel
from plotinteractions.mousedraginteraction import DragMove

matplotlib.use("Qt5Agg")


class VisualizationPlot(Figure):
    def __init__(self):
        super(VisualizationPlot, self).__init__()
        self.zoomInteraction = None
        self.dragMoveInteraction = None

    def set_zoom_on_wheel_interaction(self, active):
        if active:
            self.zoomInteraction = ZoomOnWheel(self)
        else:
            if self.zoomInteraction:
                self.zoomInteraction.disconnect()

    def set_drag_interaction(self, active):
        if active:
            self.dragMoveInteraction = DragMove(self)
        # else:
        #     if self.dragMoveInteraction:
        #         self.dragMoveInteraction.disconnect()
