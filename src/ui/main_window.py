import datetime
from PySide6.QtWidgets import QMainWindow, QSplitter, QWidget, QHBoxLayout
from PySide6.QtCore import Qt

from src.core.astronomy import AstronomyEngine
from src.core.catalog import StarCatalog
from src.ui.sky_canvas import SkyCanvas
from src.ui.controls import ControlPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CA Planetarium - Python Astronomy MVP")
        self.resize(1200, 800)

        # Initialize core engine and catalog with default site lat 59, lon 16
        self.engine = AstronomyEngine(lat=59.0, lon=16.0)
        self.catalog = StarCatalog()

        # Central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Canvas for sky rendering
        self.canvas = SkyCanvas(self.engine, self.catalog)
        splitter.addWidget(self.canvas)

        # Control panel
        self.controls = ControlPanel(self.engine)
        splitter.addWidget(self.controls)

        splitter.setSizes([900, 300])

        # Connect signals
        self.controls.time_changed.connect(self.canvas.set_time)
        self.controls.location_changed.connect(lambda lat, lon, elev: self.canvas.update())
        self.controls.constellations_toggled.connect(self.canvas.set_show_constellations)
        self.controls.az_grid_toggled.connect(self.canvas.set_show_az_grid)
        self.controls.eq_grid_toggled.connect(self.canvas.set_show_eq_grid)
        self.controls.meridian_toggled.connect(self.canvas.set_show_meridian)
        self.controls.equator_toggled.connect(self.canvas.set_show_celestial_equator)
        self.controls.mirror_toggled.connect(self.canvas.set_show_mirrored)

        # Ensure time is updated once on start
        initial_time = datetime.datetime.now(datetime.timezone.utc)
        self.controls.set_to_now()
        self.canvas.set_time(initial_time)
