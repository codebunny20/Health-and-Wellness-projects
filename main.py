# This code is generated using PyUIbuilder: https://pyuibuilder.com

import os
import customtkinter as ctk
from datetime import datetime, timedelta
from functools import partial
import json  # <-- add for saving as JSON
import sys  # <-- add for folder opening

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- NEW: HRT ENTRIES FOLDER ---
HRT_ENTRIES_DIR = os.path.join(BASE_DIR, "hrt tracker entries")
os.makedirs(HRT_ENTRIES_DIR, exist_ok=True)

# --- NEW: central export folder (optional, can be same as BASE_DIR) ---
HRT_EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(HRT_EXPORTS_DIR, exist_ok=True)

# Optional: index file to make external use of data easier
HRT_INDEX_FILE = os.path.join(HRT_ENTRIES_DIR, "_index.json")

# --- NEW: helper to build safe filenames + index map ---
def _make_hrt_filename(entry: dict) -> str:
    """Build a safe, somewhat descriptive filename for an HRT entry."""
    date = entry.get("date", "unknown") or "unknown"
    time = (entry.get("time") or "unknown").replace(":", "-").replace(" ", "_")
    meds = entry.get("medication", [])
    if isinstance(meds, list):
        meds = "_".join(meds)
    meds = meds or "med"
    safe_meds = "".join(c for c in meds if c.isalnum() or c in ("_", "-"))[:30] or "med"
    return f"{date}_{time}_{safe_meds}.json"

# track mapping from in‑memory entries to filenames on disk
hrt_entry_files: list[str | None] = []

def _write_index_file():
    """Save a small index of all HRT entries and their filenames."""
    try:
        data = []
        for entry, fname in zip(hrt_entries, hrt_entry_files):
            data.append({"file": fname, "entry": entry})
        with open(HRT_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        # index is optional; ignore errors
        pass

def save_hrt_entry_to_file(entry, index: int | None = None):
    """Save a single HRT entry as a JSON file in the hrt tracker entries folder.

    If index is given, update/overwrite the file associated with that in‑memory entry.
    """
    # decide filename
    if index is not None and 0 <= index < len(hrt_entry_files) and hrt_entry_files[index]:
        filename = hrt_entry_files[index]
    else:
        filename = _make_hrt_filename(entry)

    filepath = os.path.join(HRT_ENTRIES_DIR, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
        # keep mapping in sync
        if index is not None:
            # update existing slot
            while len(hrt_entry_files) <= index:
                hrt_entry_files.append(None)
            hrt_entry_files[index] = filename
        else:
            # append if this is a brand‑new entry
            if filename not in hrt_entry_files:
                hrt_entry_files.append(filename)
        _write_index_file()
    except Exception as e:
        # show a small error window instead of silently failing
        err = ctk.CTkToplevel()
        err.title("Save error")
        msg = ctk.CTkLabel(err, text=f"Could not save entry:\n{e}")
        msg.pack(padx=20, pady=20)
        btn = ctk.CTkButton(err, text="OK", command=err.destroy)
        btn.pack(pady=(0, 10))

# Set global appearance and default fonts for better readability
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEFAULT_FONT = ("Segoe UI", 13)
TITLE_FONT = ("Segoe UI", 20, "bold")

wellness_tracker_app = ctk.CTk()
wellness_tracker_app.configure(fg_color="#23272D")
wellness_tracker_app.title("Wellness Tracker app")
wellness_tracker_app.geometry("1100x600+0+0")  # Set window size and position at top-left
wellness_tracker_app.minsize(956, 600)  # Prevent window from being too small

# Add a small margin around the whole window
wellness_tracker_app.grid_rowconfigure(0, weight=1)
wellness_tracker_app.grid_columnconfigure(0, weight=1)

all_tabs = ctk.CTkTabview(wellness_tracker_app)
all_tabs.add("Wellness Tracker home tab")
all_tabs.add("HRT Tracker")
all_tabs.add("Universal Medication tracker")
all_tabs.add("Cycle Tracker")
all_tabs.add("Private Journal/Diary")
all_tabs.configure()
all_tabs.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")  # More margin around tabs

# Home tab
frame = ctk.CTkFrame(master=all_tabs.tab("Wellness Tracker home tab"))
frame.configure(fg_color="#2a2a2a", width=100, height=100)
frame.pack(expand=True, fill="both", padx=20, pady=20)  # More padding inside tab
frame.pack_propagate(False)  # Prevent shrinking

# This make a simple, clear home screen
# Title
home_title = ctk.CTkLabel(
    frame,
    text="Welcome to your Wellness Tracker",
    font=TITLE_FONT
)
home_title.pack(pady=(30, 15))  # More space above/below title

# A short description of the app's features
home_description = ctk.CTkLabel(
    frame,
    text=(
        "Use the tabs above to track your health and wellbeing.\n\n"
        "• HRT Tracker – log your hormone replacement therapy.\n"
        "• Universal Medication tracker – manage any medications.\n"
        "• Cycle Tracker – follow your cycle patterns.\n"
        "• Private Journal/Diary – write thoughts and notes."
    ),
    font=DEFAULT_FONT,
    justify="left"
)
home_description.pack(pady=(0, 30), padx=30, anchor="w")  # More space below description

# This adds simple help dialog for new users
def show_help():
    help_window = ctk.CTkToplevel(wellness_tracker_app)
    help_window.title("How to use this app")
    help_window.geometry("420x320")
    help_window.grab_set()

    help_label = ctk.CTkLabel(
        help_window,
        text=(
            "Getting started:\n\n"
            "1. Choose a tab at the top.\n"
            "2. Add or view information for that area.\n"
            "3. Come back often to keep your data up to date.\n\n"
            "Tabs overview:\n"
            "• HRT Tracker – record doses, dates, and notes.\n"
            "• Universal Medication tracker – track any pills or shots.\n"
            "• Cycle Tracker – log symptoms and cycle days.\n"
            "• Private Journal/Diary – write anything, just for you."
        ),
        font=DEFAULT_FONT,
        justify="left"
    )
    help_label.pack(padx=20, pady=20, anchor="w")

    close_btn = ctk.CTkButton(
        help_window,
        text="Close",
        font=DEFAULT_FONT,
        command=help_window.destroy
    )
    close_btn.pack(pady=(0, 15))

# ---------- HRT TRACKER STATE & HELPERS ----------

# simple in-memory storage: list of dicts
hrt_entries = []
# see top: hrt_entry_files keeps parallel filenames

# dynamic-field state (must exist before functions referring to it)
extra_med_fields = []
extra_dose_fields = []
extra_route_fields = []

# --- NEW: load entries from disk on startup ---
def load_hrt_entries_from_files():
    """Load all JSON entries from HRT_ENTRIES_DIR into memory."""
    hrt_entries.clear()
    hrt_entry_files.clear()
    if not os.path.isdir(HRT_ENTRIES_DIR):
        return
    for name in sorted(os.listdir(HRT_ENTRIES_DIR)):
        if not name.lower().endswith(".json"):
            continue
        if name == os.path.basename(HRT_INDEX_FILE):
            continue  # skip index file
        path = os.path.join(HRT_ENTRIES_DIR, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            # skip corrupt files
            continue

        # normalize fields to the shapes expected by the app
        date = str(data.get("date", "")).strip() or "unknown"
        time = str(data.get("time", "")).strip() or "—"
        meds = data.get("medication", [])
        if isinstance(meds, str):
            meds = [m.strip() for m in meds.split(",") if m.strip()]
        doses = data.get("dose", [])
        if isinstance(doses, str):
            doses = [d.strip() for d in doses.split(",") if d.strip()]
        routes = data.get("route", [])
        if isinstance(routes, str):
            routes = [r.strip() for r in routes.split(",") if r.strip()]
        notes = str(data.get("notes", "")).strip()

        entry = {
            "date": date,
            "time": time,
            "medication": meds or ["(unknown)"],
            "dose": doses or ["(unspecified)"],
            "route": routes or ["(unspecified)"],
            "notes": notes,
        }
        hrt_entries.append(entry)
        hrt_entry_files.append(name)
    # refresh index from loaded files
    _write_index_file()

def get_effective_value(option_menu, custom_entry):
    """If 'Other / Custom…' is selected, return custom text, else dropdown value."""
    val = option_menu.get().strip()
    if val == "Other / Custom…":
        custom = custom_entry.get().strip()
        return custom
    return val

def get_all_effective_values(field_list):
    """Return a list of values from a list of (option_menu, custom_entry) pairs."""
    vals = []
    for opt, custom in field_list:
        v = get_effective_value(opt, custom)
        if v:
            vals.append(v)
    return vals

def get_all_entry_values(field_list):
    """Return a list of values from a list of Entry widgets."""
    vals = []
    for entry in field_list:
        v = entry.get().strip()
        if v:
            vals.append(v)
    return vals

def refresh_hrt_log():
    """Redraw the HRT log text box from hrt_entries."""
    hrt_log_textbox.configure(state="normal")
    hrt_log_textbox.delete("0.0", "end")

    if not hrt_entries:
        hrt_log_textbox.insert(
            "0.0",
            "No HRT entries yet.\n\nUse the form above to add your first entry."
        )
        hrt_log_textbox.configure(state="disabled")
        return

    # sort: newest first (by date+time)
    def _parse_dt(e):
        try:
            return datetime.strptime(e["date"] + " " + (e["time"] or "00:00"), "%Y-%m-%d %H:%M")
        except Exception:
            return datetime.min

    sorted_entries = sorted(hrt_entries, key=_parse_dt, reverse=True)

    lines = []
    for idx, entry in enumerate(sorted_entries, start=1):
        meds = ", ".join(entry['medication']) if isinstance(entry['medication'], list) else entry['medication']
        doses = ", ".join(entry['dose']) if isinstance(entry['dose'], list) else entry['dose']
        routes = ", ".join(entry['route']) if isinstance(entry['route'], list) else entry['route']

        header = f"{idx}. {entry['date']} {entry['time'] or '—'} – {meds}"
        header += f" ({doses} via {routes})"
        if entry.get("notes"):
            header += f"\n    Notes: {entry['notes']}"
        lines.append(header)

        lines.append("")  # blank line between entries

    hrt_log_textbox.insert("0.0", "\n".join(lines))
    hrt_log_textbox.configure(state="disabled")

def clear_hrt_form():
    """Reset all input fields in the HRT form."""
    # reset dropdowns
    hrt_date_option.set("Today")
    hrt_time_option.set("Now")
    hrt_med_option.set("Estradiol (any form)")
    hrt_dose_option.set("Standard / as prescribed")
    hrt_route_option.set("Pill / Oral")
    # hrt_preset_menu.set("None")  # Removed: not defined

    # clear custom fields
    hrt_date_custom_entry.delete(0, "end")
    hrt_time_custom_entry.delete(0, "end")
    hrt_med_custom_entry.delete(0, "end")
    hrt_dose_custom_entry.delete(0, "end")
    hrt_notes_entry.delete(0, "end")

    hrt_delete_index.delete(0, "end")

    # Remove extra med/dose/route fields
    for widgets in [extra_med_fields, extra_dose_fields, extra_route_fields]:
        for w in list(widgets):
            if isinstance(w, tuple):
                container = w[0].master  # optionmenu parent frame
            else:
                container = w.master
            container.destroy()
        widgets.clear()

    # reset borders
    for entry in [hrt_med_custom_entry, hrt_dose_custom_entry, hrt_date_custom_entry]:
        entry.configure(border_color=None)

def _set_error(widget):
    widget.configure(border_color="#b3261e")

def _clear_error(widget):
    widget.configure(border_color=None)

def add_hrt_entry(show_errors: bool = False):
    """Collect values from form, validate, store, and refresh log.

    Also updates the corresponding JSON file on disk.
    """
    global _current_edit_sorted_idx
    try:
        # resolve date/time from dropdown + custom
        date_val = _resolve_date_from_option(
            hrt_date_option.get(),
            hrt_date_custom_entry.get().strip()
        )
        time_val = _resolve_time_from_option(
            hrt_time_option.get(),
            hrt_time_custom_entry.get().strip()
        )

        # collect meds / doses / routes
        med_vals = [get_effective_value(hrt_med_option, hrt_med_custom_entry)]
        for opt, custom in extra_med_fields:
            med_vals.append(get_effective_value(opt, custom))
        med_vals = [v for v in med_vals if v]

        dose_vals = [get_effective_value(hrt_dose_option, hrt_dose_custom_entry)]
        for opt, custom in extra_dose_fields:
            dose_vals.append(get_effective_value(opt, custom))
        dose_vals = [v for v in dose_vals if v]

        route_vals = [hrt_route_option.get().strip()]
        for opt in extra_route_fields:
            route_vals.append(opt.get().strip())
        route_vals = [v for v in route_vals if v]

        notes_val = hrt_notes_entry.get().strip()

        # simple validation
        has_error = False
        if not med_vals:
            has_error = True
            if show_errors:
                _set_error(hrt_med_custom_entry)
        else:
            _clear_error(hrt_med_custom_entry)

        if not dose_vals:
            has_error = True
            if show_errors:
                _set_error(hrt_dose_custom_entry)
        else:
            _clear_error(hrt_dose_custom_entry)

        if not date_val:
            has_error = True
            if show_errors:
                _set_error(hrt_date_custom_entry)
        else:
            _clear_error(hrt_date_custom_entry)

        if has_error:
            # NEW: brief error popup to explain missing fields
            if show_errors:
                err = ctk.CTkToplevel()
                err.title("Missing information")
                msg = ctk.CTkLabel(
                    err,
                    text="Please fill in at least one medication, one dose, and a date.",
                )
                msg.pack(padx=20, pady=20)
                ctk.CTkButton(err, text="OK", command=err.destroy).pack(pady=(0, 10))
            return

        entry = {
            "date": date_val,
            "time": time_val or "—",
            "medication": med_vals,
            "dose": dose_vals,
            "route": route_vals,
            "notes": notes_val,
        }

        # NEW: add vs edit mode
        if _current_edit_sorted_idx is not None:
            # update in‑memory entry at that real index
            real_index = _current_edit_sorted_idx
            if 0 <= real_index < len(hrt_entries):
                hrt_entries[real_index] = entry
                # update disk file
                save_hrt_entry_to_file(entry, index=real_index)
            _finish_edit_mode()
        else:
            # in-memory append
            hrt_entries.append(entry)
            # on-disk new file (save_hrt_entry_to_file will sync filename list)
            save_hrt_entry_to_file(entry)

        clear_hrt_form()
        refresh_hrt_log()
    except Exception as e:
        # show unexpected errors so they don't silently block saving
        err = ctk.CTkToplevel()
        err.title("Error adding entry")
        msg = ctk.CTkLabel(err, text=f"Something went wrong:\n{e}")
        msg.pack(padx=20, pady=20)
        btn = ctk.CTkButton(err, text="OK", command=err.destroy)
        btn.pack(pady=(0, 10))

def delete_selected_hrt_entry():
    """Delete entry by line number typed into delete index field (and remove file)."""
    idx_str = hrt_delete_index.get().strip()
    if not idx_str.isdigit():
        return
    idx = int(idx_str)
    if 1 <= idx <= len(hrt_entries):
        # compute real index in sorted order used by refresh_hrt_log()
        # refresh_hrt_log shows newest first; we'll align deletion with that order
        def _parse_dt(e):
            try:
                return datetime.strptime(e["date"] + " " + (e["time"] or "00:00"), "%Y-%m-%d %H:%M")
            except Exception:
                return datetime.min

        sorted_indices = sorted(
            range(len(hrt_entries)),
            key=lambda i: _parse_dt(hrt_entries[i]),
            reverse=True,
        )
        real_index = sorted_indices[idx - 1]

        # delete corresponding file if known
        if 0 <= real_index < len(hrt_entry_files):
            filename = hrt_entry_files[real_index]
            if filename:
                fpath = os.path.join(HRT_ENTRIES_DIR, filename)
                try:
                    if os.path.exists(fpath):
                        os.remove(fpath)
                except OSError:
                    pass
            del hrt_entry_files[real_index]

        del hrt_entries[real_index]
        hrt_delete_index.delete(0, "end")
        _write_index_file()
        refresh_hrt_log()

def duplicate_last_hrt_to_form():
    """Load the most recent entry back into the form for quick repeats."""
    if not hrt_entries:
        return
    last = hrt_entries[-1]

    # basic fields
    hrt_med_option.set(last["medication"][0] if last["medication"] else "Estradiol (any form)")
    hrt_dose_option.set(last["dose"][0] if last["dose"] else "Standard / as prescribed")
    hrt_route_option.set(last["route"][0] if last["route"] else "Pill / Oral")

    # clear dynamic extras then recreate based on lists
    for widgets in [extra_med_fields, extra_dose_fields, extra_route_fields]:
        for w in list(widgets):
            if isinstance(w, tuple):
                w[0].master.destroy()
            else:
                w.master.destroy()
        widgets.clear()

    for med in last["medication"][1:]:
        add_extra_med_field()
        opt, custom = extra_med_fields[-1]
        opt.set("Other / Custom…")
        custom.delete(0, "end")
        custom.insert(0, med)

    for dose in last["dose"][1:]:
        add_extra_dose_field()
        opt, custom = extra_dose_fields[-1]
        opt.set("Other / Custom…")
        custom.delete(0, "end")
        custom.insert(0, dose)

    for route in last["route"][1:]:
        add_extra_route_field()
        opt = extra_route_fields[-1]
        opt.set(route)

    hrt_notes_entry.delete(0, "end")
    hrt_notes_entry.insert(0, last.get("notes", ""))

# --- NEW: simple helpers for export / folder open ---

def _show_info_dialog(title: str, message: str):
    win = ctk.CTkToplevel()
    win.title(title)
    lbl = ctk.CTkLabel(win, text=message, justify="left")
    lbl.pack(padx=20, pady=20)
    ctk.CTkButton(win, text="OK", command=win.destroy).pack(pady=(0, 10))

def export_hrt_to_json():
    """Export all current HRT entries to a single JSON file."""
    if not hrt_entries:
        _show_info_dialog("Export HRT (JSON)", "No HRT entries to export.")
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(HRT_EXPORTS_DIR, f"hrt_export_{ts}.json")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(hrt_entries, f, indent=2, ensure_ascii=False)
        _show_info_dialog(
            "Export HRT (JSON)",
            f"Exported {len(hrt_entries)} entries to:\n{out_path}",
        )
    except Exception as e:
        _show_info_dialog("Export error", f"Could not export JSON:\n{e}")

def export_hrt_to_csv():
    """Export all current HRT entries to a CSV summary file."""
    if not hrt_entries:
        _show_info_dialog("Export HRT (CSV)", "No HRT entries to export.")
        return
    import csv

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(HRT_EXPORTS_DIR, f"hrt_export_{ts}.csv")
    try:
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "time", "medication", "dose", "route", "notes"])
            for e in hrt_entries:
                meds = ", ".join(e.get("medication", []))
                doses = ", ".join(e.get("dose", []))
                routes = ", ".join(e.get("route", []))
                writer.writerow([
                    e.get("date", ""),
                    e.get("time", ""),
                    meds,
                    doses,
                    routes,
                    e.get("notes", ""),
                ])
        _show_info_dialog(
            "Export HRT (CSV)",
            f"Exported {len(hrt_entries)} entries to:\n{out_path}",
        )
    except Exception as e:
        _show_info_dialog("Export error", f"Could not export CSV:\n{e}")

def open_hrt_folder():
    """Open the folder that contains individual HRT entry files."""
    try:
        if os.name == "nt":
            os.startfile(HRT_ENTRIES_DIR)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            import subprocess
            subprocess.Popen(["open", HRT_ENTRIES_DIR])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", HRT_ENTRIES_DIR])
    except Exception as e:
        _show_info_dialog("Open folder", f"Could not open folder:\n{e}")

# --- NEW: edit support helpers ---
def _load_entry_into_form(entry):
    """Populate the HRT form fields from a given entry dict."""
    clear_hrt_form()
    # date/time go to custom; do not change dropdown shortcuts
    hrt_date_option.set("Other / Custom…")
    hrt_date_custom_entry.insert(0, entry.get("date", ""))
    hrt_time_option.set("Other / Custom…")
    hrt_time_custom_entry.insert(0, entry.get("time", "").replace("—", ""))

    meds = entry.get("medication", [])
    doses = entry.get("dose", [])
    routes = entry.get("route", [])
    notes = entry.get("notes", "")

    # primary med/dose
    if meds:
        hrt_med_option.set("Other / Custom…")
        hrt_med_custom_entry.insert(0, meds[0])
    if doses:
        hrt_dose_option.set("Other / Custom…")
        hrt_dose_custom_entry.insert(0, doses[0])

    # extra meds/doses/routes
    for med in meds[1:]:
        add_extra_med_field()
        opt, custom = extra_med_fields[-1]
        opt.set("Other / Custom…")
        custom.insert(0, med)

    for dose in doses[1:]:
        add_extra_dose_field()
        opt, custom = extra_dose_fields[-1]
        opt.set("Other / Custom…")
        custom.insert(0, dose)

    for route in routes:
        # first route goes into main widget if it's still default
        if not extra_route_fields and hrt_route_option.get() == "Pill / Oral":
            hrt_route_option.set(route)
        else:
            add_extra_route_field()
            extra_route_fields[-1].set(route)

    hrt_notes_entry.insert(0, notes)

# track which entry (in log order) is being edited; None = normal add mode
_current_edit_sorted_idx: int | None = None

def start_edit_selected_hrt_entry():
    """Load selected log entry into the form for editing."""
    global _current_edit_sorted_idx
    idx_str = hrt_delete_index.get().strip()
    if not idx_str.isdigit():
        return
    idx = int(idx_str)
    if not (1 <= idx <= len(hrt_entries)):
        return

    # map visible index to in‑memory index (same logic as delete)
    def _parse_dt(e):
        try:
            return datetime.strptime(e["date"] + " " + (e["time"] or "00:00"), "%Y-%m-%d %H:%M")
        except Exception:
            return datetime.min

    sorted_indices = sorted(
        range(len(hrt_entries)),
        key=lambda i: _parse_dt(hrt_entries[i]),
        reverse=True,
    )
    real_index = sorted_indices[idx - 1]
    _current_edit_sorted_idx = real_index
    _load_entry_into_form(hrt_entries[real_index])

    # visually indicate we're editing
    hrt_save_button.configure(text="Update Entry (Ctrl+Enter)")
    hrt_delete_label.configure(text="Editing entry #:")
    hrt_form_header.configure(text="Edit HRT Entry")

def _finish_edit_mode():
    """Reset UI and state after saving/cancelling an edit."""
    global _current_edit_sorted_idx
    _current_edit_sorted_idx = None
    hrt_save_button.configure(text="Save Entry (Ctrl+Enter)")
    hrt_delete_label.configure(text="Delete / Edit entry #:")
    hrt_form_header.configure(text="Add HRT Entry")
    hrt_delete_index.delete(0, "end")

# small helper for date/time from dropdowns
def _resolve_date_from_option(option_value: str, custom_text: str) -> str:
    option_value = option_value.strip()
    if option_value == "Other / Custom…" and custom_text:
        return custom_text
    today = datetime.now().date()
    if option_value == "Today":
        return today.strftime("%Y-%m-%d")
    if option_value == "Yesterday":
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    if option_value == "2 days ago":
        return (today - timedelta(days=2)).strftime("%Y-%m-%d")
    if option_value == "1 week ago":
        return (today - timedelta(days=7)).strftime("%Y-%m-%d")
    # fallback – allow user to manually type a date into the custom box
    return custom_text or today.strftime("%Y-%m-%d")

def _resolve_time_from_option(option_value: str, custom_text: str) -> str:
    option_value = option_value.strip()
    now = datetime.now()
    if option_value == "Other / Custom…" and custom_text:
        return custom_text
    if option_value == "Now":
        return now.strftime("%H:%M")
    if option_value == "Morning":
        return "09:00"
    if option_value == "Afternoon":
        return "14:00"
    if option_value == "Evening":
        return "19:00"
    if option_value == "Night":
        return "22:00"
    # fallback – keep custom or now
    return custom_text or now.strftime("%H:%M")

def update_theme_colors():
    """Adjust widget colors for better visibility in light/dark mode."""
    bg = "#23272D"
    frame_bg = "#2a2a2a"
    text_fg = "#FFFFFF"
    button_fg = "#222831"
    button_hover = "#393E46"
    delete_fg = "#b3261e"
    delete_hover = "#7f1b16"
    entry_fg = "#23272D"
    entry_text = "#FFFFFF"
    scroll_fg = "#2a2a2a"

    wellness_tracker_app.configure(fg_color=bg)
    all_tabs.configure(fg_color=bg)
    frame.configure(fg_color=frame_bg)
    frame1.configure(fg_color=frame_bg)
    frame2.configure(fg_color=frame_bg)
    frame3.configure(fg_color=frame_bg)
    frame4.configure(fg_color=frame_bg)
    # Home tab labels
    home_title.configure(text_color=text_fg)
    home_description.configure(text_color=text_fg)
    # HRT tab labels and frames
    hrt_log_label.configure(text_color=text_fg)
    hrt_form_scroll.configure(fg_color=scroll_fg)
    hrt_log_frame.configure(fg_color=frame_bg)
    hrt_main_frame.configure(fg_color="transparent")
    hrt_date_label.configure(text_color=text_fg)
    hrt_time_label.configure(text_color=text_fg)
    hrt_med_label.configure(text_color=text_fg)
    hrt_dose_label.configure(text_color=text_fg)
    hrt_route_label.configure(text_color=text_fg)
    hrt_delete_label.configure(text_color=text_fg)
    # OptionMenus (dropdowns)
    hrt_date_option.configure(fg_color=entry_fg, text_color=entry_text, button_color=button_fg, button_hover_color=button_hover)
    hrt_time_option.configure(fg_color=entry_fg, text_color=entry_text, button_color=button_fg, button_hover_color=button_hover)
    hrt_med_option.configure(fg_color=entry_fg, text_color=entry_text, button_color=button_fg, button_hover_color=button_hover)
    hrt_dose_option.configure(fg_color=entry_fg, text_color=entry_text, button_color=button_fg, button_hover_color=button_hover)
    hrt_route_option.configure(fg_color=entry_fg, text_color=entry_text, button_color=button_fg, button_hover_color=button_hover)
    # Entries/textboxes
    hrt_date_custom_entry.configure(fg_color=entry_fg, text_color=entry_text)
    hrt_time_custom_entry.configure(fg_color=entry_fg, text_color=entry_text)
    hrt_med_custom_entry.configure(fg_color=entry_fg, text_color=entry_text)
    hrt_dose_custom_entry.configure(fg_color=entry_fg, text_color=entry_text)
    hrt_delete_index.configure(fg_color=entry_fg, text_color=entry_text)
    hrt_log_textbox.configure(fg_color=entry_fg, text_color=entry_text)
    hrt_notes_entry.configure(fg_color=entry_fg, text_color=entry_text)
    # Buttons
    help_button.configure(fg_color=button_fg, hover_color=button_hover, text_color=text_fg)
    exit_button.configure(fg_color=delete_fg, hover_color=delete_hover, text_color="#fff")
    hrt_save_button.configure(fg_color=button_fg, hover_color=button_hover, text_color=text_fg)
    hrt_clear_button.configure(
        fg_color="#444444",
        hover_color="#555555",
        text_color=text_fg
    )
    hrt_delete_button.configure(fg_color=delete_fg, hover_color=delete_hover, text_color="#fff")
    hrt_duplicate_button.configure(fg_color=button_fg, hover_color=button_hover, text_color=text_fg)
    # NEW: style export buttons
    hrt_export_json_btn.configure(fg_color=button_fg, hover_color=button_hover, text_color=text_fg)
    hrt_export_csv_btn.configure(fg_color=button_fg, hover_color=button_hover, text_color=text_fg)
    hrt_open_folder_btn.configure(fg_color=button_fg, hover_color=button_hover, text_color=text_fg)
    # Universal/Cycle/Journal tab labels
    med_label.configure(text_color=text_fg)
    cycle_label.configure(text_color=text_fg)
    journal_label.configure(text_color=text_fg)

# Buttons at the bottom of the home tab
home_buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
home_buttons_frame.pack(side="bottom", pady=25)

help_button = ctk.CTkButton(
    home_buttons_frame,
    text="How do I use this app?",
    font=DEFAULT_FONT,
    command=show_help
)
help_button.pack(side="left", padx=10)

exit_button = ctk.CTkButton(
    home_buttons_frame,
    text="Exit",
    font=DEFAULT_FONT,
    fg_color="#b3261e",
    hover_color="#7f1b16",
    command=wellness_tracker_app.destroy
)
exit_button.pack(side="left", padx=10)

# ---------- HRT TAB UI (Optimized, Multi-field, Improved Layout) ----------

# HRT tab
frame1 = ctk.CTkFrame(master=all_tabs.tab("HRT Tracker"))
frame1.configure(fg_color="#23272D", width=100, height=100)
frame1.pack(expand=True, fill="both", padx=20, pady=20)
frame1.pack_propagate(False)

# Section header for form
hrt_form_header = ctk.CTkLabel(
    frame1,
    text="Add HRT Entry",
    font=("Segoe UI", 16, "bold"),
    anchor="w",
)
hrt_form_header.pack(padx=10, pady=(10, 0), anchor="w")

# Main container: 2 columns (form | log)
hrt_main_frame = ctk.CTkFrame(frame1, fg_color="transparent")
hrt_main_frame.pack(expand=True, fill="both", padx=0, pady=0)
hrt_main_frame.pack_propagate(False)
hrt_main_frame.grid_columnconfigure(0, weight=1, uniform="hrt")
hrt_main_frame.grid_columnconfigure(1, weight=1, uniform="hrt")
hrt_main_frame.grid_rowconfigure(0, weight=1)

# ----- Left: Compact grid form -----
hrt_form_scroll = ctk.CTkScrollableFrame(
    hrt_main_frame,
    fg_color="#23272D",
    width=370,
    orientation="vertical",
)
hrt_form_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 18), pady=0)
hrt_form_scroll.grid_columnconfigure(0, weight=0)
hrt_form_scroll.grid_columnconfigure(1, weight=1)

row = 0
def add_label(text, tooltip=None):
    global row
    lbl = ctk.CTkLabel(hrt_form_scroll, text=text, font=DEFAULT_FONT, anchor="w")
    lbl.grid(row=row, column=0, sticky="w", padx=8, pady=(10 if row else 4, 4))
    if tooltip:
        lbl.bind("<Enter>", lambda e, t=tooltip: lbl.configure(text=f"{text}\n{t}"))
        lbl.bind("<Leave>", lambda e: lbl.configure(text=text))
    return lbl

# Date
hrt_date_label = add_label("Date:", "Select or enter the date of your dose.")
hrt_date_container = ctk.CTkFrame(hrt_form_scroll, fg_color="transparent")
hrt_date_container.grid(row=row, column=1, sticky="ew", padx=8, pady=6)
hrt_date_container.grid_columnconfigure(0, weight=1)
hrt_date_container.grid_columnconfigure(1, weight=0)
hrt_date_option = ctk.CTkOptionMenu(
    hrt_date_container,
    values=["Today", "Yesterday", "2 days ago", "1 week ago", "Other / Custom…"],
    font=DEFAULT_FONT,
    width=90,
)
hrt_date_option.grid(row=0, column=0, sticky="ew", padx=(0, 3))
hrt_date_option.set("Today")
hrt_date_custom_entry = ctk.CTkEntry(
    hrt_date_container,
    font=DEFAULT_FONT,
    width=90,
    placeholder_text="YYYY-MM-DD",
)
hrt_date_custom_entry.grid(row=0, column=1, sticky="ew")
row += 1

# Time
hrt_time_label = add_label("Time:", "Select or enter the time of your dose.")
hrt_time_container = ctk.CTkFrame(hrt_form_scroll, fg_color="transparent")
hrt_time_container.grid(row=row, column=1, sticky="ew", padx=8, pady=6)
hrt_time_container.grid_columnconfigure(0, weight=1)
hrt_time_container.grid_columnconfigure(1, weight=0)
hrt_time_option = ctk.CTkOptionMenu(
    hrt_time_container,
    values=["Now", "Morning", "Afternoon", "Evening", "Night", "Other / Custom…"],
    font=DEFAULT_FONT,
    width=80,
)
hrt_time_option.grid(row=0, column=0, sticky="ew", padx=(0, 3))
hrt_time_option.set("Now")
hrt_time_custom_entry = ctk.CTkEntry(
    hrt_time_container,
    font=DEFAULT_FONT,
    width=80,
    placeholder_text="HH:MM",
)
hrt_time_custom_entry.grid(row=0, column=1, sticky="ew")
row += 1

# Medication
hrt_med_label = add_label("Medication / preparation:", "Select or enter the medication name.")
hrt_med_container = ctk.CTkFrame(hrt_form_scroll, fg_color="transparent")
hrt_med_container.grid(row=row, column=1, sticky="ew", padx=8, pady=6)
hrt_med_container.grid_columnconfigure(0, weight=1)
hrt_med_container.grid_columnconfigure(1, weight=0)
hrt_med_option = ctk.CTkOptionMenu(
    hrt_med_container,
    values=[
        "Estradiol (any form)",
        "Testosterone (any form)",
        "Progesterone",
        "Anti-androgen (e.g. spironolactone)",
        "GnRH agonist / puberty blocker",
        "Other / Custom…",
    ],
    font=DEFAULT_FONT,
    width=120,
)
hrt_med_option.grid(row=0, column=0, sticky="ew", padx=(0, 3))
hrt_med_option.set("Estradiol (any form)")
hrt_med_custom_entry = ctk.CTkEntry(
    hrt_med_container,
    font=DEFAULT_FONT,
    width=120,
    placeholder_text="Custom name / brand",
)
hrt_med_custom_entry.grid(row=0, column=1, sticky="ew")
add_med_btn = ctk.CTkButton(
    hrt_med_container,
    text="+",
    width=28,
    command=lambda: add_extra_med_field(),
)
add_med_btn.grid(row=0, column=2, padx=(6,0))
row += 1

# Dose
hrt_dose_label = add_label("Dose:", "Select or enter the dose amount.")
hrt_dose_container = ctk.CTkFrame(hrt_form_scroll, fg_color="transparent")
hrt_dose_container.grid(row=row, column=1, sticky="ew", padx=8, pady=6)
hrt_dose_container.grid_columnconfigure(0, weight=1)
hrt_dose_container.grid_columnconfigure(1, weight=0)
hrt_dose_option = ctk.CTkOptionMenu(
    hrt_dose_container,
    values=[
        "Standard / as prescribed",
        "Low dose / microdosing",
        "Increased / higher than usual",
        "Missed dose",
        "Other / Custom…",
    ],
    font=DEFAULT_FONT,
    width=120,
)
hrt_dose_option.grid(row=0, column=0, sticky="ew", padx=(0, 3))
hrt_dose_option.set("Standard / as prescribed")
hrt_dose_custom_entry = ctk.CTkEntry(
    hrt_dose_container,
    font=DEFAULT_FONT,
    width=100,
    placeholder_text="e.g. 2 mg, 0.4 mL",
)
hrt_dose_custom_entry.grid(row=0, column=1, sticky="ew")
add_dose_btn = ctk.CTkButton(
    hrt_dose_container,
    text="+",
    width=28,
    command=lambda: add_extra_dose_field(),
)
add_dose_btn.grid(row=0, column=2, padx=(6,0))
row += 1

# Route
hrt_route_label = add_label("Route:", "How was the medication taken?")
hrt_route_option = ctk.CTkOptionMenu(
    hrt_form_scroll,
    values=[
        "Pill / Oral",
        "Sublingual / Buccal",
        "Injection (IM)",
        "Injection (SubQ)",
        "Patch",
        "Gel / Cream",
        "Implant",
        "Other",
    ],
    font=DEFAULT_FONT,
    width=120,
)
hrt_route_option.grid(row=row, column=1, padx=8, pady=6, sticky="ew")
hrt_route_option.set("Pill / Oral")
route_row = row
add_route_btn = ctk.CTkButton(
    hrt_form_scroll,
    text="+",
    width=28,
    command=lambda: add_extra_route_field(),
)
add_route_btn.grid(row=row, column=2, padx=(6,0))
row += 1

# --- NEW: Notes field ---
hrt_notes_label = add_label("Notes:", "Add any notes about this dose (optional).")
hrt_notes_entry = ctk.CTkEntry(
    hrt_form_scroll,
    font=DEFAULT_FONT,
    width=220,
    placeholder_text="e.g. feeling, reason, etc.",
)
hrt_notes_entry.grid(row=row, column=1, padx=8, pady=(6, 6), sticky="ew")
row += 1

# Buttons (horizontal, compact, more spacing)
hrt_buttons_frame = ctk.CTkFrame(hrt_form_scroll, fg_color="transparent")
hrt_buttons_frame.grid(row=row, column=0, columnspan=2, pady=(12, 16), sticky="ew")
hrt_buttons_frame.grid_columnconfigure(0, weight=1)
hrt_buttons_frame.grid_columnconfigure(1, weight=1)
hrt_buttons_frame.grid_columnconfigure(2, weight=1)
hrt_buttons_frame.grid_columnconfigure(3, weight=1)

# --- REPLACE Add Entry button with Save Entry button ---
hrt_save_button = ctk.CTkButton(
    hrt_buttons_frame,
    text="Save Entry (Ctrl+Enter)",
    font=DEFAULT_FONT,
    command=lambda: add_hrt_entry(show_errors=True),
    width=100,
)
hrt_save_button.grid(row=0, column=0, padx=8)

hrt_clear_button = ctk.CTkButton(
    hrt_buttons_frame,
    text="Clear (Esc)",
    font=DEFAULT_FONT,
    fg_color="#444444",
    hover_color="#555555",
    command=clear_hrt_form,
    width=80,
)
hrt_clear_button.grid(row=0, column=1, padx=8)

hrt_delete_button = ctk.CTkButton(
    hrt_buttons_frame,
    text="Delete # (Del)",
    font=("Segoe UI", 11),
    fg_color="#b3261e",
    hover_color="#7f1b16",
    width=80,
    command=lambda: delete_selected_hrt_entry(),
)
hrt_delete_button.grid(row=0, column=2, padx=8)

hrt_duplicate_button = ctk.CTkButton(
    hrt_buttons_frame,
    text="Duplicate last",
    font=("Segoe UI", 11),
    width=80,
    command=lambda: duplicate_last_hrt_to_form(),
)
hrt_duplicate_button.grid(row=0, column=3, padx=8)

row += 1

# Delete entry index
hrt_delete_label = add_label("Delete / Edit entry #:", "Type the number from the log to delete or edit.")

hrt_delete_index = ctk.CTkEntry(
    hrt_form_scroll,
    width=60,
    font=DEFAULT_FONT,
    placeholder_text="1",
)
hrt_delete_index.grid(row=row, column=1, padx=8, pady=(6, 6), sticky="w")
row += 1

# --- NEW: Edit button next to delete index ---
hrt_edit_button = ctk.CTkButton(
    hrt_form_scroll,
    text="Edit selected",
    font=("Segoe UI", 11),
    width=90,
    command=start_edit_selected_hrt_entry,
)
hrt_edit_button.grid(row=row, column=1, padx=8, pady=(0, 8), sticky="w")
row += 1

# --- NEW: Data / Export section ---
hrt_data_frame = ctk.CTkFrame(hrt_form_scroll, fg_color="transparent")
hrt_data_frame.grid(row=row, column=0, columnspan=3, padx=8, pady=(4, 12), sticky="ew")
hrt_data_frame.grid_columnconfigure(0, weight=1)
hrt_data_frame.grid_columnconfigure(1, weight=1)
hrt_data_frame.grid_columnconfigure(2, weight=1)

hrt_export_json_btn = ctk.CTkButton(
    hrt_data_frame,
    text="Export JSON",
    font=("Segoe UI", 11),
    command=export_hrt_to_json,
    width=80,
)
hrt_export_json_btn.grid(row=0, column=0, padx=4, pady=2, sticky="ew")

hrt_export_csv_btn = ctk.CTkButton(
    hrt_data_frame,
    text="Export CSV",
    font=("Segoe UI", 11),
    command=export_hrt_to_csv,
    width=80,
)
hrt_export_csv_btn.grid(row=0, column=1, padx=4, pady=2, sticky="ew")

hrt_open_folder_btn = ctk.CTkButton(
    hrt_data_frame,
    text="Open HRT folder",
    font=("Segoe UI", 11),
    command=open_hrt_folder,
    width=80,
)
hrt_open_folder_btn.grid(row=0, column=2, padx=4, pady=2, sticky="ew")

row += 1

# Divider line between form and log
divider = ctk.CTkFrame(hrt_main_frame, fg_color="#393E46", height=2)
divider.grid(row=0, column=0, sticky="sew", padx=(0,0), pady=(0,0))
divider.lower()  # keep behind form

# ----- Right: Log area -----
hrt_log_frame = ctk.CTkFrame(hrt_main_frame, fg_color="#23272D", border_width=2, border_color="#393E46")
hrt_log_frame.grid(row=0, column=1, sticky="nsew", padx=(18, 0), pady=0)
hrt_log_frame.grid_rowconfigure(1, weight=1)
hrt_log_frame.grid_columnconfigure(0, weight=1)

# Section header for log
hrt_log_header = ctk.CTkLabel(
    hrt_log_frame,
    text="HRT Log",
    font=("Segoe UI", 16, "bold"),
    anchor="w",
)
hrt_log_header.grid(row=0, column=0, padx=12, pady=(12, 2), sticky="w")

hrt_log_label = ctk.CTkLabel(
    hrt_log_frame,
    text="Most recent at top:",
    font=DEFAULT_FONT,
    anchor="w",
)
hrt_log_label.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")

hrt_log_textbox = ctk.CTkTextbox(
    hrt_log_frame,
    font=("Consolas", 11),
    wrap="word",
    height=340,
)
hrt_log_textbox.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="nsew")
hrt_log_textbox.configure(state="disabled")

# --- Add dynamic fields support ---
def _make_removable_row(container, widgets_list, entry_tuple_or_opt, row_type: str):
    """Helper: attach a small '×' button to remove this extra field."""
    remove_btn = ctk.CTkButton(
        container,
        text="×",
        width=24,
        fg_color="#b3261e",
        hover_color="#7f1b16",
        command=lambda: _remove_extra_row(container, widgets_list, entry_tuple_or_opt, row_type),
    )
    remove_btn.grid(row=0, column=len(container.grid_slaves()) , padx=(4, 0))

def _remove_extra_row(container, widgets_list, entry_tuple_or_opt, row_type: str):
    try:
        widgets_list.remove(entry_tuple_or_opt)
    except ValueError:
        pass
    container.destroy()

def add_extra_med_field():
    idx = len(extra_med_fields)
    container = ctk.CTkFrame(hrt_med_container, fg_color="transparent")
    container.grid(row=idx+1, column=0, columnspan=4, sticky="ew", pady=1)
    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=1)

    opt = ctk.CTkOptionMenu(
        container,
        values=[
            "Estradiol (any form)",
            "Testosterone (any form)",
            "Progesterone",
            "Anti-androgen (e.g. spironolactone)",
            "GnRH agonist / puberty blocker",
            "Other / Custom…",
        ],
        font=DEFAULT_FONT,
        width=120,
    )
    opt.grid(row=0, column=0, sticky="ew", padx=(0, 3))
    opt.set("Estradiol (any form)")
    custom = ctk.CTkEntry(
        container,
        font=DEFAULT_FONT,
        width=120,
        placeholder_text="Custom name / brand",
    )
    custom.grid(row=0, column=1, sticky="ew")

    pair = (opt, custom)
    extra_med_fields.append(pair)
    _make_removable_row(container, extra_med_fields, pair, "med")

def add_extra_dose_field():
    idx = len(extra_dose_fields)
    container = ctk.CTkFrame(hrt_dose_container, fg_color="transparent")
    container.grid(row=idx+1, column=0, columnspan=4, sticky="ew", pady=1)
    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=1)

    opt = ctk.CTkOptionMenu(
        container,
        values=[
            "Standard / as prescribed",
            "Low dose / microdosing",
            "Increased / higher than usual",
            "Missed dose",
            "Other / Custom…",
        ],
        font=DEFAULT_FONT,
        width=120,
    )
    opt.grid(row=0, column=0, sticky="ew", padx=(0, 3))
    opt.set("Standard / as prescribed")
    custom = ctk.CTkEntry(
        container,
        font=DEFAULT_FONT,
        width=100,
        placeholder_text="e.g. 2 mg, 0.4 mL",
    )
    custom.grid(row=0, column=1, sticky="ew")

    pair = (opt, custom)
    extra_dose_fields.append(pair)
    _make_removable_row(container, extra_dose_fields, pair, "dose")

def add_extra_route_field():
    idx = len(extra_route_fields)
    container = ctk.CTkFrame(hrt_form_scroll, fg_color="transparent")
    container.grid(row=route_row+idx+1, column=1, sticky="ew", padx=8, pady=1)
    container.grid_columnconfigure(0, weight=1)

    opt = ctk.CTkOptionMenu(
        container,
        values=[
            "Pill / Oral",
            "Sublingual / Buccal",
            "Injection (IM)",
            "Injection (SubQ)",
            "Patch",
            "Gel / Cream",
            "Implant",
            "Other",
        ],
        font=DEFAULT_FONT,
        width=120,
    )
    opt.grid(row=0, column=0, sticky="ew")
    opt.set("Pill / Oral")

    extra_route_fields.append(opt)
    _make_removable_row(container, extra_route_fields, opt, "route")

# Keyboard shortcuts for fast entry
def _hrt_shortcuts(event):
    if event.keysym == "Return" and (event.state & 0x4):  # Ctrl+Enter
        add_hrt_entry(show_errors=True)
        return "break"
    if event.keysym == "Escape":
        clear_hrt_form()
        _finish_edit_mode()
        return "break"
    if event.keysym == "Delete":
        delete_selected_hrt_entry()
        return "break"
hrt_form_scroll.bind_all("<Control-Return>", _hrt_shortcuts)
hrt_form_scroll.bind_all("<Escape>", _hrt_shortcuts)
hrt_form_scroll.bind_all("<Delete>", _hrt_shortcuts)

# Focus traversal for fast entry
for widget in [
    hrt_date_option, hrt_date_custom_entry, hrt_time_option, hrt_time_custom_entry,
    hrt_med_option, hrt_med_custom_entry, hrt_dose_option, hrt_dose_custom_entry,
    hrt_route_option, 
    hrt_save_button, hrt_clear_button, hrt_delete_index  # <-- use hrt_save_button instead of hrt_add_button
]:
    widget.bind("<Tab>", lambda e: e.widget.tk_focusNext().focus() or "break")
    widget.bind("<Shift-Tab>", lambda e: e.widget.tk_focusPrev().focus() or "break")

# initialize with entries from disk, then draw log
load_hrt_entries_from_files()
refresh_hrt_log()

# Universal Medication tab
frame2 = ctk.CTkFrame(master=all_tabs.tab("Universal Medication tracker"))
frame2.configure(fg_color="#2a2a2a", width=100, height=100)
frame2.pack(expand=True, fill="both", padx=20, pady=20)  # More padding inside tab
frame2.pack_propagate(False)
frame2.grid_rowconfigure(0, weight=1)
frame2.grid_columnconfigure(0, weight=1)
med_label = ctk.CTkLabel(
    frame2,
    text="Universal Medication Tracker\n\n(Add medication entries here.)",
    font=DEFAULT_FONT,
    justify="center"
)
med_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)  # More padding

# Cycle Tracker tab
frame3 = ctk.CTkFrame(master=all_tabs.tab("Cycle Tracker"))
frame3.configure(fg_color="#2a2a2a", width=100, height=100)
frame3.pack(expand=True, fill="both", padx=20, pady=20)  # More padding inside tab
frame3.pack_propagate(False)
frame3.grid_rowconfigure(0, weight=1)
frame3.grid_columnconfigure(0, weight=1)
cycle_label = ctk.CTkLabel(
    frame3,
    text="Cycle Tracker\n\n(Log your cycle days and symptoms here.)",
    font=DEFAULT_FONT,
    justify="center"
)
cycle_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)  # More padding

# Private Journal tab
frame4 = ctk.CTkFrame(master=all_tabs.tab("Private Journal/Diary"))
frame4.configure(fg_color="#2a2a2a", width=100, height=100)
frame4.pack(expand=True, fill="both", padx=20, pady=20)  # More padding inside tab
frame4.pack_propagate(False)
frame4.grid_rowconfigure(0, weight=1)
frame4.grid_columnconfigure(0, weight=1)
journal_label = ctk.CTkLabel(
    frame4,
    text="Private Journal / Diary\n\n(You can add a text box here for writing.)",
    font=DEFAULT_FONT,
    justify="center"
)
journal_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)  # More padding

# After all widgets are created, call once to set initial colors
update_theme_colors()

wellness_tracker_app.mainloop()