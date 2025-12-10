# HRT Tracker v1.0.0 / Still in progress..........

A simple, user-friendly Hormone Replacement Therapy (HRT) tracking application built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). Log, review, and filter your HRT doses and notes in a modern desktop interface.

## Features

- **Log HRT Doses:** Add date, time, medication, dose, route, and notes for each dose.
- **Multiple Medications:** Add multiple medications and doses per entry.
- **Edit & Delete:** Edit or remove any entry from your log.
- **Filtering:** Search and filter entries by date range or text.
- **Export:** Data is saved locally in JSON format for privacy and easy backup.
- **Modern UI:** Clean, dark-themed interface using CustomTkinter.

## Installation

1. **Clone or Download** this repository to your computer.

2. **Install Python 3.8+** if you don't have it already.

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   The only required package is:
   ```
   customtkinter
   ```

## Usage

1. Navigate to the app directory:
   ```sh
   cd "HRT Tracker v1.0.0/HRT Tracker/.pyrunner"
   ```

2. Run the app:
   ```sh
   python main.py
   ```

3. The main window will open. Use the form on the left to log new HRT doses. Your entries will appear in the table on the right.

## Data Storage

- All entries are saved in `hrt_entries.json` in the same folder as `main.py`.
- No data is sent online; everything is stored locally for privacy.

## Building an Executable

This project can be packaged as a standalone executable using PyInstaller. The `build/` folder contains artifacts from such a build. To build yourself:

```sh
pip install pyinstaller
pyinstaller main.spec
```

## Requirements

- Python 3.8 or newer
- customtkinter

## License

TBD(to be determand)
---

*Generated with [PyUIbuilder](https://pyuibuilder.com) and CustomTkinter.*