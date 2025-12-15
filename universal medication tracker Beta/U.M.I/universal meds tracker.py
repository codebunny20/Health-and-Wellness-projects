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
# Main App
# ---------------------------------------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Health Toolkit")
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