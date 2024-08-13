from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon

import custom_QWidgets
import numpy as np

import gaussian_funcs as gsf



class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, context):
        super().__init__()
        resolution = context.resolution
        icons = context.icon_paths

        self.resize(int(0.23*resolution.width()), int(1/7*resolution.height()))
        self.move(int((1/2+0.47/2)*resolution.width()+5), int((1/2-0.57/2)*resolution.height()-50))
        self.setWindowTitle('Results')
        self.setWindowIcon(QIcon(icons[0]))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def init_table(self, header):
        self.table = custom_QWidgets.TableWidget(header)
        self.layout.addWidget(self.table)


    def update_table(self, beamData, lensData, generalSettings, sampling=100, start=0, end=100):
        # print('\n------------------------')
        # print(f'Update Table - {self.table.rowCount()}')
        start = generalSettings['limits'][0]
        end = generalSettings['limits'][1]
        sampling = generalSettings['sampling']

        for i in range(self.table.rowCount()):
            self.table.removeRow(self.table.rowCount() - 1)

        self.table.resetRowNames()


        foc = lensData[0]
        pos = lensData[1]
        names = lensData[2]
        axes = lensData[3]

        sort = np.argsort(pos)
        foc, pos, names, axes = foc[sort], pos[sort], [names[i] for i in sort], [axes[i] for i in sort]

        lasers, rawArrays = gsf.get_pams(pos, foc, axes, beamData, sampling=sampling, start=start, end=end)
        self.lasers = lasers
        self.rawArrays = rawArrays

        if len(lensData[0]) == 0:
            names = ['Laser']

        else:
            names = ['Laser'] + names

        # print(len(lasers))
        # print(names)

        for i, laser in enumerate(lasers):
            # print(names[i])
            self.add_row(laser, names[i])

        # print(f'Row Count: {self.table.rowCount()}')


    def add_row(self, data, name):
        self.table.addRow(data, name)

    def get_lasers(self):
        return self.lasers, self.rawArrays

    def remove_row(self, index):
        pass
