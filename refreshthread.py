from threading import Timer, Thread, Event

class RefreshTimer():

    def __init__(self, function):
        self.function = function
        self.thread = Timer(0.1, self.function)

    def refresh(self):
        self.function()
        self.thread = Timer(0.1, self.function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()
