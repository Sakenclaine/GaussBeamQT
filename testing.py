import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QMenuBar, QMenu, QWidget, QGroupBox, QDesktopWidget, QAction
from PyQt5.QtGui import QIcon

import plot_widget, settings_widget, result_window, preferences_widget, custom_QWidgets


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.layout = QGridLayout()

        widget = QWidget()
        widget.setLayout(self.layout)


        screen = QApplication.primaryScreen()
        resolution = screen.size()
        print(f'Screen Info:\n------------\nName: {screen.name}\nSize: {screen.size()} ({screen.size().width()} x {screen.size().height()})')
        print(f'Available geometry: {screen.availableGeometry().width()} x {screen.availableGeometry().height()}')

        self.screen = screen
        self.resolution = resolution
        self.resize(int(0.47*resolution.width()), int(0.57*resolution.height()))

        num = custom_QWidgets.FloatSpinBox()
        num.setDecimals(8)
        num.setSuffix(' mm')
        self.num = num

        btn = QPushButton('Value')
        btn.clicked.connect(self.get_value)


        self.layout.addWidget(num)
        self.layout.addWidget(btn)

        self.setCentralWidget(widget)

    def get_value(self):
        print(f'Value {self.num.value()}\n')



def start_program():
    app = QApplication(sys.argv)
    #app.setStyleSheet('QLabel { font-size: 14pt;} QGroupBox {font-size: 15px; font-weight: bold;}')

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == '__main__':
    start_program()