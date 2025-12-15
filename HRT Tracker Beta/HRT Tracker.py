import customtkinter as ctk
import json
import os
import shutil
from datetime import datetime, date
from tkinter import messagebox
from pathlib import Path
import webbrowser
from tkinter import filedialog

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = str(BASE_DIR / "hrt_entries.json")
RESOURCES_FILE = str(BASE_DIR / "hrt_resources.json")
SETTINGS_FILE = str(BASE_DIR / "hrt_settings.json")


# ------------------------ Utilities ------------------------

def _safe_int(value, default, min_val=None, max_val=None):
    """Convert to int with optional clamping; fall back to default on error."""
    try:
        iv = int(value)
        if min_val is not None and iv < min_val:
            iv = min_val
        if max_val is not None and iv > max_val:
            iv = max_val
        return iv
    except Exception:
        return default


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, type(default)):
            try:
                os.replace(path, path + ".bak")
            except Exception:
                pass
            return default
        return data
    except Exception:
        try:
            backup = path + ".bak"
            if os.path.exists(path):
                os.replace(path, backup)
        except Exception:
            pass
        return default


def save_json(path, data):
    try:
        tmp = f"{path}.tmp"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        try:
            settings = load_settings()
            if settings.get("backup_on_save", False) and os.path.exists(path):
                backup = f"{path}.bak"
                try:
                    shutil.copy2(path, backup)
                except Exception:
                    pass
        except Exception:
            pass
        os.replace(tmp, path)
    except Exception as e:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        try:
            messagebox.showerror("Save error", f"Failed to save {os.path.basename(path)}:\n{e}")
        except Exception:
            pass


def load_entries():
    return load_json(DATA_FILE, [])


def save_entries(entries):
    if not isinstance(entries, list):
        entries = []
    save_json(DATA_FILE, entries)


def load_resources():
    return load_json(RESOURCES_FILE, [])


def save_resources(resources):
    if not isinstance(resources, list):
        resources = []
    save_json(RESOURCES_FILE, resources)


DEFAULT_REGIMEN_SUGGESTIONS = [
    "Estradiol (oral)", "Estradiol valerate (oral)", "Estradiol cypionate (injectable)",
    "Estradiol patch", "Estradiol gel", "Estradiol valerate (injection)",
    "Conjugated estrogens (Premarin)", "Ethinyl estradiol", "Micronized progesterone",
    "Medroxyprogesterone acetate (MPA)", "Levonorgestrel", "Norethindrone",
    "Spironolactone", "Cyproterone acetate", "Finasteride", "Dutasteride",
    "Testosterone (intramuscular)", "Testosterone (topical)", "Testosterone undecanoate",
    "Gonadotropin-releasing hormone agonist (GnRH agonist)", "Other"
]
DEFAULT_ROUTE_OPTIONS = ["Oral", "Patch", "Topical / gel", "Injection", "Sublingual", "Other"]
DEFAULT_MOOD_OPTIONS = ["Neutral", "Happy", "Irritable", "Anxious", "Euphoric", "Low", "Other"]
DEFAULT_DOSE_UNITS = ["mg", "mcg", "units", "ml", "patch", "other"]


def load_settings():
    s = load_json(SETTINGS_FILE, {
        "inclusive_language": True,
        "regimens": DEFAULT_REGIMEN_SUGGESTIONS.copy(),
        "routes": DEFAULT_ROUTE_OPTIONS.copy(),
        "units": DEFAULT_DOSE_UNITS.copy(),
        "appearance": "System",
        "color_theme": "blue",
        "date_format": "%Y-%m-%d",
        "time_format": "%H:%M",
        "show_seconds": True,
        "confirm_actions": True,
        "backup_on_save": False,
        "window_size": "1400x800",  # widened default
        "default_unit": "",
        "default_route": "",
        "note_font_size": 12
    })

    if not isinstance(s, dict):
        s = {}
    s.setdefault("inclusive_language", True)
    s.setdefault("appearance", "System")
    s.setdefault("color_theme", "blue")
    s.setdefault("date_format", "%Y-%m-%d")
    s.setdefault("time_format", "%H:%M")
    s.setdefault("show_seconds", True)
    s.setdefault("confirm_actions", True)
    s.setdefault("backup_on_save", False)
    s.setdefault("window_size", "1400x800")
    s.setdefault("default_unit", "")
    s.setdefault("default_route", "")

    if "regimens" not in s or not isinstance(s["regimens"], list):
        s["regimens"] = DEFAULT_REGIMEN_SUGGESTIONS.copy()
    if "routes" not in s or not isinstance(s["routes"], list):
        s["routes"] = DEFAULT_ROUTE_OPTIONS.copy()
    if "units" not in s or not isinstance(s["units"], list):
        s["units"] = DEFAULT_DOSE_UNITS.copy()

    s["note_font_size"] = _safe_int(s.get("note_font_size", 12), 12, 8, 32)

    if s["appearance"] not in ("System", "Light", "Dark"):
        s["appearance"] = "System"
    if s["color_theme"] not in ("blue", "green", "dark-blue"):
        s["color_theme"] = "blue"

    try:
        _ = datetime.now().strftime(s["date_format"])
    except Exception:
        s["date_format"] = "%Y-%m-%d"
    try:
        _ = datetime.now().strftime(s["time_format"])
    except Exception:
        s["time_format"] = "%H:%M"

    ws = str(s.get("window_size", "1400x800"))
    if "x" not in ws:
        ws = "1400x800"
    else:
        w, _, h = ws.partition("x")
        if not (w.isdigit() and h.isdigit()):
            ws = "1400x800"
    s["window_size"] = ws

    return s


def save_settings(settings):
    if not isinstance(settings, dict):
        settings = load_settings()
    save_json(SETTINGS_FILE, settings)


# ------------------------ Base Page ------------------------

class BasePage(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

    def show(self):
        self.lift()

    def refresh_language(self):
        pass


# ------------------------ HRT Log Page ------------------------

class HRTLogPage(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        self.title_label = ctk.CTkLabel(self, font=("Arial", 24))
        self.title_label.pack(pady=10)

        self.clock_label = ctk.CTkLabel(self, font=("Arial", 10))
        self.clock_label.pack()
        self.update_clock()

        self.info_label = ctk.CTkLabel(self, justify="left")
        self.info_label.pack(pady=5)

        self.content_scroll = ctk.CTkScrollableFrame(self)
        self.content_scroll.pack(fill="both", expand=True, padx=12, pady=(4, 10))

        form_frame = ctk.CTkFrame(self.content_scroll)
        form_frame.pack(pady=10, padx=12, fill="x")

        date_row = ctk.CTkFrame(form_frame)
        date_row.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(date_row, text="Date:").pack(side="left", padx=(0, 6))
        self.date_entry = ctk.CTkEntry(date_row, placeholder_text="YYYY-MM-DD (or format set in Settings)")
        self.date_entry.pack(side="left", fill="x", expand=True)

        time_row = ctk.CTkFrame(form_frame)
        time_row.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(time_row, text="Time:").pack(side="left", padx=(0, 6))
        self.time_entry = ctk.CTkEntry(time_row, placeholder_text="HH:MM (optional)")
        self.time_entry.pack(side="left", fill="x", expand=True)

        try:
            now = datetime.now()
            date_fmt = self.controller.settings.get("date_format", "%Y-%m-%d")
            time_fmt = self.controller.settings.get("time_format", "%H:%M")
            try:
                date_preview = now.strftime(date_fmt)
            except Exception:
                date_fmt = "%Y-%m-%d"
                date_preview = now.strftime(date_fmt)
            try:
                time_preview = now.strftime(time_fmt)
            except Exception:
                time_fmt = "%H:%M"
                time_preview = now.strftime(time_fmt)

            if not self.date_entry.get().strip():
                self.date_entry.insert(0, date_preview)
            if not self.time_entry.get().strip():
                self.time_entry.insert(0, time_preview)
        except Exception:
            pass

        self.meds_container = ctk.CTkFrame(form_frame)
        self.meds_container.pack(pady=5, fill="x")

        meds_label_frame = ctk.CTkFrame(self.meds_container)
        meds_label_frame.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(meds_label_frame, text="Medications (name / dose / route)").pack(side="left")

        try:
            vals = self.controller.settings.get("regimens", DEFAULT_REGIMEN_SUGGESTIONS)
            self.meds_suggest_menu = ctk.CTkOptionMenu(
                meds_label_frame,
                values=vals,
                command=self.insert_regimen_suggestion
            )
            self.meds_suggest_menu.set("Choose med…")
            self.meds_suggest_menu.pack(side="right", padx=(6, 0))
        except Exception:
            self.meds_suggest_menu = None

        add_med_btn = ctk.CTkButton(meds_label_frame, text="+ Add medication", width=150, command=self.add_med_row)
        add_med_btn.pack(side="right")

        self.med_rows = []
        self.add_med_row()

        mood_row = ctk.CTkFrame(form_frame)
        mood_row.pack(fill="x", pady=(6, 2))
        ctk.CTkLabel(mood_row, text="Mood:").pack(side="left", padx=(0, 6))
        self.mood_var = ctk.StringVar(value=DEFAULT_MOOD_OPTIONS[0])
        self.mood_menu = ctk.CTkOptionMenu(mood_row, values=DEFAULT_MOOD_OPTIONS, variable=self.mood_var)
        self.mood_menu.pack(side="left")

        self.symptoms_entry = ctk.CTkEntry(form_frame)
        self.symptoms_entry.pack(pady=5, fill="x")
        self.symptoms_entry.configure(placeholder_text="Symptoms or body sensations (optional)")

        notes_label = ctk.CTkLabel(self.content_scroll, text="Notes:")
        notes_label.pack(pady=(4, 0), padx=12, anchor="w")

        self.notes_box = ctk.CTkTextbox(
            self.content_scroll,
            width=700,
            height=180,
            font=("Arial", self.controller.settings.get("note_font_size", 12))
        )
        self.notes_box.pack(pady=4, padx=12, fill="x")

        save_btn = ctk.CTkButton(self.content_scroll, text="Save Entry", command=self.save_entry)
        save_btn.pack(pady=(4, 12))

        self.refresh_language()

    def update_clock(self):
        try:
            now = datetime.now()
            show_seconds = bool(self.controller.settings.get("show_seconds", True))
            fmt = "Now: %Y-%m-%d %H:%M:%S" if show_seconds else "Now: %Y-%m-%d %H:%M"
            self.clock_label.configure(text=now.strftime(fmt))
        except Exception:
            pass
        try:
            self.after(1000, self.update_clock)
        except Exception:
            pass

    def add_med_row(self, prefill=None):
        row_frame = ctk.CTkFrame(self.meds_container)
        row_frame.pack(fill="x", pady=2)

        name_entry = ctk.CTkEntry(row_frame, placeholder_text="Medication name")
        name_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        dose_entry = ctk.CTkEntry(row_frame, width=120, placeholder_text="Dose")
        dose_entry.pack(side="left", padx=(0, 6))

        try:
            unit_vals = self.controller.settings.get("units", DEFAULT_DOSE_UNITS)
            unit_menu = ctk.CTkOptionMenu(
                row_frame,
                values=unit_vals,
                command=lambda v, e=dose_entry: self._dose_unit_insert(e, v)
            )
            default_unit = self.controller.settings.get("default_unit", "")
            try:
                if default_unit and default_unit in unit_vals:
                    unit_menu.set(default_unit)
                else:
                    unit_menu.set("Unit")
            except Exception:
                try:
                    unit_menu.set("Unit")
                except Exception:
                    pass
            unit_menu.pack(side="left", padx=(0, 6))
        except Exception:
            unit_menu = None

        time_entry = ctk.CTkEntry(row_frame, width=110, placeholder_text="HH:MM")
        time_entry.pack(side="left", padx=(0, 6))

        now_btn = ctk.CTkButton(
            row_frame,
            text="Now",
            width=50,
            command=lambda te=time_entry: te.delete(0, "end") or te.insert(0, datetime.now().strftime("%H:%M"))
        )
        now_btn.pack(side="left", padx=(0, 6))

        try:
            route_vals = self.controller.settings.get("routes", DEFAULT_ROUTE_OPTIONS)
            route_menu = ctk.CTkOptionMenu(
                row_frame,
                values=route_vals,
                command=lambda v, e=name_entry: self._route_insert(e, v)
            )
            default_route = self.controller.settings.get("default_route", "")
            try:
                if default_route and default_route in route_vals:
                    route_menu.set(default_route)
                else:
                    route_menu.set("Route")
            except Exception:
                try:
                    route_menu.set("Route")
                except Exception:
                    pass
            route_menu.pack(side="left", padx=(0, 6))
        except Exception:
            route_menu = None

        remove_btn = ctk.CTkButton(
            row_frame,
            text="Remove",
            width=80,
            command=lambda rf=row_frame: self.remove_med_row(rf)
        )
        remove_btn.pack(side="right")

        if prefill:
            name_entry.insert(0, prefill.get("name", ""))
            dose_entry.insert(0, prefill.get("dose", ""))
            if unit_menu and prefill.get("unit"):
                try:
                    unit_menu.set(prefill.get("unit"))
                except Exception:
                    pass
            if prefill.get("time"):
                try:
                    time_entry.insert(0, prefill.get("time"))
                except Exception:
                    pass
            if route_menu and prefill.get("route"):
                try:
                    route_menu.set(prefill.get("route"))
                except Exception:
                    pass

        self.med_rows.append({
            "frame": row_frame,
            "name": name_entry,
            "dose": dose_entry,
            "unit": unit_menu,
            "time": time_entry,
            "route": route_menu
        })

    def remove_med_row(self, row_frame):
        for idx, r in enumerate(self.med_rows):
            if r["frame"] is row_frame:
                try:
                    r["frame"].destroy()
                except Exception:
                    pass
                del self.med_rows[idx]
                break

    def _route_insert(self, name_entry, value):
        return

    def _dose_unit_insert(self, dose_entry, value):
        if not value or value == "Unit":
            return
        cur = dose_entry.get().strip()
        if cur and not cur.endswith(value):
            dose_entry.delete(0, "end")
            dose_entry.insert(0, f"{cur} {value}")
        else:
            dose_entry.insert("end", f" {value}")

    def insert_regimen_suggestion(self, value):
        if not value or value in ("Suggest…", "Other"):
            return
        if self.med_rows:
            last = self.med_rows[-1]["name"]
            last.delete(0, "end")
            last.insert(0, value)

    def _parse_timestamp(self, date_text, time_text):
        date_fmt = self.controller.settings.get("date_format", "%Y-%m-%d")
        time_fmt = self.controller.settings.get("time_format", "%H:%M")

        date_candidates = [date_fmt, "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]
        time_candidates = [time_fmt, "%H:%M", "%I:%M %p"]

        for df in date_candidates:
            for tf in time_candidates:
                try:
                    dt = datetime.strptime(f"{date_text} {time_text}", f"{df} {tf}")
                    return dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    continue
        try:
            dt = datetime.fromisoformat(f"{date_text} {time_text}")
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            raise ValueError("Could not parse date/time.")

    def save_entry(self):
        date_text = self.date_entry.get().strip()
        time_text = self.time_entry.get().strip()
        if not date_text:
            date_text = datetime.now().strftime(self.controller.settings.get("date_format", "%Y-%m-%d"))
        if not time_text:
            time_text = datetime.now().strftime(self.controller.settings.get("time_format", "%H:%M"))

        try:
            timestamp = self._parse_timestamp(date_text, time_text)
        except ValueError:
            messagebox.showerror(
                "Invalid date/time",
                "Please use a valid date/time.\n"
                "You can adjust formats in Settings if needed."
            )
            return

        meds = []
        for r in self.med_rows:
            name = r["name"].get().strip()
            dose = r["dose"].get().strip()
            unit = ""
            if r.get("unit") is not None:
                try:
                    unit_val = r["unit"].get()
                    if unit_val != "Unit":
                        unit = unit_val
                except Exception:
                    unit = ""
            route = ""
            if r.get("route") is not None:
                try:
                    route = r["route"].get()
                    if route == "Route":
                        route = ""
                except Exception:
                    route = ""
            time_val = r.get("time").get().strip() if r.get("time") is not None else ""
            if name:
                meds.append({"name": name, "dose": dose, "unit": unit, "route": route, "time": time_val})

        mood_value = ""
        try:
            mood_value = self.mood_var.get().strip()
        except Exception:
            pass

        entry = {
            "timestamp": timestamp,
            "regimen": ", ".join(m.get("name", "") for m in meds) if meds else "",
            "route": "",
            "dose": "",
            "mood": mood_value,
            "symptoms": self.symptoms_entry.get().strip(),
            "notes": self.notes_box.get("1.0", "end").strip()
        }

        if meds:
            entry["medications"] = meds

        if not entry["regimen"]:
            messagebox.showinfo("Missing info", "Please enter at least one medication name.")
            return

        entries = load_entries()
        entries.append(entry)
        save_entries(entries)

        self.date_entry.delete(0, "end")
        self.time_entry.delete(0, "end")
        for r in list(self.med_rows):
            try:
                r["frame"].destroy()
            except Exception:
                pass
        self.med_rows = []
        self.add_med_row()
        self.symptoms_entry.delete(0, "end")
        self.notes_box.delete("1.0", "end")
        try:
            self.mood_var.set(DEFAULT_MOOD_OPTIONS[0])
        except Exception:
            pass

        try:
            self.controller.refresh_all_pages()
        except Exception:
            pass

        messagebox.showinfo("Saved", "Entry saved.")

    def refresh_language(self):
        inclusive = self.controller.settings.get("inclusive_language", True)
        self.title_label.configure(text="HRT Log")
        if inclusive:
            self.info_label.configure(
                text="This space is for your own tracking.\n"
                     "Use whatever language feels right for your body and experience."
            )
        else:
            self.info_label.configure(
                text="Track your HRT details.\nLabels may include clinical terminology."
            )

        try:
            if getattr(self, "meds_suggest_menu", None):
                self.meds_suggest_menu.configure(
                    values=self.controller.settings.get("regimens", DEFAULT_REGIMEN_SUGGESTIONS)
                )
                try:
                    self.meds_suggest_menu.set("Choose med…")
                except Exception:
                    pass
        except Exception:
            pass

        for r in getattr(self, "med_rows", []):
            try:
                if r.get("route") is not None:
                    r["route"].configure(values=self.controller.settings.get("routes", DEFAULT_ROUTE_OPTIONS))
                    try:
                        if not r["route"].get():
                            r["route"].set("Route")
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                if r.get("unit") is not None:
                    r["unit"].configure(values=self.controller.settings.get("units", DEFAULT_DOSE_UNITS))
                    try:
                        if not r["unit"].get():
                            r["unit"].set("Unit")
                    except Exception:
                        pass
            except Exception:
                pass

        try:
            new_size = _safe_int(self.controller.settings.get("note_font_size", 12), 12, 8, 32)
            self.notes_box.configure(font=("Arial", new_size))
        except Exception:
            pass


# ------------------------ History Page ------------------------

class HistoryPage(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        self.title_label = ctk.CTkLabel(self, font=("Arial", 24))
        self.title_label.pack(pady=10)

        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(pady=5, padx=10, fill="x")

        self.start_date_entry = ctk.CTkEntry(filter_frame, placeholder_text="Start YYYY-MM-DD")
        self.start_date_entry.pack(side="left", padx=4, pady=5, fill="x")
        self.end_date_entry = ctk.CTkEntry(filter_frame, placeholder_text="End YYYY-MM-DD")
        self.end_date_entry.pack(side="left", padx=4, pady=5, fill="x")

        self.search_entry = ctk.CTkEntry(filter_frame)
        self.search_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        search_btn = ctk.CTkButton(filter_frame, text="Filter", command=self.refresh_list)
        search_btn.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(filter_frame, text="Clear", command=self.clear_filters)
        clear_btn.pack(side="left", padx=5)

        refresh_btn = ctk.CTkButton(filter_frame, text="Refresh", command=self.refresh_list)
        refresh_btn.pack(side="left", padx=5)

        export_btn = ctk.CTkButton(filter_frame, text="Export", command=self.export_filtered)
        export_btn.pack(side="left", padx=5)

        self.list_frame = ctk.CTkScrollableFrame(self, width=300, height=460)
        self.list_frame.pack(side="left", padx=10, pady=10, fill="y")

        right_frame = ctk.CTkFrame(self)
        right_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)

        self.detail_box = ctk.CTkTextbox(right_frame, width=600, height=420)
        self.detail_box.pack(side="top", fill="both", expand=True)

        actions_row = ctk.CTkFrame(right_frame)
        actions_row.pack(side="bottom", fill="x", pady=(6, 0))
        self.delete_btn = ctk.CTkButton(actions_row, text="Delete Entry", command=self.delete_selected_entry)
        self.delete_btn.pack(side="left", padx=(0, 6))
        self.duplicate_btn = ctk.CTkButton(actions_row, text="Duplicate Entry", command=self.duplicate_selected_entry)
        self.duplicate_btn.pack(side="left")

        self.selected_index = None

        self.refresh_language()
        self.refresh_list()

    def refresh_language(self):
        inclusive = self.controller.settings.get("inclusive_language", True)

        self.title_label.configure(text="HRT History")

        if inclusive:
            self.search_entry.configure(placeholder_text="Search entries (any words you use)")
        else:
            self.search_entry.configure(placeholder_text="Search entries")

    def clear_filters(self):
        self.search_entry.delete(0, "end")
        self.start_date_entry.delete(0, "end")
        self.end_date_entry.delete(0, "end")
        self.refresh_list()

    def export_filtered(self):
        if not getattr(self, "display_entries", None):
            messagebox.showinfo("Nothing", "No entries to export with current filter.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.display_entries, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Exported", f"Exported {len(self.display_entries)} entries.")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get().strip().lower()
        start_text = self.start_date_entry.get().strip()
        end_text = self.end_date_entry.get().strip()

        start_date = None
        end_date = None
        try:
            if start_text:
                start_date = datetime.strptime(start_text, "%Y-%m-%d").date()
        except Exception:
            start_date = None
        try:
            if end_text:
                end_date = datetime.strptime(end_text, "%Y-%m-%d").date()
        except Exception:
            end_date = None

        entries = load_entries()
        if not isinstance(entries, list):
            entries = []

        def entry_date(e):
            ts = e.get("timestamp", "")
            if not ts:
                return None
            date_part = ts.split()[0]
            try:
                return datetime.strptime(date_part, "%Y-%m-%d").date()
            except Exception:
                try:
                    return datetime.fromisoformat(ts).date()
                except Exception:
                    return None

        entries_sorted = sorted(entries, key=lambda e: e.get("timestamp", "") or "", reverse=True)

        self.display_entries = []

        for entry in entries_sorted:
            parts = []
            for v in entry.values():
                if isinstance(v, list):
                    parts.extend(str(x) for x in v)
                else:
                    parts.append(str(v))
            blob = " ".join(parts).lower()

            if query and query not in blob:
                continue

            ed = entry_date(entry)
            if start_date and (ed is None or ed < start_date):
                continue
            if end_date and (ed is None or ed > end_date):
                continue

            i = len(self.display_entries)
            self.display_entries.append(entry)
            meds = entry.get("medications")
            label_ts = entry.get("timestamp", "")
            if meds and isinstance(meds, list) and meds:
                first = meds[0]
                first_name = first.get("name") if isinstance(first, dict) else str(first)
                btn_label = f"{label_ts} – {first_name}"
            else:
                regimen = entry.get("regimen", "") or ""
                btn_label = f"{label_ts} – {regimen[:40]}"
            btn = ctk.CTkButton(
                self.list_frame,
                text=btn_label,
                anchor="w",
                command=lambda i=i: self.show_entry(i)
            )
            btn.pack(fill="x", pady=2)

        if not self.display_entries:
            self.detail_box.delete("1.0", "end")
            self.detail_box.insert("1.0", "No entries match this filter.")
            self.selected_index = None

    def show_entry(self, index):
        try:
            entry = self.display_entries[index]
        except Exception:
            return

        self.selected_index = index
        self.detail_box.delete("1.0", "end")
        order = ["timestamp", "regimen", "route", "dose", "mood", "symptoms", "notes"]
        meds = entry.get("medications")
        if meds and isinstance(meds, list):
            self.detail_box.insert("end", "Medications:\n")
            for m in meds:
                if isinstance(m, dict):
                    line = f"  - {m.get('name','')}"
                    if m.get("dose"):
                        if m.get("unit"):
                            line += f" | {m.get('dose')} {m.get('unit')}"
                        else:
                            line += f" | {m.get('dose')}"
                    if m.get("route"):
                        line += f" | {m.get('route')}"
                    if m.get("time"):
                        line += f" | {m.get('time')}"
                    self.detail_box.insert("end", line + "\n")
                else:
                    self.detail_box.insert("end", f"  - {m}\n")

        self.detail_box.insert("end", "\n")
        for key in order:
            if key in ("regimen",) and meds:
                continue
            value = entry.get(key, "")
            if value:
                self.detail_box.insert("end", f"{key.capitalize()}: {value}\n")
        for key, value in entry.items():
            if key not in order and key != "medications":
                self.detail_box.insert("end", f"{key.capitalize()}: {value}\n")

    def delete_selected_entry(self):
        if self.selected_index is None or not getattr(self, "display_entries", None):
            messagebox.showinfo("No selection", "Select an entry to delete.")
            return
        entries = load_entries()
        entry_to_delete = self.display_entries[self.selected_index]
        key = (entry_to_delete.get("timestamp"), entry_to_delete.get("regimen"))
        idx = next((i for i, e in enumerate(entries)
                    if (e.get("timestamp"), e.get("regimen")) == key), None)
        if idx is None:
            messagebox.showerror("Delete failed", "Could not locate entry in data file.")
            return
        if self.controller.settings.get("confirm_actions", True):
            ok = messagebox.askyesno("Confirm delete", "Delete this entry?")
            if not ok:
                return
        del entries[idx]
        save_entries(entries)
        self.selected_index = None
        self.refresh_list()
        try:
            self.controller.show_status("Entry deleted.")
        except Exception:
            pass

    def duplicate_selected_entry(self):
        if self.selected_index is None or not getattr(self, "display_entries", None):
            messagebox.showinfo("No selection", "Select an entry to duplicate.")
            return
        entries = load_entries()
        original = self.display_entries[self.selected_index]
        new_entry = dict(original)
        new_entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        entries.append(new_entry)
        save_entries(entries)
        self.refresh_list()
        try:
            self.controller.show_status("Entry duplicated.")
        except Exception:
            pass


# ------------------------ Resources Page ------------------------

class ResourcesPage(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        self.title_label = ctk.CTkLabel(self, font=("Arial", 24))
        self.title_label.pack(pady=10)

        self.info_label = ctk.CTkLabel(self, justify="left")
        self.info_label.pack(pady=5)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        list_container = ctk.CTkFrame(main_frame)
        list_container.pack(side="left", fill="y", padx=5, pady=5)

        self.resource_list = ctk.CTkScrollableFrame(list_container, width=260, height=430)
        self.resource_list.pack(pady=5)

        btn_frame = ctk.CTkFrame(list_container)
        btn_frame.pack(pady=5, fill="x")
        ctk.CTkButton(btn_frame, text="New", command=self.new_resource).pack(side="left", padx=2, expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="Delete", command=self.delete_selected).pack(side="left", padx=2, expand=True, fill="x")

        detail_frame = ctk.CTkFrame(main_frame)
        detail_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(detail_frame, text="Title:").pack(pady=(0, 0), anchor="w")
        self.title_entry = ctk.CTkEntry(detail_frame)
        self.title_entry.pack(pady=2, fill="x")

        ctk.CTkLabel(detail_frame, text="Link or contact:").pack(pady=(6, 0), anchor="w")
        self.link_entry = ctk.CTkEntry(detail_frame)
        self.link_entry.pack(pady=2, fill="x")

        ctk.CTkLabel(detail_frame, text="Tags:").pack(pady=(6, 0), anchor="w")
        self.tags_entry = ctk.CTkEntry(detail_frame)
        self.tags_entry.pack(pady=2, fill="x")

        self.notes_box = ctk.CTkTextbox(detail_frame, width=500, height=320)
        self.notes_box.pack(pady=5, fill="both", expand=True)

        save_btn = ctk.CTkButton(detail_frame, text="Save Resource", command=self.save_current)
        save_btn.pack(pady=5)

        open_btn = ctk.CTkButton(detail_frame, text="Open Link", command=self.open_link)
        open_btn.pack(pady=2)

        self.selected_index = None
        self.refresh_language()
        self.refresh_list()

    def refresh_language(self):
        inclusive = self.controller.settings.get("inclusive_language", True)

        self.title_label.configure(text="HRT & Community Resources")

        if inclusive:
            self.info_label.configure(
                text="Store your own links, clinics, guides, mutual aid, and community spaces.\n"
                     "This page avoids gendered or normative labels."
            )
            self.title_entry.configure(placeholder_text="Title")
            self.link_entry.configure(placeholder_text="Link or contact info")
            self.tags_entry.configure(placeholder_text="Tags (e.g., legal, hormones, community)")
        else:
            self.info_label.configure(
                text="Store links and information related to HRT and support."
            )
            self.title_entry.configure(placeholder_text="Resource title")
            self.link_entry.configure(placeholder_text="URL or contact")
            self.tags_entry.configure(placeholder_text="Tags")

    def refresh_list(self):
        for w in self.resource_list.winfo_children():
            w.destroy()

        self.resources = load_resources()
        for idx, res in enumerate(self.resources):
            text = res.get("title", "Untitled")
            btn = ctk.CTkButton(
                self.resource_list,
                text=text,
                anchor="w",
                command=lambda i=idx: self.load_resource(i)
            )
            btn.pack(fill="x", pady=2)

    def load_resource(self, index):
        self.selected_index = index
        res = self.resources[index]

        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, res.get("title", ""))

        self.link_entry.delete(0, "end")
        self.link_entry.insert(0, res.get("link", ""))

        self.tags_entry.delete(0, "end")
        self.tags_entry.insert(0, ", ".join(res.get("tags", [])))

        self.notes_box.delete("1.0", "end")
        self.notes_box.insert("1.0", res.get("notes", ""))

    def new_resource(self):
        self.selected_index = None
        self.title_entry.delete(0, "end")
        self.link_entry.delete(0, "end")
        self.tags_entry.delete(0, "end")
        self.notes_box.delete("1.0", "end")

    def save_current(self):
        title = self.title_entry.get().strip()
        link = self.link_entry.get().strip()
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        notes = self.notes_box.get("1.0", "end").strip()

        if not title and not link and not notes:
            messagebox.showinfo("Nothing to save", "Add at least a title, link, or notes.")
            return

        resources = load_resources()
        item = {
            "title": title,
            "link": link,
            "tags": tags,
            "notes": notes
        }

        if self.selected_index is None:
            resources.append(item)
        else:
            if 0 <= self.selected_index < len(resources):
                resources[self.selected_index] = item
            else:
                resources.append(item)

        save_resources(resources)
        self.refresh_list()
        messagebox.showinfo("Saved", "Resource saved.")

    def delete_selected(self):
        if self.selected_index is None:
            messagebox.showinfo("No selection", "Select a resource to delete.")
            return

        resources = load_resources()
        if 0 <= self.selected_index < len(resources):
            ok = messagebox.askyesno("Confirm delete", "Delete selected resource?")
            if not ok:
                return
            del resources[self.selected_index]
            save_resources(resources)
            self.selected_index = None
            self.new_resource()
            self.refresh_list()
            messagebox.showinfo("Deleted", "Resource deleted.")

    def open_link(self):
        link = self.link_entry.get().strip()
        if not link:
            messagebox.showinfo("No link", "No link to open for this resource.")
            return
        try:
            if not link.startswith(("http://", "https://", "mailto:")) and "@" not in link:
                link = "http://" + link
            webbrowser.open(link)
        except Exception as e:
            messagebox.showerror("Open failed", f"Could not open link:\n{e}")


# ------------------------ Settings Page ------------------------

class SettingsPage(BasePage):
    DATE_FORMATS = [("YYYY-MM-DD", "%Y-%m-%d"), ("MM/DD/YYYY", "%m/%d/%Y"), ("DD/MM/YYYY", "%d/%m/%Y")]
    TIME_FORMATS = [("24-hour HH:MM", "%H:%M"), ("12-hour hh:MM AM/PM", "%I:%M %p")]
    APPEARANCE_OPTIONS = ["System", "Light", "Dark"]
    COLOR_THEMES = ["blue", "green", "dark-blue"]

    def __init__(self, master, controller):
        super().__init__(master, controller)

        ctk.CTkLabel(self, text="Settings", font=("Arial", 24)).pack(pady=12)

        self.inclusive_var = ctk.BooleanVar(value=self.controller.settings.get("inclusive_language", True))
        self.confirm_var = ctk.BooleanVar(value=self.controller.settings.get("confirm_actions", True))
        self.seconds_var = ctk.BooleanVar(value=self.controller.settings.get("show_seconds", True))
        self.backup_var = ctk.BooleanVar(value=self.controller.settings.get("backup_on_save", False))

        self.toggle = ctk.CTkSwitch(
            self,
            text="Use inclusive language",
            variable=self.inclusive_var,
            command=self.save_settings
        )
        self.toggle.pack(pady=(0, 10), padx=12, anchor="w")

        appearance_row = ctk.CTkFrame(self)
        appearance_row.pack(fill="x", padx=12, pady=(0, 6))
        ctk.CTkLabel(appearance_row, text="Appearance:").pack(side="left", padx=(0, 6))
        self.appearance_menu = ctk.CTkOptionMenu(
            appearance_row,
            values=self.APPEARANCE_OPTIONS,
            command=self._on_change_appearance
        )
        self.appearance_menu.set(self.controller.settings.get("appearance", "System"))
        self.appearance_menu.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(appearance_row, text="Color theme:").pack(side="left", padx=(6, 6))
        self.theme_menu = ctk.CTkOptionMenu(
            appearance_row,
            values=self.COLOR_THEMES,
            command=self._on_change_theme
        )
        self.theme_menu.set(self.controller.settings.get("color_theme", "blue"))
        self.theme_menu.pack(side="left")

        self.lists_scroll = ctk.CTkScrollableFrame(self)
        self.lists_scroll.pack(fill="both", expand=True, padx=12, pady=6)

        lists_frame = ctk.CTkFrame(self.lists_scroll)
        lists_frame.pack(fill="x", padx=6, pady=6)

        self._build_list_editor(lists_frame, "regimens", "Regimens / Meds")
        self._build_list_editor(lists_frame, "routes", "Routes")
        self._build_list_editor(lists_frame, "units", "Dose units")

        defaults_frame = ctk.CTkFrame(self.lists_scroll)
        defaults_frame.pack(fill="x", padx=6, pady=(8, 6))

        df_row = ctk.CTkFrame(defaults_frame)
        df_row.pack(fill="x", pady=(4, 4))
        ctk.CTkLabel(df_row, text="Date format:").pack(side="left", padx=(6, 6))
        self.date_menu = ctk.CTkOptionMenu(
            df_row,
            values=[d[0] for d in self.DATE_FORMATS],
            command=self._on_change_date_format
        )
        current_df = self._find_format_label(self.controller.settings.get("date_format", "%Y-%m-%d"), self.DATE_FORMATS)
        self.date_menu.set(current_df)
        self.date_menu.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(df_row, text="Time format:").pack(side="left", padx=(6, 6))
        self.time_menu = ctk.CTkOptionMenu(
            df_row,
            values=[t[0] for t in self.TIME_FORMATS],
            command=self._on_change_time_format
        )
        current_tf = self._find_format_label(self.controller.settings.get("time_format", "%H:%M"), self.TIME_FORMATS)
        self.time_menu.set(current_tf)
        self.time_menu.pack(side="left")

        def_row = ctk.CTkFrame(defaults_frame)
        def_row.pack(fill="x", pady=(4, 4))
        ctk.CTkLabel(def_row, text="Default unit:").pack(side="left", padx=(6, 6))
        self.default_unit_menu = ctk.CTkOptionMenu(
            def_row,
            values=["(none)"] + self.controller.settings.get("units", DEFAULT_DOSE_UNITS),
            command=self._on_change_default_unit
        )
        self.default_unit_menu.set(self.controller.settings.get("default_unit", "(none)") or "(none)")
        self.default_unit_menu.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(def_row, text="Default route:").pack(side="left", padx=(6, 6))
        self.default_route_menu = ctk.CTkOptionMenu(
            def_row,
            values=["(none)"] + self.controller.settings.get("routes", DEFAULT_ROUTE_OPTIONS),
            command=self._on_change_default_route
        )
        self.default_route_menu.set(self.controller.settings.get("default_route", "(none)") or "(none)")
        self.default_route_menu.pack(side="left")

        toggles_row = ctk.CTkFrame(defaults_frame)
        toggles_row.pack(fill="x", pady=(6, 4), padx=6)
        ctk.CTkSwitch(
            toggles_row,
            text="Confirm destructive actions",
            variable=self.confirm_var,
            command=self._on_toggle_confirm
        ).pack(side="left", padx=(6, 8))
        ctk.CTkSwitch(
            toggles_row,
            text="Show seconds in clock",
            variable=self.seconds_var,
            command=self._on_toggle_seconds
        ).pack(side="left", padx=(6, 8))
        ctk.CTkSwitch(
            toggles_row,
            text="Backup on save",
            variable=self.backup_var,
            command=self._on_toggle_backup
        ).pack(side="left", padx=(6, 8))

        ws_row = ctk.CTkFrame(defaults_frame)
        ws_row.pack(fill="x", pady=(6, 4), padx=6)
        ctk.CTkLabel(ws_row, text="Window size (e.g. 1400x800):").pack(side="left", padx=(6, 6))
        self.window_entry = ctk.CTkEntry(ws_row)
        self.window_entry.insert(0, self.controller.settings.get("window_size", "1400x800"))
        self.window_entry.pack(side="left", padx=(0, 12), fill="x", expand=True)

        nf_row = ctk.CTkFrame(defaults_frame)
        nf_row.pack(fill="x", pady=(4, 8), padx=6)
        ctk.CTkLabel(nf_row, text="Notes font size:").pack(side="left", padx=(6, 6))
        self.note_font_var = ctk.IntVar(value=self.controller.settings.get("note_font_size", 12))
        self.note_font_slider = ctk.CTkSlider(
            nf_row,
            from_=8,
            to=32,
            number_of_steps=24,
            variable=self.note_font_var,
            command=lambda v: None
        )
        self.note_font_slider.pack(side="left", fill="x", expand=True)
        self.note_font_label = ctk.CTkLabel(nf_row, text=str(self.note_font_var.get()))
        self.note_font_label.pack(side="left", padx=(6, 0))

        def _update_nf_label(*_args):
            try:
                self.note_font_label.configure(text=str(int(self.note_font_var.get())))
            except Exception:
                pass

        self.note_font_var.trace_add("write", _update_nf_label)

        action_row = ctk.CTkFrame(self)
        action_row.pack(fill="x", padx=12, pady=(8, 12))
        save_btn = ctk.CTkButton(action_row, text="Save Settings", command=self.apply_and_save, width=140)
        save_btn.pack(side="left", padx=(0, 6))
        reset_btn = ctk.CTkButton(
            action_row,
            text="Reset to defaults",
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=self.reset_defaults,
            width=160
        )
        reset_btn.pack(side="left", padx=(6, 0))

        self._list_editors = getattr(self, "_list_editors", {})
        self.refresh_settings_lists()
        self._apply_appearance_and_theme()

    def _find_format_label(self, pattern, candidates):
        for label, pat in candidates:
            if pat == pattern:
                return label
        return candidates[0][0]

    def _apply_appearance_and_theme(self):
        try:
            app_appearance = self.controller.settings.get("appearance", "System")
            color_theme = self.controller.settings.get("color_theme", "blue")
            try:
                self.controller.apply_theme(app_appearance, color_theme)
            except Exception:
                try:
                    ctk.set_appearance_mode(app_appearance)
                except Exception:
                    pass
                try:
                    ctk.set_default_color_theme(color_theme)
                except Exception:
                    pass
            try:
                self.controller.geometry(self.controller.settings.get("window_size", "1400x800"))
            except Exception:
                pass
        except Exception:
            pass

    def _on_change_appearance(self, v):
        self.controller.settings["appearance"] = v
        save_settings(self.controller.settings)
        try:
            self.controller.reload_settings()
        except Exception:
            try:
                self.controller.apply_theme(v, self.controller.settings.get("color_theme", "blue"))
            except Exception:
                try:
                    ctk.set_appearance_mode(v)
                except Exception:
                    pass

    def _on_change_theme(self, v):
        self.controller.settings["color_theme"] = v
        save_settings(self.controller.settings)
        try:
            self.controller.reload_settings()
        except Exception:
            try:
                self.controller.apply_theme(self.controller.settings.get("appearance", "System"), v)
            except Exception:
                try:
                    ctk.set_default_color_theme(v)
                except Exception:
                    pass

    def _on_change_date_format(self, label):
        for lab, pat in self.DATE_FORMATS:
            if lab == label:
                self.controller.settings["date_format"] = pat
                save_settings(self.controller.settings)
                return

    def _on_change_time_format(self, label):
        for lab, pat in self.TIME_FORMATS:
            if lab == label:
                self.controller.settings["time_format"] = pat
                save_settings(self.controller.settings)
                return

    def _on_change_default_unit(self, v):
        if v == "(none)":
            self.controller.settings["default_unit"] = ""
        else:
            self.controller.settings["default_unit"] = v
        save_settings(self.controller.settings)

    def _on_change_default_route(self, v):
        if v == "(none)":
            self.controller.settings["default_route"] = ""
        else:
            self.controller.settings["default_route"] = v
        save_settings(self.controller.settings)

    def _on_toggle_confirm(self):
        self.controller.settings["confirm_actions"] = self.confirm_var.get()
        save_settings(self.controller.settings)

    def _on_toggle_seconds(self):
        self.controller.settings["show_seconds"] = self.seconds_var.get()
        save_settings(self.controller.settings)

    def _on_toggle_backup(self):
        self.controller.settings["backup_on_save"] = self.backup_var.get()
        save_settings(self.controller.settings)

    def _build_list_editor(self, parent, key, label_text):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=6)

        ctk.CTkLabel(frame, text=label_text).pack(anchor="w", padx=6)

        row = ctk.CTkFrame(frame)
        row.pack(fill="x", pady=(6, 0), padx=6)
        entry = ctk.CTkEntry(row, placeholder_text="Add new item and click Add")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        add_btn = ctk.CTkButton(row, text="Add", width=80, command=lambda k=key, e=entry: self._add_list_item(k, e))
        add_btn.pack(side="right")

        items_container = ctk.CTkScrollableFrame(frame, height=120)
        items_container.pack(fill="x", pady=(6, 0), padx=6)
        if not hasattr(self, "_list_editors"):
            self._list_editors = {}
        self._list_editors[key] = {"entry": entry, "container": items_container}

    def _add_list_item(self, key, entry_widget):
        v = entry_widget.get().strip()
        if not v:
            return
        lst = self.controller.settings.get(key, [])
        if v in lst:
            entry_widget.delete(0, "end")
            return
        lst.append(v)
        self.controller.settings[key] = lst
        save_settings(self.controller.settings)
        entry_widget.delete(0, "end")
        self.refresh_settings_lists()
        try:
            self.controller.refresh_all_pages()
        except Exception:
            pass

    def _delete_list_item(self, key, index):
        lst = self.controller.settings.get(key, [])
        if 0 <= index < len(lst):
            del lst[index]
            self.controller.settings[key] = lst
            save_settings(self.controller.settings)
            self.refresh_settings_lists()
            try:
                self.controller.refresh_all_pages()
            except Exception:
                pass

    def _move_list_item(self, key, index, delta):
        lst = self.controller.settings.get(key, [])
        if not lst:
            return
        new_index = index + delta
        if new_index < 0 or new_index >= len(lst):
            return
        lst[index], lst[new_index] = lst[new_index], lst[index]
        self.controller.settings[key] = lst
        save_settings(self.controller.settings)
        self.refresh_settings_lists()
        try:
            self.controller.refresh_all_pages()
        except Exception:
            pass

    def refresh_settings_lists(self):
        for key, ed in self._list_editors.items():
            cont = ed["container"]
            for w in cont.winfo_children():
                w.destroy()
            items = self.controller.settings.get(key, [])
            for idx, it in enumerate(items):
                item_row = ctk.CTkFrame(cont)
                item_row.pack(fill="x", pady=2, padx=4)
                lbl = ctk.CTkLabel(item_row, text=str(it), anchor="w")
                lbl.pack(side="left", fill="x", expand=True)
                btns = ctk.CTkFrame(item_row)
                btns.pack(side="right")
                up_btn = ctk.CTkButton(
                    btns, text="▲", width=36,
                    command=lambda k=key, i=idx: self._move_list_item(k, i, -1)
                )
                up_btn.pack(side="left", padx=(0, 4))
                down_btn = ctk.CTkButton(
                    btns, text="▼", width=36,
                    command=lambda k=key, i=idx: self._move_list_item(k, i, 1)
                )
                down_btn.pack(side="left", padx=(0, 4))
                del_btn = ctk.CTkButton(
                    btns, text="Delete", width=70,
                    command=lambda k=key, i=idx: self._delete_list_item(k, i)
                )
                del_btn.pack(side="left")
        try:
            units = ["(none)"] + self.controller.settings.get("units", DEFAULT_DOSE_UNITS)
            routes = ["(none)"] + self.controller.settings.get("routes", DEFAULT_ROUTE_OPTIONS)
            try:
                self.default_unit_menu.configure(values=units)
                cur = self.controller.settings.get("default_unit", "(none)") or "(none)"
                if cur not in units:
                    cur = "(none)"
                self.default_unit_menu.set(cur)
            except Exception:
                pass
            try:
                self.default_route_menu.configure(values=routes)
                cur2 = self.controller.settings.get("default_route", "(none)") or "(none)"
                if cur2 not in routes:
                    cur2 = "(none)"
                self.default_route_menu.set(cur2)
            except Exception:
                pass
        except Exception:
            pass

    def save_settings(self):
        self.controller.settings["inclusive_language"] = self.inclusive_var.get()
        save_settings(self.controller.settings)
        try:
            self.controller.reload_settings()
        except Exception:
            try:
                self.controller.refresh_all_pages()
            except Exception:
                pass

    def apply_and_save(self):
        self.controller.settings["inclusive_language"] = self.inclusive_var.get()
        self.controller.settings["confirm_actions"] = self.confirm_var.get()
        self.controller.settings["show_seconds"] = self.seconds_var.get()
        self.controller.settings["backup_on_save"] = self.backup_var.get()
        ws = self.window_entry.get().strip()
        if ws and "x" in ws:
            w, _, h = ws.partition("x")
            if w.isdigit() and h.isdigit():
                self.controller.settings["window_size"] = ws
        nf = _safe_int(self.note_font_var.get(), 12, 8, 32)
        self.controller.settings["note_font_size"] = nf
        save_settings(self.controller.settings)
        try:
            self.controller.reload_settings()
        except Exception:
            self._apply_appearance_and_theme()
            try:
                self.controller.refresh_all_pages()
            except Exception:
                pass
        messagebox.showinfo("Settings", "Settings saved and applied.")

    def reset_defaults(self):
        ok = True
        if self.controller.settings.get("confirm_actions", True):
            ok = messagebox.askyesno("Reset", "Reset settings to defaults? This will overwrite current lists.")
        if not ok:
            return
        self.controller.settings = {
            "inclusive_language": True,
            "regimens": DEFAULT_REGIMEN_SUGGESTIONS.copy(),
            "routes": DEFAULT_ROUTE_OPTIONS.copy(),
            "units": DEFAULT_DOSE_UNITS.copy(),
            "appearance": "System",
            "color_theme": "blue",
            "date_format": "%Y-%m-%d",
            "time_format": "%H:%M",
            "show_seconds": True,
            "confirm_actions": True,
            "backup_on_save": False,
            "window_size": "1400x800",  # widened default
            "default_unit": "",
            "default_route": "",
            "note_font_size": 12
        }
        save_settings(self.controller.settings)
        self.inclusive_var.set(True)
        self.confirm_var.set(True)
        self.seconds_var.set(True)
        self.backup_var.set(False)
        self.window_entry.delete(0, "end")
        self.window_entry.insert(0, "1400x800")
        self.note_font_var.set(12)
        self.appearance_menu.set("System")
        self.theme_menu.set("blue")
        self.date_menu.set(self._find_format_label("%Y-%m-%d", self.DATE_FORMATS))
        self.time_menu.set(self._find_format_label("%H:%M", self.TIME_FORMATS))
        self.refresh_settings_lists()
        self._apply_appearance_and_theme()
        try:
            self.controller.refresh_all_pages()
        except Exception:
            pass
        messagebox.showinfo("Reset", "Settings restored to defaults.")


# ------------------------ Help Page ------------------------

class HelpPage(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        self.title_label = ctk.CTkLabel(self, text="HRT Tracker Help & Guide", font=("Arial", 24))
        self.title_label.pack(pady=10)

        info = (
            "Overview\n"
            "========\n"
            "HRT Tracker is a personal logging tool for hormone‑related regimens, symptoms, "
            "and resources. Nothing is sent anywhere: all data is stored as JSON files on "
            "your own computer in the same folder as this program.\n\n"
            "This help page explains each part of the app in detail and how it all fits together.\n\n"
            "Data Files\n"
            "----------\n"
            f"- Entries file: {DATA_FILE}\n"
            f"- Resources file: {RESOURCES_FILE}\n"
            f"- Settings file: {SETTINGS_FILE}\n\n"
            "If any file becomes corrupted, the app will quietly rename it with a '.bak' extension "
            "and start from a safe default so the program keeps working.\n\n"
            "1. HRT Log Page\n"
            "----------------\n"
            "Use this page for day‑to‑day logging of what you take and how you feel.\n\n"
            "Key sections:\n"
            "- Clock: Shows the current date and time. You can show or hide seconds in Settings.\n"
            "- Date / Time fields:\n"
            "  • Date: Defaults to 'today' when you open the app, using the format chosen in Settings.\n"
            "  • Time: Defaults to 'now' when leaving it blank. Format also follows Settings (24‑hour or 12‑hour).\n"
            "  If parsing fails, the app shows an error and does not save the entry.\n\n"
            "- Medications list:\n"
            "  • Each row has: medication name, dose, dose unit, time for that dose, and route.\n"
            "  • '+ Add medication' adds another row.\n"
            "  • 'Remove' removes a specific row.\n"
            "  • 'Unit' dropdown inserts a unit into the dose field (e.g. '2 mg').\n"
            "  • 'Route' dropdown (e.g. Oral, Patch, Injection) comes from Settings and can be customized.\n"
            "  • 'Now' button on each row fills in the current time for that medication.\n"
            "  • The 'Choose med…' dropdown at the top lets you quickly insert a common medication name "
            "    into the last row.\n\n"
            "- Mood:\n"
            "  • A dropdown with common options (Neutral, Happy, Irritable, etc.).\n"
            "  • You can leave it as‑is or change it each time.\n\n"
            "- Symptoms:\n"
            "  • A single‑line field for any sensations, side‑effects, or notes about your body.\n"
            "  • Optional; you can leave it empty.\n\n"
            "- Notes:\n"
            "  • A multi‑line text box for detailed notes.\n"
            "  • Font size can be adjusted under Settings ➜ 'Notes font size'.\n\n"
            "- Save Entry:\n"
            "  • Saves a snapshot of: timestamp, medication list, mood, symptoms, and notes to the entries file.\n"
            "  • At least one medication name is required; otherwise you'll be asked to add one first.\n"
            "  • After saving, the form resets so you can add another entry.\n\n"
            "2. History Page\n"
            "----------------\n"
            "The History page lets you review, filter, and manage saved entries.\n\n"
            "Filtering & search:\n"
            "- 'Start YYYY-MM-DD' / 'End YYYY-MM-DD':\n"
            "  • Filter entries whose date falls within this range.\n"
            "  • The filter expects YYYY-MM-DD; if parsing fails, that date filter is ignored.\n"
            "- Search box:\n"
            "  • Searches across timestamps, medications, mood, symptoms, notes, and any other fields.\n"
            "  • Matching is case‑insensitive and finds simple substrings.\n"
            "- Buttons:\n"
            "  • Filter: Apply current date and search filters.\n"
            "  • Clear: Reset all filters.\n"
            "  • Refresh: Reloads the underlying data from disk (useful if the JSON file changed externally).\n"
            "  • Export: Saves the currently filtered entries to a new JSON file of your choice.\n\n"
            "Entry list and details:\n"
            "- Left side: A scrollable list of buttons, one per entry.\n"
            "  • Each button shows the timestamp and either the first medication or the regimen summary.\n"
            "- Right side: A detailed text view for the selected entry.\n"
            "  • Shows a 'Medications:' section with each item's name, dose, unit, route, and per‑medication time.\n"
            "  • Shows fields like Mood, Symptoms, Notes, and any extra stored keys.\n\n"
            "Managing entries:\n"
            "- 'Delete Entry':\n"
            "  • Deletes the currently selected entry from the data file.\n"
            "  • If 'Confirm destructive actions' is enabled in Settings, you'll be asked to confirm first.\n"
            "- 'Duplicate Entry':\n"
            "  • Copies the selected entry and assigns it a new timestamp set to the current time.\n"
            "  • This is useful for quickly logging repeated regimens with minor edits.\n\n"
            "3. Resources Page\n"
            "------------------\n"
            "Use this page to store links, contacts, and notes about clinics, guides, or community resources.\n\n"
            "Layout:\n"
            "- Left side:\n"
            "  • A scrollable list of saved resources.\n"
            "  • 'New' button clears the editor so you can create a new resource.\n"
            "  • 'Delete' removes the currently selected resource after confirmation.\n"
            "- Right side:\n"
            "  • Title: A short name for the resource.\n"
            "  • Link or contact: Website URL, email, phone, etc.\n"
            "  • Tags: Keywords separated by commas (e.g. 'legal, hormones, community').\n"
            "  • Notes: A larger box for any details.\n"
            "  • 'Save Resource': Stores or updates the resource in the JSON file.\n"
            "  • 'Open Link': Opens the link in your default browser.\n"
            "    - If you omit 'http://' or 'https://', the app will try to add 'http://' for you.\n"
            "\n"
            "4. Settings Page\n"
            "-----------------\n"
            "The Settings page controls app behavior, language, lists, and appearance.\n\n"
            "Language & inclusivity:\n"
            "- 'Use inclusive language':\n"
            "  • When enabled, help text and placeholders aim to avoid gendered or normative terms.\n"
            "  • When disabled, wording can be more clinical or neutral.\n\n"
            "Appearance & theme:\n"
            "- Appearance (System / Light / Dark):\n"
            "  • Controls the overall brightness mode of the app.\n"
            "  • 'System' follows your OS preference when supported.\n"
            "- Color theme (blue / green / dark-blue):\n"
            "  • Controls the accent colors for buttons and widgets.\n"
            "  • Changes are applied app‑wide.\n\n"
            "Custom lists:\n"
            "- Regimens / Meds:\n"
            "  • Items appear in the 'Choose med…' dropdown on the HRT Log page.\n"
            "  • Use 'Add' to define your own common regimens or medication names.\n"
            "  • Use the ▲ / ▼ buttons to reorder items; 'Delete' removes an item.\n"
            "- Routes:\n"
            "  • Items appear in the 'Route' dropdown for each medication row.\n"
            "  • Can include anything useful to you, such as 'Oral', 'IM', 'Patch', 'Sublingual', etc.\n"
            "- Dose units:\n"
            "  • Items appear in the 'Unit' dropdown for each medication row.\n"
            "  • Examples: mg, mcg, units, ml, patches.\n\n"
            "Date / time and defaults:\n"
            "- Date format:\n"
            "  • Choose whether dates like today's appear as '2025-01-31', '01/31/2025', or '31/01/2025'.\n"
            "- Time format:\n"
            "  • 24‑hour (e.g. 13:45) or 12‑hour (e.g. 01:45 PM).\n"
            "  • The HRT Log page uses these when pre‑filling date/time.\n"
            "- Default unit / Default route:\n"
            "  • Pre‑selected values for new medication rows.\n"
            "  • Choose '(none)' if you prefer them blank.\n\n"
            "Other behavior:\n"
            "- Confirm destructive actions:\n"
            "  • When enabled, the app asks for confirmation before deleting entries or resources.\n"
            "- Show seconds in clock:\n"
            "  • Toggles whether the main clock shows seconds.\n"
            "- Backup on save:\n"
            "  • When enabled, the app keeps a '.bak' backup of JSON files before overwriting them.\n"
            "  • Useful as an extra safety net.\n"
            "- Window size:\n"
            "  • Sets the default size of the app window (e.g. '1400x800').\n"
            "  • Incorrect values are ignored and the app falls back to a safe default.\n"
            "- Notes font size:\n"
            "  • Controls the font size of multi‑line note fields (primarily on the HRT Log page).\n"
            "  • Allowed range is 8–32 points.\n\n"
            "Saving & resetting:\n"
            "- 'Save Settings':\n"
            "  • Applies and persists all current settings, including appearance and note font size.\n"
            "- 'Reset to defaults':\n"
            "  • Restores all settings to sensible defaults.\n"
            "  • This also resets custom lists for regimens, routes, and units.\n"
            "  • If confirmation is enabled, you'll be asked before resetting.\n\n"
            "5. Status Bar & Messages\n"
            "------------------------\n"
            "At the bottom of the main window, a small status bar briefly shows messages such as:\n"
            "- 'Viewing HRT Log' when you switch pages.\n"
            "- 'Entry deleted.' or 'Entry duplicated.' after actions on the History page.\n"
            "These messages clear automatically after a short delay.\n\n"
            "6. Safety, Backups, and Limits\n"
            "------------------------------\n"
            "- Local‑only data:\n"
            "  • This app does not sync or transmit your entries. Everything stays in JSON files locally.\n"
            "- Backup behavior:\n"
            "  • If 'Backup on save' is enabled, a '.bak' file is kept alongside each main JSON file.\n"
            "  • If something goes wrong when loading a JSON file, the app renames it to '.bak' and "
            "    starts from defaults so that it can still run.\n"
            "- Large histories:\n"
            "  • The app is designed for typical personal use. Very large history files may slow down "
            "    filtering or loading slightly, but the JSON format remains the same.\n\n"
            "7. Troubleshooting\n"
            "-------------------\n"
            "- If the app refuses to parse your date/time:\n"
            "  • Check the date format setting (Settings ➜ Date format) and match it in the HRT Log page.\n"
            "  • Try a simpler date like '2025-01-31' and time like '13:45' to confirm.\n"
            "- If the window looks wrong after changing size or theme:\n"
            "  • Close and reopen the app; it will re‑apply window size and theme from Settings.\n"
            "  • You can always reset to defaults if something seems off.\n"
            "- If JSON files become corrupted:\n"
            "  • The app automatically renames problematic files to '.bak' and recreates new ones.\n"
            "  • You can open the '.bak' files in a text editor if you need to manually rescue old data.\n\n"
            "8. Personalization Tips\n"
            "------------------------\n"
            "- Use custom regimens for common patterns (e.g. 'Evening oral estradiol' or 'Weekly injection').\n"
            "- Use tags on Resources to quickly group clinics, guides, community spaces, and legal help.\n"
            "- Adjust the notes font size to what feels comfortable for extended journaling.\n"
        )

        self.text_box = ctk.CTkTextbox(self, wrap="word", width=800, height=500)
        self.text_box.pack(fill="both", expand=True, padx=12, pady=(6, 12))
        self.text_box.insert("1.0", info)
        self.text_box.configure(state="disabled")

    def refresh_language(self):
        pass


# ------------------------ Main App ------------------------

class HRTTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HRT Tracker")
        self.settings = load_settings()

        try:
            self.apply_theme(
                self.settings.get("appearance", "System"),
                self.settings.get("color_theme", "blue")
            )
        except Exception:
            pass

        try:
            self.geometry(self.settings.get("window_size", "1400x800"))
        except Exception:
            self.geometry("1400x800")

        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="HRT Toolkit", font=("Arial", 20)).pack(pady=20)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(side="right", fill="both", expand=True)

        self.container = ctk.CTkFrame(main_frame)
        self.container.pack(side="top", fill="both", expand=True)

        self.status_var = ctk.StringVar(value="")
        status_bar = ctk.CTkLabel(main_frame, textvariable=self.status_var, anchor="w")
        status_bar.pack(side="bottom", fill="x")

        self.pages = {}

        self.add_page("HRT Log", HRTLogPage)
        self.add_page("History", HistoryPage)
        self.add_page("Resources", ResourcesPage)
        self.add_page("Settings", SettingsPage)
        self.add_page("Help", HelpPage)

        self.show_page("HRT Log")

    def add_page(self, name, page_class):
        page = page_class(self.container, self)
        page.place(relwidth=1, relheight=1)
        self.pages[name] = page

        btn = ctk.CTkButton(self.sidebar, text=name, command=lambda n=name: self.show_page(n))
        btn.pack(pady=5, fill="x")

    def show_page(self, name):
        self.pages[name].show()
        try:
            self.show_status(f"Viewing {name}")
        except Exception:
            pass

    def refresh_all_pages(self):
        for page in self.pages.values():
            try:
                if hasattr(page, "refresh_language"):
                    page.refresh_language()
            except Exception:
                pass

    def apply_theme(self, appearance=None, color_theme=None):
        try:
            if appearance:
                try:
                    ctk.set_appearance_mode(appearance)
                except Exception:
                    pass
            if color_theme:
                try:
                    ctk.set_default_color_theme(color_theme)
                except Exception:
                    pass
        except Exception:
            pass

        def _refresh(widget):
            try:
                widget.update_idletasks()
            except Exception:
                pass
            for child in widget.winfo_children():
                _refresh(child)

        try:
            _refresh(self)
        except Exception:
            pass
        try:
            for page in self.pages.values():
                try:
                    _refresh(page)
                except Exception:
                    pass
        except Exception:
            pass

    def reload_settings(self):
        try:
            self.settings = load_settings()
        except Exception:
            return

        try:
            self.apply_theme(
                self.settings.get("appearance", "System"),
                self.settings.get("color_theme", "blue")
            )
        except Exception:
            pass

        try:
            self.geometry(self.settings.get("window_size", "1400x800"))
        except Exception:
            pass

        try:
            for page in self.pages.values():
                page.controller.settings = self.settings
        except Exception:
            pass

        try:
            self.refresh_all_pages()
        except Exception:
            pass

    def show_status(self, text, duration_ms=3000):
        try:
            self.status_var.set(text)
        except Exception:
            return

        def clear():
            try:
                if self.status_var.get() == text:
                    self.status_var.set("")
            except Exception:
                pass

        try:
            self.after_cancel(getattr(self, "_status_after_id", None))
        except Exception:
            pass
        try:
            self._status_after_id = self.after(duration_ms, clear)
        except Exception:
            pass


if __name__ == "__main__":
    app = HRTTrackerApp()
    app.mainloop()