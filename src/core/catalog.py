import numpy as np

class StarCatalog:
    def __init__(self):
        # A curated list of prominent bright stars for MVP
        # Format: (name, ra_deg, dec_deg, magnitude, spectral_type)
        self.raw_stars = [
            ("Sirius", 101.28715, -16.71612, -1.46, "A1V"),
            ("Canopus", 95.98792, -52.69566, -0.74, "F0II"),
            ("Arcturus", 213.91530, 19.18241, -0.05, "K1III"),
            ("Alpha Centauri", 219.90210, -60.83398, -0.27, "G2V"),
            ("Vega", 279.23473, 38.78369, 0.03, "A0V"),
            ("Capella", 79.17233, 45.99801, 0.08, "G8III"),
            ("Rigel", 78.63447, -8.20164, 0.12, "B8Iae"),
            ("Procyon", 114.82549, 5.22493, 0.38, "F5IV-V"),
            ("Betelgeuse", 88.79294, 7.40706, 0.50, "M1Ib"),
            ("Achernar", 24.42852, -57.23675, 0.45, "B3V"),
            ("Hadar", 210.95581, -60.37303, 0.61, "B1III"),
            ("Altair", 297.69582, 8.86832, 0.77, "A7V"),
            ("Acrux", 186.64958, -63.09909, 0.77, "B0.5IV"),
            ("Aldebaran", 68.98016, 16.50930, 0.85, "K5III"),
            ("Antares", 247.35192, -26.43200, 0.96, "M1.5Iab"),
            ("Spica", 201.29825, -11.16132, 0.98, "B1V"),
            ("Pollux", 116.32896, 28.02621, 1.14, "K0III"),
            ("Fomalhaut", 344.41269, -29.62223, 1.17, "A3V"),
            ("Deneb", 310.35798, 45.28034, 1.25, "A2Ia"),
            ("Mimosa", 191.93042, -59.68875, 1.25, "B0.5III"),
            ("Regulus", 152.09297, 11.96721, 1.35, "B7V"),
            ("Adhara", 104.65645, -28.97208, 1.50, "B2II"),
            ("Castor", 113.64941, 31.88829, 1.58, "A1V"),
            ("Gacrux", 187.79129, -57.11321, 1.64, "M3.5III"),
            ("Shaula", 263.41583, -37.10382, 1.62, "B2IV"),
            ("Polaris", 37.95456, 89.26411, 1.98, "F7Ib"),
            # Additional stars for constellations
            ("Dubhe", 165.932, 61.751, 1.79, "K0III"),
            ("Merak", 165.460, 56.382, 2.37, "A1V"),
            ("Phecda", 178.457, 53.692, 2.44, "A0V"),
            ("Megrez", 183.855, 57.033, 3.31, "A3V"),
            ("Alioth", 193.507, 55.959, 1.77, "A0p"),
            ("Mizar", 200.971, 54.925, 2.23, "A2V"),
            ("Alkaid", 206.885, 49.313, 1.86, "B3V"),
            ("Bellatrix", 81.283, 6.349, 1.64, "B2III"),
            ("Alnilam", 84.053, -1.201, 1.70, "B0Iab"),
            ("Alnitak", 85.189, -1.942, 1.77, "O9.5Ib"),
            ("Saiph", 86.939, -9.669, 2.07, "B0.5Iab"),
        ]
        
        # Generate some synthetic background random stars to enrich the MVP view
        np.random.seed(42)
        for i in range(500):
            name = f"Star {i+1}"
            ra = np.random.uniform(0, 360)
            dec = np.random.uniform(-90, 90)
            mag = np.random.uniform(2.0, 6.5)
            spec = "G0"
            self.raw_stars.append((name, ra, dec, mag, spec))

        self.names = [s[0] for s in self.raw_stars]
        self.ra = np.array([s[1] for s in self.raw_stars])
        self.dec = np.array([s[2] for s in self.raw_stars])
        self.mag = np.array([s[3] for s in self.raw_stars])
        self.spectral = [s[4] for s in self.raw_stars]

        # Map star name to index for constellation lines
        self.name_to_idx = {name: idx for idx, name in enumerate(self.names)}

        # Constellation lines defined by pairs of star names
        self.constellation_lines = [
            # Big Dipper (Ursa Major)
            ("Dubhe", "Merak"),
            ("Merak", "Phecda"),
            ("Phecda", "Megrez"),
            ("Megrez", "Dubhe"),
            ("Megrez", "Alioth"),
            ("Alioth", "Mizar"),
            ("Mizar", "Alkaid"),
            # Orion
            ("Betelgeuse", "Bellatrix"),
            ("Bellatrix", "Rigel"),
            ("Rigel", "Saiph"),
            ("Saiph", "Alnitak"),
            ("Alnitak", "Alnilam"),
            ("Alnilam", "Betelgeuse"), # simplified stick
            ("Alnitak", "Betelgeuse"),
        ]

        # Common Nebulae & DSOs: (Name, RA_deg, Dec_deg, type, radius_deg)
        self.nebulae = [
            ("Orion Nebula (M42)", 83.822, -5.391, "Emission Nebula", 1.0),
            ("Crab Nebula (M1)", 83.633, 22.0145, "Supernova Remnant", 0.5),
            ("Andromeda Galaxy (M31)", 10.684, 41.269, "Galaxy", 1.5),
            ("Ring Nebula (M57)", 283.396, 33.029, "Planetary Nebula", 0.4),
            ("Lagoon Nebula (M8)", 271.079, -24.383, "Emission Nebula", 1.2),
        ]
