from queue import Full
from matplotlib.widgets import RectangleSelector

class HistoricalZoom:
    def __init__(self, fig) -> None:
        self.fig = fig
        self.is_active = False
        self.curr_ax = []
        self.list_of_zoom_box = []
        self.history = [] # list of tuple;(x_range, y_range)
        self.current_range_index = 0
        self.first_zoom = True


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
        x_range = (eclick.xdata, erelease.xdata)
        y_range = (eclick.ydata, erelease.ydata)
        if self.first_zoom:
            ax = self.curr_ax[:][0]
            self.history.append((ax.get_xlim(), ax.get_ylim()))
            self.first_zoom = False
        self.history.append((x_range, y_range))
        self.current_range_index = len(self.history)-1
        self.do_zoom(x_range, y_range)


    def on_mouse_click(self, event):
        if event.inaxes:
            if self.is_active:
                self.curr_ax[:] = [event.inaxes]

    def next_range(self):
        self.current_range_index += 1
        if self.current_range_index < len(self.history):
            x,y = self.history[self.current_range_index]
            self.do_zoom(x,y)
        else:
            self.current_range_index = len(self.history)-1 


    def previous_range(self):
        if self.current_range_index > 0 :
            self.current_range_index -= 1
            x,y = self.history[self.current_range_index]
            self.do_zoom(x,y)
        else:
            self.current_range_index = 0


    def do_zoom(self, x, y):
        axis = (self.curr_ax[:])[-1]
        if x[0] != x[1] and y[0] != y[1]:
            axis.set_xlim(x)
            axis.set_ylim(y)
            self.fig.canvas.draw()

    def reset(self):
        self.first_zoom = True
        self.history.clear()
