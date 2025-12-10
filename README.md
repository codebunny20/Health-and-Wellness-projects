# Wellness Tracker Suite

A modern, user-friendly desktop application for tracking your health and wellbeing, including Hormone Replacement Therapy (HRT), medications, cycles, and private journaling. Built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), this suite provides a clean, dark-themed interface and local data storage for privacy.

---

## Features

- **HRT Tracker:**  
  Log, review, and manage your Hormone Replacement Therapy doses with support for multiple medications, doses, and routes per entry. Edit, delete, and export your entries easily.

- **Universal Medication Tracker:**  
  Track any medications you take, with a dedicated tab for flexible logging.

- **Cycle Tracker:**  
  Log cycle days and symptoms to monitor patterns over time.

- **Private Journal/Diary:**  
  Write private notes and reflections in a secure, local journal.

- **Data Export:**  
  Export your HRT log as JSON or CSV for backup or analysis.

- **Modern UI:**  
  Clean, dark-themed interface with intuitive navigation and keyboard shortcuts.

- **Local Storage:**  
  All data is stored locally on your device for maximum privacy.

---

## Installation

### 1. Clone or Download

Download or clone this repository to your computer.

### 2. Install Python

Ensure you have **Python 3.8+** installed.  
[Download Python here](https://www.python.org/downloads/)

### 3. Install Dependencies

Navigate to the project folder and install required packages:

```sh
pip install -r requirements.txt
```

The only required package is:
```
customtkinter
```

---

## Usage

1. **Run the Application**

   From the `Wellness Tracker suite` directory, start the app:

   ```sh
   python main.py
   ```

2. **Navigate the Tabs**

   - **Wellness Tracker home tab:** Overview and help.
   - **HRT Tracker:** Log and manage HRT doses.
   - **Universal Medication tracker:** Track any medications.
   - **Cycle Tracker:** Log cycle days and symptoms.
   - **Private Journal/Diary:** Write personal notes.

3. **Keyboard Shortcuts**

   - **Ctrl+Enter:** Save entry
   - **Esc:** Clear form/cancel edit
   - **Delete:** Delete selected entry

---

## Data Storage

- **HRT Entries:**  
  Saved as individual JSON files in `hrt tracker entries/` within the app directory.  
  An index file (`_index.json`) keeps track of all entries.

- **Exports:**  
  Exported files are saved in the `exports/` folder.

- **Privacy:**  
  All data is stored locally. No information is sent online.

---

## Exporting Data

- **Export as JSON:**  
  Click "Export JSON" in the HRT Tracker tab to save all entries as a single JSON file.

- **Export as CSV:**  
  Click "Export CSV" to save a spreadsheet-friendly summary.

- **Open HRT Folder:**  
  Click "Open HRT folder" to view all individual entry files.

---

## Building an Executable

You can package the app as a standalone executable using [PyInstaller](https://pyinstaller.org/):

```sh
pip install pyinstaller
pyinstaller main.spec
```

The built executable will appear in the `dist` or `build` folder.

---

## Requirements

- Python 3.8 or newer
- customtkinter

---

## Project Structure

```
Wellness Tracker suite/
│
├── main.py                # Main application code
├── requirements.txt       # Python dependencies
├── exports/               # Exported data (JSON/CSV)
├── hrt tracker entries/   # Individual HRT entry files
│   └── _index.json        # Index of HRT entries
└── ... (other files/folders)
```

---

## License

TBD (to be determined)

---

*Generated with [PyUIbuilder](https://pyuibuilder.com) and CustomTkinter.*