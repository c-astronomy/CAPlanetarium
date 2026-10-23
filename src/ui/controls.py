import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QDateTimeEdit, QDoubleSpinBox, QGroupBox, QFormLayout, QSlider, QCheckBox
)
from PySide6.QtCore import Qt, QDateTime, QTime, Signal, QTimer

from src.core.astronomy import AstronomyEngine

class ControlPanel(QWidget):
    time_changed = Signal(datetime.datetime)
    location_changed = Signal(float, float, float)
    constellations_toggled = Signal(bool)
    az_grid_toggled = Signal(bool)
    eq_grid_toggled = Signal(bool)
    meridian_toggled = Signal(bool)
    equator_toggled = Signal(bool)
    mirror_toggled = Signal(bool)
    dst_offset_changed = Signal(float)

    def __init__(self, engine: AstronomyEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        
        layout = QVBoxLayout(self)
        
        # Time Controls Group
        time_group = QGroupBox("Time & Simulation")
        time_layout = QVBoxLayout(time_group)
        
        # Initialize with current local system time
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.dateTimeChanged.connect(self.on_datetime_changed)
        time_layout.addWidget(self.datetime_edit)

        # DST Offset SpinBox
        dst_layout = QHBoxLayout()
        dst_layout.addWidget(QLabel("DST / Timezone Offset:"))
        self.spin_dst = QDoubleSpinBox()
        self.spin_dst.setRange(0.0, 5.0)
        self.spin_dst.setSingleStep(1.0)
        self.spin_dst.setValue(2.0) # Default +2h for summer time / user timezone
        self.spin_dst.setSuffix(" h")
        self.spin_dst.valueChanged.connect(self.on_dst_changed)
        dst_layout.addWidget(self.spin_dst)
        time_layout.addLayout(dst_layout)

        # Time of Day Slider (0 to 24 hours in minutes: 0 to 1440)
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Time of Day:"))
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 1440)
        self.time_slider.setValue(60 * 22)
        self.time_slider.sliderMoved.connect(self.on_slider_moved)
        slider_layout.addWidget(self.time_slider)
        time_layout.addLayout(slider_layout)
        
        time_btn_layout = QHBoxLayout()
        self.btn_now = QPushButton("Now")
        self.btn_now.clicked.connect(self.set_to_now)
        time_btn_layout.addWidget(self.btn_now)
        
        self.btn_realtime = QPushButton("Realtime (1x)")
        self.is_realtime_playing = False
        self.btn_realtime.clicked.connect(self.toggle_realtime)
        time_btn_layout.addWidget(self.btn_realtime)

        self.btn_fast = QPushButton("Fast Forward")
        self.is_fast_playing = False
        self.btn_fast.clicked.connect(self.toggle_fast)
        time_btn_layout.addWidget(self.btn_fast)

        time_layout.addLayout(time_btn_layout)
        layout.addWidget(time_group)

        # View Options Group
        view_group = QGroupBox("View Options")
        view_layout = QVBoxLayout(view_group)
        
        self.chk_constellations = QCheckBox("Show Constellation Lines")
        self.chk_constellations.setChecked(True)
        self.chk_constellations.toggled.connect(self.constellations_toggled.emit)
        view_layout.addWidget(self.chk_constellations)

        self.chk_az_grid = QCheckBox("Show Azimuthal Grid (Alt/Az)")
        self.chk_az_grid.setChecked(True)
        self.chk_az_grid.toggled.connect(self.az_grid_toggled.emit)
        view_layout.addWidget(self.chk_az_grid)

        self.chk_eq_grid = QCheckBox("Show Equatorial Grid (RA/Dec)")
        self.chk_eq_grid.setChecked(False)
        self.chk_eq_grid.toggled.connect(self.eq_grid_toggled.emit)
        view_layout.addWidget(self.chk_eq_grid)

        self.chk_meridian = QCheckBox("Show Meridian Line")
        self.chk_meridian.setChecked(True)
        self.chk_meridian.toggled.connect(self.meridian_toggled.emit)
        view_layout.addWidget(self.chk_meridian)

        self.chk_equator = QCheckBox("Show Celestial Equator")
        self.chk_equator.setChecked(True)
        self.chk_equator.toggled.connect(self.equator_toggled.emit)
        view_layout.addWidget(self.chk_equator)

        self.chk_mirror = QCheckBox("Stellarium Mirror View (E on Left)")
        self.chk_mirror.setChecked(False)
        self.chk_mirror.toggled.connect(self.mirror_toggled.emit)
        view_layout.addWidget(self.chk_mirror)

        layout.addWidget(view_group)
        
        # Location Controls Group
        loc_group = QGroupBox("Observer Location")
        loc_form = QFormLayout(loc_group)
        
        self.spin_lat = QDoubleSpinBox()
        self.spin_lat.setRange(-90.0, 90.0)
        self.spin_lat.setValue(engine.lat)
        self.spin_lat.setSuffix(" °")
        self.spin_lat.valueChanged.connect(self.on_location_changed)
        loc_form.addRow("Latitude:", self.spin_lat)
        
        self.spin_lon = QDoubleSpinBox()
        self.spin_lon.setRange(-180.0, 180.0)
        self.spin_lon.setValue(engine.lon)
        self.spin_lon.setSuffix(" °")
        self.spin_lon.valueChanged.connect(self.on_location_changed)
        loc_form.addRow("Longitude:", self.spin_lon)
        
        self.spin_elev = QDoubleSpinBox()
        self.spin_elev.setRange(-500.0, 10000.0)
        self.spin_elev.setValue(engine.elevation)
        self.spin_elev.setSuffix(" m")
        self.spin_elev.valueChanged.connect(self.on_location_changed)
        loc_form.addRow("Elevation:", self.spin_elev)
        
        layout.addWidget(loc_group)
        layout.addStretch()

        # Timers
        self.realtime_timer = QTimer(self)
        self.realtime_timer.setInterval(1000)
        self.realtime_timer.timeout.connect(lambda: self.advance_time_secs(1))

        self.fast_timer = QTimer(self)
        self.fast_timer.setInterval(100)
        self.fast_timer.timeout.connect(lambda: self.advance_time_secs(600))

    def get_current_time(self) -> datetime.datetime:
        qdt = self.datetime_edit.dateTime()
        dt = qdt.toPython().replace(tzinfo=datetime.timezone.utc)
        offset_hours = self.spin_dst.value()
        # datetime_edit displays local civil time; subtract offset to get UTC for astronomy engine
        if offset_hours != 0:
            dt = dt - datetime.timedelta(hours=offset_hours)
        return dt

    def on_datetime_changed(self, qdt: QDateTime):
        dt = self.get_current_time()
        self.time_changed.emit(dt)
        total_mins = qdt.time().hour() * 60 + qdt.time().minute()
        self.time_slider.blockSignals(True)
        self.time_slider.setValue(total_mins)
        self.time_slider.blockSignals(False)

    def on_dst_changed(self, val: float):
        self.dst_offset_changed.emit(val)
        self.on_datetime_changed(self.datetime_edit.dateTime())

    def on_slider_moved(self, minutes: int):
        qdt = self.datetime_edit.dateTime()
        hour = minutes // 60
        minute = minutes % 60
        qdt.setTime(QTime(hour, minute))
        self.datetime_edit.setDateTime(qdt)

    def set_to_now(self):
        # Set datetime_edit to current local system time directly
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())

    def toggle_realtime(self):
        if self.is_fast_playing:
            self.toggle_fast()
        self.is_realtime_playing = not self.is_realtime_playing
        if self.is_realtime_playing:
            self.realtime_timer.start()
            self.btn_realtime.setText("Pause (1x)")
        else:
            self.realtime_timer.stop()
            self.btn_realtime.setText("Realtime (1x)")

    def toggle_fast(self):
        if self.is_realtime_playing:
            self.toggle_realtime()
        self.is_fast_playing = not self.is_fast_playing
        if self.is_fast_playing:
            self.fast_timer.start()
            self.btn_fast.setText("Pause Fast")
        else:
            self.fast_timer.stop()
            self.btn_fast.setText("Fast Forward")

    def advance_time_secs(self, secs: int):
        current_qdt = self.datetime_edit.dateTime()
        new_qdt = current_qdt.addSecs(secs)
        self.datetime_edit.setDateTime(new_qdt)

    def on_location_changed(self):
        lat = self.spin_lat.value()
        lon = self.spin_lon.value()
        elev = self.spin_elev.value()
        self.engine.update_location(lat, lon, elev)
        self.location_changed.emit(lat, lon, elev)
