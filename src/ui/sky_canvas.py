import datetime
import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

from src.core.astronomy import AstronomyEngine
from src.core.catalog import StarCatalog

class SkyCanvas(QWidget):
    def __init__(self, engine: AstronomyEngine, catalog: StarCatalog, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.catalog = catalog
        self.obstime = datetime.datetime.now(datetime.timezone.utc)
        
        self.show_constellations = True
        self.show_az_grid = True
        self.show_eq_grid = False
        self.show_meridian = True
        self.show_celestial_equator = True
        self.show_mirrored = False
        
        # Interactive view parameters
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1.0
        
        self.setMouseTracking(True)

    def set_time(self, t: datetime.datetime):
        self.obstime = t
        self.update()

    def set_show_constellations(self, show: bool):
        self.show_constellations = show
        self.update()

    def set_show_az_grid(self, show: bool):
        self.show_az_grid = show
        self.update()

    def set_show_eq_grid(self, show: bool):
        self.show_eq_grid = show
        self.update()

    def set_show_meridian(self, show: bool):
        self.show_meridian = show
        self.update()

    def set_show_celestial_equator(self, show: bool):
        self.show_celestial_equator = show
        self.update()

    def set_show_mirrored(self, show: bool):
        self.show_mirrored = show
        self.update()

    def _proj(self, x: float, y: float, cx: float) -> tuple[float, float]:
        if self.show_mirrored:
            return 2 * cx - x, y
        return x, y

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        cx = width / 2 + self.pan_x
        cy = height / 2 + self.pan_y
        radius = min(width, height) * 0.45 * self.zoom

        # Draw dark night sky background
        painter.fillRect(0, 0, width, height, QColor(10, 15, 30))

        # Draw horizon circle
        painter.setPen(QPen(QColor(50, 70, 100), 2))
        painter.setBrush(QBrush(QColor(15, 22, 40)))
        painter.drawEllipse(int(cx - radius), int(cy - radius), int(radius * 2), int(radius * 2))

        # Render Azimuthal Grid if enabled
        if self.show_az_grid:
            painter.setPen(QPen(QColor(30, 50, 80), 1, Qt.DashLine))
            for alt_deg in [30, 60]:
                r_grid = radius * (1.0 - alt_deg / 90.0)
                painter.drawEllipse(int(cx - r_grid), int(cy - r_grid), int(r_grid * 2), int(r_grid * 2))
                painter.setPen(QColor(120, 140, 170))
                painter.setFont(QFont("Arial", 8))
                tx, ty = self._proj(cx + 4, cy - r_grid, cx)
                painter.drawText(int(tx), int(ty), f"Alt {alt_deg}°")
                painter.setPen(QPen(QColor(30, 50, 80), 1, Qt.DashLine))

            painter.setPen(QPen(QColor(35, 55, 85), 1, Qt.DotLine))
            for az_deg in range(0, 360, 45):
                az_rad = np.radians(az_deg)
                x2 = cx + radius * np.sin(az_rad)
                y2 = cy - radius * np.cos(az_rad)
                px1, py1 = self._proj(cx, cy, cx)
                px2, py2 = self._proj(x2, y2, cx)
                painter.drawLine(int(px1), int(py1), int(px2), int(py2))

                lx = cx + (radius + 12) * np.sin(az_rad)
                ly = cy - (radius + 12) * np.cos(az_rad)
                plx, ply = self._proj(lx, ly, cx)
                painter.setPen(QColor(140, 160, 190))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(int(plx - 10), int(ply + 4), f"{az_deg}°")
                painter.setPen(QPen(QColor(35, 55, 85), 1, Qt.DotLine))

        # Draw cardinal directions
        painter.setFont(QFont("Arial", 11, QFont.Bold))
        painter.setPen(QColor(200, 200, 220))
        n_pos = self._proj(cx - 10, cy - radius - 10, cx)
        e_pos = self._proj(cx + radius + 10, cy + 5, cx)
        s_pos = self._proj(cx - 10, cy + radius + 20, cx)
        w_pos = self._proj(cx - radius - 30, cy + 5, cx)
        
        painter.drawText(int(n_pos[0]), int(n_pos[1]), "N (0°)")
        painter.drawText(int(e_pos[0]), int(e_pos[1]), "E (90°)" if not self.show_mirrored else "E (90°) [Left]")
        painter.drawText(int(s_pos[0]), int(s_pos[1]), "S (180°)")
        painter.drawText(int(w_pos[0]), int(w_pos[1]), "W (270°)")

        # Render Meridian Line if enabled
        if self.show_meridian:
            painter.setPen(QPen(QColor(100, 150, 200, 150), 1.5, Qt.DashDotLine))
            mer_alts = np.linspace(0, 90, 46)
            mer_azs_n = np.zeros_like(mer_alts)
            r_n = radius * (1.0 - mer_alts / 90.0)
            mx_n = cx + r_n * np.sin(np.radians(mer_azs_n))
            my_n = cy - r_n * np.cos(np.radians(mer_azs_n))
            for k in range(len(mx_n) - 1):
                p1 = self._proj(mx_n[k], my_n[k], cx)
                p2 = self._proj(mx_n[k+1], my_n[k+1], cx)
                painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))

            mer_azs_s = np.full_like(mer_alts, 180.0)
            r_s = radius * (1.0 - mer_alts / 90.0)
            mx_s = cx + r_s * np.sin(np.radians(mer_azs_s))
            my_s = cy - r_s * np.cos(np.radians(mer_azs_s))
            for k in range(len(mx_s) - 1):
                p1 = self._proj(mx_s[k], my_s[k], cx)
                p2 = self._proj(mx_s[k+1], my_s[k+1], cx)
                painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))

        # Render Celestial Equator Line if enabled (Dec = 0 across RA 0-360)
        if self.show_celestial_equator:
            painter.setPen(QPen(QColor(80, 200, 180, 200), 1.5, Qt.SolidLine))
            ce_ras = np.linspace(0, 360, 145)
            ce_decs = np.zeros_like(ce_ras)
            ce_alts, ce_azs = self.engine.get_altaz(ce_ras, ce_decs, self.obstime)
            vis = ce_alts > 0
            if np.any(vis):
                ce_az_rad = np.radians(ce_azs[vis])
                ce_r = radius * (1.0 - ce_alts[vis] / 90.0)
                cx_pts = cx + ce_r * np.sin(ce_az_rad)
                cy_pts = cy - ce_r * np.cos(ce_az_rad)
                for k in range(len(cx_pts) - 1):
                    p1 = self._proj(cx_pts[k], cy_pts[k], cx)
                    p2 = self._proj(cx_pts[k+1], cy_pts[k+1], cx)
                    painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))

        # Render Equatorial Grid if enabled
        if self.show_eq_grid:
            painter.setPen(QPen(QColor(40, 90, 90, 140), 1, Qt.DashLine))
            for dec_line in [-60, -30, 30, 60]:
                ras = np.linspace(0, 360, 73)
                decs = np.full_like(ras, dec_line)
                d_alts, d_azs = self.engine.get_altaz(ras, decs, self.obstime)
                vis = d_alts > 0
                if np.any(vis):
                    d_az_rad = np.radians(d_azs[vis])
                    d_r = radius * (1.0 - d_alts[vis] / 90.0)
                    dx = cx + d_r * np.sin(d_az_rad)
                    dy = cy - d_r * np.cos(d_az_rad)
                    for k in range(len(dx) - 1):
                        p1 = self._proj(dx[k], dy[k], cx)
                        p2 = self._proj(dx[k+1], dy[k+1], cx)
                        painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
                
                # Label Declination degrees
                if len(d_alts) > 0 and d_alts[0] > 0:
                    px, py = self._proj(cx + radius * (1.0 - d_alts[0]/90.0) * np.sin(np.radians(d_azs[0])), 
                                        cy - radius * (1.0 - d_alts[0]/90.0) * np.cos(np.radians(d_azs[0])), cx)
                    painter.setPen(QColor(100, 180, 180))
                    painter.setFont(QFont("Arial", 7))
                    painter.drawText(int(px), int(py), f"Dec {dec_line}°")
                    painter.setPen(QPen(QColor(40, 90, 90, 140), 1, Qt.DashLine))

            for ra_line in range(0, 360, 30):
                decs = np.linspace(-80, 80, 33)
                ras = np.full_like(decs, ra_line)
                r_alts, r_azs = self.engine.get_altaz(ras, decs, self.obstime)
                vis = r_alts > 0
                if np.any(vis):
                    r_az_rad = np.radians(r_azs[vis])
                    r_r = radius * (1.0 - r_alts[vis] / 90.0)
                    rx = cx + r_r * np.sin(r_az_rad)
                    ry = cy - r_r * np.cos(r_az_rad)
                    for k in range(len(rx) - 1):
                        p1 = self._proj(rx[k], ry[k], cx)
                        p2 = self._proj(rx[k+1], ry[k+1], cx)
                        painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
                
                if len(r_alts) > 0 and r_alts[0] > 0:
                    px, py = self._proj(cx + radius * (1.0 - r_alts[0]/90.0) * np.sin(np.radians(r_azs[0])), 
                                        cy - radius * (1.0 - r_alts[0]/90.0) * np.cos(np.radians(r_azs[0])), cx)
                    painter.setPen(QColor(80, 160, 160))
                    painter.setFont(QFont("Arial", 7))
                    painter.drawText(int(px), int(py), f"RA {ra_line}°")
                    painter.setPen(QPen(QColor(40, 90, 90, 140), 1, Qt.DashLine))

        # Compute Alt/Az for all stars
        alts, azs = self.engine.get_altaz(self.catalog.ra, self.catalog.dec, self.obstime)

        # Precompute screen positions for stars
        az_rad = np.radians(azs)
        r_dist = radius * (1.0 - alts / 90.0)
        sx = cx + r_dist * np.sin(az_rad)
        sy = cy - r_dist * np.cos(az_rad)

        # Render North Celestial Pole (NCP)
        ncp_alt, ncp_az = self.engine.get_altaz(np.array([0.0]), np.array([90.0]), self.obstime)
        if ncp_alt[0] > 0:
            ncp_r = radius * (1.0 - ncp_alt[0] / 90.0)
            ncp_az_rad = np.radians(ncp_az[0])
            ncp_x = cx + ncp_r * np.sin(ncp_az_rad)
            ncp_y = cy - ncp_r * np.cos(ncp_az_rad)
            pncp = self._proj(ncp_x, ncp_y, cx)
            
            painter.setPen(QPen(QColor(255, 120, 120), 1.5))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(int(pncp[0] - 6), int(pncp[1] - 6), 12, 12)
            painter.drawLine(int(pncp[0] - 10), int(pncp[1]), int(pncp[0] + 10), int(pncp[1]))
            painter.drawLine(int(pncp[0]), int(pncp[1] - 10), int(pncp[0]), int(pncp[1] + 10))
            painter.setPen(QColor(255, 180, 180))
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.drawText(int(pncp[0] + 12), int(pncp[1] + 4), "NCP")

        # Render Constellation lines if enabled
        if self.show_constellations:
            painter.setPen(QPen(QColor(70, 100, 140, 160), 1.5, Qt.SolidLine))
            for star1_name, star2_name in self.catalog.constellation_lines:
                if star1_name in self.catalog.name_to_idx and star2_name in self.catalog.name_to_idx:
                    idx1 = self.catalog.name_to_idx[star1_name]
                    idx2 = self.catalog.name_to_idx[star2_name]
                    if alts[idx1] > 0 and alts[idx2] > 0:
                        p1 = self._proj(sx[idx1], sy[idx1], cx)
                        p2 = self._proj(sx[idx2], sy[idx2], cx)
                        painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))

        # Render Nebulae / DSOs
        neb_ra = np.array([n[1] for n in self.catalog.nebulae])
        neb_dec = np.array([n[2] for n in self.catalog.nebulae])
        neb_alts, neb_azs = self.engine.get_altaz(neb_ra, neb_dec, self.obstime)
        
        for i, (name, ra, dec, ntype, rad_deg) in enumerate(self.catalog.nebulae):
            alt = neb_alts[i]
            az = neb_azs[i]
            if alt > 0:
                n_az_rad = np.radians(az)
                n_r = radius * (1.0 - alt / 90.0)
                nx = cx + n_r * np.sin(n_az_rad)
                ny = cy - n_r * np.cos(n_az_rad)
                pn = self._proj(nx, ny, cx)
                
                painter.setPen(QPen(QColor(220, 100, 200, 200), 1, Qt.DashLine))
                painter.setBrush(QBrush(QColor(200, 100, 200, 30)))
                sz = max(10, int(rad_deg * 15 * self.zoom))
                painter.drawEllipse(int(pn[0] - sz/2), int(pn[1] - sz/2), sz, sz)
                
                painter.setPen(QColor(240, 180, 240))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(int(pn[0] + sz/2 + 4), int(pn[1]), name)

        # Render stars above horizon (alt > 0)
        visible_mask = alts > 0
        if np.any(visible_mask):
            vis_indices = np.where(visible_mask)[0]
            for i in vis_indices:
                x, y = sx[i], sy[i]
                mag = self.catalog.mag[i]
                name = self.catalog.names[i]

                px, py = self._proj(x, y, cx)
                size = max(1.5, 5.0 - mag * 0.7)
                
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(240, 245, 255, int(min(255, max(100, 255 - mag * 30))))))
                painter.drawEllipse(int(px - size/2), int(py - size/2), int(max(2, size)), int(max(2, size)))

                if mag < 1.5:
                    painter.setPen(QColor(180, 200, 230))
                    painter.setFont(QFont("Arial", 9))
                    painter.drawText(int(px + 6), int(py + 4), name)

        # Draw status info on top left
        painter.setPen(QColor(220, 220, 220))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(20, 30, f"Time (UTC): {self.obstime.strftime('%Y-%m-%d %H:%M:%S')}")
        painter.drawText(20, 50, f"Location: Lat {self.engine.lat:.2f}°, Lon {self.engine.lon:.2f}°")
        if self.show_mirrored:
            painter.drawText(20, 70, "[Stellarium View: Mirrored E/W]")
