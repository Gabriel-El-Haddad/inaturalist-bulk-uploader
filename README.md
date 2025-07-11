# 🦋 iNaturalist Bulk Uploader

A simple Python tool (utilizing [pyinaturalist](https://github.com/pyinat/pyinaturalist)) to upload folders of photos to [iNaturalist](https://www.inaturalist.org/) as individual observations, automatically assigning species names, timestamps, and attaching media.

Each folder is treated as one observation, using the folder name as the taxon name.

---

## 📦 Features

- 🔁 Batch upload photos from folders
- 🏷️ Automatically assigns taxon using folder name
- 🕓 Uses EXIF or file modified time as observation date
- 🖼️ Supports `.jpg`, `.jpeg`, and `.png`
- ✅ Compatible with macOS, Linux, and Windows

---

## 🧰 Requirements

- Python 3.8+
- iNaturalist account (with a valid [API token](https://www.inaturalist.org/users/api_token))
- Photos organized into folders by species


## 🚀 Getting Started

### 1. Clone the repository

```
git clone https://github.com/yourusername/inat-bulk-uploader.git
cd inat-bulk-uploader
```

### 2. Configure your environment

- Copy the `.env.dist` file to `.env`:
```
cp .env.dist .env
```
- Edit .env and provide your values (use a valid [API token](https://www.inaturalist.org/users/api_token)):
```
INAT_ACCESS_TOKEN=your_access_token_here
PHOTO_ROOT=/full/path/to/folder/of/folders (With the desired folder structure - see below)
```
#### 📁 Folder Structure

```
PHOTO_ROOT/
├── Monarch Butterfly/
│   ├── monarch1.jpg
│   └── monarch2.jpg
├── Milkweed/
│   ├── milkweed1.png
│   └── milkweed2.png
```
- Each subfolder is uploaded as one observation.
- Folder names are used to guess the species. (If no taxon match is found, the folder name will be used as a fallback)

### 3. Set up a virtual environment

#### On macOS / Linux:
```
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```
#### On windows
```
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```
Once activated, your terminal should show (venv) at the beginning of the prompt. This means the virtual environment is active.

⚠ **Complete the following steps in your virtual environment** - this helps avoid package conflicts and system-wide issues.

### 4. Install the dependencies

```
pip install python-dotenv pyinaturalist exifread
```

### 5. Running the Script

Once setup is complete, just run:
```
python upload_folders_to_inat.py
```
You’ll see logs for each folder, including matched taxa, upload success, and observation URLs.

### 📝 License
MIT License. Feel free to fork, use, and adapt the code.

