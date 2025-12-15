import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# ---------------------------------------------------------
# Base Page Class (All pages inherit from this)
# ---------------------------------------------------------
class BasePage(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

    def show(self):
        self.lift()


# ---------------------------------------------------------
# Medication Tracker Page
# ---------------------------------------------------------
class MedicationTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        ctk.CTkLabel(self, text="Medication Tracker", font=("Arial", 24)).pack(pady=20)

        self.med_entry = ctk.CTkEntry(self, placeholder_text="Medication Name")
        self.med_entry.pack(pady=5)

        self.dose_entry = ctk.CTkEntry(self, placeholder_text="Dosage")
        self.dose_entry.pack(pady=5)

        self.time_entry = ctk.CTkEntry(self, placeholder_text="Time Taken")
        self.time_entry.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_med)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=400, height=200)
        self.output.pack(pady=10)

    def add_med(self):
        med = self.med_entry.get()
        dose = self.dose_entry.get()
        time = self.time_entry.get()

        if med and dose and time:
            self.output.insert("end", f"{med} - {dose} at {time}\n")
            self.med_entry.delete(0, "end")
            self.dose_entry.delete(0, "end")
            self.time_entry.delete(0, "end")


# ---------------------------------------------------------
# Sleep Tracker Page
# ---------------------------------------------------------
class SleepTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        ctk.CTkLabel(self, text="Sleep Tracker", font=("Arial", 24)).pack(pady=20)

        self.bed_entry = ctk.CTkEntry(self, placeholder_text="Bedtime (e.g., 10:30 PM)")
        self.bed_entry.pack(pady=5)

        self.wake_entry = ctk.CTkEntry(self, placeholder_text="Wake Time (e.g., 6:45 AM)")
        self.wake_entry.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_sleep)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=400, height=200)
        self.output.pack(pady=10)

    def add_sleep(self):
        bed = self.bed_entry.get()
        wake = self.wake_entry.get()

        if bed and wake:
            self.output.insert("end", f"Bed: {bed} | Wake: {wake}\n")
            self.bed_entry.delete(0, "end")
            self.wake_entry.delete(0, "end")


# ---------------------------------------------------------
# Meal / Calorie Tracker Page
# ---------------------------------------------------------
class MealTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        ctk.CTkLabel(self, text="Meal & Calorie Tracker", font=("Arial", 24)).pack(pady=20)

        self.meal_entry = ctk.CTkEntry(self, placeholder_text="Meal Name")
        self.meal_entry.pack(pady=5)

        self.cal_entry = ctk.CTkEntry(self, placeholder_text="Calories")
        self.cal_entry.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_meal)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=400, height=200)
        self.output.pack(pady=10)

    def add_meal(self):
        meal = self.meal_entry.get()
        cal = self.cal_entry.get()

        if meal and cal:
            self.output.insert("end", f"{meal} - {cal} calories\n")
            self.meal_entry.delete(0, "end")
            self.cal_entry.delete(0, "end")


# ---------------------------------------------------------
# New pages: Mood, Hydration, Symptom, Period, Exercise,
# Habit, Journal, Pain Scale, Vitals
# ---------------------------------------------------------
class MoodTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(self, text="Mood Tracker", font=("Arial", 24)).pack(pady=20)

        self.mood_menu = ctk.CTkOptionMenu(self, values=["Happy", "Sad", "Anxious", "Neutral", "Angry", "Excited"])
        self.mood_menu.pack(pady=5)

        self.notes = ctk.CTkTextbox(self, width=400, height=100)
        self.notes.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_mood)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=400, height=150)
        self.output.pack(pady=10)

    def add_mood(self):
        mood = self.mood_menu.get()
        note = self.notes.get("0.0", "end").strip()
        if mood:
            line = f"Mood: {mood}"
            if note:
                line += f" | Notes: {note}"
            self.output.insert("end", line + "\n")
            self.notes.delete("0.0", "end")


class HydrationTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(self, text="Hydration Tracker", font=("Arial", 24)).pack(pady=20)

        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Amount (ml or glasses)")
        self.amount_entry.pack(pady=5)

        self.time_entry = ctk.CTkEntry(self, placeholder_text="Time (optional)")
        self.time_entry.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_hydration)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=400, height=200)
        self.output.pack(pady=10)

    def add_hydration(self):
        amt = self.amount_entry.get()
        tm = self.time_entry.get()
        if amt:
            line = f"{amt}"
            if tm:
                line += f" at {tm}"
            self.output.insert("end", line + "\n")
            self.amount_entry.delete(0, "end")
            self.time_entry.delete(0, "end")


class SymptomTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(self, text="Symptom Tracker", font=("Arial", 24)).pack(pady=20)

        self.symptom_entry = ctk.CTkEntry(self, placeholder_text="Symptom")
        self.symptom_entry.pack(pady=5)

        self.severity_menu = ctk.CTkOptionMenu(self, values=["Mild", "Moderate", "Severe"])
        self.severity_menu.pack(pady=5)

        self.sym_notes = ctk.CTkTextbox(self, width=400, height=100)
        self.sym_notes.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_symptom)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=400, height=150)
        self.output.pack(pady=10)

    def add_symptom(self):
        sym = self.symptom_entry.get()
        sev = self.severity_menu.get()
        note = self.sym_notes.get("0.0", "end").strip()
        if sym:
            line = f"{sym} - {sev}"
            if note:
                line += f" | Notes: {note}"
            self.output.insert("end", line + "\n")
            self.symptom_entry.delete(0, "end")
            self.sym_notes.delete("0.0", "end")


class PeriodTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(self, text="Period Tracker", font=("Arial", 24)).pack(pady=20)

        self.start_entry = ctk.CTkEntry(self, placeholder_text="Start Date (e.g., 2025-05-01)")
        self.start_entry.pack(pady=5)

        self.end_entry = ctk.CTkEntry(self, placeholder_text="End Date (optional)")
        self.end_entry.pack(pady=5)

        self.flow_menu = ctk.CTkOptionMenu(self, values=["Light", "Medium", "Heavy"])
        self.flow_menu.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_period)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=400, height=200)
        self.output.pack(pady=10)

    def add_period(self):
        start = self.start_entry.get()
        end = self.end_entry.get()
        flow = self.flow_menu.get()
        if start:
            line = f"Start: {start}"
            if end:
                line += f" | End: {end}"
            line += f" | Flow: {flow}"
            self.output.insert("end", line + "\n")
            self.start_entry.delete(0, "end")
            self.end_entry.delete(0, "end")


class ExerciseTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(self, text="Exercise Tracker", font=("Arial", 24)).pack(pady=20)

        self.type_entry = ctk.CTkEntry(self, placeholder_text="Exercise Type (e.g., Walk)")
        self.type_entry.pack(pady=5)

        self.duration_entry = ctk.CTkEntry(self, placeholder_text="Duration (minutes)")
        self.duration_entry.pack(pady=5)

        self.cal_entry = ctk.CTkEntry(self, placeholder_text="Estimated Calories")
        self.cal_entry.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_exercise)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=400, height=200)
        self.output.pack(pady=10)

    def add_exercise(self):
        typ = self.type_entry.get()
        dur = self.duration_entry.get()
        cal = self.cal_entry.get()
        if typ and (dur or cal):
            line = f"{typ}"
            if dur:
                line += f" - {dur} min"
            if cal:
                line += f" - {cal} kcal"
            self.output.insert("end", line + "\n")
            self.type_entry.delete(0, "end")
            self.duration_entry.delete(0, "end")
            self.cal_entry.delete(0, "end")


class HabitTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(self, text="Habit Tracker", font=("Arial", 24)).pack(pady=20)

        self.habit_entry = ctk.CTkEntry(self, placeholder_text="Habit Name")
        self.habit_entry.pack(pady=5)

        self.status_menu = ctk.CTkOptionMenu(self, values=["Done", "Missed", "Skipped"])
        self.status_menu.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_habit)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=400, height=200)
        self.output.pack(pady=10)

    def add_habit(self):
        habit = self.habit_entry.get()
        status = self.status_menu.get()
        if habit:
            self.output.insert("end", f"{habit} - {status}\n")
            self.habit_entry.delete(0, "end")


class JournalPage(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(self, text="Journal / Notes", font=("Arial", 24)).pack(pady=20)

        self.title_entry = ctk.CTkEntry(self, placeholder_text="Title (optional)")
        self.title_entry.pack(pady=5, fill="x", padx=20)

        self.journal_text = ctk.CTkTextbox(self, width=600, height=250)
        self.journal_text.pack(pady=5, padx=20)

        self.save_button = ctk.CTkButton(self, text="Save Note", command=self.save_note)
        self.save_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=600, height=150)
        self.output.pack(pady=10)

    def save_note(self):
        title = self.title_entry.get()
        note = self.journal_text.get("0.0", "end").strip()
        if note:
            header = f"{title} - " if title else ""
            self.output.insert("end", f"{header}{note}\n---\n")
            self.title_entry.delete(0, "end")
            self.journal_text.delete("0.0", "end")


class PainScaleTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(self, text="Pain Scale Tracker", font=("Arial", 24)).pack(pady=20)

        self.pain_slider = ctk.CTkSlider(self, from_=0, to=10)
        self.pain_slider.set(0)
        self.pain_slider.pack(pady=5, fill="x", padx=60)

        self.pain_notes = ctk.CTkEntry(self, placeholder_text="Notes")
        self.pain_notes.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_pain)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=400, height=150)
        self.output.pack(pady=10)

    def add_pain(self):
        val = int(round(self.pain_slider.get()))
        note = self.pain_notes.get()
        line = f"Pain: {val}/10"
        if note:
            line += f" | {note}"
        self.output.insert("end", line + "\n")
        self.pain_notes.delete(0, "end")


class VitalsTracker(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(self, text="Vitals Tracker", font=("Arial", 24)).pack(pady=20)

        self.bp_entry = ctk.CTkEntry(self, placeholder_text="Blood Pressure (e.g., 120/80)")
        self.bp_entry.pack(pady=5)

        self.hr_entry = ctk.CTkEntry(self, placeholder_text="Heart Rate (bpm)")
        self.hr_entry.pack(pady=5)

        self.temp_entry = ctk.CTkEntry(self, placeholder_text="Temperature (°C/°F)")
        self.temp_entry.pack(pady=5)

        self.resp_entry = ctk.CTkEntry(self, placeholder_text="Respiratory Rate")
        self.resp_entry.pack(pady=5)

        self.spo2_entry = ctk.CTkEntry(self, placeholder_text="SpO2 (%)")
        self.spo2_entry.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Entry", command=self.add_vitals)
        self.add_button.pack(pady=10)

        self.output = ctk.CTkTextbox(self, width=500, height=200)
        self.output.pack(pady=10)

    def add_vitals(self):
        bp = self.bp_entry.get()
        hr = self.hr_entry.get()
        temp = self.temp_entry.get()
        resp = self.resp_entry.get()
        spo2 = self.spo2_entry.get()
        if any([bp, hr, temp, resp, spo2]):
            parts = []
            if bp: parts.append(f"BP: {bp}")
            if hr: parts.append(f"HR: {hr} bpm")
            if temp: parts.append(f"T: {temp}")
            if resp: parts.append(f"RR: {resp}")
            if spo2: parts.append(f"SpO2: {spo2}%")
            self.output.insert("end", " | ".join(parts) + "\n")
            self.bp_entry.delete(0, "end")
            self.hr_entry.delete(0, "end")
            self.temp_entry.delete(0, "end")
            self.resp_entry.delete(0, "end")
            self.spo2_entry.delete(0, "end")


# ---------------------------------------------------------
# Main App
# ---------------------------------------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Care Corner")
        self.geometry("900x600")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="Tools", font=("Arial", 20)).pack(pady=20)

        # Container for pages
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="right", fill="both", expand=True)

        # Dictionary of pages
        self.pages = {}

        # Register pages here
        self.add_page("Medication Tracker", MedicationTracker)
        self.add_page("Sleep Tracker", SleepTracker)
        self.add_page("Meal Tracker", MealTracker)
        # newly added pages
        self.add_page("Mood Tracker", MoodTracker)
        self.add_page("Hydration Tracker", HydrationTracker)
        self.add_page("Symptom Tracker", SymptomTracker)
        self.add_page("Period Tracker", PeriodTracker)
        self.add_page("Exercise Tracker", ExerciseTracker)
        self.add_page("Habit Tracker", HabitTracker)
        self.add_page("Journal / Notes", JournalPage)
        self.add_page("Pain Scale", PainScaleTracker)
        self.add_page("Vitals Tracker", VitalsTracker)

        # Default page
        self.show_page("Medication Tracker")

    # -----------------------------------------------------
    # Add new pages easily
    # -----------------------------------------------------
    def add_page(self, name, page_class):
        page = page_class(self.container, self)
        page.place(relwidth=1, relheight=1)
        self.pages[name] = page

        # Add button to sidebar
        btn = ctk.CTkButton(self.sidebar, text=name, command=lambda n=name: self.show_page(n))
        btn.pack(pady=5, fill="x")

    def show_page(self, name):
        page = self.pages[name]
        page.show()


if __name__ == "__main__":
    app = App()
    app.mainloop()