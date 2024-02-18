import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListView
from PyQt6.QtCore import QThread, QObject, pyqtSignal, Qt, QStringListModel

class Worker(QObject):
    finished = pyqtSignal()
    new_item = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def do_work(self):
        for i in range(5):
            time.sleep(1)  # Simulate work
            self.new_item.emit(f"Item {i}")

        self.finished.emit()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.list_view = QListView()
        self.button = QPushButton("Start Adding Items")

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.list_view)
        self.setLayout(layout)

        self.worker = Worker()
        self.thread = QThread()

        self.worker.moveToThread(self.thread)

        self.worker.new_item.connect(self.add_item)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)

        self.button.clicked.connect(self.start_work)
        self.thread.started.connect(self.worker.do_work)

    def start_work(self):
        self.thread.start()

    def add_item(self, item):
        model = self.list_view.model()
        if model is None:
            model = QStringListModel()
            self.list_view.setModel(model)
        model.insertRow(model.rowCount())
        index = model.index(model.rowCount() - 1)
        model.setData(index, item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
