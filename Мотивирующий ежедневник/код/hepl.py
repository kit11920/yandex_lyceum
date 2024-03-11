import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QButtonGroup
from PyQt5.QtCore import QSettings


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.f = QWidget()
        self.btn_group_hbts = QButtonGroup()
        self.f.addWidget(self.btn_group_hbts)


def exept_hooks(cls, exeption, trades):
    sys.__excepthook__(cls, exeption, trades)


if __name__ == '__main__':
    sys.excepthook = exept_hooks
    app = QApplication(sys.argv)
    main = MyWidget()
    main.show()
    sys.exit(app.exec())