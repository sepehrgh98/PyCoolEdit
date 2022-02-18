class Observer:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self, batch):
        for observer in self._observers:
            observer.update(batch)
