from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT 

class MyCustomToolbar(NavigationToolbar2QT): 
    def __init__(self, plotCanvas, parent):
        # create the default toolbar
        NavigationToolbar2QT.__init__(self, plotCanvas, parent)
    
    def is_zoom(self):
        return self.mode.name == 'ZOOM'

    def is_pan(self):
        return self.mode.name == 'PAN'

        