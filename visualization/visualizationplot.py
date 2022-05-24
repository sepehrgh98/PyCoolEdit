import matplotlib
from matplotlib.figure import Figure
from visualization.plotinteractions.scrollzoominteraction import ZoomOnWheel
from visualization.plotinteractions.boxzoominteraction import ZoomOnBox
from visualization.plotinteractions.mousedraginteraction import PanAndZoom
from visualization.plotinteractions.doubleclickinteraction import DoubleClick
from visualization.plotinteractions.selectdatainteraction import SelectOnBox
from PyQt5.QtCore import pyqtSlot

matplotlib.use("Qt5Agg")


class VisualizationPlot(Figure):
    def __init__(self, *args, **kwargs):
        super(VisualizationPlot, self).__init__(*args, **kwargs)

        self.zoomOnWheelInteraction = None
        self.zoomOnBoxInteraction = None
        self.selectInteraction = None
        self.doubleClickInteraction = None
        self.dragMoveInteraction = None

    def set_zoom_on_wheel_interaction(self, active):
        if active:
            self.zoomOnWheelInteraction = ZoomOnWheel(self)
        # else:
        #     if self.zoomInteraction:
        #         self.zoomInteraction.disconnect()

    def set_zoom_on_box_interaction(self, active):
        if active:
            self.zoomOnBoxInteraction = ZoomOnBox(self)
        # else:
        #     if self.zoomInteraction:
        #         self.zoomInteraction.disconnect()

    def set_select_interaction(self, active):
        if active:
            self.selectInteraction = SelectOnBox(self)
            # self.selectInteraction.resultIsReady.connect(self.handle_selection_interaction)
        # else:
        #     if self.zoomInteraction:
        #         self.zoomInteraction.disconnect()

    def set_double_click_interaction(self, active):
        if active:
            self.doubleClickInteraction = DoubleClick(self)

    def set_drag_interaction(self, active):
        if active:
            self.dragMoveInteraction = PanAndZoom(self)
        # else:
        #     if self.dragMoveInteraction:
        #         self.dragMoveInteraction.disconnect()

    @pyqtSlot(int, int)
    def handle_selection_interaction(self, x1, x2):
        print(x1, x2)
