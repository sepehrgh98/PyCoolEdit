from PyQt5.QtWidgets import QWidget, QHBoxLayout, QScrollArea
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt, pyqtSignal
from matplotlib.widgets import RectangleSelector


class SubPlotWidget(QWidget):
    selectionRangeHasBeenSet = pyqtSignal(tuple, tuple)

    def __init__(self, fig):
        QWidget.__init__(self)
        self.setLayout(QHBoxLayout())

        # setup figure
        self.fig = fig
        self.fig.patch.set_color('#151a1e')
        self.fig.subplots_adjust(left=0.061, bottom=0.007, right=0.9980, top=0.993, wspace=0, hspace=0.2)
        self.fig.tight_layout()

        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()

        self.navbar = NavigationToolbar(self.canvas, self)

        self.scroll = QScrollArea(self)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.canvas)
        self.layout().addWidget(self.scroll)

        # list to store the axis last used with a mouseclick
        self.curr_ax = []
        self.list_of_select_box = []

    def enable_select_action(self):
        if self.fig.axes:
            self.list_of_select_box = [RectangleSelector(
                ax,
                self.onselect,
                drawtype='box',
                useblit=True,
                button=[1, 3],  # disable middle button
                minspanx=5, minspany=5,
                spancoords='pixels',
                interactive=False,
            ) for ax in self.fig.axes]
            self.canvas.mpl_connect('button_press_event', self.on_mouse_press)

    def on_mouse_press(self, event):
        if event.inaxes:
            self.curr_ax[:] = [event.inaxes]

    def onselect(self, eclick, erelease):
        pre_coor = self.curr_ax[:][0].transData.inverted().transform((eclick.x, eclick.y))
        rel_coor = self.curr_ax[:][0].transData.inverted().transform((erelease.x, erelease.y))
        self.selectionRangeHasBeenSet.emit((pre_coor[0], rel_coor[0]), (pre_coor[1], rel_coor[1]))

    def get_canvas(self):
        return self.canvas

    def get_nav_tool(self):
        return self.navbar
