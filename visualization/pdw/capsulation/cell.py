class Cell:
    _x_start = 0
    _x_end = 0
    _y_start = 0
    _y_end = 0
    is_trigged = False
    counter = 0

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self) -> str:
        return str(self.is_trigged)

    def output(self):
        if self.is_trigged:
            x_output = self._x_start + (self._x_end - self._x_start)/2
            y_output = self._y_start + (self._y_end - self._y_start)/2
            return x_output, y_output
        else:
            return None

    def feed(self):
        if not self.is_trigged:
            self.is_trigged = True
        self.counter += 1

    @property
    def x_start(self):
        return self._x_start

    @x_start.setter
    def x_start(self, _x_start):
        self._x_start = _x_start

    @property
    def x_end(self):
        return self._x_end

    @x_end.setter
    def x_end(self, _x_end):
        self._x_end = _x_end

    
    @property
    def y_start(self):
        return self._y_start

    @y_start.setter
    def y_start(self, _y_start):
        self._y_start = _y_start
    
    @property
    def y_end(self):
        return self._y_end

    @y_end.setter
    def y_end(self, _y_end):
        self._y_end = _y_end