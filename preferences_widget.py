from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, \
    QTabWidget
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

# https://stackoverflow.com/questions/51404102/pyqt5-tabwidget-vertical-tab-horizontal-text-alignment-left

class Preferences(QWidget):
    def __init__(self, context):
        super().__init__()
        resolution = context.resolution
        icons = context.icon_paths

        self.plot_prefs = context.plot_prefs

        self.resize(int(0.23*resolution.width()), int(1/7*resolution.height()))
        self.setWindowTitle('Preferences')
        self.setWindowIcon(QIcon(icons[1]))
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "General")
        self.tabs.addTab(self.tab2, "Customize Plot")

        doneBtn = QPushButton('Done')

        self.layout.addWidget(self.tabs)
        self.layout.addWidget(doneBtn)


