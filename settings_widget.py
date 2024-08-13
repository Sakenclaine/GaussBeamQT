# from PyQt5.QtWidgets import QPushButton, QWidget, QGridLayout, QGroupBox, QLabel, QVBoxLayout, QHBoxLayout, \
#     QDoubleSpinBox, QRadioButton, QSpinBox, QScrollArea, QSlider

from PyQt5.Qt import *
from PyQt5 import QtCore

from custom_QWidgets import FloatSpinBox, QHLine

import numpy as np
import utilities
import gaussian_funcs as gsf

class SettingsWidget(QWidget):
    wavelength = 390.0
    waist_X = 0.1
    waist_Y = 0.1
    ray_X = gsf.rayleigh(waist_X, wavelength)
    ray_Y = gsf.rayleigh(waist_Y, wavelength)
    z0_X = 0.0
    z0_Y = 0.0
    divergence_X = gsf.theta(waist_X, ray_X, parent='init')
    divergence_Y = gsf.theta(waist_Y, ray_Y, parent='init')

    update_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)

        self.lenses = {}
        self.pams = [r'$w_{0,x}$', r'$w_{0,y}$', r'$z_{R,x}$', r'$z_{R,y}$', r'$z_{0,x}$', r'$z_{0,y}$', r'wavelength', r'divergence']
        self.paramInputs = []

        bigFont = QFont()
        bigFont.setPointSize(13)
        bigFont.setBold(True)
        self.bigFont = bigFont

        smallFont = QFont()
        smallFont.setPointSize(10)
        smallFont.setBold(False)
        self.smallFont = smallFont

        pixmaps = []
        for pam in self.pams:
            formula_pixmap = utilities.mathTex_to_QPixmap(pam, 12)
            pixmaps.append(formula_pixmap)

        labels = []
        for pix in pixmaps:
            label = QLabel()
            label.setPixmap(pix)
            label.resize(pix.width(), pix.height())

            labels.append(label)

        self.labels = labels

        mainLayout = QGridLayout()

        addLens = QPushButton('Add Lens')
        addLens.clicked.connect(self.add_lens)

        testParams = QPushButton('Update Plot')
        testParams.clicked.connect(self.update_plot)
        mainLayout.addWidget(testParams)

        laserSet = self.laser_settings()

        generalSet = QGroupBox('General Settings', font=bigFont)
        genLayout = QGridLayout()
        generalSet.setLayout(genLayout)

        # Settings for displaying ellipticity function
        ellSet = QGroupBox('Ellipticity', font=smallFont)
        ellSet.setCheckable(True)
        ellLayout = QHBoxLayout()
        ellSet.setLayout(ellLayout)

        ell = QRadioButton('x/y')
        ell.mode = "xy"
        ellLayout.addWidget(ell)

        ell = QRadioButton('y/x')
        ell.mode = "yx"
        ellLayout.addWidget(ell)

        ell = QRadioButton('individual')
        ell.mode = "ind"
        ell.setChecked(True)
        ellLayout.addWidget(ell)

        genLayout.addWidget(ellSet)

        waistMode = QGroupBox('Output radius', font=smallFont)
        modeLayout = QHBoxLayout()
        waistMode.setLayout(modeLayout)

        # modeBtn = QRadioButton('1/e^2')
        # modeBtn.mode = "1/e^2"
        # modeLayout.addWidget(modeBtn)
        #
        # genLayout.addWidget(waistMode)

        sampling = QSpinBox(font=smallFont)
        sampling.setPrefix('Sampling:  ')
        sampling.setMaximum(1000)
        sampling.setValue(500)
        genLayout.addWidget(sampling)

        # Setting the area, the beam profile is drawn
        start, end = QSpinBox(font=smallFont), QSpinBox(font=smallFont)
        start.setPrefix('Start:  ')
        start.setMinimum(-10000)
        start.setMaximum(10000)
        end.setPrefix('End:  ')
        end.setMinimum(-10000)
        end.setMaximum(10000)
        end.setValue(600)

        start.editingFinished.connect(lambda: self.update_limits(start.value(), 'min'))
        end.editingFinished.connect(lambda: self.update_limits(end.value(), 'max'))

        self.start_end = (start, end)

        genLayout.addWidget(start)
        genLayout.addWidget(end)

        generalSet.setMaximumHeight(250)

        self.generalSettings = {'ellipticity': ellSet, 'sampling': sampling, 'start_lim': start, 'end_lim': end}

        scroll = QScrollArea(widgetResizable=True)
        # scroll.setMaximumHeight(500)

        sliderSet = QGroupBox('Lens positions', font=bigFont)
        slLayout = QGridLayout()
        sliderSet.setLayout(slLayout)
        self.slLayout = slLayout

        scroll.setWidget(sliderSet)

        mainLayout.addWidget(addLens)
        mainLayout.addWidget(laserSet)
        mainLayout.addWidget(generalSet)
        mainLayout.addWidget(scroll)

        self.setLayout(mainLayout)

        self.beam_params = self.get_params()
        self.lens_params = self.get_lens_params()
        self.general = self.get_general_settings()

    def laser_settings(self):
        labels = self.labels

        laserSet = QGroupBox('Laser Parameters', font=self.bigFont)
        laserSet.setToolTip('')
        laserLayout = QGridLayout()
        laserLayout.setSpacing(8)
        laserSet.setMaximumHeight(250)

        vLayout = QVBoxLayout()
        hLayout = QHBoxLayout()

        # center the grid with stretch on both sides
        # hLayout.addStretch(1)
        hLayout.addLayout(laserLayout)
        # hLayout.addStretch(1)

        vLayout.addLayout(hLayout)
        # push grid to the top of the window
        vLayout.addStretch(0)

        laserSet.setLayout(vLayout)

        ## Laser Parameters
        w_X, w_Y = FloatSpinBox(), FloatSpinBox()
        w_X.setSuffix(' mm')
        w_X.setDecimals(8)
        w_Y.setDecimals(8)
        w_Y.setSuffix(' mm')
        w_X.setValue(0.1)
        w_Y.setValue(0.1)
        w_X.setToolTip('Waist in x-direction with 1/e^2\nPress Enter for setting value.')
        w_Y.setToolTip('Waist in y-direction with 1/e^2\nPress Enter for setting value.')

        w_X.setSingleStep(0.1)
        w_Y.setSingleStep(0.1)

        zR_X, zR_Y = FloatSpinBox(), FloatSpinBox()
        zR_X.setSuffix(' mm')
        zR_Y.setSuffix(' mm')
        zR_X.setMaximum(100000)
        zR_Y.setMaximum(100000)
        zR_X.setDecimals(8)
        zR_Y.setDecimals(8)
        zR_X.setValue(gsf.rayleigh(w_X.value(), self.wavelength))
        zR_Y.setValue(gsf.rayleigh(w_X.value(), self.wavelength))

        z0_X, z0_Y = FloatSpinBox(), FloatSpinBox()
        z0_X.setSuffix(' mm')
        z0_Y.setSuffix(' mm')
        z0_X.setMinimum(-5000)
        z0_X.setMaximum(5000)
        z0_Y.setMinimum(-5000)
        z0_Y.setMaximum(5000)

        wav = QDoubleSpinBox()
        wav.setSuffix(' nm')
        wav.setMaximum(2000)
        wav.setValue(390)

        divergence = QDoubleSpinBox()
        divergence.setSuffix(' mrad')
        divergence.setDecimals(3)

        self.paramInputs = [w_X, w_Y, zR_X, zR_Y, z0_X, z0_Y, wav, divergence]

        # Connect Functions
        w_X.editingFinished.connect(self.update_waist_X)
        w_Y.editingFinished.connect(self.update_waist_Y)
        wav.valueChanged.connect(self.update_wavelength)
        zR_X.editingFinished.connect(self.update_rayleigh_X)
        zR_Y.editingFinished.connect(self.update_rayleigh_Y)

        z0_X.valueChanged.connect(self.update_plot)
        z0_Y.valueChanged.connect(self.update_plot)

        laserLayout.addWidget(labels[0], 0, 0)
        laserLayout.addWidget(labels[1], 0, 1)

        laserLayout.addWidget(labels[2], 2, 0)
        laserLayout.addWidget(labels[3], 2, 1)

        laserLayout.addWidget(labels[4], 4, 0)
        laserLayout.addWidget(labels[5], 4, 1)

        laserLayout.addWidget(labels[6], 6, 0)
        # laserLayout.addWidget(labels[7], 6, 1)

        laserLayout.addWidget(w_X, 1, 0)
        laserLayout.addWidget(w_Y, 1, 1)

        laserLayout.addWidget(zR_X, 3, 0)
        laserLayout.addWidget(zR_Y, 3, 1)

        laserLayout.addWidget(z0_X, 5, 0)
        laserLayout.addWidget(z0_Y, 5, 1)

        laserLayout.addWidget(wav, 7, 0)
        # laserLayout.addWidget(divergence, 7, 1)

        for child in laserSet.children()[1:]:
            child.setFont(self.smallFont)

        return laserSet

    def get_params(self):
        """

        :return: numpy array of all parameters [waist x, waist y, rayleigh x, rayleigh y, waist pos x, waist pos y, wavelength, divergence]
        """
        values = []

        for input in self.paramInputs:
            values.append(input.value())

        return np.array(values)

    def add_lens(self):
        num = len(self.lenses)
        # print(f'\nNumber of lenses: {num}')

        current_Inds = [int(elem.split('_')[1]) for elem in self.lenses.keys()]

        # print(f'Lens indices: {current_Inds}')

        if current_Inds:
            lensInd = current_Inds[-1] + 1

        else:
            lensInd = 0


        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(self.start_end[0].value())
        slider.setMaximum(self.start_end[1].value())
        slider.valueChanged.connect(lambda: self.update_pos_slider(lensInd, slider.value()))

        pos = QDoubleSpinBox(font=self.smallFont)
        pos.setSuffix(' mm')
        pos.setMinimum(self.start_end[0].value())
        pos.setMaximum(self.start_end[1].value())
        pos.valueChanged.connect(lambda: self.update_pos_box(lensInd, pos.value()))

        rem = QPushButton('Remove Lens', font=self.smallFont)
        rem.clicked.connect(lambda: self.remove_lens(lensInd))


        axis = QGroupBox('Axis', font=self.smallFont)
        axisLayout = QVBoxLayout()

        rb = QRadioButton('both')
        rb.axis = 'both'
        rb.setChecked(True)
        axisLayout.addWidget(rb)

        rb = QRadioButton('x')
        rb.axis = 'x'
        axisLayout.addWidget(rb)

        rb = QRadioButton('y')
        rb.axis = 'y'
        axisLayout.addWidget(rb)

        axis.setLayout(axisLayout)

        name = QLineEdit(font=self.smallFont)
        name.setPlaceholderText(f"Lens {lensInd}")

        focal = QDoubleSpinBox(font=self.smallFont)
        focal.setSuffix(' mm')
        focal.setMinimum(-3000)
        focal.setMaximum(3000)
        focal.setValue(100)

        sep = QHLine()

        self.lenses[f'l_{lensInd}'] = {'name': name, 'posSlid': slider, 'posBox': pos, 'focus': focal, 'axis': axis,
                                   'sep': sep, 'remove': rem}

        numNew = lensInd # len(self.lenses)
        # print(f'New lens number: {numNew}')

        ws = 5
        self.slLayout.addWidget(rem, ws*numNew, 0)
        self.slLayout.addWidget(name, ws*numNew+1, 0)
        self.slLayout.addWidget(focal, ws*numNew+2, 0)
        self.slLayout.addWidget(slider, ws*numNew+3, 0)
        self.slLayout.addWidget(pos, ws*numNew+3, 1)
        self.slLayout.addWidget(axis, ws*numNew, 1, 3, 1)

        self.slLayout.addWidget(sep, ws*numNew+4, 0, 1, 2)

        # print(self.lenses)
        # print(list(self.lenses.keys()))

    def remove_lens(self, num):
        print(f'Remove Lens {num}')
        for key in self.lenses[f'l_{num}']:
            # print(f'\n-------------{key}')
            # print(self.lenses[f'l_{num}'][key])
            # print(self.lenses[f'l_{num}'][key].children())

            self.lenses[f'l_{num}'][key].deleteLater()
            # self.slLayout.removeWidget(self.lenses[f'l_{num}'][key])

        self.lenses.pop(f'l_{num}')

        self.update_plot()

    def update_pos_slider(self, slider, value):
        # print('-----------------------')
        # print(f'Slider: {slider}, {value}')
        # print('--------------------------\n')
        self.lenses[f'l_{slider}']['posBox'].setValue(int(value))

    def update_pos_box(self, slider, value):
        # print('-----------------------')
        # print(f'Box: {slider}, {value}')
        # print('--------------------------\n')

        self.lenses[f'l_{slider}']['posSlid'].setValue(int(value))
        self.update_plot()

    def update_wavelength(self, val):
        self.wavelength = val

        self.ray_X = gsf.rayleigh(self.waist_X, self.wavelength)
        self.divergence_X = gsf.theta(self.waist_X, self.ray_X, parent='wavelength')
        self.paramInputs[2].setValue(self.ray_X)

        self.ray_Y = gsf.rayleigh(self.waist_Y, self.wavelength)
        self.divergence_Y = gsf.theta(self.waist_Y, self.ray_Y, parent='wavelength')
        self.paramInputs[3].setValue(self.ray_Y)

        self.update_plot()

    def update_waist_X(self):
        val = self.paramInputs[0].value()
        self.waist_X = self.paramInputs[0].value()
        # print(f'Value: {val}, {self.paramInputs[0].value()}')

        if val != 0:
            self.ray_X = gsf.rayleigh(val, self.wavelength)
            self.divergence_X = gsf.theta(val, self.ray_X, parent='waist X')
            self.paramInputs[2].setValue(self.ray_X)
            # print(f'Set ray X: {self.ray_X}')
            self.update_plot()

    def update_waist_Y(self):
        val = self.paramInputs[1].value()
        self.waist_Y = val

        if val != 0:
            self.ray_Y = gsf.rayleigh(val, self.wavelength)
            self.divergence_Y = gsf.theta(val, self.ray_Y, parent='waist Y')
            self.paramInputs[3].setValue(self.ray_Y)
            self.update_plot()

    def update_rayleigh_X(self):
        val = self.paramInputs[2].value()
        self.ray_X = val
        self.waist_X = gsf.waistFromRayleigh(val, self.wavelength)
        self.paramInputs[0].setValue(self.waist_X)
        self.update_plot()

    def update_rayleigh_Y(self):
        val = self.paramInputs[3].value()
        self.ray_Y = val
        self.waist_Y = gsf.waistFromRayleigh(val, self.wavelength)
        self.paramInputs[1].setValue(self.waist_Y)
        self.update_plot()

    def update_limits(self, val, ty):
        if ty == 'max':
            for key in self.lenses:
                # print(self.lenses[key]['posSlid'])
                self.lenses[key]['posSlid'].setMaximum(val)
                self.lenses[key]['posBox'].setMaximum(val)


        elif ty == 'min':
            for key in self.lenses:
                # print(key)
                self.lenses[key]['posSlid'].setMinimum(val)
                self.lenses[key]['posBox'].setMinimum(val)


        self.update_plot()

    # def update_wavelength(self, val):
    #     self.wavelength = val
    #     self.ray_X = gsf.rayleigh(self.waist_X, self.wavelength)
    #     self.ray_Y = gsf.rayleigh(self.waist_Y, self.wavelength)
    #
    #     self.divergence_X = gsf.theta(self.waist_X, self.ray_X)
    #     self.divergence_Y = gsf.theta(self.waist_Y, self.ray_Y)
    #
    #     self.update_plot()

    def get_pos(self):
        pos = []
        for key in self.lenses:
            posBox = self.lenses[key]['posBox'].value()

            pos.append(posBox)

        return np.array(pos)

    def get_focals(self):
        focals = []

        for key in self.lenses:
            focus = self.lenses[key]['focus'].value()

            focals.append(focus)

        return np.array(focals)

    def get_lens_params(self):
        num = len(self.lenses)
        focals = self.get_focals()
        pos = self.get_pos()

        names = []
        axes = []
        for i, key in enumerate(self.lenses):
            name = self.lenses[key]['name'].text()
            axis_bts = self.lenses[key]['axis'].children()[1:]

            for bt in axis_bts:
                if bt.isChecked():
                    axes.append(bt.axis)

            if name != '':
                names.append(name)

            else:
                names.append(self.lenses[key]['name'].placeholderText())

        return (focals, pos, names, axes)

    def get_general_settings(self):
        ellipticity = None
        sampling = self.generalSettings['sampling'].value()
        limits = (self.generalSettings['start_lim'].value(), self.generalSettings['end_lim'].value())

        if self.generalSettings['ellipticity'].isChecked():
            radioButtons = [elem for elem in self.generalSettings['ellipticity'].children() if isinstance(elem, QRadioButton)]

            for rb in radioButtons:
                if rb.isChecked():
                    ellipticity = rb.text()

        return {'ellip': ellipticity, 'sampling': sampling, 'limits': limits}

    def get_all(self):
        self.beam_params = self.get_params()
        self.lens_params = self.get_lens_params()
        self.general = self.get_general_settings()

        return self.beam_params, self.lens_params, self.general

    def get_all_beam_params(self) -> dict:
        pams = {}
        for att in self.class_attributes():
            pams[att] = getattr(self, att)

        return pams

    def get_lims(self):
        start = self.start_end[0].value()
        end = self.start_end[1].value()
        return start, end

    def class_attributes(self):
        atts = ['waist_X', 'waist_Y', 'ray_X', 'ray_Y', 'z0_X', 'z0_Y', 'divergence_X', 'divergence_Y', 'wavelength']
        return atts

    def update_plot(self):
        self.beam_params = self.get_params()
        self.lens_params = self.get_lens_params()
        self.general = self.get_general_settings()

        self.update_signal.emit()





