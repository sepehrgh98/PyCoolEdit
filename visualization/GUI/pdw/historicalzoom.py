from PyQt5.QtCore import  QThread, QObject, pyqtSignal
from matplotlib.widgets import RectangleSelector

class HistoricalZoom(QObject):
# class HistoricalZoom:
    zoom_requested = pyqtSignal(str,tuple,tuple)
    def __init__(self, fig, target_ax = None) -> None:
        super(HistoricalZoom, self).__init__()
        self.fig = fig
        self.target_ax = target_ax
        self.is_active = False
        self.curr_ax = []
        self.list_of_zoom_box = []
        self.history = [] # list of tuple;(x_range, y_range)
        self.current_range_index = 0
        self.first_zoom = True
        self.original_range = None

        # moving to thread
        self.objThread = QThread(self)
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()


    def setup_rect(self):
        if self.fig.axes:
            self.list_of_zoom_box = [RectangleSelector(
                ax,
                self.on_zoom_dragged,
                drawtype='box',
                useblit=True,
                button=[1],
                minspanx=1, minspany=1,
                spancoords='data',
                interactive=False,
                rectprops = dict(facecolor='blue', edgecolor = 'black',
                 alpha=0.2, fill=True)
            ) for ax in self.fig.axes]
            [rect.set_active(False) for rect in self.list_of_zoom_box]
            self.mouse_press_ev = self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        

    def activate(self, active):
        [rect.set_active(active) for rect in self.list_of_zoom_box]
        self.is_active = active

    def on_zoom_dragged(self,eclick, erelease):
        ax = self.curr_ax[:][0]
        if self.target_ax != None and ax != self.target_ax:
            return
        x_range = (eclick.xdata, erelease.xdata)
        y_range = (eclick.ydata, erelease.ydata)
        if self.first_zoom:
            self.history.append((ax.get_xlim(), ax.get_ylim()))
            self.original_range = (ax.get_xlim(), ax.get_ylim())
            self.first_zoom = False

        self.history.append((x_range, y_range))
        self.current_range_index = len(self.history)-1 
        self.do_zoom(x_range, y_range)

    def on_mouse_click(self, event):
        if event.inaxes:
            if self.is_active:
                self.curr_ax[:] = [event.inaxes]

    def do_zoom(self, x, y):
        label = (((self.curr_ax[:])[-1].get_ylabel()).split('('))[0]
        self.zoom_requested.emit(label,x, y)


    def reset(self):
        self.first_zoom = True
        self.history.clear()

