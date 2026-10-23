import datetime
import numpy as np
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
from astropy.time import Time
import astropy.units as u

class AstronomyEngine:
    def __init__(self, lat: float = 40.0, lon: float = -75.0, elevation: float = 0.0):
        """
        Initialize the astronomy engine with observer location.
        :param lat: Latitude in degrees (-90 to +90)
        :param lon: Longitude in degrees (-180 to +180)
        :param elevation: Elevation in meters
        """
        self.lat = lat
        self.lon = lon
        self.elevation = elevation
        self.update_location(lat, lon, elevation)

    def update_location(self, lat: float, lon: float, elevation: float):
        self.lat = lat
        self.lon = lon
        self.elevation = elevation
        self.location = EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=elevation * u.m)

    def get_altaz(self, ra_deg: np.ndarray, dec_deg: np.ndarray, obstime: datetime.datetime) -> tuple[np.ndarray, np.ndarray]:
        """
        Convert ICRS RA/Dec coordinates to Horizon Alt/Az for the given observer and time.
        :param ra_deg: Right Ascension in degrees (array or float)
        :param dec_deg: Declination in degrees (array or float)
        :param obstime: timezone-aware or UTC datetime object
        :return: (altitude_deg, azimuth_deg)
        """
        t = Time(obstime)
        altaz_frame = AltAz(obstime=t, location=self.location)
        
        coord = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame='icrs')
        coord_altaz = coord.transform_to(altaz_frame)
        
        return coord_altaz.alt.deg, coord_altaz.az.deg
