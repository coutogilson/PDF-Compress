# PDF-Compress

[🇧🇷 Português](README.md) | 🇺🇸 **English**

PDF compressor with a graphical interface, using **GhostScript** or **PyMuPDF** as the compression engine, with automatic fallback between them.

Ideal for reducing the size of heavy PDFs (banners, scanned documents, presentations) without losing visual content.

## Features

- 🖥️ Simple graphical interface (Windows and Linux)
- 🔧 **3 compression methods**:
  - **Automatic** — tries GhostScript first; if unavailable, falls back to Python (PyMuPDF)
  - **GhostScript** — professional compression with quality profiles (`/prepress`, `/printer`, `/ebook`, `/screen`)
  - **Python (PyMuPDF)** — rasterizes pages at the chosen DPI and recompresses as JPEG (no GhostScript required)
- 🎚️ **JPEG quality** (50–95%) and **DPI** (72–300) controls
- 🎨 Optional color optimization (reduces to 256 colors)
- 📊 Detailed log with original size, compressed size and reduction percentage

## Prerequisites

| Requirement | Windows | Linux |
|---|---|---|
| Python 3.10+ | ✅ | ✅ |
| tkinter | Included in the Python installer | `sudo apt install python3-tk` |
| GhostScript | **Optional** ([download](https://ghostscript.com/releases/gsdnld.html)) | **Optional** (`sudo apt install ghostscript`) |

> 💡 GhostScript is **optional**: without it, the Python method (PyMuPDF) works normally.

## Install and run (from source)

### Windows

```powershell
git clone https://github.com/coutogilson/PDF-Compress.git
cd PDF-Compress
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Linux

```bash
git clone https://github.com/coutogilson/PDF-Compress.git
cd PDF-Compress
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Executables (no Python required)

Download the latest version from the [Releases](https://github.com/coutogilson/PDF-Compress/releases) page:

| File | Platform | Usage |
|---|---|---|
| `PDF-Compress-windows-x64.exe` | Windows 10/11 (64-bit) | Run directly, no installation |
| `PDF-Compress-linux-x64.AppImage` | Linux (64-bit) — **recommended** | `chmod +x PDF-Compress-linux-x64.AppImage && ./PDF-Compress-linux-x64.AppImage` |
| `PDF-Compress-linux-x64` | Linux (64-bit) — plain binary | `chmod +x PDF-Compress-linux-x64 && ./PDF-Compress-linux-x64` |

> 💡 The **AppImage** is portable and integrates with the applications menu (with icon) when using tools like [AppImageLauncher](https://github.com/TheAssassin/AppImageLauncher).

### ⚠️ Windows SmartScreen warning

When downloading the `.exe` from the browser, Windows may show **"Windows protected your PC"**. This happens because the executable is new and **does not have a digital code signature** (paid certificate) — **it is not a virus**.

To run it anyway:

1. Click **"More info"**
2. Click **"Run anyway"**

**To make sure the file is legitimate:** compare the SHA-256 hash of the downloaded file with the one published on the Release page:

```powershell
Get-FileHash .\PDF-Compress-windows-x64.exe -Algorithm SHA256
```

**Warning-free alternative (recommended):** install via **winget** (Microsoft's official package manager), which validates the package:

```powershell
winget install coutogilson.PDF-Compress
```

> 💡 Over time and with download volume, the file's reputation grows in SmartScreen and the warning disappears naturally.

## How it works

| Method | Pros | Cons |
|---|---|---|
| **GhostScript** | Fast, preserves vector text, professional profiles | Requires external installation |
| **Python (PyMuPDF)** | No external dependencies, preserves exact page dimensions | Converts pages to images (text is no longer selectable); slower on large PDFs |

In **Automatic** mode, the app detects GhostScript (in PATH or `C:\Program Files\gs`) and falls back to PyMuPDF if needed.

## Security

- The app only reads and writes the PDF files chosen by the user — no data is sent over the network.
- No credentials or secrets are required to run or build.

## License

Distributed under the [GPL v3](LICENSE) license.
