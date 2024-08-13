from PyQt5.QtWidgets import QDoubleSpinBox, QFrame, QTableWidget, QTableWidgetItem, QWidget
from PyQt5 import QtCore

import locale

locale.setlocale(locale.LC_ALL, '')


# TODO: Separate value changed connect to only update when enter is pressed

class FloatSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super(FloatSpinBox, self).__init__(parent)


    def valueFromText(self, p_str):
        value = p_str.split(' ')[0]
        value = locale.atof(value)
        # print(f'Value from Text: {value}')

        return value

    def textFromValue(self, p_float): # real signature unknown; restored from __doc__
        """ textFromValue(self, float) -> str """#
        value = p_float
        # print(value)

        if value >= 0.001:
            return locale.format_string('%0.3f', value)

        elif value == 0:
            return locale.format_string('%0.3f', value)

        else:
            return locale.format_string('%0.3E', value)

    # def keyReleaseEvent(self, *args, **kwargs): # real signature unknown
    #     print('Key Press')
    #     print(args[0], args[0].key())
    #
    #     return args[0].key()


    # def valueChanged(self, *args, **kwargs):

    # def editingFinished(self, *args, **kwargs):



class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class TableWidget(QTableWidget):
    def __init__(self, dataInit):
        super(TableWidget, self).__init__()
        colNum = len(dataInit)
        # print(dataInit)

        self.rowNames = []

        self.setColumnCount(colNum)
        self.setHorizontalHeaderLabels(list(dataInit.keys()))

        self.addRow(dataInit, 'Laser')


    def addRow(self, data, rowName):
        rowPosition = self.rowCount()
        self.insertRow(rowPosition)

        self.rowNames.append(rowName)
        self.setVerticalHeaderLabels(self.rowNames)

        for i, key in enumerate(data):
            newitem = QTableWidgetItem(str(data[key]))

            self.setItem(rowPosition, i, newitem)

        # newitem = QTableWidgetItem(data)

    def resetRowNames(self):
        self.rowNames = []





class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, ):
        pass


class Preferences(QWidget):
    def __init__(self, prefs):
        super(Preferences, self).__init__()

        self.prefs = prefs



    def done(self):
        # get all preferences
        pass

    def add_tab(self, prefs):
        # add tab for different categories
        pass

    def parse_prefs(self, prefs):
        for key in prefs:
            pass




