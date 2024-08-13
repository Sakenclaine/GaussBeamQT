from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QMenuBar, QMenu, QWidget, QAction
from PyQt5.QtGui import QIcon

import plot_widget, settings_widget, result_window, preferences_widget
from utilities import resource_path

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        screen = QApplication.primaryScreen()
        resolution = screen.size()
        print(f'Screen Info:\n------------\nName: {screen.name}\nSize: {screen.size()} ({screen.size().width()} x {screen.size().height()})')
        print(f'Available geometry: {screen.availableGeometry().width()} x {screen.availableGeometry().height()}')

        self.screen = screen
        self.resolution = resolution


        self.plot_prefs = {'x_axis': {'color': (255, 0, 0), 'width': 4}, 'y_axis': {'color': (0, 255, 0), 'width': 4},
                           'ellipticity': {'color': 'b', 'width': 2}, 'mirrored': False, 'font': None, 'fontsize': 12}


        self.prefs = {'General': None, 'Plot Window': {'x_axis': {'type': 'Color', 'color': (255, 0, 0), 'width': 4}, 'y_axis': {'color': (0, 255, 0), 'width': 4},
                           'ellipticity': {'color': 'b', 'width': 2}, 'mirrored': False, 'font': None, 'fontsize': 12}}


        # self.mainPath = pathlib.Path(os.getcwd()).parents[0]
        # pathlib.Path(f"{self.mainPath}/Logs").mkdir(parents=True, exist_ok=True)
        # self.logPath = f'{self.mainPath}\\Logs'
        # print(self.mainPath, self.logPath)

        main_icon = resource_path('GB_icon.png')

        self.icon_paths = [main_icon]

        self.setWindowTitle("Gaussian Beam")
        self.setWindowIcon(QIcon(main_icon))
        self.resize(int(0.47*resolution.width()), int(0.57*resolution.height()))

        self.initialze()


    def initialze(self):
        # Setup Menubar
        #####################################################
        menu = QMenuBar()
        main_menu = QMenu("Main", self)
        menu.addMenu(main_menu)

        prefs_action = QAction("Preferences", self)
        prefs_action.setStatusTip("This is your button2")
        prefs_action.triggered.connect(self.open_preferences)

        main_menu.addAction(prefs_action)
        self.setMenuBar(menu)
        #####################################################

        self.layout = QGridLayout()

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.settings = settings_widget.SettingsWidget()
        self.settings.setMaximumWidth(300)

        self.resWindow = result_window.AnotherWindow(self)
        self.resWindow.show()

        self.plot = plot_widget.PlotWidget(**{'settings': self.settings, 'results': self.resWindow})

        self.layout.addWidget(self.settings)
        self.layout.addWidget(self.plot, 0, 1)

        self.plot.plot(self.settings.get_all()[0], self.settings.get_all()[1], self.settings.get_all()[2])
        self.resWindow.init_table(self.settings.get_all_beam_params())

        self.settings.update_signal.connect(self.update_plot)

        self.update_plot()


    def update_plot(self):
        self.plot.update_plot(self.settings.beam_params, self.settings.lens_params, self.settings.general)
        self.resWindow.update_table(self.settings.beam_params, self.settings.lens_params, self.settings.general)


    def open_preferences(self):
        self.pref_window = preferences_widget.Preferences(self)

        self.pref_window.show()


    def close_preferences(self, prefs):
        self.plot_prefs = prefs

        print(prefs)














