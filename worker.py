from PyQt5.QtCore import *
import traceback



class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()


    @pyqtSlot()
    def run(self):
        flag = 1
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except:
            flag = 0
            self.signals.error.emit()
            traceback.print_exc()
            return
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit(flag)  # Done



class WorkerSignals(QObject):

    finished = pyqtSignal(int)
    error = pyqtSignal()
    result = pyqtSignal(object)