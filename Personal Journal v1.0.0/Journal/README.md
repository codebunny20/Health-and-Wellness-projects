# Personal Journal v1.0.0

A simple, privacy‑focused Personal Journal desktop application built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

Use it to record daily thoughts, events, moods, or any notes you want to keep privately on your own machine. Entries are stored locally in a JSON file for easy backup and manual inspection.

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

- **Daily Journal Entries**  
  Record a title, date, time, and rich text notes for each journal entry.

- **Tags / Categories**  
  Optionally tag entries (e.g. `work`, `friends`, `health`, `goals`) to make them easier to find later.

- **Search & Filtering**  
  Filter entries by:
  - Date or date range
  - Title / body text
  - Tags or keywords

- **Edit & Delete**  
  Update existing entries or remove ones you no longer need.

- **Local JSON Storage**  
  All entries are written to a JSON file on your local disk:
  - No internet / cloud dependency
  - Easy manual backups
  - Human‑readable format

- **Modern Dark UI**  
  Built with CustomTkinter for a minimal, dark‑themed experience with good defaults.

---

## How It Works

- The application opens a **CustomTkinter** main window.
- Typically the layout is:
  - **Left side**: entry editor (date, title, tags, text).
  - **Right side**: list/table of saved entries with basic info (date, title, tags).
- When you create or edit an entry:
  - The entry is stored in memory for the current session.
  - The entire journal dataset is written to a JSON file (e.g. `journal_entries.json`) in the same directory as the main script.
- On startup, the app:
  - Looks for `journal_entries.json`.
  - If it exists and is valid JSON, loads all entries.
  - Populates the list/table so you can browse, search, and edit your existing journal.

---

## Installation

1. **Clone or download** this project to your computer:

   ```sh
   git clone "<your-repo-url>.git"
   cd "Personal Journal v1.0.0"
   ```

2. **Install Python 3.8+**  
   Download from [python.org](https://www.python.org/downloads/) and make sure `python` (or `python3`) is available in your terminal.

3. **Create and activate a virtual environment (recommended):**

   ```sh
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # source .venv/bin/activate   # macOS/Linux
   ```

4. **Install dependencies:**  
   If you have a `requirements.txt`:

   ```sh
   pip install -r requirements.txt
   ```

   Otherwise install at least:

   ```sh
   pip install customtkinter
   ```

---

## Running the Application

From the root of the project (the folder that contains this `Journal` directory):

```sh
cd "Journal"
python main.py
```

- Adjust `main.py` to the actual entry-point file name used in your project.
- A window called something like “Personal Journal” should appear.

If the window does not open or the script exits with an error, see [Troubleshooting](#troubleshooting).

---

## Using the Application

### Adding a New Entry

1. Open the app.
2. Find the **entry form**, usually on the left or top:
   - Date (defaults to today if left blank in some designs).
   - Time (optional, for more precise logging).
   - Title / subject.
   - Tags (comma‑separated list like `work, mood, exercise`).
   - Main text area for your journal content.
3. Fill in at least the required fields (typically title + text).
4. Click **Add**, **Save**, or **Create Entry** (exact label depends on the UI).
5. The new entry will be added to the list/table of entries.

### Viewing & Editing Entries

1. Select an existing entry from the list/table on the right.
2. Either:
   - Click an **Edit** button, or
   - Double‑click the entry row (depending on how your UI is wired).
3. The entry’s data will be loaded into the form.
4. Change any fields you like (date, title, tags, text).
5. Click **Save** or **Update**:
   - The list/table refreshes.
   - The underlying JSON file is updated.

### Deleting Entries

1. Select one entry in the list/table.
2. Click **Delete** (or a trash‑can icon).
3. Confirm the dialog if one appears.
4. The entry is removed:
   - From the on‑screen list/table.
   - From the JSON data file.

> Some variants of the UI may support multi‑select delete (select several entries and delete at once).

### Filtering & Searching

Depending on your implementation, you will typically have one or more of:

- **Date filter**  
  Choose a single date or a start and end date:
  - Only entries within that date or range are shown.
- **Text search**  
  Type text into a search box:
  - Filters entries whose title or body contains the given text.
- **Tag filter**  
  Select a tag from a dropdown or type a tag:
  - Shows only entries containing that tag.

Filters only affect what you see. They **do not** delete or modify entries.

---

## Data Storage & Format

By default, the app stores data in a file like `journal_entries.json` in the same directory as `main.py` (or whichever script is used as the entry point).

No data is uploaded anywhere: it stays on your local disk only.

A typical JSON structure might look like:

```json
[
  {
    "id": "8f7b2a0e-1234-4abc-9876-abcdefabcdef",
    "date": "2025-01-10",
    "time": "21:30",
    "title": "Great day with friends",
    "tags": ["friends", "social"],
    "content": "Met some friends for dinner today. We talked about ..."
  },
  {
    "id": "1d3a9cbe-0000-1111-2222-333333333333",
    "date": "2025-01-11",
    "time": "08:15",
    "title": "Morning reflections",
    "tags": ["morning", "mood"],
    "content": "Feeling more relaxed today. Planning to focus on ..."
  }
]
```

> You can back up your journal by copying this JSON file to another folder, a USB stick, or any backup location.

---

## Configuration & Customization

Common customization points:

### Theme & Appearance

You can change appearance mode (dark/light/system) and color themes in the initialization code, e.g.:

```python
# ...existing code...
import customtkinter

customtkinter.set_appearance_mode("dark")      # "light" or "system"
customtkinter.set_default_color_theme("blue")  # "dark-blue", "green", etc.
# ...existing code...
```

### Data File Location

If you prefer to store your journal data in a custom folder (e.g. `Documents/PersonalJournal`):

1. Create that folder if it does not exist.
2. Update the path used for loading/saving the JSON file, for example:

```python
# ...existing code...
from pathlib import Path

DATA_DIR = Path.home() / "Documents" / "PersonalJournal"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = DATA_DIR / "journal_entries.json"
# use DATA_FILE for all load/save operations
# ...existing code...
```

### Additional Fields

You can extend the schema with additional fields such as:

- Mood rating (1–10).
- Weather.
- Location.
- “Favorite” / starred flag.

This typically requires:

1. Adding new UI widgets to the entry form.
2. Extending the Python data structure representing an entry.
3. Adjusting JSON load/save logic to include the new fields.
4. Updating the entry list/table to display or sort by the new data.

---

## Exporting & Backup

### Manual Backup

- Close the application.
- Make a copy of `journal_entries.json` and store it somewhere safe:
  - Another folder or drive.
  - Cloud backup of your choice (if you are comfortable with that).

### Export to Text / Markdown (optional feature)

If you add export functionality:

- Provide a menu item like **File → Export**.
- Export options might include:
  - All entries to a single `.md` or `.txt` file.
  - One file per entry, named by date + title.
- Be sure to sanitize file names for invalid characters.

---

## Building the Standalone Executable

I package the app into a standalone executable using **PyInstaller**.

1. Install PyInstaller:

   ```sh
   pip install pyinstaller
   ```

2. From the directory that contains your `main.py` (usually `Journal/`), run:

   ```sh
   pyinstaller --noconfirm --onefile --windowed main.py
   ```

   Or, if you have a `.spec` file:

   ```sh
   pyinstaller main.spec
   ```

3. After the build completes:
   - The `dist/` folder will contain the generated executable.
   - The `build/` folder holds intermediate files and can be deleted later.

Note: Paths to icons, themes, or other assets may need to be adjusted in your PyInstaller spec.

---

## Project Structure

A typical layout for this app:

```text
Personal Journal v1.0.0/
├─ README.md                 # High-level project README (optional)
└─ Journal/
   ├─ README.md              # This document
   ├─ main.py                # Application entry point
   ├─ journal_entries.json   # Data file (created at runtime)
   ├─ requirements.txt       # Python dependencies (optional)
   ├─ main.spec              # PyInstaller spec (optional)
   ├─ build/                 # PyInstaller build artifacts (optional)
   └─ dist/                  # Generated executables (optional)
```

> Actual names may differ depending on how you organized your files.

---

## Requirements

- **Python**: 3.8 or newer
- **Python packages**:
  - `customtkinter`
  - Any other packages you added (e.g. `tkcalendar`, `pydantic`, etc.)

Install via:

```sh
pip install -r requirements.txt
```

Or manually:

```sh
pip install customtkinter
```

---

## Troubleshooting

- **Window does not open / script crashes**  
  - Check Python version:

    ```sh
    python --version
    ```

  - Run the script from a terminal and read the error message.
  - Make sure all required packages are installed in the current environment.

- **`ModuleNotFoundError: No module named 'customtkinter'`**  
  - Install the missing package:

    ```sh
    pip install customtkinter
    ```

  - Double‑check that your virtual environment is activated.

- **Entries do not persist between sessions**  
  - Confirm that `journal_entries.json` is being created or updated.
  - Check file permissions in the directory.
  - Ensure the program is not crashing before it writes changes.

- **JSON file is corrupted or invalid**  
  - Close the application.
  - Make a backup copy of the corrupted file.
  - Try to open it in a text editor and fix obvious syntax issues (missing commas, brackets).
  - If not recoverable, start a new file with:

    ```json
    []
    ```

---

## Roadmap / Future Ideas

Potential enhancements:

- Password protection and/or encrypted journal file.
- Rich text formatting (bold, italics, headings) or Markdown preview.
- Attachments support (images, PDFs).
- Automatic backups / versioning of entries.
- Calendar view with per‑day entry summaries.
- Statistics (entries per day/week, mood tracking charts).
- Localization / multi‑language support.
- More keyboard shortcuts and better accessibility.

---

## License

TBD (to be determined).

> Until a license is specified, treat this project as **all rights reserved**.  
> Do not redistribute or reuse code without the author's permission.

---

## Credits

- UI scaffold based on [PyUIbuilder](https://pyuibuilder.com) (if used).
- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
- Journal logic, data model, and UI refinements by the project author (Codebunny20).
