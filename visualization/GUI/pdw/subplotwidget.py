from tkinter.messagebox import NO
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QScrollArea, QAction, QMenu, QActionGroup, QApplication
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from visualization.GUI.customnavigationtoolbar import MyCustomToolbar as NavigationToolbar
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from matplotlib.widgets import RectangleSelector
from matplotlib.figure import Figure
from PyQt5.QtGui import QIcon, QCursor
from visualization.GUI.pdw.historicalzoom import HistoricalZoom
from matplotlib.widgets import MultiCursor


from visualization.visualizationparams import ShowPolicy



class SubPlotWidget(QWidget):
    selectionRangeHasBeenSet = pyqtSignal(str, tuple, tuple)
    # selectionRangeHasBeenSet = pyqtSignal(tuple)
    unselectAllRequested = pyqtSignal()
    unselectSpecialArea = pyqtSignal(tuple)
    forwardZoomRequested = pyqtSignal()
    backeardZoomRequested = pyqtSignal()
    resetZoomRequested = pyqtSignal()


    def __init__(self):
        QWidget.__init__(self)
        self.setLayout(QHBoxLayout())

        # variables
        self.mouse_press_ev = None
        self.channel_plot_size = 200
        self.selection_area = []
        # self.selection_area_y = (-1, -1)
        self.show_policy = ShowPolicy.scroll

        # setup figure
        self.fig = Figure()
        self.fig.patch.set_color('#151a1e')
        self.fig.subplots_adjust(left=0.061, bottom=0.06, right=0.9980, top=0.98, wspace=0, hspace=0.1)
        self.fig.tight_layout()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.draw()

        # setup hist figure
        self.hist_fig = Figure()
        self.hist_fig.patch.set_color('#151a1e')
        self.hist_fig.subplots_adjust(left=0.061, bottom=0.06, right=0.9980, top=0.98, wspace=0, hspace=0.1)
        self.hist_fig.tight_layout()
        self.hist_canvas = FigureCanvas(self.hist_fig)
        self.hist_canvas.draw()

        # navtollbar
        self.mpl_toolbar = NavigationToolbar(self.canvas, None)
        # self.canvas.mpl_connect('release_zoom', self.handle_release_zoom)
        self.historical_zoom = HistoricalZoom(self.fig)


        # menu items
        self.available_action = []
        self.canvasMenu = QMenu(self)

        # creating QAction Instances
        self.lineMarkerAction = QAction("Line Marker", self)
        self.pointMarkerAction = QAction("Point Marker", self)
        # self.zoomAction = QAction("Zoom", self)
        # self.dragAction = QAction("Drag", self)
 
        # making actions checkable
        self.lineMarkerAction.setCheckable(True)
        self.pointMarkerAction.setCheckable(True)
        # self.zoomAction.setCheckable(True)
        # self.dragAction.setCheckable(True)
        # self.normalAction.setChecked(True)
 
        # adding these actions to the selection menu
        self.canvasMenu.addAction(self.lineMarkerAction)
        self.canvasMenu.addAction(self.pointMarkerAction)
        # self.canvasMenu.addAction(self.zoomAction)
        # self.canvasMenu.addAction(self.dragAction)
 
        # creating a action group
        action_group = QActionGroup(self)
 
        # adding these action to the action group
        action_group.addAction(self.lineMarkerAction)
        action_group.addAction(self.pointMarkerAction)
        # action_group.addAction(self.zoomAction)
        # action_group.addAction(self.dragAction)


 
        self.canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self.exec_canvas_menu)

        self.scroll = QScrollArea(self)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.plot_container = QWidget()
        layout = QHBoxLayout(self.plot_container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.hist_canvas.setMaximumWidth(150)
        layout.addWidget(self.canvas)
        layout.addWidget(self.hist_canvas)       
        self.scroll.setWidget(self.plot_container)

        self.layout().addWidget(self.scroll)

        # list to store the axis last used with a mouseclick
        self.curr_ax = []
        self.list_of_select_box = []


        self.setup_connections()

    def setup_connections(self):
        self.forwardZoomRequested.connect(self.historical_zoom.next_range)
        self.backeardZoomRequested.connect(self.historical_zoom.previous_range)
        self.resetZoomRequested.connect(self.historical_zoom.reset)
        # action connections
        self.lineMarkerAction.triggered.connect(self.setup_line_marker)
        # self.selectAction.triggered.connect(self.enable_select_action)
        # self.zoomAction.triggered.connect(self.enable_zoom_action)
        # self.dragAction.triggered.connect(self.enable_pan_action)

    def enable_select_action(self, active):
        # self.selectAction.setChecked(active)
        if active:
            self.canvas.setCursor(QCursor(Qt.PointingHandCursor))
            if self.historical_zoom.is_active:
                self.historical_zoom.activate(False)
            if self.mpl_toolbar.is_pan():
                self.mpl_toolbar.pan(False)
            [rect.set_active(True) for rect in self.list_of_select_box]
            self.mouse_press_ev = self.canvas.mpl_connect('button_press_event', self.on_mouse_click)

        else:
            self.canvas.setCursor(QCursor(Qt.ArrowCursor))
            [rect.set_active(False) for rect in self.list_of_select_box]
            self.canvas.mpl_disconnect(self.mouse_press_ev)
    
    def enable_normal_action(self, active):
        if active:
            self.enable_select_action(False)
            if self.mpl_toolbar.is_zoom():
                self.mpl_toolbar.zoom(False)
            if self.mpl_toolbar.is_pan():
                self.mpl_toolbar.pan(False)

    def enable_zoom_action(self, active):
        if active:
            self.enable_select_action(False)
            self.enable_select_action(False)
            if self.mpl_toolbar.is_pan():
                self.mpl_toolbar.pan(False)
        self.canvas.setCursor(QCursor(Qt.CrossCursor))
        self.zoomAction.setChecked(active)
        self.historical_zoom.activate(active)
    
    def enable_pan_action(self, active):
        self.dragAction.setChecked(active)
        self.mpl_toolbar.pan(active)

    def on_mouse_click(self, event):
        if event.inaxes:
            if event.button == MouseButton.LEFT:
                self.curr_ax[:] = [event.inaxes]
            if event.dblclick:
                self.unselectAllRequested.emit()

    def onselect(self, eclick, erelease):
        label = (((self.curr_ax[:])[-1].get_ylabel()).split('('))[0]
        pre_coor = (eclick.xdata, eclick.ydata)
        rel_coor = (erelease.xdata, erelease.ydata)
        if eclick.button == MouseButton.LEFT and erelease.button == MouseButton.LEFT:
            self.selection_area.append((pre_coor[0], rel_coor[0]))
            self.selectionRangeHasBeenSet.emit(label ,(pre_coor[0], rel_coor[0]), (pre_coor[1], rel_coor[1]))
        elif eclick.button == MouseButton.RIGHT and erelease.button == MouseButton.RIGHT:
            f_point = eclick.xdata
            l_point = erelease.xdata
            m_point = (erelease.xdata - eclick.xdata)/2
            for area in self.selection_area:
                if (f_point >= area[0] and f_point <= area[1]) or (l_point >= area[0] and l_point <= area[1]) or (m_point >= area[0] and m_point <= area[1]):
                    self.selection_area.remove(area)
                    self.unselectSpecialArea.emit(area)
                    break

    def get_figure(self):
        return self.fig

    def get_nav_tool(self):
        return self.mpl_toolbar

    def get_hist_figure(self):
        return self.hist_fig

    @pyqtSlot()
    def setup_rect(self):
        if self.fig.axes:
            self.list_of_select_box = [RectangleSelector(
                ax,
                self.onselect,
                drawtype='box',
                useblit=True,
                button=[1,3],
                minspanx=5, minspany=5,
                spancoords='pixels',
                interactive=False,
            ) for ax in self.fig.axes]
            [rect.set_active(False) for rect in self.list_of_select_box]
        self.historical_zoom.setup_rect()

    def set_fig_size(self):
        if self.show_policy == ShowPolicy.scroll:
            number_of_channels = len(self.fig.axes)
            self.plot_container.setMinimumHeight(number_of_channels*self.channel_plot_size)
            self.plot_container.setMaximumHeight(number_of_channels*self.channel_plot_size) 
        elif self.show_policy == ShowPolicy.non_scroll:
            widget_size = self.parentWidget().size()
            self.plot_container.setMinimumHeight(widget_size.height())
            self.plot_container.setMaximumHeight(widget_size.height()) 

    def exec_canvas_menu(self, point):
        self.last_point = point
        self.canvasMenu.exec_(self.canvas.mapToGlobal(point))

    def clear(self):
        self.fig.clear()
        self.hist_fig.clear()
        self.curr_ax = []
        self.list_of_select_box = []
        self.canvas.draw()
        self.hist_canvas.draw()

    def has_selected_area(self):
        return len(self.selection_area)

    def clear_selection_area(self):
        self.selection_area.clear()

    def set_show_policy(self, policy):
        if self.show_policy != policy:
            self.show_policy = policy
            self.set_fig_size()

    @pyqtSlot()
    def setup_line_marker(self):
        self.line_cursor = MultiCursor(self.canvas, tuple(self.fig.axes), color = 'r', lw=1,horizOn=False, vertOn=True, linestyle='--', useblit=True)
        self.line_cursor.set_active(False)

    @pyqtSlot(bool)
    def activate_line_marker(self, active):
        if active:
            self.line_cursor.set_active(True)
            self.point_marker.set_active(False)
            self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        else:
            self.line_cursor.set_active(False)
        self.canvas.flush_events()
        self.canvas.draw()

    @pyqtSlot()
    def setup_point_marker(self):
        self.point_marker = MultiCursor(self.canvas, tuple(self.fig.axes), color = 'r', lw=1,horizOn=True, vertOn=True, linestyle='--', useblit=True)
        self.point_marker.set_active(False)

    @pyqtSlot(bool)
    def activate_point_marker(self, active):
        if active:
            self.point_marker.set_active(True)
            self.line_cursor.set_active(False)
        else:
            self.point_marker.set_active(False)
        self.canvas.flush_events()
        self.canvas.draw()

    def on_mouse_move(self, event):
        if self.line_cursor.active and event.inaxes in self.fig.axes:
            print(event.xdata)






