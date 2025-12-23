import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import datetime
from pathlib import Path
import json
# NEW: popup import
from kivy.uix.popup import Popup
# NEW: graphics for section backgrounds
from kivy.graphics import Color, RoundedRectangle
import subprocess
import sys

kivy.require('1.10.0')

# NEW: helper to support both normal run and frozen EXE (PyInstaller, cx_Freeze, etc.)
def get_app_base_dir() -> Path:
    """
    Return the base directory for the app, working both in source and frozen EXE.
    """
    if getattr(sys, "frozen", False):
        # When frozen, __file__ may not exist; use the executable path.
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

# Theme palettes
THEMES = {
    "Light": {
        "bg": get_color_from_hex("#F5F7FA"),
        "panel_bg": get_color_from_hex("#FFFFFF"),
        "text": get_color_from_hex("#1F2933"),
        "muted": get_color_from_hex("#52606D"),
        "accent": get_color_from_hex("#3B82F6"),
        "danger": get_color_from_hex("#DC2626"),
        "input_bg": get_color_from_hex("#FFFFFF"),
    },
    "Dark": {
        "bg": get_color_from_hex("#1E293B"),
        "panel_bg": get_color_from_hex("#243447"),
        "text": get_color_from_hex("#F1F5F9"),
        "muted": get_color_from_hex("#94A3B8"),
        "accent": get_color_from_hex("#60A5FA"),
        "danger": get_color_from_hex("#F87171"),
        "input_bg": get_color_from_hex("#334155"),
    }
}

# Spinner/value constants
MED_STATUS_VALUES = ("Taken", "Missed", "Skipped", "Unknown")
HRT_TYPE_VALUES = ("Estrogen", "Testosterone", "Blocker", "Progesterone", "Other")
ADMIN_METHOD_VALUES = ("Oral", "Injection IM", "Injection SubQ", "Patch", "Gel", "Sublingual", "Other")

# Add a list of common medications (customize as needed)
COMMON_MEDICATIONS = [
    "Estradiol", "Spironolactone", "Finasteride", "Cyproterone", "Progesterone",
    "Testosterone", "Leuprorelin", "Bicalutamide", "Dutasteride", "Other"
]

# NEW: Dose measurement units
DOSE_UNITS = ["mg", "mcg", "ml", "IU", "patch", "tablet", "capsule", "g", "Other"]

class TAWTApp(App):
    title = "HRT-Tracker"
    theme_key: str = "Light"
    theme: dict

    # SETTINGS: persistence helpers
    def _settings_dir(self) -> Path:
        # UPDATED: use app base dir so paths work from EXE
        d = get_app_base_dir() / "Settings"
        d.mkdir(exist_ok=True)
        return d

    def _settings_file(self) -> Path:
        return self._settings_dir() / "app_settings.json"

    def load_settings(self):
        f = self._settings_file()
        if f.exists():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                theme = data.get("theme", "Light")
                if theme in THEMES:
                    self.theme_key = theme
            except Exception:
                pass  # ignore corrupt file
        else:
            self.save_settings()  # create with defaults

    def save_settings(self):
        data = {"theme": self.theme_key}
        try:
            self._settings_file().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print("Failed to save settings:", e)

    def build(self):
        """Build root widget."""
        self.load_settings()  # NEW: load persisted theme before building
        self.theme = THEMES.get(self.theme_key, THEMES["Light"])
        Window.clearcolor = self.theme["bg"]
        self.main_root = self._build_root_layout(self.theme)  # NEW: keep reference for rebuild
        return self.main_root

    def _styled_label(self, text: str, theme: dict, bold: bool = False, accent: bool = False, height: int = 40) -> Label:
        label = Label(
            text=f"[b]{text}[/b]" if bold else text,
            markup=True,
            font_size="16sp",
            color=theme["accent"] if accent else theme["text"],
            size_hint_y=None,
            height=height,
            halign="left",
            valign="middle"
        )
        # Bind size to text_size so halign/valign work and avoid overlap/clipping.
        label.bind(size=lambda inst, _: setattr(inst, "text_size", inst.size))
        return label

    def _styled_input(
        self,
        hint: str,
        theme: dict,
        text: str = "",
        height: int = 40,
        multiline: bool = False,
        input_filter=None
    ) -> TextInput:
        return TextInput(
            text=text,
            hint_text=hint,
            multiline=multiline,
            input_filter=input_filter,
            size_hint_y=None,
            height=height,
            background_color=theme["input_bg"],
            foreground_color=theme["text"],
            padding=(8, 8)
        )

    def _styled_spinner(self, default: str, values: tuple[str, ...], theme: dict, height: int = 40) -> Spinner:
        return Spinner(
            text=default,
            values=values,
            size_hint_y=None,
            height=height,
            background_color=theme["input_bg"],
            color=theme["text"]
        )

    # NEW: unified button styling with better dark-mode contrast
    def _styled_button(self, text: str, theme: dict, height: int = 40, kind: str = "accent", size_hint=(1, None), width=None) -> Button:
        bg = theme.get(kind, theme["accent"])
        fg = theme["text"] if self.theme_key == "Dark" else theme["panel_bg"]
        btn = Button(
            text=text,
            size_hint=size_hint,
            height=height,
            background_color=bg,
            color=fg
        )
        if width:
            btn.width = width
        return btn

    def _add_section_background(self, section: BoxLayout, theme: dict):
        """Add a rounded background to a section."""
        with section.canvas.before:
            Color(*theme["panel_bg"])
            section._bg_rect = RoundedRectangle(pos=section.pos, size=section.size, radius=[6])
        section.bind(pos=lambda inst, v: setattr(inst._bg_rect, "pos", v))
        section.bind(size=lambda inst, v: setattr(inst._bg_rect, "size", v))

    def _build_section(self, title: str, rows: list[tuple[str, kivy.uix.widget.Widget]], theme: dict) -> BoxLayout:
        section = BoxLayout(orientation="vertical", spacing=8, padding=8, size_hint_y=None)
        section.bind(minimum_height=section.setter("height"))
        section.add_widget(self._styled_label(title, theme, bold=True, accent=True, height=40))
        grid = GridLayout(cols=2, spacing=6, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for label, widget in rows:
            grid.add_widget(self._styled_label(label, theme, height=40))
            grid.add_widget(widget)
        section.add_widget(grid)
        self._add_section_background(section, theme)
        return section

    # NEW: build medications section with dynamic entries
    def _build_medications_section(self, theme: dict) -> BoxLayout:
        section = BoxLayout(orientation="vertical", spacing=8, padding=8, size_hint_y=None)
        section.bind(minimum_height=section.setter("height"))
        section.add_widget(self._styled_label("Medications", theme, bold=True, accent=True, height=40))
        self.med_entries = []
        self.medications_holder = BoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
        self.medications_holder.bind(minimum_height=self.medications_holder.setter("height"))
        self.add_medication_entry(theme)  # initial entry
        section.add_widget(self.medications_holder)
        add_btn = self._styled_button("Add Medication", theme)
        add_btn.bind(on_press=lambda *_: self.add_medication_entry(theme))
        section.add_widget(add_btn)
        return section

    # NEW: create a single medication entry (returns and stores widget dict)
    def _new_med_entry(self, theme: dict) -> dict:
        status = self._styled_spinner("Taken", MED_STATUS_VALUES, theme)
        # Medication name input and dropdown
        name = self._styled_input("Medication name", theme)
        med_spinner = Spinner(
            text="Select...",
            values=tuple(COMMON_MEDICATIONS),
            size_hint_y=None,
            height=40,
            background_color=theme["input_bg"],
            color=theme["text"]
        )
        # When a medication is selected, fill the name input
        def on_med_select(spinner, value):
            if value != "Other":
                name.text = value
            else:
                name.text = ""
        med_spinner.bind(text=on_med_select)

        # Dose input and unit spinner
        dose = self._styled_input("Dose (e.g. 2)", theme)
        dose_unit_spinner = Spinner(
            text="mg",
            values=DOSE_UNITS,
            size_hint_y=None,
            height=40,
            background_color=theme["input_bg"],
            color=theme["text"],
            size_hint=(None, None),
            width=70
        )

        time = self._styled_input("Time", theme, text=datetime.datetime.now().strftime("%H:%M"))
        grid = GridLayout(cols=2, spacing=6, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        # Add spinner and input for medication name
        grid.add_widget(self._styled_label("Medication:", theme, height=40))
        med_name_box = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=40)
        med_name_box.add_widget(med_spinner)
        med_name_box.add_widget(name)
        grid.add_widget(med_name_box)
        # ...rest of the fields...
        grid.add_widget(self._styled_label("Status:", theme, height=40))
        grid.add_widget(status)
        # Dose row with unit spinner
        grid.add_widget(self._styled_label("Dose:", theme, height=40))
        dose_box = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=40)
        dose_box.add_widget(dose)
        dose_box.add_widget(dose_unit_spinner)
        grid.add_widget(dose_box)
        grid.add_widget(self._styled_label("Time:", theme, height=40))
        grid.add_widget(time)
        remove_btn = self._styled_button("Delete", theme, height=36, kind="danger")
        grid.add_widget(self._styled_label("Remove:", theme, height=36))
        grid.add_widget(remove_btn)
        entry = {
            "container": grid,
            "status": status,
            "name": name,
            "dose": dose,
            "dose_unit": dose_unit_spinner,
            "time": time,
            "remove_btn": remove_btn
        }
        remove_btn.bind(on_press=lambda *_: self.remove_medication_entry(entry))
        return entry

    # NEW: add medication entry to holder
    def add_medication_entry(self, theme: dict):
        entry = self._new_med_entry(theme)
        self.med_entries.append(entry)
        self.medications_holder.add_widget(entry["container"])

    # NEW: remove a medication entry
    def remove_medication_entry(self, entry: dict):
        if entry in self.med_entries:
            self.med_entries.remove(entry)
            self.medications_holder.remove_widget(entry["container"])

    # NEW: create a single HRT type entry
    def _new_hrt_type_entry(self, theme: dict) -> dict:
        type_spinner = self._styled_spinner("Estrogen", HRT_TYPE_VALUES, theme)
        method_spinner = self._styled_spinner("Oral", ADMIN_METHOD_VALUES, theme)
        grid = GridLayout(cols=2, spacing=6, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for lbl, w in [("Type:", type_spinner), ("Method:", method_spinner)]:
            grid.add_widget(self._styled_label(lbl, theme, height=40))
            grid.add_widget(w)
        remove_btn = self._styled_button("Delete", theme, height=36, kind="danger")
        grid.add_widget(self._styled_label("Remove:", theme, height=36))
        grid.add_widget(remove_btn)
        entry = {"container": grid, "type": type_spinner, "method": method_spinner, "remove_btn": remove_btn}
        remove_btn.bind(on_press=lambda *_: self.remove_hrt_type_entry(entry))
        return entry

    # NEW: add HRT type entry
    def add_hrt_type_entry(self, theme: dict):
        entry = self._new_hrt_type_entry(theme)
        self.hrt_type_entries.append(entry)
        self.hrt_types_holder.add_widget(entry["container"])

    # NEW: remove HRT type entry
    def remove_hrt_type_entry(self, entry: dict):
        if entry in self.hrt_type_entries:
            self.hrt_type_entries.remove(entry)
            self.hrt_types_holder.remove_widget(entry["container"])

    # NEW: build HRT Details section (multiple types + side effects)
    def _build_hrt_types_section(self, theme: dict) -> BoxLayout:
        section = BoxLayout(orientation="vertical", spacing=8, padding=8, size_hint_y=None)
        section.bind(minimum_height=section.setter("height"))
        section.add_widget(self._styled_label("HRT Details", theme, bold=True, accent=True, height=40))
        self.hrt_type_entries = []
        self.hrt_types_holder = BoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
        self.hrt_types_holder.bind(minimum_height=self.hrt_types_holder.setter("height"))
        self.add_hrt_type_entry(theme)  # initial entry
        section.add_widget(self.hrt_types_holder)
        add_btn = self._styled_button("Add HRT Type", theme)
        add_btn.bind(on_press=lambda *_: self.add_hrt_type_entry(theme))
        section.add_widget(add_btn)
        # Side effects below dynamic types
        effects_grid = GridLayout(cols=2, spacing=6, size_hint_y=None)
        effects_grid.bind(minimum_height=effects_grid.setter("height"))
        effects_grid.add_widget(self._styled_label("Side Effects:", theme, height=40))
        effects_grid.add_widget(self.side_effects_input)
        section.add_widget(effects_grid)
        return section

    def _build_root_layout(self, theme: dict) -> BoxLayout:
        root = BoxLayout(orientation="vertical", spacing=12, padding=16)

        # REPLACED: header label -> top bar with settings and view entries buttons
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=8)
        header = self._styled_label("Daily HRT & Wellness Tracker", theme, bold=True, accent=True, height=50)
        header.size_hint_x = 1
        # Settings and View Entries buttons
        view_entries_btn = self._styled_button("View Entries", theme, height=50, size_hint=(None, 1), width=130)
        view_entries_btn.bind(on_press=self.open_view_entries)
        settings_btn = self._styled_button("Settings", theme, height=50, size_hint=(None, 1), width=110)
        settings_btn.bind(on_press=self.open_settings)
        top_bar.add_widget(header)
        top_bar.add_widget(view_entries_btn)
        top_bar.add_widget(settings_btn)
        root.add_widget(top_bar)

        # Scrollable form
        scroll = ScrollView(size_hint=(1, 1))
        form = BoxLayout(orientation="vertical", spacing=16, size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        today_str = datetime.date.today().isoformat()
        now_time_str = datetime.datetime.now().strftime("%H:%M")

        # Inputs as instance attributes for later access
        self.date_input = self._styled_input("", theme, text=today_str)
        self.sleep_input = self._styled_input("Hours slept", theme, input_filter="int")
        self.notes_input = self._styled_input("Notes (symptoms, triggers, positives)", theme, height=120, multiline=True)
        self.side_effects_input = self._styled_input("Side effects / changes noticed", theme, height=100, multiline=True)
        self.dysphoria_input = self._styled_input("0-10", theme, input_filter="int")
        self.euphoria_input = self._styled_input("0-10", theme, input_filter="int")
        # NEW: mood and energy inputs
        self.mood_input = self._styled_input("0-10", theme, input_filter="int")
        self.energy_input = self._styled_input("0-10", theme, input_filter="int")

        form.add_widget(self._build_section("Daily Basics", [
            ("Date:", self.date_input),
            ("Sleep (hrs):", self.sleep_input),
        ], theme))

        form.add_widget(self._build_medications_section(theme))

        form.add_widget(self._build_hrt_types_section(theme))

        form.add_widget(self._build_section("Wellness Metrics", [
            ("Mood:", self.mood_input),
            ("Energy:", self.energy_input),
            ("Dysphoria:", self.dysphoria_input),
            ("Euphoria:", self.euphoria_input),
            ("Notes:", self.notes_input),
        ], theme))

        scroll.add_widget(form)
        root.add_widget(scroll)

        # Save button
        save_btn = self._styled_button("Save Entry", theme, height=50)
        save_btn.bind(on_press=self.save_entry)
        root.add_widget(save_btn)

        return root

    # NEW: method to open Journal.py
    def open_journal(self, *_):
        # UPDATED: build path relative to app base dir for EXE compatibility
        journal_path = str((get_app_base_dir().parent / "Journal" / "Journal.py").resolve())
        try:
            subprocess.Popen([sys.executable, journal_path])
        except Exception as e:
            print("Failed to open Journal:", e)

    # NEW: method to open Cycle Tracker.py
    def open_cycle_tracker(self, *_):
        cycle_path = str((get_app_base_dir().parent / "Cycle Tracker" / "Cycle Tracker.py").resolve())
        try:
            subprocess.Popen([sys.executable, cycle_path])
        except Exception as e:
            print("Failed to open Cycle Tracker:", e)

    def _build_settings_content(self):
        """(Re)build settings popup content for current theme."""
        content = BoxLayout(orientation="vertical", padding=12, spacing=12)
        content.add_widget(self._styled_label("Settings", self.theme, bold=True, accent=True, height=40))
        theme_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=8)
        theme_row.add_widget(self._styled_label("Theme:", self.theme, height=40))
        theme_spinner = Spinner(
            text=self.theme_key,
            values=tuple(THEMES.keys()),
            size_hint=(1, 1),
            background_color=self.theme["input_bg"],
            color=self.theme["text"]
        )
        theme_spinner.bind(text=lambda inst, val: self.change_theme(val))
        theme_row.add_widget(theme_spinner)
        content.add_widget(theme_row)
        close_btn = self._styled_button("Close", self.theme, kind="accent")
        close_btn.bind(on_press=lambda *_: self.settings_popup.dismiss())
        content.add_widget(close_btn)
        return content

    def open_settings(self, *_):
        """Open (or refresh) settings popup."""
        if not hasattr(self, "settings_popup") or not self.settings_popup:
            self.settings_popup = Popup(title="Settings", content=BoxLayout(), size_hint=(0.6, 0.5))
        # Rebuild content each time to reflect current theme.
        self.settings_popup.content = self._build_settings_content()
        self.settings_popup.open()

    def change_theme(self, theme_name: str):
        """Apply selected theme and rebuild UI safely by replacing the old root, keeping settings popup on top."""
        if theme_name not in THEMES or theme_name == self.theme_key:
            return
        self.theme_key = theme_name
        self.save_settings()  # NEW: persist theme
        self.theme = THEMES[self.theme_key]
        Window.clearcolor = self.theme["bg"]
        new_root = self._build_root_layout(self.theme)
        old_root = self.main_root
        parent = old_root.parent
        if parent:
            idx = parent.children.index(old_root)
            parent.remove_widget(old_root)
            self.main_root = new_root
            parent.add_widget(self.main_root)
            while parent.children.index(self.main_root) != idx:
                parent.children.insert(idx, parent.children.pop(parent.children.index(self.main_root)))
        else:
            self.main_root = new_root
            self.root = self.main_root
        if getattr(self, "settings_popup", None) and self.settings_popup.parent:
            self.settings_popup.content = self._build_settings_content()
            self.settings_popup.dismiss()
            self.settings_popup.open()

    def _entries_dir(self) -> Path:
        """Return path to the Entry''s directory (create if missing)."""
        # UPDATED: use app base dir for EXE distribution
        d = get_app_base_dir() / "Entry''s"
        d.mkdir(exist_ok=True)
        return d

    def _write_entry(self, data: dict):
        """Append entry to a per-date JSON file as a list."""
        date_key = data.get("date") or datetime.date.today().isoformat()
        file_path = self._entries_dir() / f"{date_key}.json"
        if file_path.exists():
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    existing = json.load(f)
                if not isinstance(existing, list):
                    existing = [existing]
            except Exception:
                existing = []
        else:
            existing = []
        existing.append(data)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    def _collect_entry(self) -> dict:
        """Collect current form data into a dict."""
        return {
            "date": self.date_input.text.strip(),
            "sleep_hours": self.sleep_input.text.strip(),
            "medications": [
                {
                    "status": e["status"].text,
                    "name": e["name"].text.strip(),
                    "dose": e["dose"].text.strip(),
                    "dose_unit": e["dose_unit"].text if "dose_unit" in e else "",
                    "time": e["time"].text.strip(),
                } for e in getattr(self, "med_entries", [])
            ],
            "hrt_types": [
                {
                    "type": e["type"].text,
                    "method": e["method"].text,
                } for e in getattr(self, "hrt_type_entries", [])
            ],
            "side_effects": self.side_effects_input.text.strip(),
            "dysphoria": self.dysphoria_input.text.strip(),
            "euphoria": self.euphoria_input.text.strip(),
            "mood": self.mood_input.text.strip(),        # NEW
            "energy": self.energy_input.text.strip(),    # NEW
            "notes": self.notes_input.text.strip(),
            "timestamp_saved": datetime.datetime.now().isoformat(timespec="seconds"),
        }

    def save_entry(self, *_):
        """Handle save button press: collect and persist."""
        data = self._collect_entry()
        self._write_entry(data)
        print("Entry Saved to folder Entry''s:", data)

    # NEW: View Entries popup
    def open_view_entries(self, *_):
        # Popup with date selector and entries list
        content = BoxLayout(orientation="vertical", padding=12, spacing=12)
        content.add_widget(self._styled_label("View Saved Entries", self.theme, bold=True, accent=True, height=40))

        # Get all saved entry dates
        def get_all_entry_dates():
            entries_dir = self._entries_dir()
            return sorted([
                f.stem for f in entries_dir.glob("*.json")
                if f.is_file() and len(f.stem) == 10 and f.stem[4] == '-' and f.stem[7] == '-'
            ])

        all_dates = get_all_entry_dates()
        default_date = datetime.date.today().isoformat()
        if default_date not in all_dates and all_dates:
            default_date = all_dates[-1]  # fallback to most recent

        date_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=8)
        date_row.add_widget(self._styled_label("Date:", self.theme, height=40))
        date_spinner = Spinner(
            text=default_date,
            values=all_dates if all_dates else [default_date],
            size_hint=(1, 1),
            background_color=self.theme["input_bg"],
            color=self.theme["text"]
        )
        date_row.add_widget(date_spinner)
        content.add_widget(date_row)

        entries_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        entries_box.bind(minimum_height=entries_box.setter("height"))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(entries_box)
        content.add_widget(scroll)

        def entry_to_text(entry):
            # Format the entry dict as readable text
            lines = []
            lines.append(f"Date: {entry.get('date', '')}")
            lines.append(f"Sleep Hours: {entry.get('sleep_hours', '')}")
            lines.append("Medications:")
            for med in entry.get("medications", []):
                med_str = f"  - [{med.get('status', '')}] {med.get('name', '')} ({med.get('dose', '')} {med.get('dose_unit', '')}) at {med.get('time', '')}"
                lines.append(med_str)
            lines.append("HRT Types:")
            for hrt in entry.get("hrt_types", []):
                hrt_str = f"  - {hrt.get('type', '')} via {hrt.get('method', '')}"
                lines.append(hrt_str)
            lines.append(f"Side Effects: {entry.get('side_effects', '')}")
            lines.append(f"Mood: {entry.get('mood', '')}")
            lines.append(f"Energy: {entry.get('energy', '')}")
            lines.append(f"Dysphoria: {entry.get('dysphoria', '')}")
            lines.append(f"Euphoria: {entry.get('euphoria', '')}")
            lines.append(f"Notes: {entry.get('notes', '')}")
            lines.append(f"Saved: {entry.get('timestamp_saved', '')}")
            return "\n".join(lines)

        def load_entries_for_date(date_str):
            entries_box.clear_widgets()
            file_path = self._entries_dir() / f"{date_str}.json"
            if file_path.exists():
                try:
                    with file_path.open("r", encoding="utf-8") as f:
                        entries = json.load(f)
                    if not isinstance(entries, list):
                        entries = [entries]
                    for idx, entry in enumerate(entries, 1):
                        entry_text = entry_to_text(entry)
                        entry_label = self._styled_label(
                            f"Entry {idx}:\n{entry_text}",
                            self.theme, height=220
                        )
                        entries_box.add_widget(entry_label)
                except Exception as e:
                    entries_box.add_widget(self._styled_label(f"Error loading entries: {e}", self.theme, height=40))
            else:
                entries_box.add_widget(self._styled_label("No entries for this date.", self.theme, height=40))

        # Initial load
        load_entries_for_date(date_spinner.text.strip())

        # Reload on date change
        def on_date_change(instance, value):
            load_entries_for_date(value.strip())
        date_spinner.bind(text=on_date_change)

        close_btn = self._styled_button("Close", self.theme, kind="accent")
        popup = Popup(title="View Entries", content=content, size_hint=(0.8, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

# NOTE: add this helper at the bottom of the file, below existing code.
def main():
    """Console entry point used by setup.py and EXE builders."""
    app = TAWTApp()
    app.run()

if __name__ == "__main__":
    # UPDATED: optional tiny CLI to trigger PyInstaller build
    if "--build-exe" in sys.argv:
        # NEW: ensure Settings dir and default app_settings.json exist before bundling
        base_dir = get_app_base_dir()
        settings_dir = base_dir / "Settings"
        settings_dir.mkdir(exist_ok=True)
        settings_file = settings_dir / "app_settings.json"
        if not settings_file.exists():
            # default settings file so first run of the EXE has a theme
            settings_file.write_text(
                json.dumps({"theme": "Dark"}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        # Build platform-specific add-data string safely (handles spaces on Windows)
        if sys.platform.startswith("win"):
            add_data_arg = f"{settings_dir};Settings"
        else:
            add_data_arg = f"{settings_dir}:Settings"

        # Run PyInstaller to create a one-file build, bundling Settings folder.
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--name=HRT-Tracker",
            "--onefile",      # remove for one-folder build if you prefer
            "--windowed",
            f"--add-data={add_data_arg}",
            "HRT-Tracker.py",
        ]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)
    else:
        main()