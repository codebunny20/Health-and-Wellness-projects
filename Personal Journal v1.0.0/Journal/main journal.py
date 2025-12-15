# This code is generated using PyUIbuilder: https://pyuibuilder.com

import os
import datetime
import customtkinter as ctk
from tkinter import messagebox
import json  # for settings persistence
import sys

# Replace the previous BASE_DIR/JOURNAL_DIR/SETTINGS_PATH logic with a per-user app data folder
APP_NAME = "PersonalJournal"

def get_user_data_dir():
    """Return a stable per-user application data directory.
    When bundled as an executable (e.g. PyInstaller), use a platform-appropriate
    user data location so files persist across updates. During development,
    use the script folder for convenience.
    """
    if getattr(sys, "frozen", False):
        # running as a bundled app/exe
        if os.name == "nt":
            base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or os.path.expanduser("~")
        elif sys.platform == "darwin":
            base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
        else:
            base = os.getenv("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
        return os.path.join(base, APP_NAME)
    # not frozen -> keep using the script folder (easier for development)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_user_data_dir()
# ensure the base app dir exists (safe both in development and after packaging)
os.makedirs(BASE_DIR, exist_ok=True)

JOURNAL_DIR = os.path.join(BASE_DIR, "journals")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")

# Ensure storage folder exists
os.makedirs(JOURNAL_DIR, exist_ok=True)

def load_settings():
    """Load settings from disk; return dict with sane defaults on error."""
    defaults = {
        "accessibility": "Default",
        "geometry": "900x500",
    }
    if not os.path.exists(SETTINGS_PATH):
        return defaults
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        defaults.update({k: v for k, v in data.items() if k in defaults})
    except Exception:
        # ignore corrupt file and fall back to defaults
        pass
    return defaults

def save_settings(settings: dict):
    """Persist settings dict to disk."""
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        # best-effort; ignore save errors
        pass

# load settings before creating window so geometry is applied
_app_settings = load_settings()

main = ctk.CTk()
main.configure(fg_color="#23272D")
main.title("Journal / Diary")
main.geometry(_app_settings.get("geometry", "900x500"))  # use saved size

# allow window to expand
main.grid_rowconfigure(1, weight=1)   # content row
main.grid_columnconfigure(0, weight=0)
main.grid_columnconfigure(1, weight=1)

# ----------------- helper functions -----------------

current_file_path = None  # track which entry is open


def list_entries():
    """Refresh the listbox with existing journal entries."""
    entry_list.delete(0, "end")
    files = sorted(
        [f for f in os.listdir(JOURNAL_DIR) if f.endswith(".txt")],
        reverse=True,
    )
    for f in files:
        # nice label: date + title (filename without extension, replace _ with space)
        name = os.path.splitext(f)[0].replace("_", " ")
        entry_list.insert("end", name)


def get_selected_file():
    sel = entry_list.curselection()
    if not sel:
        return None
    label = entry_list.get(sel[0])
    filename = label.replace(" ", "_") + ".txt"
    return os.path.join(JOURNAL_DIR, filename)


def new_entry():
    global current_file_path
    current_file_path = None
    title_entry.delete(0, "end")
    title_entry.insert(0, datetime.date.today().isoformat())
    text.delete("1.0", "end")
    update_status("New entry started")


def save_entry(event=None):
    global current_file_path

    title = title_entry.get().strip()
    if not title:
        messagebox.showwarning("Missing title", "Please enter a title for this entry.")
        return

    safe_title = title.replace(" ", "_")
    filename = f"{safe_title}.txt"
    path = os.path.join(JOURNAL_DIR, filename)

    content = text.get("1.0", "end").rstrip()
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        messagebox.showerror("Save error", f"Could not save entry:\n{e}")
        return

    current_file_path = path
    list_entries()
    # select the saved entry in list
    for i in range(entry_list.size()):
        if entry_list.get(i) == title:
            entry_list.select_clear(0, "end")
            entry_list.select_set(i)
            break
    update_status(f"Saved: {title}")


def load_selected(event=None):
    global current_file_path
    path = get_selected_file()
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        messagebox.showerror("Load error", f"Could not load entry:\n{e}")
        return

    # update UI
    filename = os.path.splitext(os.path.basename(path))[0]
    title_entry.delete(0, "end")
    title_entry.insert(0, filename.replace("_", " "))
    text.delete("1.0", "end")
    text.insert("1.0", content)
    current_file_path = path
    update_status(f"Opened: {title_entry.get().strip()}")


def delete_entry():
    global current_file_path
    path = get_selected_file()
    if not path:
        messagebox.showinfo("Delete", "Select an entry to delete.")
        return

    if not messagebox.askyesno("Delete entry", "Are you sure you want to delete this entry?"):
        return

    try:
        os.remove(path)
    except OSError as e:
        messagebox.showerror("Delete error", f"Could not delete entry:\n{e}")
        return

    if current_file_path == path:
        current_file_path = None
        title_entry.delete(0, "end")
        text.delete("1.0", "end")

    list_entries()
    update_status("Entry deleted")


# ----------------- accessibility + settings window -----------------

accessibility_option_menu_options = ["Default", "Large text", "High contrast"]

def apply_accessibility(option: str):
    """Apply simple visual changes for chosen accessibility preset."""
    # base colors / sizes
    bg_main = "#23272D"
    text_color = "#FFFFFF"
    header_bg = "#1E2227"
    font_size = 12

    if option == "Large text":
        font_size = 14
    elif option == "High contrast":
        bg_main = "#000000"
        header_bg = "#000000"
        text_color = "#FFFFFF"

    # apply to main containers (minimal demo – expand as needed)
    try:
        main.configure(fg_color=bg_main)
        header_frame.configure(fg_color=header_bg)
        title_label.configure(text_color=text_color)
        text.configure(text_color=text_color)
        title_label.configure(font=ctk.CTkFont(size=font_size + 4, weight="bold"))
        # extend as needed for more widgets
    except Exception:
        pass

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("400x300")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)

        # Accessibility / theme section
        acc_label = ctk.CTkLabel(self, text="Theme / Accessibility", font=ctk.CTkFont(size=13, weight="bold"))
        acc_label.grid(row=0, column=0, padx=16, pady=(16, 6), sticky="w")

        self.accessibility_var = ctk.StringVar(
            value=_app_settings.get("accessibility", "Default")
        )

        acc_menu = ctk.CTkOptionMenu(
            self,
            variable=self.accessibility_var,
            values=accessibility_option_menu_options,
            command=self.on_accessibility_change,
        )
        acc_menu.grid(row=1, column=0, padx=16, pady=(0, 10), sticky="ew")

        close_btn = ctk.CTkButton(self, text="Close", command=self.destroy, width=80)
        close_btn.grid(row=2, column=0, padx=16, pady=(10, 16), sticky="e")

        # make window modal-ish
        self.transient(master)
        self.focus()
        self.grab_set()

    def on_accessibility_change(self, choice: str):
        apply_accessibility(choice)
        _app_settings["accessibility"] = choice
        save_settings(_app_settings)

_settings_window_ref = None  # keep a single instance

def open_settings_window():
    global _settings_window_ref
    if _settings_window_ref is not None and _settings_window_ref.winfo_exists():
        _settings_window_ref.focus()
        return
    _settings_window_ref = SettingsWindow(main)

# Add a simple Info / About window
_info_window_ref = None

class InfoWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("About / Info")
        self.geometry("400x300")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        info_text = (
            "Personal Journal\n\n"
            "How to use:\n"
            "- Click New or press Ctrl+N to start a new entry (title defaults to today's date).\n"
            "- Enter a title and write your entry in the editor.\n"
            "- Click Save or press Ctrl+S to save the entry.\n"
            "- Select an entry in the list to open it; use Delete to remove it.\n\n"
            "Entries are stored as .txt files in the 'journals' folder next to this app."
        )

        info_label = ctk.CTkLabel(self, text=info_text, justify="left", wraplength=320)
        info_label.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="nw")

        close_btn = ctk.CTkButton(self, text="Close", command=self.destroy, width=80)
        close_btn.grid(row=1, column=0, padx=12, pady=(6, 12), sticky="e")

        # make window modal-ish
        self.transient(master)
        self.focus()
        self.grab_set()

def open_info_window():
    global _info_window_ref
    if _info_window_ref is not None and _info_window_ref.winfo_exists():
        _info_window_ref.focus()
        return
    _info_window_ref = InfoWindow(main)

# ----------------- UI layout -----------------

# HEADER BAR
header_frame = ctk.CTkFrame(main, fg_color="#1E2227", corner_radius=0)
header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
header_frame.grid_columnconfigure(0, weight=1)  # title stretch
header_frame.grid_columnconfigure(1, weight=0)
header_frame.grid_columnconfigure(2, weight=0)
header_frame.grid_columnconfigure(3, weight=0)

title_label = ctk.CTkLabel(
    master=header_frame,
    text="📓 Personal Journal",
    font=ctk.CTkFont(size=18, weight="bold"),
    text_color="#FFFFFF",
)
title_label.grid(row=0, column=0, padx=16, pady=8, sticky="w")

# new Info button (placed to the left of Settings)
info_button = ctk.CTkButton(
    master=header_frame,
    text="Info",
    fg_color="#3A3F45",
    hover_color="#4B525A",
    width=70,
    height=30,
    text_color="#fff",
    corner_radius=5,
    command=open_info_window,
)
info_button.grid(row=0, column=1, padx=6, pady=8)

settings_button = ctk.CTkButton(
    master=header_frame,
    text="Settings",
    fg_color="#3A3F45",
    hover_color="#4B525A",
    width=90,
    height=30,
    text_color="#fff",
    corner_radius=5,
    command=open_settings_window,  # open our settings window
)
settings_button.grid(row=0, column=2, padx=12, pady=8)

# MAIN CONTENT AREA (SIDEBAR + EDITOR)
content_frame = ctk.CTkFrame(main, fg_color="#23272D", corner_radius=0)
content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=0, pady=(0, 0))
content_frame.grid_columnconfigure(0, weight=0)  # sidebar
content_frame.grid_columnconfigure(1, weight=1)  # editor
content_frame.grid_rowconfigure(0, weight=1)

# SIDEBAR (entries list + buttons)
sidebar_frame = ctk.CTkFrame(content_frame, fg_color="#202328", corner_radius=0)
sidebar_frame.grid(row=0, column=0, sticky="nsew")
sidebar_frame.grid_rowconfigure(1, weight=1)

sidebar_label = ctk.CTkLabel(
    sidebar_frame,
    text="Entries",
    font=ctk.CTkFont(size=14, weight="bold"),
    text_color="#FFFFFF",
)
sidebar_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

# Listbox container for nicer padding
list_container = ctk.CTkFrame(sidebar_frame, fg_color="#202328")
list_container.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="nsew")
list_container.grid_rowconfigure(0, weight=1)
list_container.grid_columnconfigure(0, weight=1)

entry_list = ctk.CTkListbox(list_container, width=220, height=320) if hasattr(ctk, "CTkListbox") else None
if entry_list is None:
    import tkinter as tk
    entry_list = tk.Listbox(
        list_container,
        bg="#2C3036",
        fg="white",
        highlightthickness=0,
        selectbackground="#029CFF",
        borderwidth=0,
    )
entry_list.grid(row=0, column=0, sticky="nsew")

# Sidebar buttons
sidebar_btns_frame = ctk.CTkFrame(sidebar_frame, fg_color="#202328")
sidebar_btns_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
sidebar_btns_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="buttons")

new_btn = ctk.CTkButton(sidebar_btns_frame, text="New", command=new_entry, height=30)
new_btn.grid(row=0, column=0, padx=3)

save_btn = ctk.CTkButton(sidebar_btns_frame, text="Save", command=save_entry, height=30)
save_btn.grid(row=0, column=1, padx=3)

delete_btn = ctk.CTkButton(
    sidebar_btns_frame,
    text="Delete",
    command=delete_entry,
    fg_color="#9b1c1c",
    hover_color="#7a1515",
    height=30,
)
delete_btn.grid(row=0, column=2, padx=3)

# EDITOR AREA (title + toolbar + text)
editor_frame = ctk.CTkFrame(content_frame, fg_color="#25282E", corner_radius=0)
editor_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=8)
editor_frame.grid_rowconfigure(2, weight=1)
editor_frame.grid_columnconfigure(0, weight=1)

# Title row
title_row = ctk.CTkFrame(editor_frame, fg_color="#25282E")
title_row.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
title_row.grid_columnconfigure(1, weight=1)

title_label = ctk.CTkLabel(
    title_row,
    text="Title",
    font=ctk.CTkFont(size=13, weight="bold"),
    text_color="#FFFFFF",
)
title_label.grid(row=0, column=0, padx=(0, 6))

title_entry = ctk.CTkEntry(
    title_row,
    placeholder_text="Entry title (e.g. 2025-01-01 My day)",
    width=400,
)
title_entry.grid(row=0, column=1, sticky="ew")

# Small toolbar row (date + shortcuts hint)
toolbar_row = ctk.CTkFrame(editor_frame, fg_color="#25282E")
toolbar_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))
toolbar_row.grid_columnconfigure(0, weight=1)
toolbar_row.grid_columnconfigure(1, weight=0)

date_label = ctk.CTkLabel(
    toolbar_row,
    text=f"Today: {datetime.date.today().isoformat()}",
    font=ctk.CTkFont(size=11),
    text_color="#aaaaaa",
)
date_label.grid(row=0, column=0, sticky="w")

shortcut_label = ctk.CTkLabel(
    toolbar_row,
    text="Shortcuts: Ctrl+N = New, Ctrl+S = Save",
    font=ctk.CTkFont(size=11),
    text_color="#888888",
)
shortcut_label.grid(row=0, column=1, sticky="e")

# Text editor
text = ctk.CTkTextbox(
    master=editor_frame,
    fg_color="#181A1F",
    text_color="#FFFFFF",
    corner_radius=5,
)
text.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

# STATUS BAR
status_bar = ctk.CTkLabel(
    main,
    text="Ready",
    anchor="w",
    font=ctk.CTkFont(size=10),
    text_color="#CCCCCC",
)
status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 4))

# ----------------- bindings and init -----------------

def update_status(msg: str):
    status_bar.configure(text=msg)

def on_close():
    """Save geometry (and any other runtime settings) before exit."""
    try:
        _app_settings["geometry"] = main.winfo_geometry()
        save_settings(_app_settings)
    finally:
        main.destroy()

# apply accessibility preset once on startup
apply_accessibility(_app_settings.get("accessibility", "Default"))

# Double-click or Enter on list to open entry
entry_list.bind("<Double-Button-1>", load_selected)
entry_list.bind("<Return>", load_selected)

# Shortcuts
main.bind("<Control-s>", save_entry)
main.bind("<Control-n>", lambda e: new_entry())

# Initial load
list_entries()
new_entry()
update_status("Ready – create a new entry or select one from the list.")

main.protocol("WM_DELETE_WINDOW", on_close)
main.mainloop()