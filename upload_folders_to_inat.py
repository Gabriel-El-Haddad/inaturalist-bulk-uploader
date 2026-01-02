from dotenv import load_dotenv
import os
from pyinaturalist import create_observation, get_taxa
from datetime import datetime
import exifread
from exifread.utils import Ratio

load_dotenv()

access_token = os.getenv("INAT_ACCESS_TOKEN")
PHOTO_ROOT = os.getenv("PHOTO_ROOT")

if not access_token or not PHOTO_ROOT:
    raise ValueError("❌ Missing INAT_ACCESS_TOKEN or PHOTO_ROOT in .env file")


def get_taxon_name_and_id(name: str):
    results = get_taxa(q=name, access_token=access_token)
    if results and "results" in results and len(results["results"]) > 0:
        taxon = results["results"][0]
        print(f"🧬 Matched '{name}' to: {taxon['name']} (ID: {taxon['id']})")
        return taxon["name"], taxon["id"]
    else:
        print(f"❌ No taxon match for '{name}'")
    return None, None


def _ratio_to_float(r):
    if isinstance(r, Ratio):
        return float(r.num) / float(r.den)
    return float(r)


def _dms_to_decimal(dms, ref: str):
    deg = _ratio_to_float(dms[0])
    minutes = _ratio_to_float(dms[1])
    seconds = _ratio_to_float(dms[2])
    dec = deg + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ("S", "W"):
        dec = -dec
    return dec


def get_observed_on_fast(photo_paths):
    """Fast: use earliest file modified time (no EXIF reads)."""
    try:
        earliest = min(os.path.getmtime(p) for p in photo_paths)
        return datetime.fromtimestamp(earliest).isoformat()
    except Exception:
        return datetime.now().isoformat()


def get_first_photo_location_fast(photo_paths, max_scan=5):
    """
    Efficient: scan only the first few photos for GPS EXIF, stop early.
    Increase max_scan if GPS isn't usually in the first photos.
    """
    for path in photo_paths[:max_scan]:
        try:
            with open(path, "rb") as f:
                tags = exifread.process_file(f, details=False)

            lat_tag = tags.get("GPS GPSLatitude")
            lat_ref = tags.get("GPS GPSLatitudeRef")
            lon_tag = tags.get("GPS GPSLongitude")
            lon_ref = tags.get("GPS GPSLongitudeRef")

            if lat_tag and lat_ref and lon_tag and lon_ref:
                lat = _dms_to_decimal(lat_tag.values, str(lat_ref.values))
                lon = _dms_to_decimal(lon_tag.values, str(lon_ref.values))
                return lat, lon
        except Exception:
            continue

    return None, None


def upload_folder_as_observation(folder_path):
    folder_name = os.path.basename(folder_path).replace("_", " ").strip()
    taxon_name, taxon_id = get_taxon_name_and_id(folder_name)

    photos = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not photos:
        print(f"⚠️  No photos found in {folder_path}")
        return

    # Make order deterministic; helps GPS scan hit the “first” photos consistently
    photos.sort()

    # Efficient metadata extraction
    observed_on = get_observed_on_fast(photos)
    lat, lon = get_first_photo_location_fast(photos, max_scan=5)

    try:
        if taxon_id:
            print(f"✅ Using taxon_id={taxon_id} (not just species_guess)")
        else:
            print(f"⚠️  No match found, using folder name as species_guess: {folder_name}")

        if lat is not None and lon is not None:
            print(f"📍 Found GPS EXIF: lat={lat}, lon={lon}")
        else:
            print("⚠️  No GPS EXIF found in first scanned photos (location will be blank)")

        # If we have a match, set a real taxon assignment (not just a placeholder guess)
        if taxon_id:
            create_observation(
                access_token=access_token,
                photos=photos,
                observed_on_string=observed_on,
                description=f"Uploaded from folder: {folder_name}",
                taxon_id=taxon_id,
                latitude=lat,
                longitude=lon,
            )
        else:
            create_observation(
                access_token=access_token,
                photos=photos,
                observed_on_string=observed_on,
                description=f"Uploaded from folder: {folder_name}",
                species_guess=folder_name,
                latitude=lat,
                longitude=lon,
            )

        print(f"✅ Uploaded {folder_name}")

    except Exception as e:
        print(f"❌ Error while uploading '{folder_name}': {e}")


# --- Main loop ---
print(f"\n📂 Scanning folders in: {PHOTO_ROOT}\n")

for folder in os.listdir(PHOTO_ROOT):
    full_path = os.path.join(PHOTO_ROOT, folder)
    if os.path.isdir(full_path):
        print(f"📤 Processing folder: {folder}")
        upload_folder_as_observation(full_path)
        print("-" * 40)

print("✅ Done processing all folders.\n")
