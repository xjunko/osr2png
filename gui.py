from PyQt5 import QtCore, QtGui, QtWidgets, uic
from qasync import QEventLoop, asyncSlot

import sys, asyncio


class Ui(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("meme")
        self.windowwidth = self.default_width = 700
        self.windowheight = self.default_height = 600
        self.setFixedSize(QtCore.QSize(self.windowwidth, self.windowheight))
        self.setStyleSheet("background-color: rgb(30, 30, 33);")

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(0, 0, 700, 300)
        self.label.setPixmap(QtGui.QPixmap('res/sample.png').scaled(700, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        # ...
        self.settingsLabel = QtWidgets.QLabel(self)
        self.settingsLabel.setText('eajdodn')

        self.show()




def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    tiddies = Ui()
    tiddies.show()


    loop.run_forever()


if __name__ == '__main__':
    main()