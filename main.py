# This code is generated using PyUIbuilder: https://pyuibuilder.com

import os
import customtkinter as ctk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set global appearance and default fonts for better readability
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEFAULT_FONT = ("Segoe UI", 13)
TITLE_FONT = ("Segoe UI", 20, "bold")

wellness_tracker_app = ctk.CTk()
wellness_tracker_app.configure(fg_color="#23272D")
wellness_tracker_app.title("Wellness Tracker app")
wellness_tracker_app.geometry("850x540")  # Increased window size

# Add a small margin around the whole window
wellness_tracker_app.grid_rowconfigure(0, weight=1)
wellness_tracker_app.grid_columnconfigure(0, weight=1)

all_tabs = ctk.CTkTabview(wellness_tracker_app)
all_tabs.add("Wellness Tracker home tab")
all_tabs.add("HRT Tracker")
all_tabs.add("Universal Medication tracker")
all_tabs.add("Cycle Tracker")
all_tabs.add("Private Journal/Diary")
all_tabs.add("Settings")  # <-- new Settings tab
all_tabs.configure()
all_tabs.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")  # More margin around tabs

# Home tab
frame = ctk.CTkFrame(master=all_tabs.tab("Wellness Tracker home tab"))
frame.configure(fg_color="#2a2a2a", width=100, height=100)
frame.pack(expand=True, fill="both", padx=20, pady=20)  # More padding inside tab

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

# new helper to switch to settings tab
def open_settings():
    all_tabs.set("Settings")

# Buttons at the bottom of the home tab
home_buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
home_buttons_frame.pack(side="bottom", pady=25)  # More space below buttons

help_button = ctk.CTkButton(
    home_buttons_frame,
    text="How do I use this app?",
    font=DEFAULT_FONT,
    command=show_help
)
help_button.pack(side="left", padx=10)

settings_button = ctk.CTkButton(  # <-- new Settings button
    home_buttons_frame,
    text="Settings",
    font=DEFAULT_FONT,
    command=open_settings,
)
settings_button.pack(side="left", padx=10)

exit_button = ctk.CTkButton(
    home_buttons_frame,
    text="Exit",
    font=DEFAULT_FONT,
    fg_color="#b3261e",
    hover_color="#7f1b16",
    command=wellness_tracker_app.destroy
)
exit_button.pack(side="left", padx=10)

# ---------- HRT TRACKER STATE & HELPERS ----------

# simple in-memory storage: list of dicts
hrt_entries = []


def get_effective_value(option_menu, custom_entry):
    """If 'Other / Custom…' is selected, return custom text, else dropdown value."""
    val = option_menu.get().strip()
    if val == "Other / Custom…":
        custom = custom_entry.get().strip()
        return custom
    return val


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

    lines = []
    for idx, entry in enumerate(hrt_entries, start=1):
        # one block per entry, numbered for easy reference
        lines.append(
            f"{idx}. {entry['date']} {entry['time']} - {entry['medication']} "
            f"({entry['dose']} via {entry['route']})\n"
            f"    Notes: {entry['notes'] or '—'}\n"
        )
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

    # clear custom fields
    hrt_date_custom_entry.delete(0, "end")
    hrt_time_custom_entry.delete(0, "end")
    hrt_med_custom_entry.delete(0, "end")
    hrt_dose_custom_entry.delete(0, "end")

    hrt_notes_textbox.delete("0.0", "end")


def add_hrt_entry():
    """Collect values from form, validate, store, and refresh log."""
    # resolve dropdown + custom
    date_val = get_effective_value(hrt_date_option, hrt_date_custom_entry)
    time_val = get_effective_value(hrt_time_option, hrt_time_custom_entry)
    med_val = get_effective_value(hrt_med_option, hrt_med_custom_entry)
    dose_val = get_effective_value(hrt_dose_option, hrt_dose_custom_entry)
    route_val = hrt_route_option.get().strip()
    notes_val = hrt_notes_textbox.get("0.0", "end").strip()

    # very light validation: require date, medication, and dose
    if not date_val or not med_val or not dose_val:
        # quick feedback by coloring fields
        if not date_val:
            hrt_date_custom_entry.configure(border_color="red")
        else:
            hrt_date_custom_entry.configure(border_color=None)

        if not med_val:
            hrt_med_custom_entry.configure(border_color="red")
        else:
            hrt_med_custom_entry.configure(border_color=None)

        if not dose_val:
            hrt_dose_custom_entry.configure(border_color="red")
        else:
            hrt_dose_custom_entry.configure(border_color=None)
        return

    # reset any error borders
    hrt_date_custom_entry.configure(border_color=None)
    hrt_med_custom_entry.configure(border_color=None)
    hrt_dose_custom_entry.configure(border_color=None)

    entry = {
        "date": date_val,
        "time": time_val or "—",
        "medication": med_val,
        "dose": dose_val,
        "route": route_val or "unspecified",
        "notes": notes_val,
    }
    hrt_entries.append(entry)
    clear_hrt_form()
    refresh_hrt_log()


def delete_selected_hrt_entry():
    """Delete entry by line number typed into delete index field."""
    idx_str = hrt_delete_index.get().strip()
    if not idx_str.isdigit():
        return
    idx = int(idx_str)
    if 1 <= idx <= len(hrt_entries):
        del hrt_entries[idx - 1]
        hrt_delete_index.delete(0, "end")
        refresh_hrt_log()


# ---------- HRT TAB UI ----------

# HRT tab
frame1 = ctk.CTkFrame(master=all_tabs.tab("HRT Tracker"))
frame1.configure(fg_color="#2a2a2a", width=100, height=100)
frame1.pack(expand=True, fill="both", padx=20, pady=20)  # More padding inside tab

# Top title
hrt_title = ctk.CTkLabel(
    frame1,
    text="HRT Tracker",
    font=TITLE_FONT,
    anchor="w",
)
hrt_title.pack(padx=15, pady=(20, 10), anchor="w")  # More space above/below title

hrt_subtitle = ctk.CTkLabel(
    frame1,
    text="Log any type of hormone replacement therapy for your transition.",
    font=DEFAULT_FONT,
    anchor="w",
)
hrt_subtitle.pack(padx=15, pady=(0, 15), anchor="w")  # More space below subtitle

# Container for form + log
hrt_main_frame = ctk.CTkFrame(frame1, fg_color="transparent")
hrt_main_frame.pack(expand=True, fill="both", padx=10, pady=10)  # Slightly more padding

hrt_main_frame.grid_columnconfigure(0, weight=1)  # form
hrt_main_frame.grid_columnconfigure(1, weight=1)  # log
hrt_main_frame.grid_rowconfigure(0, weight=1)

# ----- Left side: form -----
hrt_form_frame = ctk.CTkFrame(hrt_main_frame)
hrt_form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))  # More space between form/log

for i in range(10):
    hrt_form_frame.grid_rowconfigure(i, weight=0)
hrt_form_frame.grid_rowconfigure(10, weight=1)
hrt_form_frame.grid_columnconfigure(0, weight=0)
hrt_form_frame.grid_columnconfigure(1, weight=1)

# Date (dropdown + custom)
hrt_date_label = ctk.CTkLabel(hrt_form_frame, text="Date:", font=DEFAULT_FONT)
hrt_date_label.grid(row=0, column=0, padx=5, pady=(10, 2), sticky="w")

hrt_date_container = ctk.CTkFrame(hrt_form_frame, fg_color="transparent")
hrt_date_container.grid(row=0, column=1, padx=5, pady=(10, 2), sticky="ew")
hrt_date_container.grid_columnconfigure(0, weight=1)
hrt_date_container.grid_columnconfigure(1, weight=0)

hrt_date_option = ctk.CTkOptionMenu(
    hrt_date_container,
    values=[
        "Today",
        "Yesterday",
        "2 days ago",
        "1 week ago",
        "Other / Custom…",
    ],
    font=DEFAULT_FONT,
)
hrt_date_option.grid(row=0, column=0, sticky="ew", padx=(0, 5))
hrt_date_option.set("Today")

hrt_date_custom_entry = ctk.CTkEntry(
    hrt_date_container,
    font=DEFAULT_FONT,
    width=90,
    placeholder_text="YYYY-MM-DD",
)
hrt_date_custom_entry.grid(row=0, column=1, sticky="ew")

# Time (dropdown + custom)
hrt_time_label = ctk.CTkLabel(hrt_form_frame, text="Time:", font=DEFAULT_FONT)
hrt_time_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")

hrt_time_container = ctk.CTkFrame(hrt_form_frame, fg_color="transparent")
hrt_time_container.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
hrt_time_container.grid_columnconfigure(0, weight=1)
hrt_time_container.grid_columnconfigure(1, weight=0)

hrt_time_option = ctk.CTkOptionMenu(
    hrt_time_container,
    values=[
        "Now",
        "Morning",
        "Afternoon",
        "Evening",
        "Night",
        "Other / Custom…",
    ],
    font=DEFAULT_FONT,
)
hrt_time_option.grid(row=0, column=0, sticky="ew", padx=(0, 5))
hrt_time_option.set("Now")

hrt_time_custom_entry = ctk.CTkEntry(
    hrt_time_container,
    font=DEFAULT_FONT,
    width=80,
    placeholder_text="HH:MM",
)
hrt_time_custom_entry.grid(row=0, column=1, sticky="ew")

# Medication name (dropdown + custom)
hrt_med_label = ctk.CTkLabel(hrt_form_frame, text="Medication / preparation:", font=DEFAULT_FONT)
hrt_med_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

hrt_med_container = ctk.CTkFrame(hrt_form_frame, fg_color="transparent")
hrt_med_container.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
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
)
hrt_med_option.grid(row=0, column=0, sticky="ew", padx=(0, 5))
hrt_med_option.set("Estradiol (any form)")

hrt_med_custom_entry = ctk.CTkEntry(
    hrt_med_container,
    font=DEFAULT_FONT,
    width=160,
    placeholder_text="Custom name / brand",
)
hrt_med_custom_entry.grid(row=0, column=1, sticky="ew")

# Dose (dropdown + custom)
hrt_dose_label = ctk.CTkLabel(hrt_form_frame, text="Dose:", font=DEFAULT_FONT)
hrt_dose_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")

hrt_dose_container = ctk.CTkFrame(hrt_form_frame, fg_color="transparent")
hrt_dose_container.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
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
)
hrt_dose_option.grid(row=0, column=0, sticky="ew", padx=(0, 5))
hrt_dose_option.set("Standard / as prescribed")

hrt_dose_custom_entry = ctk.CTkEntry(
    hrt_dose_container,
    font=DEFAULT_FONT,
    width=140,
    placeholder_text="e.g. 2 mg, 0.4 mL",
)
hrt_dose_custom_entry.grid(row=0, column=1, sticky="ew")

# Route
hrt_route_label = ctk.CTkLabel(hrt_form_frame, text="Route:", font=DEFAULT_FONT)
hrt_route_label.grid(row=4, column=0, padx=5, pady=2, sticky="w")
hrt_route_option = ctk.CTkOptionMenu(
    hrt_form_frame,
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
)
hrt_route_option.grid(row=4, column=1, padx=5, pady=2, sticky="ew")
hrt_route_option.set("Pill / Oral")

# Notes
hrt_notes_label = ctk.CTkLabel(hrt_form_frame, text="Notes (optional):", font=DEFAULT_FONT)
hrt_notes_label.grid(row=5, column=0, padx=5, pady=(10, 2), sticky="w")
hrt_notes_textbox = ctk.CTkTextbox(hrt_form_frame, height=120, font=DEFAULT_FONT)
hrt_notes_textbox.grid(row=5, column=0, columnspan=2, padx=10, pady=(0, 15), sticky="nsew")  # More padding

# Buttons
hrt_buttons_frame = ctk.CTkFrame(hrt_form_frame, fg_color="transparent")
hrt_buttons_frame.grid(row=6, column=0, columnspan=2, pady=(10, 15), sticky="e")  # More space above/below buttons

hrt_add_button = ctk.CTkButton(
    hrt_buttons_frame,
    text="Add Entry",
    font=DEFAULT_FONT,
    command=add_hrt_entry,
)
hrt_add_button.pack(side="right", padx=5)

hrt_clear_button = ctk.CTkButton(
    hrt_buttons_frame,
    text="Clear Form",
    font=DEFAULT_FONT,
    fg_color="#444444",
    hover_color="#555555",
    command=clear_hrt_form,
)
hrt_clear_button.pack(side="right", padx=5)

# Delete entry by index
hrt_delete_label = ctk.CTkLabel(
    hrt_form_frame,
    text="Delete entry # (see log on the right):",
    font=("Segoe UI", 11),
)
hrt_delete_label.grid(row=7, column=0, padx=5, pady=(5, 2), sticky="w")
hrt_delete_index = ctk.CTkEntry(
    hrt_form_frame,
    width=60,
    font=DEFAULT_FONT,
    placeholder_text="1",
)
hrt_delete_index.grid(row=7, column=1, padx=5, pady=(5, 2), sticky="w")

hrt_delete_button = ctk.CTkButton(
    hrt_form_frame,
    text="Delete",
    font=("Segoe UI", 11),
    fg_color="#b3261e",
    hover_color="#7f1b16",
    width=70,
    command=delete_selected_hrt_entry,
)
hrt_delete_button.grid(row=7, column=1, padx=(90, 5), pady=(5, 2), sticky="w")

# ----- Right side: log -----
hrt_log_frame = ctk.CTkFrame(hrt_main_frame)
hrt_log_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 0))  # More space between form/log

hrt_log_frame.grid_rowconfigure(0, weight=0)
hrt_log_frame.grid_rowconfigure(1, weight=1)
hrt_log_frame.grid_columnconfigure(0, weight=1)

hrt_log_label = ctk.CTkLabel(
    hrt_log_frame,
    text="HRT log (most recent at top):",
    font=DEFAULT_FONT,
    anchor="w",
)
hrt_log_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="w")  # More space above/below log label

hrt_log_textbox = ctk.CTkTextbox(hrt_log_frame, font=("Consolas", 11), wrap="word")
hrt_log_textbox.grid(row=1, column=0, padx=10, pady=(0, 15), sticky="nsew")  # More padding
hrt_log_textbox.configure(state="disabled")

# initialize with empty message
refresh_hrt_log()

# Universal Medication tab
frame2 = ctk.CTkFrame(master=all_tabs.tab("Universal Medication tracker"))
frame2.configure(fg_color="#2a2a2a", width=100, height=100)
frame2.pack(expand=True, fill="both", padx=20, pady=20)  # More padding inside tab
med_label = ctk.CTkLabel(
    frame2,
    text="Universal Medication Tracker\n\n(Add medication entries here.)",
    font=DEFAULT_FONT,
    justify="center"
)
med_label.pack(expand=True, padx=10, pady=10)  # More padding

# Cycle Tracker tab
frame3 = ctk.CTkFrame(master=all_tabs.tab("Cycle Tracker"))
frame3.configure(fg_color="#2a2a2a", width=100, height=100)
frame3.pack(expand=True, fill="both", padx=20, pady=20)  # More padding inside tab
cycle_label = ctk.CTkLabel(
    frame3,
    text="Cycle Tracker\n\n(Log your cycle days and symptoms here.)",
    font=DEFAULT_FONT,
    justify="center"
)
cycle_label.pack(expand=True, padx=10, pady=10)  # More padding

# Private Journal tab
frame4 = ctk.CTkFrame(master=all_tabs.tab("Private Journal/Diary"))
frame4.configure(fg_color="#2a2a2a", width=100, height=100)
frame4.pack(expand=True, fill="both", padx=20, pady=20)  # More padding inside tab
journal_label = ctk.CTkLabel(
    frame4,
    text="Private Journal / Diary\n\n(You can add a text box here for writing.)",
    font=DEFAULT_FONT,
    justify="center"
)
journal_label.pack(expand=True, padx=10, pady=10)  # More padding

# Settings tab (simple placeholder for now)
settings_frame = ctk.CTkFrame(master=all_tabs.tab("Settings"))
settings_frame.configure(fg_color="#2a2a2a", width=100, height=100)
settings_frame.pack(expand=True, fill="both", padx=20, pady=20)  # More padding inside tab

settings_label = ctk.CTkLabel(
    settings_frame,
    text="Settings\n\n(You can add app options and preferences here.)",
    font=DEFAULT_FONT,
    justify="center"
)
settings_label.pack(expand=True, padx=10, pady=10)  # More padding

wellness_tracker_app.mainloop()