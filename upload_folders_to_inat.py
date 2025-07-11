from dotenv import load_dotenv
import os
from pyinaturalist import create_observation, get_taxa
from datetime import datetime
import exifread

load_dotenv()

access_token = os.getenv('INAT_ACCESS_TOKEN')
PHOTO_ROOT = os.getenv('PHOTO_ROOT')

if not access_token or not PHOTO_ROOT:
    raise ValueError("❌ Missing INAT_ACCESS_TOKEN or PHOTO_ROOT in .env file")


def get_taxon_name_and_id(name: str):
    results = get_taxa(q=name, access_token=access_token)
    if results and 'results' in results and len(results['results']) > 0:
        taxon = results['results'][0]
        print(f"🧬 Matched '{name}' to: {taxon['name']} (ID: {taxon['id']})")
        return taxon['name'], taxon['id']
    else:
        print(f"❌ No taxon match for '{name}'")
    return None, None


def get_earliest_photo_date(photo_paths):
    dates = []
    for path in photo_paths:
        exif_date = None
        try:
            with open(path, 'rb') as f:
                tags = exifread.process_file(f, stop_tag='EXIF DateTimeOriginal', details=False)
                date_str = str(tags.get('EXIF DateTimeOriginal') or tags.get('Image DateTime'))
                if date_str:
                    exif_date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except Exception:
            pass

        if exif_date:
            dates.append(exif_date)
        else:
            try:
                # If PNG file does not have exif data
                mtime = os.path.getmtime(path)
                dates.append(datetime.fromtimestamp(mtime))
            except Exception:
                continue

    if dates:
        return min(dates).isoformat()
    return None


def upload_folder_as_observation(folder_path):
    folder_name = os.path.basename(folder_path).replace("_", " ").strip()
    taxon_name, taxon_id = get_taxon_name_and_id(folder_name)

    photos = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    if not photos:
        print(f"⚠️  No photos found in {folder_path}")
        return

    observed_on = get_earliest_photo_date(photos) or datetime.now().isoformat()

    try:
        if taxon_name:
            print(f"🔎 Using species_guess: {taxon_name}")
        else:
            print(f"⚠️  No match found, using folder name as species_guess: {folder_name}")

        create_observation(
            access_token=access_token,
            photos=photos,
            observed_on_string=observed_on,
            description=f'Uploaded from folder: {folder_name}',
            species_guess=taxon_name or folder_name,
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
