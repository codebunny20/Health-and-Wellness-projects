# Universal Medication Tracker v1.0.0

A flexible, privacy‑focused desktop application for tracking **any** medications, supplements, or treatments.  
Built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), it helps you log doses, schedules, and notes in a modern local‑only interface.

Use it to keep a clear history of what you take, when you take it, and how you feel.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Using the Application](#using-the-application)
  - [Adding a New Entry](#adding-a-new-entry)
  - [Viewing & Editing Entries](#viewing--editing-entries)
  - [Deleting Entries](#deleting-entries)
  - [Filtering & Searching](#filtering--searching)
- [Data Storage & Format](#data-storage--format)
- [Configuration & Customization](#configuration--customization)
- [Exporting & Backup](#exporting--backup)
- [Building the Standalone Executable](#building-a-standalone-executable)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)
- [Roadmap / Future Ideas](#roadmap--future-ideas)
- [License](#license)
- [Credits](#credits)

---

## Features

- **Universal Medication / Supplement Log**  
  Track any type of medication, supplement, or treatment:
  - Name (e.g. `Metformin`, `Vitamin D`, `Ibuprofen`)
  - Dose (`500 mg`, `10 ml`, `1 tablet`)
  - Route (`oral`, `IM`, `SC`, `inhalation`, `topical`, etc.)
  - Frequency / schedule notes (e.g. `BID`, `once daily`, `as needed`)

- **Multiple Medications per Entry**  
  Log several medications taken at the same date/time as one combined entry (e.g. morning meds pack).

- **Flexible Notes Field**  
  Add free‑text notes for:
  - Symptoms or side effects
  - Context (with food, missed dose, extra dose)
  - Doctor’s instructions or changes

- **Search & Filtering**  
  Filter your log by:
  - Date or date range
  - Medication name
  - Route / dose text
  - Keywords in notes

- **Edit & Delete**  
  Correct mistakes or remove obsolete entries at any time.

- **Local JSON Storage**  
  All data is stored in a JSON file on your disk:
  - No accounts, no internet requirement
  - Easy to back up and inspect manually
  - Human‑readable and portable

- **Modern Dark UI**  
  Uses CustomTkinter for a clean, dark‑themed appearance with responsive layout.

---

## How It Works

Conceptually, the tracker is split into two main areas:

- **Left side** – Entry form:
  - Date & time inputs
  - Patient / profile (optional, if multi‑user support is added)
  - One or more medication rows: name, dose, route
  - Notes area

- **Right side** – Entries table/list:
  - Shows past doses with compact info (date, time, meds summary, key notes)
  - Supports selection, filtering, and editing

Runtime behavior:

1. On startup:
   - The app looks for a JSON data file (e.g. `med_entries.json`) in the runner directory.
   - If it exists and is valid, all entries are loaded into memory.
   - The right‑hand table is populated with these entries.

2. When you **add** or **edit** an entry:
   - The in‑memory list is updated.
   - The full list of entries is written back to the JSON file (simple overwrite).

3. When you **delete** an entry:
   - It is removed from the in‑memory list.
   - The JSON file is rewritten without that entry.

There is no background sync or cloud component. Everything is explicit and local.

---

## Installation

1. **Download or clone** this project:

   ```sh
   git clone "<your-repo-url>.git"
   cd "universal medication tracker v1.0.0"
   ```

2. **Install Python 3.8+**  
   Download from [python.org](https://www.python.org/downloads/) and ensure `python` (or `python3`) is available in your terminal.

3. **Create and activate a virtual environment (recommended):**

   ```sh
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # source .venv/bin/activate   # macOS / Linux
   ```

4. **Install dependencies:**

   If a `requirements.txt` file is present:

   ```sh
   pip install -r requirements.txt
   ```

   Otherwise, at minimum:

   ```sh
   pip install customtkinter
   ```

   Additional optional packages (if you add them) might include:
   - `tkcalendar` for date pickers
   - `pydantic` or `dataclasses` utilities for data modeling

---

## Running the Application

The exact layout of your project may differ. A common pattern (mirroring your HRT/Journal projects) is:

```text
universal medication tracker v1.0.0/
├─ README.md
└─ Universal Medication Tracker/
   └─ .pyrunner/
      └─ main.py
```

From the project root, run:

```sh
cd "Universal Medication Tracker/.pyrunner"
python main.py
```

- Adjust paths or filenames if your structure is different.
- A window titled something like “Universal Medication Tracker” should appear.

If the window does not open or an exception occurs, see [Troubleshooting](#troubleshooting).

---

## Using the Application

### Adding a New Entry

1. Open the application.

2. Locate the **entry form** (usually on the left):

   Typical fields:

   - **Date** – defaults to today in many implementations.
   - **Time** – optional or defaulted to current time.
   - **Medications list** – one or more rows with:
     - Medication name
     - Dose (text)
     - Route (dropdown or text)
   - **Notes** – free text.

   In some UIs you may have:
   - An **“Add medication row”** button for multiple meds in one entry.
   - A **Patient/Profile** selector if multi‑user tracking is implemented.

3. Fill out at least the required fields (commonly date, medication name, and dose).

4. Click **Add**, **Save**, or **Create Entry** (name varies by UI).

5. The entry appears in the **entries table** on the right with a summary like:

   - `2025-01-12 08:30 – Metformin 500 mg (oral); Vitamin D 2000 IU (oral)`

### Viewing & Editing Entries

1. In the entries table:

   - Click a row once to select it.
   - Or double‑click to open it for editing (if implemented).

2. Click the **Edit** button or similar control.

3. The selected entry’s details are loaded back into the entry form:
   - Date / time
   - All medications in that entry
   - Notes

4. Modify any fields you need (e.g. corrected dose, added med, updated notes).

5. Click **Save** / **Update** to commit changes:

   - The table refreshes with the updated values.
   - The JSON file is rewritten with the modified entry.

### Deleting Entries

1. Select one or more entries in the table.

2. Click **Delete** (or use a trash icon / context menu, depending on your UI).

3. Confirm the delete if a confirmation dialog opens.

4. The entry/entries are removed from:

   - The in‑memory list.
   - The JSON data file on disk.

> If you support multi‑select, deleting several rows at once will remove all of them from the file.

### Filtering & Searching

Depending on how your interface is wired, you may have:

- **Date or date‑range filter**  
  - Choose a single date to see entries for that day.
  - Specify a start and end date to show everything in that range.

- **Medication filter / search box**  
  - Type a medication name or part of it (e.g. `met`, `vitamin`).
  - The table only shows entries that contain that text in any medication row.

- **Notes search**  
  - Enter keywords like `headache`, `missed`, `with breakfast`.
  - Entries whose notes contain that text remain visible.

Filters affect **only what is displayed**; they do not modify the underlying data.

---

## Data Storage & Format

By default, data is stored in a file such as `med_entries.json` in the same directory as your `main.py` file (often the `.pyrunner` directory).

No online storage, no sync, no external server – just a single JSON file.

A **simple single‑medication per entry** schema might look like:

```json
[
  {
    "id": "5f4b8a01-1234-4567-8901-abcdefabcdef",
    "date": "2025-01-12",
    "time": "08:30",
    "medication": "Metformin",
    "dose": "500 mg",
    "route": "oral",
    "notes": "Taken with breakfast."
  }
]
```

A **multi‑medication per entry** schema might look like:

```json
[
  {
    "id": "e1c9f0e2-0000-1111-2222-333333333333",
    "date": "2025-01-12",
    "time": "08:30",
    "medications": [
      {
        "name": "Metformin",
        "dose": "500 mg",
        "route": "oral"
      },
      {
        "name": "Vitamin D",
        "dose": "2000 IU",
        "route": "oral"
      }
    ],
    "notes": "All morning meds. No side effects."
  }
]
```

> You can safely back up your data by copying this JSON file to another location (external drive, sync folder, etc.).

---

## Configuration & Customization

You can adapt the app to your preferences and workflow.

### Theme & Appearance

CustomTkinter allows dark/light/system themes and multiple color palettes.  
In your main script (pseudo‑example):

```python
# filepath: c:\Users\Admin\OneDrive\Desktop\.WT\universal medication tracker v1.0.0\Universal Medication Tracker\.pyrunner\main.py
# ...existing code...
import customtkinter

customtkinter.set_appearance_mode("dark")          # or "light", "system"
customtkinter.set_default_color_theme("dark-blue") # or "blue", "green", etc.
# ...existing code...
```

You may also scale widgets (e.g. `customtkinter.set_widget_scaling(1.2)`).

### Data File Location

If you prefer storing your log in a specific folder (for example, under `Documents/MedicationTracker`):

```python
# filepath: c:\Users\Admin\OneDrive\Desktop\.WT\universal medication tracker v1.0.0\Universal Medication Tracker\.pyrunner\data.py
# ...existing code...
from pathlib import Path

DATA_DIR = Path.home() / "Documents" / "MedicationTracker"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = DATA_DIR / "med_entries.json"
# Use DATA_FILE for all load/save operations
# ...existing code...
```

This avoids mixing application code and user data.

### Custom Fields

Some ideas for additional fields:

- **Time of day tag** – `morning`, `noon`, `evening`, `bedtime`.
- **Indication / reason** – why you’re taking the medication.
- **Adherence flags** – `missed`, `late`, `partial dose`.
- **Side‑effect rating** – severity scale (1–10).

To add such fields:

1. Update the UI form to include input controls (entries, dropdowns, sliders).
2. Extend the in‑memory data model for each entry.
3. Modify serialization / deserialization to handle the new keys.
4. Add columns or formatting in the entries table.

---

## Exporting & Backup

### Manual Backup

1. Close the application.
2. Find the JSON data file (e.g. `med_entries.json`).
3. Copy it to:
   - Another folder or drive, and/or
   - A secure cloud storage of your choice.

To restore, simply copy it back to the original location.

### Export to CSV / Text / Markdown (optional feature)

If you implement export features, common options are:

- **Export to CSV**  
  Suitable for spreadsheets or importing into other tools.

- **Export to Markdown / Text**  
  Good for human‑readable summaries or archiving.

A typical UX:

- Menu item: **File → Export…**
- Dialog to choose:
  - Format (CSV, TXT, MD)
  - Export all entries, or filter by date range / medication.

Make sure to:

- Escape/quote commas for CSV.
- Sanitize filenames if exporting “one file per entry”.

---

## Building the Standalone Executable

I package the app into a standalone executable using **PyInstaller**.

1. Install PyInstaller:

   ```sh
   pip install pyinstaller
   ```

2. From the directory that contains your `main.py` or `main.spec` (often the `.pyrunner` folder):

   ```sh
   pyinstaller --noconfirm --onefile --windowed main.py
   # or, if you have a spec file:
   pyinstaller main.spec
   ```

3. After the build:

   - `dist/` will contain the executable.
   - `build/` contains temporary files and can be deleted later.

If your app uses icons or extra resources, you may need to:

- Reference them with `sys._MEIPASS` inside the bundled app.
- Add them as **data files** in `main.spec`.

---

## Project Structure

A typical project layout:

```text
universal medication tracker v1.0.0/
├─ README.md                        # This document
├─ requirements.txt                 # Python dependencies (optional)
└─ Universal Medication Tracker/
   └─ .pyrunner/
      ├─ main.py                    # Application entry point
      ├─ med_entries.json           # Data file (created at runtime)
      ├─ main.spec                  # PyInstaller spec (optional)
      ├─ build/                     # PyInstaller build artifacts (optional)
      └─ dist/                      # Generated executables (optional)
```

Your actual names and structure may vary slightly; adjust commands accordingly.

---

## Requirements

- **Python**: 3.8 or newer
- **Core Python package**:
  - `customtkinter`

Optional (depending on your implementation):

- `tkcalendar` – date picker widgets
- `pydantic` or other validation libraries
- `pandas` – if you add advanced CSV export/analysis

Install dependencies via:

```sh
pip install -r requirements.txt
```

Or manually:

```sh
pip install customtkinter
# plus any other packages you use
```

---

## Troubleshooting

- **Window does not open / app exits immediately**
  - Check your Python version:

    ```sh
    python --version
    ```

  - Run the app from a terminal and read the printed error message.
  - Verify that all required packages are installed in the active environment.

- **`ModuleNotFoundError: No module named 'customtkinter'`**
  - Install the package:

    ```sh
    pip install customtkinter
    ```

  - Confirm that the same interpreter/environment runs `main.py`.

- **Entries are not being saved**
  - Ensure the JSON file (e.g. `med_entries.json`) is writable.
  - Check for exceptions in the console when you click **Save**.
  - Confirm that you are not running the app from a location with restricted permissions.

- **JSON file is corrupted or unreadable**
  - Close the app.
  - Make a backup of the corrupted file.
  - Try to open it in a text editor and look for issues:
    - Missing commas
    - Truncated entries
    - Unclosed brackets
  - If not salvageable, you can start anew with a minimal valid JSON:

    ```json
    []
    ```

- **UI layout issues (widgets too small or too large)**
  - Check any scaling calls:

    ```python
    customtkinter.set_widget_scaling(1.0)
    customtkinter.set_window_scaling(1.0)
    ```

  - Try different values (e.g. `1.1`, `0.9`) to match your display.

---

## Roadmap / Future Ideas

Some potential directions for future versions:

- Medication **schedules** with reminders (e.g. next dose time).
- **Adherence reports** (missed / taken on time stats).
- Generated **summaries for healthcare providers** (PDF, Markdown).
- Per‑medication graphs (e.g. dose frequency over time).
- Tagging system (`pain management`, `chronic`, `as needed`).
- Multi‑profile support (e.g. track meds for several people or pets).
- Optional **password protection / encryption** of the JSON file.
- Localization / multi‑language support.
- Better keyboard shortcuts and accessibility features.

---

## License

TBD (to be determined).

> Until a license is specified, treat this project as **all rights reserved**.  
> Do not redistribute or reuse code without the author's permission.

---

## Credits

- UI layout and scaffolding inspired by [PyUIbuilder](https://pyuibuilder.com) (if used).
- Built on [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
- Medication tracking logic, data model, and UI refinements by the project author (Codebunny20).
