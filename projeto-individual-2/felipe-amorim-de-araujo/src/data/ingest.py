# src/data/ingest.py
import requests
import pandas as pd
from pathlib import Path
from io import BytesIO
from PIL import Image
from astroquery.sdss import SDSS
from astropy.coordinates import SkyCoord
import astropy.units as u

SDSS_CUTOUT_URL = "https://skyserver.sdss.org/dr17/SkyServerWS/ImgCutout/getjpeg"

CLASS_MAP = {3: "galaxy", 6: "star", 5: "quasar"}

# Curated sky regions: mix of galaxy-rich and sparse fields
SAMPLE_REGIONS = [
    (180.0,   0.0),   # equatorial field
    (210.0,  54.0),   # near Virgo cluster (galaxy-rich)
    (130.0,  20.0),
    (240.0,  30.0),
    (150.0,  10.0),
    (200.0,  -5.0),
    (170.0,  45.0),
    (190.0,  25.0),
    (220.0,  15.0),
    (160.0,  35.0),
    (230.0,   5.0),
    (140.0,  50.0),
    (250.0,  20.0),
    (175.0,  -2.0),
    (205.0,  60.0),
    (185.0,  40.0),
    (215.0,  -8.0),
    (155.0,  28.0),
    (245.0,  42.0),
    (195.0,  12.0),
]


def query_region(ra: float, dec: float, radius_deg: float = 0.05) -> pd.DataFrame:
    """Query SDSS PhotoObj catalog for objects in a sky region."""
    coord = SkyCoord(ra=ra, dec=dec, unit=u.deg)
    result = SDSS.query_region(
        coordinates=coord,
        radius=radius_deg * u.deg,
        photoobj_fields=["objID", "ra", "dec", "type", "petroRad_r", "psfMag_r", "flags"],
        data_release=17,
    )
    if result is None:
        return pd.DataFrame()

    df = result.to_pandas()
    df = df[df["type"].isin(CLASS_MAP.keys())].copy()
    df = df[df["psfMag_r"] < 22.0]
    df = df[df["flags"] == 0]
    df["class_name"] = df["type"].map(CLASS_MAP)
    return df.reset_index(drop=True)


def download_cutout(
    ra: float,
    dec: float,
    output_path: Path,
    scale: float = 0.2,
    width: int = 640,
    height: int = 640,
) -> Path:
    """Download a JPEG sky cutout centered on (ra, dec)."""
    params = {"ra": ra, "dec": dec, "scale": scale, "width": width, "height": height, "opt": ""}
    response = requests.get(SDSS_CUTOUT_URL, params=params, timeout=30)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img.save(output_path)
    return output_path


def build_dataset(
    output_dir: Path,
    n_regions: int = 20,
    radius_deg: float = 0.05,
    scale: float = 0.2,
) -> dict:
    """Download images for N sky regions. Returns ingestion stats."""
    images_dir = output_dir / "raw"
    images_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped = 0

    for i, (ra, dec) in enumerate(SAMPLE_REGIONS[:n_regions]):
        objects = query_region(ra, dec, radius_deg=radius_deg)
        if objects.empty:
            skipped += 1
            continue

        img_path = images_dir / f"field_{i:04d}.jpg"
        download_cutout(ra, dec, img_path, scale=scale)
        downloaded += 1

    return {"downloaded": downloaded, "skipped": skipped}
