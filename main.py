import sys
from PyQt5.QtWidgets import QApplication

import main_window



def start_program():
    app = QApplication(sys.argv)
    #app.setStyleSheet('QLabel { font-size: 14pt;} QGroupBox {font-size: 15px; font-weight: bold;}')

    window = main_window.MainWindow()
    window.show()

    app.exec()


if __name__ == '__main__':
    start_program()