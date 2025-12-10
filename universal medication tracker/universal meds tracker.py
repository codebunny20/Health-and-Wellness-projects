# This code is generated using PyUIbuilder: https://pyuibuilder.com

import os
import json
import datetime
import customtkinter as ctk
from tkinter import messagebox  # added

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "medication_log.txt")
JSON_PATH = os.path.join(BASE_DIR, "medication_log.json")

# in‑memory list of entries (each entry is a dict)
med_entries: list[dict] = []
filtered_type: str | None = None  # for type filtering
filtered_date_range: str = "Today"  # "Today", "Last 7 days", "All"
search_text: str = ""  # substring filter (name/notes)
selected_entry_index: int | None = None  # currently selected entry in med_entries


def format_entry(entry: dict) -> str:
    """Return a single‑line human readable log string for export."""
    return (
        f"{entry['timestamp']} | "
        f"{entry['type']} | "
        f"{entry['time_of_day']} | "
        f"{entry['name']} {entry['dose']} | "
        f"{entry['notes']}"
    )


def pretty_format_entry(entry: dict, index: int) -> str:
    """Multi‑line format for display in the textbox."""
    return (
        f"#{index + 1}  {entry['timestamp']}\n"
        f"  Type: {entry['type']} | Time: {entry['time_of_day']}\n"
        f"  Med : {entry['name']}  ({entry['dose']})\n"
        f"  Notes: {entry['notes']}\n"
        "----------------------------------------\n"
    )


def parse_timestamp_safe(ts: str) -> datetime.datetime | None:
    """Safely parse timestamp, return None on failure."""
    try:
        return datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M")
    except Exception:
        return None


def get_filtered_entries() -> list[dict]:
    """Return entries that match type, date range, and text search filters."""
    global med_entries, filtered_type, filtered_date_range, search_text
    now = datetime.datetime.now()
    today = now.date()
    filtered = []

    st = (search_text or "").strip().lower()

    for e in med_entries:
        # type filter
        if filtered_type and filtered_type != "All types" and e.get("type") != filtered_type:
            continue

        # date filter
        dt = parse_timestamp_safe(e.get("timestamp", ""))
        if dt is None:
            # keep malformed timestamps so user can still see/fix them
            pass
        else:
            d = dt.date()
            if filtered_date_range == "Today" and d != today:
                continue
            if filtered_date_range == "Last 7 days" and (today - d).days > 7:
                continue
            # "All" passes everything

        # search filter
        if st:
            text_blob = f"{e.get('name','')} {e.get('notes','')}".lower()
            if st not in text_blob:
                continue

        filtered.append(e)
    return filtered


def refresh_log_text():
    """Render all filtered entries into the log textbox."""
    global selected_entry_index
    text.configure(state="normal")
    text.delete("1.0", "end")

    data = get_filtered_entries()

    if not data:
        text.insert("end", "No medications match the current filters.\n")
    else:
        for idx, e in enumerate(data):
            text.insert("end", pretty_format_entry(e, idx))

    # whenever filters change or list changes, clear selection
    selected_entry_index = None
    selected_label.configure(text="Selected entry: none")

    # update count label
    count_label.configure(text=f"Visible entries: {len(data)}")
    text.configure(state="disabled")


def add_entry():
    """Read UI fields, validate, add entry and update UI."""
    name = name_entry.get().strip()
    dose = dose_entry.get().strip()
    mtype = option_menu_var.get()
    tod = option_menu1_var.get()
    notes_val = notes_var.get().strip()

    if not name:
        messagebox.showwarning("Missing name", "Please enter medication name.")  # changed
        return

    if mtype == "Select medication type":
        messagebox.showwarning("Missing type", "Please select medication type.")  # changed
        return

    if tod == "Select time of day":
        messagebox.showwarning("Missing time", "Please select time of day.")  # changed
        return

    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "name": name,
        "dose": dose or "unspecified dose",
        "type": mtype,
        "time_of_day": tod,
        "notes": notes_val,
    }
    med_entries.append(entry)
    save_all_entries()      # JSON persistence
    append_entry_to_txt(entry)  # simple text export

    # clear quick fields (keep type/time)
    name_entry.delete(0, "end")
    dose_entry.delete(0, "end")
    notes_var.set("")
    refresh_log_text()
    update_today_summary()


def append_entry_to_txt(entry: dict):
    """Append a single entry to the legacy text file."""
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(format_entry(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())
    except OSError as e:
        messagebox.showwarning(  # changed
            "Save error (TXT)",
            f"Could not append to medication_log.txt:\n{e}",
        )


def save_all_entries():
    """Write all entries to JSON for robust storage."""
    try:
        # ensure directory exists (important when running from new locations)
        os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(med_entries, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
    except OSError as e:
        messagebox.showwarning(  # changed
            "Save error (JSON)",
            f"Could not save medication_log.json:\n{e}",
        )


def load_entries_from_json():
    """Load entries from JSON if present."""
    global med_entries
    if not os.path.exists(JSON_PATH):
        return False
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            # basic sanity clean-up
            cleaned: list[dict] = []
            for e in data:
                if not isinstance(e, dict):
                    continue
                cleaned.append(
                    {
                        "timestamp": e.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
                        "name": e.get("name", ""),
                        "dose": e.get("dose", ""),
                        "type": e.get("type", "Unknown"),
                        "time_of_day": e.get("time_of_day", ""),
                        "notes": e.get("notes", ""),
                    }
                )
            med_entries = cleaned
            return True
    except OSError:
        return False
    except json.JSONDecodeError:
        # corrupt file -> tell user and stop using it
        messagebox.showwarning(  # changed
            "Load error (JSON)",
            "medication_log.json is corrupted and could not be read.\n"
                    "A new file will be created on next save.",
        )
        return False
    return False


def load_entries_from_txt_legacy():
    """Legacy loader from TXT; used only if JSON not available."""
    if not os.path.exists(LOG_PATH):
        return
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(" | ")
                if len(parts) >= 5:
                    # timestamp, type, time_of_day, "name dose", notes
                    name_and_dose = parts[3]
                    med_entries.append(
                        {
                            "timestamp": parts[0],
                            "type": parts[1],
                            "time_of_day": parts[2],
                            "name": name_and_dose,  # we no longer try to split this
                            "dose": "",
                            "notes": parts[4],
                        }
                    )
                else:
                    med_entries.append(
                        {
                            "timestamp": parts[0],
                            "type": "loaded",
                            "time_of_day": "",
                            "name": "",
                            "dose": "",
                            "notes": line,
                        }
                    )
    except OSError:
        pass


def update_today_summary():
    """Show a compact count of today's medications."""
    today = datetime.datetime.now().date()
    today_entries = []
    for e in med_entries:
        dt = parse_timestamp_safe(e.get("timestamp", ""))
        if dt and dt.date() == today:
            today_entries.append(e)

    by_type: dict[str, int] = {}
    for e in today_entries:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1

    summary_text.configure(state="normal")
    summary_text.delete("1.0", "end")
    if not today_entries:
        summary_text.insert("end", "No entries for today yet.")
    else:
        summary_text.insert("end", f"Total today: {len(today_entries)}\n")
        for t, count in sorted(by_type.items(), key=lambda x: x[0]):
            summary_text.insert("end", f"  • {t}: {count}\n")
    summary_text.configure(state="disabled")


def on_filter_change(choice: str):
    """Filter by medication type."""
    global filtered_type
    filtered_type = choice
    refresh_log_text()


def on_date_filter_change(choice: str):
    """Filter by date range."""
    global filtered_date_range
    filtered_date_range = choice
    refresh_log_text()


def on_search_change(*_args):
    """Update search text as user types."""
    global search_text
    search_text = search_var.get()
    refresh_log_text()


def on_log_click(event):
    """
    Mouse click handler for the log textbox.
    Detect which '#N' entry line was clicked and store its index.
    """
    global selected_entry_index
    try:
        # get the index where the user clicked
        click_index = text.index(f"@{event.x},{event.y}")
        line_no = int(click_index.split(".")[0])
    except Exception:
        selected_entry_index = None
        selected_label.configure(text="Selected entry: none")
        return

    # find the nearest preceding line that starts with "#"
    try:
        current_line = line_no
        while current_line >= 1:
            line_content = text.get(f"{current_line}.0", f"{current_line}.0 lineend")
            if line_content.startswith("#"):
                # line format "#N  timestamp..."
                try:
                    num_part = line_content.split()[0].lstrip("#")
                    visible_idx = int(num_part) - 1
                    filtered = get_filtered_entries()
                    if 0 <= visible_idx < len(filtered):
                        entry_obj = filtered[visible_idx]
                        # map entry_obj back to med_entries
                        real_idx = med_entries.index(entry_obj)
                        selected_entry_index = real_idx
                        # update label with friendly text
                        name = entry_obj.get("name", "unknown")
                        ts = entry_obj.get("timestamp", "?")
                        selected_label.configure(text=f"Selected entry: {name} @ {ts}")
                        return
                except Exception:
                    break
            current_line -= 1
    except Exception:
        pass

    # If we reach here, no valid selection
    selected_entry_index = None
    selected_label.configure(text="Selected entry: none")


def get_selected_entry_index() -> int | None:
    """
    Return the currently selected entry index in med_entries.
    Ensures it is within range and returns None if not valid.
    """
    global selected_entry_index
    if selected_entry_index is None:
        return None
    if not (0 <= selected_entry_index < len(med_entries)):
        selected_entry_index = None
        return None
    return selected_entry_index


def delete_selected_entry():
    """
    Delete the currently selected entry from med_entries.
    """
    global selected_entry_index

    idx = get_selected_entry_index()
    if idx is None:
        messagebox.showwarning("No selection", "Click on an entry in the log first.")  # changed
        return

    entry = med_entries[idx]
    name = entry.get("name", "this entry")
    ts = entry.get("timestamp", "?")

    # simple confirmation dialog (changed from CTkMessagebox to askyesno)
    confirm = messagebox.askyesno(
        "Delete entry?",
        f"Delete '{name}' @ {ts}?\nThis cannot be undone.",
        icon="warning",
    )
    if not confirm:
        return

    # remove entry and persist
    try:
        del med_entries[idx]
    except IndexError:
        messagebox.showwarning(  # changed
            "Delete error",
            "The selected entry is no longer available.",
        )
        selected_entry_index = None
        selected_label.configure(text="Selected entry: none")
        # ensure Add button is back to normal
        add_btn.configure(text="Add medication entry", command=add_entry)
        return

    save_all_entries()
    refresh_log_text()
    update_today_summary()

    # clear selection and restore Add button behavior
    selected_entry_index = None
    selected_label.configure(text="Selected entry: none")
    add_btn.configure(text="Add medication entry", command=add_entry)


def edit_selected_entry():
    idx = get_selected_entry_index()
    if idx is None:
        messagebox.showwarning("No selection", "Click on an entry in the log first.")  # changed
        return
    entry = med_entries[idx]

    # Simple in-place editor using the left side fields
    name_entry.delete(0, "end")
    name_entry.insert(0, entry.get("name", ""))

    dose_entry.delete(0, "end")
    dose_entry.insert(0, entry.get("dose", ""))

    option_menu_var.set(entry.get("type", "Select medication type") or "Select medication type")
    option_menu1_var.set(entry.get("time_of_day", "Select time of day") or "Select time of day")
    notes_var.set(entry.get("notes", ""))

    def apply_changes():
        new_name = name_entry.get().strip()
        new_dose = dose_entry.get().strip()
        new_type = option_menu_var.get()
        new_tod = option_menu1_var.get()
        new_notes = notes_var.get().strip()

        if not new_name:
            messagebox.showwarning("Missing name", "Please enter medication name.")  # changed
            return

        if new_type == "Select medication type":
            messagebox.showwarning("Missing type", "Please select medication type.")  # changed
            return

        if new_tod == "Select time of day":
            messagebox.showwarning("Missing time", "Please select time of day.")  # changed
            return

        # re-check that the selection is still valid
        real_idx = get_selected_entry_index()
        if real_idx is None:
            messagebox.showwarning(  # changed
                "Edit error",
                "The selected entry is no longer available.",
            )
            # restore Add button behavior
            add_btn.configure(text="Add medication entry", command=add_entry)
            return

        entry_ref = med_entries[real_idx]
        entry_ref["name"] = new_name
        entry_ref["dose"] = new_dose or "unspecified dose"
        entry_ref["type"] = new_type
        entry_ref["time_of_day"] = new_tod
        entry_ref["notes"] = new_notes

        save_all_entries()  # save edited entry
        refresh_log_text()
        update_today_summary()
        # reset selection and label
        global selected_entry_index
        selected_entry_index = None
        selected_label.configure(text="Selected entry: none")
        # return button back to normal "Add" behavior
        add_btn.configure(text="Add medication entry", command=add_entry)

    # Temporarily repurpose the Add button to "Save changes"
    add_btn.configure(text="Save changes", command=apply_changes)


main = ctk.CTk()
main.configure(fg_color="#23272D")
main.title("Universal Medication Tracker")
main.geometry("1020x560")
main.minsize(900, 520)

# configure grid for responsive layout
main.grid_columnconfigure(0, weight=0)   # left column fixed
main.grid_columnconfigure(1, weight=1)   # right column grows
main.grid_rowconfigure(0, weight=1)

# === LEFT PANEL ===
left_panel = ctk.CTkFrame(master=main, fg_color="#2b2f36", corner_radius=0)
left_panel.grid(row=0, column=0, sticky="nsew")
left_panel.grid_rowconfigure(3, weight=1)

left_header = ctk.CTkLabel(left_panel, text="New Medication Entry", text_color="#fff", anchor="w")
left_header.grid(row=0, column=0, padx=16, pady=(16, 4), sticky="ew")

# the frame that holds the entry fields
frame = ctk.CTkFrame(master=left_panel, fg_color="#23272D")
frame.grid(row=1, column=0, padx=12, pady=(4, 12), sticky="nsew")
frame.grid_columnconfigure(0, weight=1)

# Medication type option menu
option_menu_options = ["Prescribed", "Over-the-counter", "Supplement", "Herbal", "Other"]
option_menu_var = ctk.StringVar(value="Select medication type")
option_menu = ctk.CTkOptionMenu(frame, variable=option_menu_var, values=option_menu_options)
option_menu.configure(
    fg_color="#029CFF",
    text_color="#fff",
    corner_radius=5,
    button_color="#36719f",
    button_hover_color="#093c5e",
    dropdown_fg_color="#5C6266",
    dropdown_text_color="#fff",
    dropdown_hover_color="#2990E4",
)
option_menu.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="ew")

# Time of day option menu
option_menu1_options = ["Morning", "Afternoon", "Evening", "Night", "As needed"]
option_menu1_var = ctk.StringVar(value="Select time of day")
option_menu1 = ctk.CTkOptionMenu(frame, variable=option_menu1_var, values=option_menu1_options)
option_menu1.configure(
    fg_color="#029CFF",
    text_color="#fff",
    corner_radius=5,
    button_color="#36719f",
    button_hover_color="#093c5e",
    dropdown_fg_color="#5C6266",
    dropdown_text_color="#fff",
    dropdown_hover_color="#2990E4",
)
option_menu1.grid(row=1, column=0, padx=10, pady=6, sticky="ew")

# Medication name
name_label = ctk.CTkLabel(frame, text="Medication name:")
name_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
name_entry = ctk.CTkEntry(frame, placeholder_text="e.g. Ibuprofen")
name_entry.grid(row=3, column=0, padx=10, pady=(2, 6), sticky="ew")

# Dropdown for common medication names
def on_medication_select(choice: str):
    if choice and choice != "Select medication":
        name_entry.delete(0, "end")
        name_entry.insert(0, choice)

medication_options = [
    "Select medication",
    "Ibuprofen",
    "Paracetamol",
    "Aspirin",
    "Amoxicillin",
    "Metformin",
    "Atorvastatin",
    "Omeprazole",
    "Lisinopril",
    "Vitamin D",
]
medication_var = ctk.StringVar(value="Select medication")
medication_menu = ctk.CTkOptionMenu(
    frame,
    variable=medication_var,
    values=medication_options,
    command=on_medication_select,
)
medication_menu.configure(
    fg_color="#029CFF",
    text_color="#fff",
    corner_radius=5,
    button_color="#36719f",
    button_hover_color="#093c5e",
    dropdown_fg_color="#5C6266",
    dropdown_text_color="#fff",
    dropdown_hover_color="#2990E4",
)
medication_menu.grid(row=4, column=0, padx=10, pady=(0, 6), sticky="ew")

# Dose
dose_label = ctk.CTkLabel(frame, text="Dose:")
dose_label.grid(row=5, column=0, padx=10, pady=(6, 0), sticky="w")
dose_entry = ctk.CTkEntry(frame, placeholder_text="e.g. 200 mg, 1 tablet")
dose_entry.grid(row=6, column=0, padx=10, pady=(2, 6), sticky="ew")

# Dropdown for common dose options
def on_dose_select(choice: str):
    if choice and choice != "Select dose":
        dose_entry.delete(0, "end")
        dose_entry.insert(0, choice)

dose_options = [
    "Select dose",
    "1 tablet",
    "2 tablets",
    "5 mg",
    "10 mg",
    "20 mg",
    "50 mg",
    "100 mg",
    "200 mg",
    "250 mg",
    "500 mg",
    "1 capsule",
    "2 capsules",
    "5 mL",
    "10 mL",
]
dose_var = ctk.StringVar(value="Select dose")
dose_menu = ctk.CTkOptionMenu(
    frame,
    variable=dose_var,
    values=dose_options,
    command=on_dose_select,
)
dose_menu.configure(
    fg_color="#029CFF",
    text_color="#fff",
    corner_radius=5,
    button_color="#36719f",
    button_hover_color="#093c5e",
    dropdown_fg_color="#5C6266",
    dropdown_text_color="#fff",
    dropdown_hover_color="#2990E4",
)
dose_menu.grid(row=7, column=0, padx=10, pady=(0, 6), sticky="ew")

# Short notes (optional)
notes_label = ctk.CTkLabel(frame, text="Notes (optional):")
notes_label.grid(row=8, column=0, padx=10, pady=(6, 0), sticky="w")
notes_var = ctk.StringVar()
notes_entry = ctk.CTkEntry(frame, textvariable=notes_var, placeholder_text="e.g. Take with food")
notes_entry.grid(row=9, column=0, padx=10, pady=(2, 10), sticky="ew")

# Add button
add_btn = ctk.CTkButton(frame, text="Add medication entry", command=add_entry)
add_btn.grid(row=10, column=0, padx=10, pady=(0, 10), sticky="ew")

# Helper label at bottom of left panel
label2 = ctk.CTkLabel(
    master=left_panel,
    text="Entries are saved to medication_log.json and exported to medication_log.txt",
    text_color="#aaaaaa",
    anchor="w",
)
label2.grid(row=2, column=0, padx=16, pady=(0, 8), sticky="ew")

# === RIGHT PANEL ===
right_panel = ctk.CTkFrame(master=main, fg_color="#23272D", corner_radius=0)
right_panel.grid(row=0, column=1, sticky="nsew")
right_panel.grid_columnconfigure(0, weight=1)
right_panel.grid_rowconfigure(1, weight=1)

# Header row with title + filter
log_header_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
log_header_frame.grid(row=0, column=0, padx=16, pady=(16, 4), sticky="ew")
log_header_frame.grid_columnconfigure(0, weight=1)

label1 = ctk.CTkLabel(log_header_frame, text="Medication Log", text_color="#fff", anchor="w")
label1.grid(row=0, column=0, sticky="w")

filter_label = ctk.CTkLabel(log_header_frame, text="Filter by type:", text_color="#cccccc")
filter_label.grid(row=0, column=1, padx=(16, 4))

filter_values = ["All types"] + option_menu_options
filter_var = ctk.StringVar(value="All types")
filter_menu = ctk.CTkOptionMenu(
    log_header_frame,
    variable=filter_var,
    values=filter_values,
    command=on_filter_change,
)
filter_menu.configure(
    fg_color="#029CFF",
    text_color="#fff",
    corner_radius=5,
    button_color="#36719f",
    button_hover_color="#093c5e",
    dropdown_fg_color="#5C6266",
    dropdown_text_color="#fff",
    dropdown_hover_color="#2990E4",
)
filter_menu.grid(row=0, column=2, padx=(4, 0))

# Date filter
date_filter_label = ctk.CTkLabel(log_header_frame, text="Date:", text_color="#cccccc")
date_filter_label.grid(row=0, column=3, padx=(16, 4))

date_filter_values = ["Today", "Last 7 days", "All"]
date_filter_var = ctk.StringVar(value="Today")
date_filter_menu = ctk.CTkOptionMenu(
    log_header_frame,
    variable=date_filter_var,
    values=date_filter_values,
    command=on_date_filter_change,
)
date_filter_menu.configure(
    fg_color="#029CFF",
    text_color="#fff",
    corner_radius=5,
    button_color="#36719f",
    button_hover_color="#093c5e",
    dropdown_fg_color="#5C6266",
    dropdown_text_color="#fff",
    dropdown_hover_color="#2990E4",
)
date_filter_menu.grid(row=0, column=4, padx=(4, 0))

# Search box
search_label = ctk.CTkLabel(log_header_frame, text="Search:", text_color="#cccccc")
search_label.grid(row=0, column=5, padx=(16, 4))
search_var = ctk.StringVar()
search_var.trace_add("write", on_search_change)
search_entry = ctk.CTkEntry(log_header_frame, textvariable=search_var, placeholder_text="name or notes")
search_entry.grid(row=0, column=6, padx=(0, 4))

# Log frame
frame1 = ctk.CTkFrame(master=right_panel, fg_color="#23272D")
frame1.grid(row=1, column=0, padx=16, pady=(4, 8), sticky="nsew")
frame1.grid_rowconfigure(0, weight=1)
frame1.grid_columnconfigure(0, weight=1)

text = ctk.CTkTextbox(master=frame1)
text.configure(fg_color="#343739", text_color="#fff", corner_radius=5)
text.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
# bind mouse click to selection handler
text.bind("<Button-1>", on_log_click)

# Controls under log: count + edit
controls_frame = ctk.CTkFrame(master=right_panel, fg_color="#23272D")
controls_frame.grid(row=2, column=0, padx=16, pady=(0, 4), sticky="ew")
controls_frame.grid_columnconfigure(0, weight=1)

count_label = ctk.CTkLabel(controls_frame, text="Visible entries: 0", text_color="#cccccc", anchor="w")
count_label.grid(row=0, column=0, sticky="w", padx=(8, 4))

edit_btn = ctk.CTkButton(controls_frame, text="Edit selected", width=120, command=edit_selected_entry)
edit_btn.grid(row=0, column=1, padx=4)

delete_btn = ctk.CTkButton(controls_frame, text="Delete selected", width=120, fg_color="#b3261e",
                           hover_color="#7f1914", command=delete_selected_entry)
delete_btn.grid(row=0, column=2, padx=4)

# show which entry is currently selected
selected_label = ctk.CTkLabel(controls_frame, text="Selected entry: none", text_color="#aaaaaa", anchor="w")
selected_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=(8, 4), pady=(2, 0))

# Today summary area
summary_label = ctk.CTkLabel(right_panel, text="Today's Summary", text_color="#fff", anchor="w")
summary_label.grid(row=3, column=0, padx=16, pady=(4, 0), sticky="ew")

summary_frame = ctk.CTkFrame(right_panel, fg_color="#23272D")
summary_frame.grid(row=4, column=0, padx=16, pady=(4, 16), sticky="ew")
summary_frame.grid_columnconfigure(0, weight=1)

summary_text = ctk.CTkTextbox(summary_frame, height=60)
summary_text.configure(fg_color="#343739", text_color="#fff", corner_radius=5)
summary_text.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

# Keyboard shortcut: Enter in notes field adds entry
def _on_enter(_event):
    add_btn.invoke()

notes_entry.bind("<Return>", _on_enter)

# Load existing log and show it
if not load_entries_from_json():
    # first run or JSON missing: fall back to TXT and then save as JSON
    load_entries_from_txt_legacy()
    save_all_entries()

refresh_log_text()
update_today_summary()

main.mainloop()