# This code is generated using PyUIbuilder: https://pyuibuilder.com

import os
import json
import customtkinter as ctk
from datetime import datetime, timedelta
import ctypes
from ctypes import wintypes
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "hrt_entries.json")

DATA_VERSION = 2

hrt_entries = []
filtered_hrt_entries: list[dict] = []

table_row_labels = []
current_meds: list[dict] = []  # each: {"med": str, "dose": str}
med_row_widgets: list[tuple] = []

# --- NEW: keep track if we’re editing instead of adding ---
editing_index: int | None = None  # index into hrt_entries we’re replacing

MED_PRESETS = ["Estradiol", "Progesterone", "Spironolactone", "Testosterone", "Blocker combo", "Custom"]
DOSE_PRESETS = ["0.5 mg", "1 mg", "2 mg", "3 mg", "4 mg", "5 mg", "10 mg", "Custom"]
TIME_OF_DAY_PRESETS = ["Now", "Morning", "Afternoon", "Evening", "Night"]

def _validate_entry_dict(raw) -> dict | None:
    """Validate a single entry dict from disk, return cleaned version or None."""
    if not isinstance(raw, dict):
        return None
    allowed_keys = {"date", "time", "med", "dose", "route", "notes", "group_id"}
    entry = {k: (str(raw.get(k, "")).strip()) for k in allowed_keys}
    if not entry["med"] or not entry["dose"]:
        return None
    try:
        if entry["date"]:
            datetime.strptime(entry["date"], "%Y-%m-%d")
    except Exception:
        entry["date"] = ""
    try:
        if entry["time"]:
            datetime.strptime(entry["time"], "%H:%M")
    except Exception:
        entry["time"] = ""
    if not entry.get("group_id"):
        entry["group_id"] = str(uuid.uuid4())
    return entry

def load_hrt_entries():
    """Load entries from JSON file into memory with basic validation."""
    global hrt_entries, filtered_hrt_entries
    if not os.path.exists(DATA_FILE):
        hrt_entries = []
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        hrt_entries = []
        safe_show_error("Could not read saved data (file may be corrupt). Starting with an empty list.")
        return

    if isinstance(data, dict) and "entries" in data:
        raw_entries = data.get("entries", [])
    else:
        raw_entries = data if isinstance(data, list) else []

    cleaned: list[dict] = []
    for item in raw_entries:
        valid = _validate_entry_dict(item)
        if valid is not None:
            cleaned.append(valid)
    hrt_entries = cleaned
    filtered_hrt_entries = list(hrt_entries)

def save_hrt_entries():
    """Persist in‑memory entries to JSON file (with version wrapper)."""
    payload = {
        "version": DATA_VERSION,
        "entries": hrt_entries,
    }
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception:
        safe_show_error("Could not save entries to disk. Your latest changes may not be persisted.")

def safe_show_error(message: str):
    """Wrapper around show_error that never raises."""
    try:
        show_error(message)
    except Exception:
        print(f"ERROR: {message}")

def show_error(message: str):
    """Simple popup error dialog."""
    dialog = ctk.CTkToplevel()
    dialog.title("Error")
    dialog.configure(fg_color="#2a2a2a")
    dialog.geometry("320x160")

    dialog.transient(wellness_tracker_app)
    dialog.grab_set()
    try:
        dialog.update_idletasks()
        if wellness_tracker_app.winfo_ismapped():
            x = wellness_tracker_app.winfo_rootx()
            y = wellness_tracker_app.winfo_rooty()
            w = wellness_tracker_app.winfo_width()
            h = wellness_tracker_app.winfo_height()
            dx = x + (w // 2) - (320 // 2)
            dy = y + (h // 2) - (160 // 2)
            dialog.geometry(f"320x160+{dx}+{dy}")
    except Exception:
        pass

    ctk.CTkLabel(dialog, text=message, wraplength=300, justify="left").pack(padx=12, pady=(20, 10))
    ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=(0, 16))

def set_time_from_preset(selection: str):
    """Fill time_entry based on quick-select option."""
    if selection == "Now":
        value = datetime.now().strftime("%H:%M")
    elif selection == "Morning":
        value = "08:00"
    elif selection == "Afternoon":
        value = "13:00"
    elif selection == "Evening":
        value = "18:00"
    elif selection == "Night":
        value = "22:00"
    else:
        return
    time_entry.delete(0, "end")
    time_entry.insert(0, value)

def _validate_date(date_val: str) -> bool:
    if not date_val:
        return True
    try:
        datetime.strptime(date_val, "%Y-%m-%d")
        return True
    except Exception:
        return False

def _validate_time(time_val: str) -> bool:
    if not time_val:
        return True
    try:
        datetime.strptime(time_val, "%H:%M")
        return True
    except Exception:
        return False

def _sync_current_meds_from_widgets():
    """Read med/dose widgets into current_meds list."""
    global current_meds
    new_list: list[dict] = []
    for _row_frame, med_widget, dose_widget in med_row_widgets:
        med_val = med_widget.get().strip()
        dose_val = dose_widget.get().strip()
        if med_val or dose_val:
            new_list.append({"med": med_val, "dose": dose_val})
    current_meds = new_list

def _rebuild_med_rows():
    """Rebuild med rows UI from current_meds."""
    global med_row_widgets
    for row_frame, _m, _d in med_row_widgets:
        row_frame.destroy()
    med_row_widgets = []

    for idx, med_item in enumerate(current_meds):
        _add_med_row_to_ui(med_item.get("med", ""), med_item.get("dose", ""), idx)

    if not current_meds:
        current_meds.append({"med": "", "dose": ""})
        _add_med_row_to_ui("", "", 0)

def _add_med_row_to_ui(med_val: str = "", dose_val: str = "", row_index: int | None = None):
    """Create a single row in the meds editor table."""
    global med_row_widgets
    row_frame = ctk.CTkFrame(meds_table_body, fg_color="transparent")
    row_frame.pack(fill="x", pady=2)

    med_combo = ctk.CTkComboBox(
        row_frame,
        values=MED_PRESETS,
        width=150,
    )
    med_combo.pack(side="left", padx=(0, 4))
    med_combo.set(med_val or MED_PRESETS[0])

    dose_combo = ctk.CTkComboBox(
        row_frame,
        values=DOSE_PRESETS,
        width=100,
    )
    dose_combo.pack(side="left", padx=(0, 4))
    dose_combo.set(dose_val or DOSE_PRESETS[1])

    remove_btn = ctk.CTkButton(
        row_frame,
        text="–",
        width=28,
        fg_color="#8b2b2b",
        command=lambda rf=row_frame: _remove_med_row(rf),
    )
    remove_btn.pack(side="left", padx=(4, 0))

    med_row_widgets.append((row_frame, med_combo, dose_combo))

def _remove_med_row(row_frame):
    """Remove a med row both from UI and current_meds."""
    global med_row_widgets, current_meds
    idx_to_remove = None
    for idx, (rf, _m, _d) in enumerate(med_row_widgets):
        if rf is row_frame:
            idx_to_remove = idx
            break
    if idx_to_remove is None:
        return
    row_frame.destroy()
    del med_row_widgets[idx_to_remove]
    _sync_current_meds_from_widgets()
    if not med_row_widgets:
        current_meds = [{"med": "", "dose": ""}]
        _rebuild_med_rows()

def add_hrt_entry():
    """Add a new group of meds OR save edits to an existing one."""
    global editing_index
    try:
        _sync_current_meds_from_widgets()
        date_val = date_entry.get().strip()
        route_val = route_option.get().strip()
        time_val = time_entry.get().strip()
        notes_val = notes_entry.get("0.0", "end").strip()

        if not date_val:
            date_val = datetime.now().strftime("%Y-%m-%d")
        if not time_val:
            time_val = datetime.now().strftime("%H:%M")

        if not _validate_date(date_val):
            show_error("Date must be in the format YYYY-MM-DD.")
            return
        if not _validate_time(time_val):
            show_error("Time must be in the format HH:MM (24‑hour).")
            return

        meds_clean = [
            m for m in current_meds
            if m.get("med", "").strip() and m.get("dose", "").strip()
        ]
        if not meds_clean:
            show_error("Add at least one medication (name and dose).")
            return

        group_id = str(uuid.uuid4())
        if editing_index is not None and 0 <= editing_index < len(hrt_entries):
            group_id = hrt_entries[editing_index].get("group_id", group_id)
            gid = group_id
            hrt_entries[:] = [e for e in hrt_entries if e.get("group_id") != gid]

        for m in meds_clean:
            hrt_entries.append(
                {
                    "group_id": group_id,
                    "date": date_val,
                    "time": time_val,
                    "med": m["med"].strip(),
                    "dose": m["dose"].strip(),
                    "route": route_val or "Other",
                    "notes": notes_val,
                }
            )

        save_hrt_entries()
        editing_index = None
        add_button.configure(text="Add Entry")
        clear_hrt_form()
        apply_filters_and_refresh()
    except Exception as exc:
        safe_show_error(f"Unexpected error while adding entry:\n{exc!r}")

def clear_hrt_form():
    """Reset the form fields and meds list."""
    global current_meds, editing_index
    editing_index = None
    add_button.configure(text="Add Entry")
    set_today()
    time_entry.delete(0, "end")
    time_entry.insert(0, datetime.now().strftime("%H:%M"))
    notes_entry.delete("0.0", "end")
    route_option.set("Oral")
    current_meds = [{"med": "", "dose": ""}]
    _rebuild_med_rows()

def on_row_click(row_index: int):
    """Highlight selected row and remember index."""
    global selected_row_index
    selected_row_index = row_index
    for idx, labels in enumerate(table_row_labels):
        base = "#262626" if idx % 2 == 0 else "#2b2b2b"
        bg = base if idx != row_index else "#3b3f45"
        for lbl in labels:
            lbl.configure(fg_color=bg)
    try:
        delete_button.configure(state="normal")
        edit_button.configure(state="normal")
    except Exception:
        pass

def delete_selected_entry():
    """Delete currently selected row (single med), if any."""
    global selected_row_index, hrt_entries, filtered_hrt_entries
    try:
        if selected_row_index is None:
            return
        if not (0 <= selected_row_index < len(filtered_hrt_entries)):
            selected_row_index = None
            refresh_hrt_table()
            return
        entry_to_delete = filtered_hrt_entries[selected_row_index]
        try:
            hrt_entries.remove(entry_to_delete)
        except ValueError:
            pass
        save_hrt_entries()
        selected_row_index = None
        apply_filters_and_refresh()
    except Exception as exc:
        safe_show_error(f"Unexpected error while deleting entry:\n{exc!r}")

def _load_entry_into_form(entry: dict):
    """Populate the form from a single entry dict."""
    global current_meds
    date_entry.delete(0, "end")
    date_entry.insert(0, entry.get("date", ""))
    time_entry.delete(0, "end")
    time_entry.insert(0, entry.get("time", ""))
    route_option.set(entry.get("route", "Oral") or "Oral")
    notes_entry.delete("0.0", "end")
    notes_entry.insert("0.0", entry.get("notes", ""))
    current_meds = [{"med": entry.get("med", ""), "dose": entry.get("dose", "")}]
    _rebuild_med_rows()

def edit_selected_entry():
    """Switch form into 'edit' mode for the selected group."""
    global editing_index
    try:
        if selected_row_index is None:
            safe_show_error("Select a row first to edit.")
            return
        if not (0 <= selected_row_index < len(filtered_hrt_entries)):
            safe_show_error("Selected row is out of range.")
            return
        entry = filtered_hrt_entries[selected_row_index]
        try:
            editing_index = hrt_entries.index(entry)
        except ValueError:
            editing_index = None
        _load_entry_into_form(entry)
        add_button.configure(text="Save Changes")
    except Exception as exc:
        safe_show_error(f"Unexpected error while editing entry:\n{exc!r}")

def fill_from_last_entry():
    """Quickly fill form using values from the most recent entry."""
    if not hrt_entries:
        safe_show_error("No previous entry to copy from.")
        return
    last = sorted(hrt_entries, key=lambda e: (e.get("date", ""), e.get("time", "")))[-1]
    _load_entry_into_form(last)

def apply_filters_and_refresh():
    """Apply current search and date filters, refresh table."""
    global filtered_hrt_entries, selected_row_index

    text_val = filter_text_entry.get().strip().lower() if filter_text_entry.get() else ""
    from_val = filter_from_entry.get().strip()
    to_val = filter_to_entry.get().strip()

    from_dt = None
    to_dt = None
    if from_val:
        try:
            from_dt = datetime.strptime(from_val, "%Y-%m-%d").date()
        except Exception:
            pass
    if to_val:
        try:
            to_dt = datetime.strptime(to_val, "%Y-%m-%d").date()
        except Exception:
            pass

    result = []
    for e in hrt_entries:
        if from_dt or to_dt:
            try:
                e_date = datetime.strptime(e.get("date", ""), "%Y-%m-%d").date()
            except Exception:
                continue
            if from_dt and e_date < from_dt:
                continue
            if to_dt and e_date > to_dt:
                continue

        if text_val:
            haystack = " ".join(
                [
                    e.get("med", ""),
                    e.get("dose", ""),
                    e.get("route", ""),
                    e.get("notes", ""),
                ]
            ).lower()
            if text_val not in haystack:
                continue

        result.append(e)

    filtered_hrt_entries = result
    selected_row_index = None
    refresh_hrt_table()

def clear_filters():
    filter_text_entry.delete(0, "end")
    filter_from_entry.delete(0, "end")
    filter_to_entry.delete(0, "end")
    apply_filters_and_refresh()

def quick_filter_today():
    today = datetime.now().strftime("%Y-%m-%d")
    filter_from_entry.delete(0, "end")
    filter_from_entry.insert(0, today)
    filter_to_entry.delete(0, "end")
    filter_to_entry.insert(0, today)
    apply_filters_and_refresh()

def quick_filter_last_7():
    today = datetime.now().date()
    start = (today - timedelta(days=6)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    filter_from_entry.delete(0, "end")
    filter_from_entry.insert(0, start)
    filter_to_entry.delete(0, "end")
    filter_to_entry.insert(0, end)
    apply_filters_and_refresh()

def quick_filter_all():
    clear_filters()

def refresh_hrt_table():
    """Rebuild the table UI from filtered_hrt_entries."""
    global table_row_labels
    table_row_labels = []
    for child in table_body_frame.winfo_children():
        child.destroy()

    for row_idx, entry in enumerate(filtered_hrt_entries):
        row_labels = []
        bg_base = "#262626" if row_idx % 2 == 0 else "#2b2b2b"

        def make_label(col, text, wrap=False):
            lbl = ctk.CTkLabel(
                table_body_frame,
                text=text,
                anchor="w",
                fg_color=bg_base,
                wraplength=220 if wrap else 0,
                justify="left",
                padx=4,
                pady=2,
            )
            lbl.grid(row=row_idx, column=col, padx=1, pady=1, sticky="nw")
            lbl.bind("<Button-1>", lambda _e, r=row_idx: on_row_click(r))
            row_labels.append(lbl)

        make_label(0, entry.get("date", ""))
        make_label(1, entry.get("time", ""))
        make_label(2, entry.get("med", ""))
        make_label(3, entry.get("dose", ""))
        make_label(4, entry.get("route", ""))
        make_label(5, entry.get("notes", ""), wrap=True)
        table_row_labels.append(row_labels)

    try:
        if selected_row_index is None:
            delete_button.configure(state="disabled")
            edit_button.configure(state="disabled")
        else:
            delete_button.configure(state="normal")
            edit_button.configure(state="normal")
    except Exception:
        pass

def snap_window_to_top_left(root):
    """Position the window at the top-left of the usable work area (avoids taskbar)."""
    left, top = 0, 0
    try:
        if os.name == "nt":
            SPI_GETWORKAREA = 0x0030
            rect = wintypes.RECT()
            if ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0):
                left, top = rect.left, rect.top
    except Exception:
        pass

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    if width <= 1 or height <= 1:
        try:
            size = root.geometry().split("+")[0]
            w, h = size.split("x")
            width, height = int(w), int(h)
        except Exception:
            width, height = 900, 600

    root.geometry(f"{width}x{height}+{left}+{top}")
    root.update_idletasks()

# --- UI SETUP ---
wellness_tracker_app = ctk.CTk()
wellness_tracker_app.configure(fg_color="#23272D")
wellness_tracker_app.title("HRT Tracker")
wellness_tracker_app.geometry("900x600")
wellness_tracker_app.minsize(900, 600)
snap_window_to_top_left(wellness_tracker_app)

all_tabs = ctk.CTkTabview(wellness_tracker_app)
all_tabs.add("HRT Tracker")
all_tabs.configure()
all_tabs.pack(side=ctk.LEFT, anchor='n', fill="both", expand=True)

frame1 = ctk.CTkFrame(master=all_tabs.tab("HRT Tracker"))
frame1.configure(fg_color="#2a2a2a")
frame1.pack(expand=True, fill="both", padx=10, pady=10)

form_frame = ctk.CTkFrame(frame1, fg_color="#333333", corner_radius=8)
form_frame.pack(side="left", fill="y", padx=(0, 10), pady=0)
ctk.CTkLabel(form_frame, text="Log HRT Dose", font=("Segoe UI", 16, "bold")).grid(
    row=0, column=0, columnspan=3, pady=(8, 12), padx=8, sticky="w"
)

when_frame = ctk.CTkFrame(form_frame, fg_color="#3b3b3b")
when_frame.grid(row=1, column=0, columnspan=3, padx=8, pady=(0, 8), sticky="ew")
ctk.CTkLabel(when_frame, text="When", font=("Segoe UI", 13, "bold")).grid(
    row=0, column=0, columnspan=3, padx=8, pady=(6, 4), sticky="w"
)

ctk.CTkLabel(when_frame, text="Date:").grid(row=1, column=0, padx=(8, 4), pady=4, sticky="e")
date_entry = ctk.CTkEntry(when_frame, width=110)
date_entry.grid(row=1, column=1, padx=(0, 4), pady=4, sticky="w")

def set_today():
    date_entry.delete(0, "end")
    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

def set_yesterday():
    date_entry.delete(0, "end")
    date_entry.insert(0, (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))

quick_date_frame = ctk.CTkFrame(when_frame, fg_color="transparent")
quick_date_frame.grid(row=1, column=2, padx=(0, 8), pady=4, sticky="w")
ctk.CTkButton(quick_date_frame, text="Today", width=60, command=set_today).pack(side="left", padx=(0, 2))
ctk.CTkButton(quick_date_frame, text="Yesterday", width=80, command=set_yesterday).pack(side="left")

ctk.CTkLabel(when_frame, text="Time:").grid(row=2, column=0, padx=(8, 4), pady=4, sticky="e")
time_entry = ctk.CTkEntry(when_frame, width=80)
time_entry.grid(row=2, column=1, padx=(0, 4), pady=4, sticky="w")

time_preset_menu = ctk.CTkOptionMenu(
    when_frame,
    values=TIME_OF_DAY_PRESETS,
    command=set_time_from_preset,
    width=110,
)
time_preset_menu.grid(row=2, column=2, padx=(0, 8), pady=4, sticky="w")
time_preset_menu.set("Now")

ctk.CTkLabel(form_frame, text="Medications", font=("Segoe UI", 13, "bold")).grid(
    row=2, column=0, columnspan=3, padx=8, pady=(4, 2), sticky="w"
)
meds_table_container = ctk.CTkFrame(form_frame, fg_color="#2f2f2f")
meds_table_container.grid(row=3, column=0, columnspan=3, padx=8, pady=(0, 4), sticky="ew")

meds_header = ctk.CTkFrame(meds_table_container, fg_color="transparent")
meds_header.pack(fill="x", padx=4, pady=(4, 2))
ctk.CTkLabel(meds_header, text="Medication", width=140).pack(side="left", padx=(0, 4))
ctk.CTkLabel(meds_header, text="Dose", width=80).pack(side="left", padx=(0, 4))

meds_table_body = ctk.CTkScrollableFrame(meds_table_container, fg_color="#252525", height=120)
meds_table_body.pack(fill="both", expand=True, padx=4, pady=(0, 4))

meds_controls = ctk.CTkFrame(meds_table_container, fg_color="transparent")
meds_controls.pack(fill="x", padx=4, pady=(0, 4))

def _on_add_med_row_click():
    _sync_current_meds_from_widgets()
    current_meds.append({"med": "", "dose": ""})
    _rebuild_med_rows()

ctk.CTkButton(
    meds_controls,
    text="Add medication",
    width=130,
    command=_on_add_med_row_click,
).pack(side="left", pady=(2, 4))

ctk.CTkLabel(form_frame, text="Route").grid(row=4, column=0, padx=8, pady=(4, 2), sticky="w")
route_option = ctk.CTkOptionMenu(
    form_frame,
    values=["Oral", "Sublingual", "Patch", "Injection (IM)", "Injection (SC)", "Gel", "Cream", "Other"],
    width=160,
)
route_option.grid(row=4, column=1, columnspan=2, padx=8, pady=(4, 2), sticky="w")
route_option.set("Oral")

ctk.CTkLabel(form_frame, text="Notes").grid(row=5, column=0, padx=8, pady=(4, 2), sticky="nw")
notes_entry = ctk.CTkTextbox(form_frame, width=260, height=80)
notes_entry.grid(row=5, column=1, columnspan=2, padx=8, pady=(4, 2), sticky="w")

actions_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
actions_frame.grid(row=6, column=0, columnspan=3, padx=8, pady=(8, 8), sticky="ew")

add_button = ctk.CTkButton(actions_frame, text="Add Entry", command=add_hrt_entry)
add_button.pack(side="right", padx=(4, 0))

clear_button = ctk.CTkButton(actions_frame, text="Clear", fg_color="#555555", command=clear_hrt_form)
clear_button.pack(side="right", padx=(4, 4))

same_as_last_button = ctk.CTkButton(actions_frame, text="Same as last", fg_color="#444444", command=fill_from_last_entry)
same_as_last_button.pack(side="left")

table_frame = ctk.CTkFrame(frame1, fg_color="#333333")
table_frame.pack(side="left", fill="both", expand=True)

ctk.CTkLabel(table_frame, text="Logged HRT Doses", font=("Segoe UI", 16, "bold")).pack(
    anchor="w", padx=8, pady=(8, 4)
)

filters_frame = ctk.CTkFrame(table_frame, fg_color="#3b3b3b")
filters_frame.pack(fill="x", padx=4, pady=(0, 4))

ctk.CTkLabel(filters_frame, text="Search:").grid(row=0, column=0, padx=4, pady=4, sticky="e")
filter_text_entry = ctk.CTkEntry(filters_frame, width=180, placeholder_text="med, dose, notes...")
filter_text_entry.grid(row=0, column=1, padx=4, pady=4, sticky="w")

quick_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
quick_frame.grid(row=0, column=2, padx=(12, 4), pady=4, sticky="w")
ctk.CTkButton(quick_frame, text="Today", width=70, command=quick_filter_today).pack(side="left", padx=(0, 2))
ctk.CTkButton(quick_frame, text="Last 7 days", width=90, command=quick_filter_last_7).pack(side="left", padx=(0, 2))
ctk.CTkButton(quick_frame, text="All", width=60, command=quick_filter_all).pack(side="left", padx=(0, 2))

ctk.CTkLabel(filters_frame, text="From:").grid(row=1, column=0, padx=4, pady=2, sticky="e")
filter_from_entry = ctk.CTkEntry(filters_frame, width=100, placeholder_text="YYYY-MM-DD")
filter_from_entry.grid(row=1, column=1, padx=4, pady=2, sticky="w")

ctk.CTkLabel(filters_frame, text="To:").grid(row=1, column=2, padx=(12, 4), pady=2, sticky="e")
filter_to_entry = ctk.CTkEntry(filters_frame, width=100, placeholder_text="YYYY-MM-DD")
filter_to_entry.grid(row=1, column=3, padx=4, pady=2, sticky="w")

ctk.CTkButton(filters_frame, text="Apply", width=70, command=apply_filters_and_refresh).grid(
    row=1, column=4, padx=(12, 2), pady=2
)
ctk.CTkButton(filters_frame, text="Clear", width=70, fg_color="#555555", command=clear_filters).grid(
    row=1, column=5, padx=(2, 4), pady=2
)

header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
header_frame.pack(fill="x", padx=4)

headers = ["Date", "Time", "Medication", "Dose", "Route", "Notes"]
for idx, h in enumerate(headers):
    ctk.CTkLabel(header_frame, text=h, font=("Segoe UI", 12, "bold")).grid(row=0, column=idx, padx=4, pady=2, sticky="w")

table_body_frame = ctk.CTkScrollableFrame(table_frame, fg_color="#2b2b2b")
table_body_frame.pack(fill="both", expand=True, padx=4, pady=(0, 8))

row_actions_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
row_actions_frame.pack(fill="x", padx=4, pady=(0, 8))

selected_row_index = None
edit_button = ctk.CTkButton(
    row_actions_frame,
    text="Edit Selected",
    fg_color="#2b6ca3",
    command=edit_selected_entry,
    state="disabled",
)
edit_button.pack(side="right", padx=4, pady=4)

delete_button = ctk.CTkButton(
    row_actions_frame,
    text="Delete Selected",
    fg_color="#8b2b2b",
    command=delete_selected_entry,
    state="disabled",
)
delete_button.pack(side="right", padx=4, pady=4)

set_today()
time_entry.delete(0, "end")
time_entry.insert(0, datetime.now().strftime("%H:%M"))
current_meds = [{"med": "", "dose": ""}]
_rebuild_med_rows()

load_hrt_entries()
apply_filters_and_refresh()

wellness_tracker_app.mainloop()