# HRT Tracker v1.0.0

A simple, user-friendly Hormone Replacement Therapy (HRT) tracking application built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).  
It lets you log, review, and filter your HRT doses and notes in a modern desktop interface, with all data stored locally for privacy.

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
- [Building the Standalone Executable](#building-a-standalone-executable)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)
- [Roadmap / Future Ideas](#roadmap--future-ideas)
- [License](#license)
- [Credits](#credits)

---

## Features

- **Log HRT Doses**  
  Add date, time, medication, dose, route, and notes for each dose.

- **Multiple Medications per Entry**  
  Support for multiple medications and/or multiple doses in a single log entry.

- **Edit & Delete**  
  Update or remove any existing entry from your log.

- **Filtering & Search**  
  Filter data by:
  - Date or date range
  - Text search (e.g. medication name, notes)

- **Local JSON Storage**  
  Data is stored in a simple JSON file for:
  - Privacy (no network communication)
  - Easy backup and manual inspection

- **Modern Dark UI**  
  Uses CustomTkinter for a clean, dark-themed, native desktop look.

---
## How It Works

- The application starts a **CustomTkinter** window.
- On the left, there is a **form** to add or edit HRT entries.
- On the right, there is a **table/list** of saved entries.
- When you save an entry:
  - It is stored in memory for the running session.
  - It is also persisted to a JSON file (`hrt_entries.json`) in the same directory as `main.py`.
- On startup, the app:
  - Loads existing entries from `hrt_entries.json` (if it exists).
  - Populates the table with all previously saved data.

---

## Installation

1. **Clone or download** this repository to your computer:
   ```sh
   git clone "<your-repo-url>.git"
   cd "HRT Tracker v1.0.0"
   ```

2. **Install Python 3.8+**  
   Download from [python.org](https://www.python.org/downloads/) and ensure `python` (or `python3`) is available in your terminal.

3. **Create and activate a virtual environment (recommended)**:
   ```sh
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # source .venv/bin/activate   # macOS/Linux
   ```

4. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
   The core required package is:
   ```text
   customtkinter
   ```

---

## Running the Application

From the root of this project:

1. Navigate to the app runner directory:
   ```sh
   cd "HRT Tracker/.pyrunner"
   ```

2. Run the main script:
   ```sh
   python main.py
   ```

3. The main window should open.  
   If nothing happens or there is an error, see the [Troubleshooting](#troubleshooting) section.

---

## Using the Application

 1. Adding a New Entry
 In the main window, locate the **input form** (usually on the left side):
   - Date selector / input
   - Time selector / input
   - Medication name
   - Dose (e.g. `2 mg`, `0.5 ml`)
   - Route (e.g. `oral`, `sublingual`, `IM`, `SC`, `patch`)
   - Optional notes (mood, side effects, cycle info, etc.)

2. Fill in the desired fields.

3. Click the **Add** or **Save** button (label may vary depending on UI text) to create the entry.

4. The new entry will appear in the entries table on the right.

### Viewing & Editing Entries

1. Select an entry in the table.
2. Use the **Edit** button (or double-click, depending on implementation) to load the entry back into the form.
3. Adjust any fields you need to change.
4. Confirm the edit to update the entry in both:
   - The table.
   - The underlying JSON file.

### Deleting Entries

1. Select an entry in the table.
2. Click the **Delete** button.
3. Confirm the deletion if a confirmation dialog appears.
4. The entry is removed from:
   - The table.
   - The JSON data file.

### Filtering & Searching

Depending on the current UI:

- **Date filter**:  
  Choose a specific date or a start/end date range to limit visible entries.

- **Text search**:  
  Enter a search term (e.g. `estradiol`, `patch`, `mood`) to filter entries whose fields (medication, notes, etc.) contain that text.

Filters only affect how data is displayed; they do not delete or change the stored entries.

---

## Data Storage & Format

- All entries are saved in `hrt_entries.json` in the same directory as `main.py`.
- No data is sent online; everything is stored locally.

A simplified example of the JSON format:

```json
[
  {
    "id": "e7dbb19a-1234-4567-8901-abcdefabcdef",
    "date": "2025-01-10",
    "time": "08:30",
    "medication": "Estradiol",
    "dose": "2 mg",
    "route": "oral",
    "notes": "Felt normal, no side effects."
  },
  {
    "id": "a5cd932b-0000-1111-2222-333333333333",
    "date": "2025-01-10",
    "time": "21:00",
    "medication": "Spironolactone",
    "dose": "50 mg",
    "route": "oral",
    "notes": "Slightly tired."
  }
]
```

> You can back up or move your data by copying `hrt_entries.json` to a safe location.

---

## Configuration & Customization

Depending on how you extend the app, common customization points include:

- **Theme & appearance**  
  CustomTkinter supports light/dark themes and scaling:
  ```python
  # ...existing code...
  # Example (inside main.py or app setup)
  customtkinter.set_appearance_mode("dark")      # "light" or "system"
  customtkinter.set_default_color_theme("blue")  # "dark-blue", "green", etc.
  # ...existing code...
  ```

- **Default data file path**  
  If you want to store `hrt_entries.json` in a different folder (e.g. `Documents/HRTTracker`), modify the path used when saving/loading the JSON file in `main.py` (or equivalent data module).

- **Additional fields**  
  You can add fields like:
  - Mood rating
  - Cycle day
  - Lab values (e.g. estradiol level)
  
  This typically requires:
  - Updating the UI form.
  - Modifying the JSON schema.
  - Adjusting load/save logic and table columns.

---

## Building the Standalone Executable

I packaged this project into a standalone executable using **PyInstaller**.

1. Installe PyInstaller:
   ```sh
   pip install pyinstaller
   ```

2.from the `.pyrunner` directory (or where `main.spec` is located), run:
   ```sh
   pyinstaller main.spec
   ```

3. PyInstaller will create a `dist/` folder containing the executable.

> The `build/` folder contains intermediate artifacts from such a build.  
> You can delete and recreate it when needed.

---

## Project Structure

A typical layout for this project:

```text
HRT Tracker v1.0.0/
├─ README.md                  # This document
├─ requirements.txt
└─ HRT Tracker/
   └─ .pyrunner/
      ├─ main.py              # Application entrypoint
      ├─ hrt_entries.json     # Data file (created at runtime)
      ├─ main.spec            # PyInstaller spec (if present)
      ├─ build/               # Build artifacts (optional)
      └─ dist/                # Generated executables (optional)
```

> Actual file names and folders may vary slightly depending on your setup.

---

## Requirements

- **Python**: 3.8 or newer
- **Packages**:
  - `customtkinter`

Install all dependencies using:

```sh
pip install -r requirements.txt
```

---

## Troubleshooting

- **App does not start / window does not appear**
  - Ensure you are running with the correct Python version:
    ```sh
    python --version
    ```
  - Check the terminal output for error messages.
  - Verify that `customtkinter` is installed.

- **`ModuleNotFoundError: No module named 'customtkinter'`**
  - Install the dependency:
    ```sh
    pip install customtkinter
    ```
  - Ensure you are using the same Python environment where you installed it.

- **Entries are not being saved**
  - Confirm that `hrt_entries.json` is writable in the current directory.
  - Run the terminal as administrator (on Windows) if you suspect permission issues.
  - Check if the program crashes on save; see terminal output.

- **JSON file looks corrupted**
  - If `hrt_entries.json` is partially written (e.g. power loss), the app might fail to load it.
  - Make a backup of the corrupted file.
  - Try to manually fix the JSON or start with a fresh file (empty list: `[]`).

---

## Roadmap / Future Ideas

Planned or possible future enhancements:

- Tag system (e.g. morning/evening, lab days, mood tags).
- More advanced statistics and charts (e.g. dose history, trends).
- Optional password protection / encrypted data file.
- Improved editing workflows (bulk editing, batch delete).
- Better accessibility (keyboard navigation, screen reader friendliness).
- Localization / multi-language support.

---

## License

TBD (to be determined).

> Until a license is specified, treat this as **all rights reserved**.  
> Do not redistribute or reuse code without the author's permission.

---

## Credits

- UI scaffold generated with [PyUIbuilder](https://pyuibuilder.com).
- Built using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
- HRT Tracker logic, data model, and UI refinements by the project author (Codebunny20).