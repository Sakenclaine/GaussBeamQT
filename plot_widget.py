from PyQt5.QtWidgets import QWidget, QGridLayout, QGraphicsEllipseItem

from pyqtgraph import PlotWidget
import pyqtgraph as pg
import numpy as np

import gaussian_funcs as gsf


class PlotWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(PlotWidget, self).__init__()
        mainLayout = QGridLayout()

        self.settings = kwargs.get('settings')
        self.results = kwargs.get('results')

        self.graphWidget = pg.PlotWidget()

        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y=True)

        self.p1 = self.graphWidget.plotItem

        # Define pens with different colors for x and y-axis of beam and draggable cursor
        penX = pg.mkPen(color=(255, 0, 0), width=4)
        penY = pg.mkPen(color=(0, 255, 0), width=4)
        penCursor = pg.mkPen(color=(0, 208, 230), width=2)

        self.ellPen = pg.mkPen(color='b', width=2) # pen for drawing lenses

        self.xRad = self.graphWidget.plot([], [], pen=penX)
        self.yRad = self.graphWidget.plot([], [], pen=penY)

        self.xRadMirror = self.graphWidget.plot([], [], pen=penX)
        self.yRadMirror = self.graphWidget.plot([], [], pen=penY)

        # styles = {'color': 'k', 'font-size': '18px'}
        self.graphWidget.setLabel('bottom', 'z position (mm)')
        self.graphWidget.setLabel('left', 'beam radius (mm)')

        self.cursor = pg.InfiniteLine(movable=True, angle=90, pen=penCursor)
        self.cursor.sigDragged.connect(self.cursor_label)
        self.graphWidget.addItem(self.cursor)

        self.label = pg.InfLineLabel(self.cursor, text='')
        self.label.setMovable(True)

        mainLayout.addWidget(self.graphWidget)
        self.setLayout(mainLayout)

    def cursor_label(self, cursor):
        zPos = cursor.value()
        lasers, rawArrays = self.results.get_lasers()
        lenses = self.settings.get_lens_params()
        lims = self.settings.get_lims()

        lPos = [lims[0]] + list(lenses[1][np.argsort(lenses[1])]) + [lims[1]]

        if len(lasers) == 1:
            radX = gsf.beam_radius(rawArrays[2][0], rawArrays[4][0], zPos, rawArrays[0][0]) * 10**3
            radY = gsf.beam_radius(rawArrays[3][0], rawArrays[5][0], zPos, rawArrays[1][0]) * 10 ** 3
            self.label.setHtml(f'z: {zPos: .3f}mm <br />wX(z): {radX: .3f} <math>&mu;<math>m <br />wY(z): {radY: .3f} <math>&mu;<math>m')

        else:
            j = 1
            for i, elem in enumerate(lPos[:-1]):
                # print(elem, zPos, lPos[j])
                if elem <= zPos <= lPos[j]:
                    if np.isnan(rawArrays[2][i]) == True:
                        # print('x value is nan')
                        k = i
                        while np.isnan(rawArrays[2][k]) == True:
                            k -= 1

                        radX = gsf.beam_radius(rawArrays[2][k], rawArrays[4][k], zPos, rawArrays[0][k]) * 10 ** 3

                    else:
                        radX = gsf.beam_radius(rawArrays[2][i], rawArrays[4][i], zPos, rawArrays[0][i]) * 10 ** 3

                    if np.isnan(rawArrays[3][i]) == True:
                        k = i
                        # print(f'y value is nan {k}, {rawArrays[3][k]}, {np.isnan(rawArrays[3][k])}')
                        while np.isnan(rawArrays[3][k]) == True:
                            # print(f'Loop: {np.isnan(rawArrays[3][k])}')
                            k -= 1

                        # print(k)
                        radY = gsf.beam_radius(rawArrays[3][k], rawArrays[5][k], zPos, rawArrays[1][k]) * 10 ** 3

                    else:
                        radY = gsf.beam_radius(rawArrays[3][i], rawArrays[5][i], zPos, rawArrays[1][i]) * 10 ** 3

                    self.label.setHtml(
                        f'z: {zPos: .3f}mm <br />wX(z): {radX: .3f} <math>&mu;<math>m <br />wY(z): {radY: .3f} <math>&mu;<math>m')

                j += 1

    def plot(self, beamData, lensData, generalSettings):
        # print('Init Plot')
        # print(beamData, lensData, generalSettings)

        start = generalSettings['limits'][0]
        end = generalSettings['limits'][1]
        sampling = generalSettings['sampling']
        ellipticity = generalSettings['ellip']
        mirrored = True

        xs = np.linspace(start, end, sampling)

        xwaist = gsf.beam_radius(beamData[0], beamData[2], xs, beamData[4])
        ywaist = gsf.beam_radius(beamData[1], beamData[3], xs, beamData[5])

        self.xRad.setData(xs, xwaist, name='x_radius')
        self.yRad.setData(xs, ywaist, name='y_radius')

        self.lensItems = []

        self.fill_curve = pg.FillBetweenItem(curve1=self.xRad, curve2=self.yRad, brush=(50, 50, 200, 50))
        self.graphWidget.addItem(self.fill_curve)

        if ellipticity != None:
            self.p2 = pg.ViewBox()
            self.p1.showAxis('right')
            axRight = self.p1.getAxis('right')
            axRight.setGrid(False)
            axRight.setLabel('ellipticity')

            self.p1.scene().addItem(self.p2)
            self.p1.getAxis('right').linkToView(self.p2)
            self.p2.setXLink(self.p1)

            self.ell = pg.PlotCurveItem([], [], pen='b')

            self.p2.addItem(self.ell)
            self.p2.setGeometry(self.p1.vb.sceneBoundingRect())

        if mirrored == True:
            self.xRadMirror.setData(xs, -xwaist, name='x_radius_mirror')
            self.yRadMirror.setData(xs, -ywaist, name='y_radius_mirror')

    def update_plot(self, beamData, lensData, generalSettings):
        # print('\n ==================\nUpdate Plot')
        # print(beamData, generalSettings)

        start = generalSettings['limits'][0]
        end = generalSettings['limits'][1]
        sampling = generalSettings['sampling']
        ellipticity = generalSettings['ellip']
        mirrored = True

        for lens in self.lensItems:
            self.graphWidget.removeItem(lens)

        self.p2.removeItem(self.ell)

        if len(lensData[0]) == 0:
            # print(lensData)
            xs = np.linspace(start, end, sampling)

            radsX = gsf.beam_radius(beamData[0], beamData[2], xs, beamData[4])
            radsY = gsf.beam_radius(beamData[1], beamData[3], xs, beamData[5])

            self.xRad.setData(xs, radsX)
            self.yRad.setData(xs, radsY)

            if mirrored == True:
                self.xRadMirror.setData(xs, -radsX, name='x_radius_mirror')
                self.yRadMirror.setData(xs, -radsY, name='y_radius_mirror')

        else:
            # print('-------------------\nlenses are present')
            foc = lensData[0]
            pos = lensData[1]
            names = lensData[2]
            axes = lensData[3]

            sort = np.argsort(pos)
            foc, pos, names, axes = foc[sort], pos[sort], [names[i] for i in sort], [axes[i] for i in sort]

            # print(pos, foc, names)

            xs, radsX, radsY = gsf.beam_with_lenses(pos, foc, axes, beamData, sampling=sampling, start=start, end=end)

            self.xRad.setData(xs, radsX)
            self.yRad.setData(xs, radsY)

            if mirrored == True:
                self.xRadMirror.setData(xs, -radsX, name='x_radius_mirror')
                self.yRadMirror.setData(xs, -radsY, name='y_radius_mirror')


            width = 10 * end / 800
            height = 0.8 * self.graphWidget.getAxis('left').range[1] + 0.3

            for z in pos:
                lens = QGraphicsEllipseItem(z-0.5*width, -0.5*height, width, height)  # pg.QtGui.QGraphicsEllipseItem(z-0.5*width, 0, width, height)
                lens.setPen(pg.mkPen((0, 0, 0, 100), width=1.5))
                lens.setBrush(pg.mkBrush((50, 50, 200, 30)))
                self.lensItems.append(lens)
                self.graphWidget.addItem(lens)


        if ellipticity != None:
            if ellipticity == 'x/y':
                ell = radsX / radsY

            elif ellipticity == 'y/x':
                ell = radsY / radsX

            elif ellipticity == 'individual':
                ell = np.zeros_like(radsX)
                for i, val in enumerate(radsX):
                    if val <= radsY[i]:
                        ell[i] = val / radsY[i]

                    else:
                        ell[i] = radsY[i] / val

            self.p2 = pg.ViewBox()
            self.p1.showAxis('right')
            self.p1.scene().addItem(self.p2)
            self.p1.getAxis('right').linkToView(self.p2)
            self.p2.setXLink(self.p1)

            self.ell = pg.PlotCurveItem(xs, ell, pen='b')

            self.p2.addItem(self.ell)
            self.p2.setGeometry(self.p1.vb.sceneBoundingRect())

        else:
            self.p1.scene().removeItem(self.p2)
            self.p1.hideAxis('right')


        self.graphWidget.removeItem(self.fill_curve)
        # self.graphWidget['fill'].clear()
        self.fill_curve = pg.FillBetweenItem(curve1=self.xRad, curve2=self.yRad, brush=(50, 50, 200, 50))
        self.graphWidget.addItem(self.fill_curve)



    def set_prefs(self, prefs):
        print(prefs)












