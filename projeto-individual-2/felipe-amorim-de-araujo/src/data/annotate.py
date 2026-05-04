# src/data/annotate.py
"""
Auto-annotation of SDSS sky images using catalog data.

Converts catalog object positions (RA, Dec) to pixel-space bounding boxes,
enabling fine-tuning of YOLOS-small without manual labeling.
"""
import math
import json
from pathlib import Path

from src.data.ingest import query_region, download_cutout

ASTRO_LABEL_MAP = {"star": 0, "galaxy": 1, "quasar": 2}
ASTRO_ID2LABEL = {0: "star", 1: "galaxy", 2: "quasar"}

_TYPE_TO_CLASS = {6: "star", 3: "galaxy", 5: "quasar"}

# ~150 regions covering the SDSS North Galactic Cap footprint (RA 120-260, Dec -5 to 65).
TRAINING_REGIONS: list[tuple[float, float]] = [
    (180.0,   0.0),
    (210.0,  54.0),
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
    (186.0,  11.0),
    (187.0,  13.0),
    (188.0,  15.0),
    (189.0,  17.0),
    (191.0,  11.0),
    (192.0,  13.0),
    (193.0,  15.0),
    (194.0,  17.0),
    (186.5,  12.5),
    (191.5,  14.5),
    (194.5,  27.5),
    (194.0,  28.0),
    (195.0,  27.0),
    (195.5,  28.5),
    (120.0,   0.0),
    (120.0,  10.0),
    (120.0,  20.0),
    (120.0,  30.0),
    (120.0,  40.0),
    (120.0,  50.0),
    (120.0,  60.0),
    (130.0,  -5.0),
    (130.0,   5.0),
    (130.0,  30.0),
    (130.0,  40.0),
    (130.0,  55.0),
    (130.0,  65.0),
    (140.0,   0.0),
    (140.0,  10.0),
    (140.0,  20.0),
    (140.0,  30.0),
    (140.0,  40.0),
    (140.0,  60.0),
    (150.0,  -5.0),
    (150.0,   5.0),
    (150.0,  20.0),
    (150.0,  30.0),
    (150.0,  40.0),
    (150.0,  50.0),
    (150.0,  60.0),
    (160.0,   0.0),
    (160.0,  10.0),
    (160.0,  20.0),
    (160.0,  45.0),
    (160.0,  55.0),
    (165.0,  -3.0),
    (165.0,   7.0),
    (165.0,  17.0),
    (165.0,  27.0),
    (165.0,  37.0),
    (165.0,  47.0),
    (165.0,  57.0),
    (170.0,   0.0),
    (170.0,  10.0),
    (170.0,  20.0),
    (170.0,  30.0),
    (170.0,  55.0),
    (175.0,   5.0),
    (175.0,  15.0),
    (175.0,  25.0),
    (175.0,  50.0),
    (175.0,  60.0),
    (180.0,  10.0),
    (180.0,  20.0),
    (180.0,  30.0),
    (180.0,  40.0),
    (180.0,  55.0),
    (185.0,   0.0),
    (185.0,   5.0),
    (185.0,  20.0),
    (185.0,  30.0),
    (185.0,  50.0),
    (190.0,   0.0),
    (190.0,  10.0),
    (190.0,  30.0),
    (190.0,  40.0),
    (190.0,  55.0),
    (195.0,   0.0),
    (195.0,  20.0),
    (195.0,  35.0),
    (195.0,  45.0),
    (195.0,  60.0),
    (200.0,   5.0),
    (200.0,  15.0),
    (200.0,  25.0),
    (200.0,  35.0),
    (200.0,  45.0),
    (205.0,   0.0),
    (205.0,  10.0),
    (205.0,  20.0),
    (205.0,  30.0),
    (205.0,  50.0),
    (210.0,   0.0),
    (210.0,  10.0),
    (210.0,  20.0),
    (210.0,  30.0),
    (210.0,  45.0),
    (215.0,   5.0),
    (215.0,  15.0),
    (215.0,  25.0),
    (215.0,  40.0),
    (215.0,  55.0),
    (220.0,   0.0),
    (220.0,  25.0),
    (220.0,  35.0),
    (220.0,  50.0),
    (225.0,  10.0),
    (225.0,  20.0),
    (225.0,  30.0),
    (225.0,  45.0),
    (230.0,  15.0),
    (230.0,  25.0),
    (230.0,  40.0),
    (230.0,  55.0),
    (235.0,   5.0),
    (235.0,  15.0),
    (235.0,  30.0),
    (235.0,  50.0),
    (240.0,   0.0),
    (240.0,  10.0),
    (240.0,  40.0),
    (240.0,  55.0),
    (245.0,  15.0),
    (245.0,  25.0),
    (245.0,  55.0),
    (250.0,   5.0),
    (250.0,  30.0),
    (250.0,  45.0),
    (255.0,  10.0),
    (255.0,  25.0),
    (255.0,  40.0),
    (260.0,  15.0),
    (260.0,  35.0),
]


def radec_to_pixel(
    obj_ra: float,
    obj_dec: float,
    center_ra: float,
    center_dec: float,
    scale: float = 0.2,
    width: int = 640,
    height: int = 640,
) -> tuple[float, float]:
    """Convert (RA, Dec) to pixel (x, y) in an SDSS cutout. RA increases left, Dec increases up."""
    dec_rad = math.radians(center_dec)
    delta_ra_arcsec = (obj_ra - center_ra) * 3600.0 * math.cos(dec_rad)
    delta_dec_arcsec = (obj_dec - center_dec) * 3600.0
    px = width / 2.0 - delta_ra_arcsec / scale
    py = height / 2.0 - delta_dec_arcsec / scale
    return px, py


def estimate_half_width_px(
    petro_rad_r: float,
    scale: float = 0.2,
    min_box_px: float = 8.0,
    max_box_px: float = 80.0,
) -> float:
    """Estimate bbox half-width in pixels from Petrosian radius. Falls back to min_box_px for point sources."""
    try:
        if petro_rad_r <= 0 or math.isnan(petro_rad_r):
            return min_box_px
    except (TypeError, ValueError):
        return min_box_px
    radius_px = petro_rad_r / scale
    return max(min_box_px, min(radius_px * 2.0, max_box_px))


def generate_annotations(
    ra: float,
    dec: float,
    radius_deg: float = 0.05,
    scale: float = 0.2,
    width: int = 640,
    height: int = 640,
) -> list[dict]:
    """Return normalized [cx, cy, w, h] bbox annotations for SDSS objects in the field."""
    import pandas as pd

    df = query_region(ra, dec, radius_deg=radius_deg)
    if df.empty:
        return []

    annotations = []
    for _, row in df.iterrows():
        class_name = row["class_name"]
        if class_name not in ASTRO_LABEL_MAP:
            continue

        px, py = radec_to_pixel(
            row["ra"], row["dec"],
            center_ra=ra, center_dec=dec,
            scale=scale, width=width, height=height,
        )

        if not (0 <= px < width and 0 <= py < height):
            continue

        half_w = estimate_half_width_px(float(row["petroRad_r"]), scale=scale)

        x1 = max(0.0, px - half_w)
        y1 = max(0.0, py - half_w)
        x2 = min(float(width), px + half_w)
        y2 = min(float(height), py + half_w)

        cx = (x1 + x2) / 2.0 / width
        cy = (y1 + y2) / 2.0 / height
        bw = (x2 - x1) / width
        bh = (y2 - y1) / height

        annotations.append({
            "bbox": [cx, cy, bw, bh],
            "category_id": ASTRO_LABEL_MAP[class_name],
        })

    return annotations


def build_annotated_dataset(
    output_dir: Path,
    regions: list[tuple[float, float]] | None = None,
    radius_deg: float = 0.05,
    scale: float = 0.2,
    width: int = 640,
    height: int = 640,
) -> dict:
    """Download SDSS cutouts and write annotations.json. Returns summary stats."""
    from src.model.guardrails import validate_input, GuardrailError
    from PIL import Image

    regions = regions or TRAINING_REGIONS
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    metadata: list[dict] = []
    downloaded = skipped_sdss = skipped_guardrail = skipped_no_objects = 0

    for i, (ra, dec) in enumerate(regions):
        annotations = generate_annotations(ra, dec, radius_deg=radius_deg, scale=scale, width=width, height=height)
        if not annotations:
            skipped_no_objects += 1
            continue

        img_path = raw_dir / f"field_{i:04d}.jpg"
        if not img_path.exists():
            try:
                download_cutout(ra, dec, img_path, scale=scale, width=width, height=height)
            except Exception:
                skipped_sdss += 1
                continue

        try:
            validate_input(Image.open(img_path).convert("RGB"))
        except GuardrailError:
            skipped_guardrail += 1
            img_path.unlink(missing_ok=True)
            continue

        metadata.append({
            "image_file": img_path.name,
            "center_ra": ra,
            "center_dec": dec,
            "objects": annotations,
        })
        downloaded += 1

    annotations_path = output_dir / "annotations.json"
    annotations_path.write_text(json.dumps(metadata, indent=2))

    return {
        "downloaded": downloaded,
        "skipped_no_sdss_objects": skipped_no_objects,
        "skipped_sdss_error": skipped_sdss,
        "skipped_guardrail": skipped_guardrail,
        "total_objects": sum(len(m["objects"]) for m in metadata),
        "annotations_path": str(annotations_path),
    }
