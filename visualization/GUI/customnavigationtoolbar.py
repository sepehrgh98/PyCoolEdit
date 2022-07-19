from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT 
from PyQt5.QtWidgets import QToolButton

class MyCustomToolbar(NavigationToolbar2QT): 
    def __init__(self, plotCanvas, parent):
        # create the default toolbar
        NavigationToolbar2QT.__init__(self, plotCanvas, parent)

        self.clearButtons=[]
		# Search through existing buttons
		# next use for placement of custom button
        next=None
        for c in self.findChildren(QToolButton):
            if next is None:
                next=c
			# Don't want to see subplots and customize
            if str(c.text()) in ('Subplots','Customize','Forward', 'Pan', 'Save'):
                c.defaultAction().setVisible(False)
                continue

    
    def is_zoom(self):
        return self.mode.name == 'ZOOM'

    def is_pan(self):
        return self.mode.name == 'PAN'
    

        