import matplotlib.pyplot as plt
import matplotlib.lines as lines


class DraggableLines:
    def __init__(self, ax, kind, XorY):
        self.ax = ax
        self.c = ax.get_figure().canvas
        self.o = kind
        self.XorY = XorY
        self.follower = None
        self.releaser = None
        x = 0
        y = 0

        if kind == "h":
            x = [-1, 1]
            y = [XorY, XorY]
        elif kind == "v":
            x = [XorY, XorY]
            y = [-1, 1]
        self.line = lines.Line2D(x, y, picker=5)
        self.ax.add_line(self.line)
        self.c.draw_idle()
        self.sid = self.c.mpl_connect('pick_event', self.click_online)

    def click_online(self, event):
        if event.artist == self.line:
            print("line selected ", event.artist)
            self.follower = self.c.mpl_connect("motion_notify_event", self.follow_mouse)
            self.releaser = self.c.mpl_connect("button_press_event", self.release_onclick)

    def follow_mouse(self, event):
        if self.o == "h":
            self.line.set_ydata([event.ydata, event.ydata])
        else:
            self.line.set_xdata([event.xdata, event.xdata])
        self.c.draw_idle()

    def release_onclick(self, event):
        if self.o == "h":
            self.XorY = self.line.get_ydata()[0]
        else:
            self.XorY = self.line.get_xdata()[0]

        print(self.XorY)

        self.c.mpl_disconnect(self.releaser)
        self.c.mpl_disconnect(self.follower)

    def set_range(self, val_range):
        if self.o == "h":
            self.line.set_xdata(val_range)
        elif self.o == "v":
            self.line.set_ydata(val_range)


if __name__ == "__main__":
    fig = plt.figure()
    # ax = fig.add_subplot(111)
    ax = fig.subplots(2, 1)
    Vline = DraggableLines(ax[0], "h", 0.5)
    Tline = DraggableLines(ax[0], "v", 1.5)
    Tline2 = DraggableLines(ax[0], "v", 0.1)
    plt.show()
