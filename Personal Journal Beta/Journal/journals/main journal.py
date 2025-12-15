import customtkinter as ctk
import json
import os
from datetime import datetime
from tkinter import filedialog

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

DATA_FOLDER = "journals"
os.makedirs(DATA_FOLDER, exist_ok=True)


# ---------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------
def get_journal_path(name):
    return os.path.join(DATA_FOLDER, f"{name}.json")


def load_entries(journal_name):
    path = get_journal_path(journal_name)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_entries(journal_name, entries):
    path = get_journal_path(journal_name)
    with open(path, "w") as f:
        json.dump(entries, f, indent=4)


# ---------------------------------------------------------
# Base Page Class
# ---------------------------------------------------------
class BasePage(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

    def show(self):
        self.lift()


# ---------------------------------------------------------
# Page: New Entry
# ---------------------------------------------------------
class NewEntryPage(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        ctk.CTkLabel(self, text="New Journal Entry", font=("Arial", 24)).pack(pady=20)

        self.title_entry = ctk.CTkEntry(self, placeholder_text="Entry Title")
        self.title_entry.pack(pady=10, fill="x", padx=40)

        # Mood dropdown
        self.mood_var = ctk.StringVar(value="Neutral")
        ctk.CTkLabel(self, text="Mood").pack()
        ctk.CTkOptionMenu(self, variable=self.mood_var,
                          values=["Happy", "Neutral", "Sad", "Anxious", "Tired", "Excited"]).pack(pady=5)

        # Tags
        self.tags_entry = ctk.CTkEntry(self, placeholder_text="Tags (comma separated)")
        self.tags_entry.pack(pady=10, fill="x", padx=40)

        # Textbox
        self.textbox = ctk.CTkTextbox(self, width=700, height=400)
        self.textbox.pack(pady=10)

        save_btn = ctk.CTkButton(self, text="Save Entry", command=self.save_entry)
        save_btn.pack(pady=20)

    def save_entry(self):
        title = self.title_entry.get().strip()
        content = self.textbox.get("1.0", "end").strip()
        mood = self.mood_var.get()
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]

        if not title or not content:
            return

        entry = {
            "title": title,
            "content": content,
            "mood": mood,
            "tags": tags,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        entries = load_entries(self.controller.current_journal)
        entries.append(entry)
        save_entries(self.controller.current_journal, entries)

        self.title_entry.delete(0, "end")
        self.tags_entry.delete(0, "end")
        self.textbox.delete("1.0", "end")


# ---------------------------------------------------------
# Page: View & Search Entries
# ---------------------------------------------------------
class ViewEntriesPage(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        ctk.CTkLabel(self, text="Your Journal Entries", font=("Arial", 24)).pack(pady=20)

        # Search bar
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search by keyword, tag, or mood")
        self.search_entry.pack(pady=5, fill="x", padx=40)

        ctk.CTkButton(self, text="Search", command=self.refresh_entries).pack(pady=5)

        # List of entries
        self.entry_list = ctk.CTkScrollableFrame(self, width=250, height=500)
        self.entry_list.pack(side="left", padx=20, pady=10)

        # Display area
        self.display = ctk.CTkTextbox(self, width=500, height=500)
        self.display.pack(side="right", padx=20, pady=10)

        self.refresh_entries()

    def refresh_entries(self):
        for widget in self.entry_list.winfo_children():
            widget.destroy()

        query = self.search_entry.get().lower().strip()
        entries = load_entries(self.controller.current_journal)

        for idx, entry in enumerate(entries):
            if query:
                if query not in entry["title"].lower() and \
                   query not in entry["content"].lower() and \
                   query not in entry["mood"].lower() and \
                   not any(query in tag.lower() for tag in entry["tags"]):
                    continue

            btn = ctk.CTkButton(
                self.entry_list,
                text=f"{entry['timestamp']} - {entry['title']}",
                command=lambda i=idx: self.show_entry(i),
                width=200
            )
            btn.pack(pady=5)

    def show_entry(self, index):
        entries = load_entries(self.controller.current_journal)
        entry = entries[index]

        self.display.delete("1.0", "end")
        self.display.insert("end", f"Title: {entry['title']}\n")
        self.display.insert("end", f"Date: {entry['timestamp']}\n")
        self.display.insert("end", f"Mood: {entry['mood']}\n")
        self.display.insert("end", f"Tags: {', '.join(entry['tags'])}\n\n")
        self.display.insert("end", entry["content"])


# ---------------------------------------------------------
# Page: Statistics Dashboard
# ---------------------------------------------------------
class StatsPage(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        ctk.CTkLabel(self, text="Journal Statistics", font=("Arial", 24)).pack(pady=20)

        self.stats_box = ctk.CTkTextbox(self, width=700, height=500)
        self.stats_box.pack(pady=20)

        self.refresh_stats()

    def refresh_stats(self):
        entries = load_entries(self.controller.current_journal)

        mood_count = {}
        tag_count = {}
        total_words = 0

        for e in entries:
            mood_count[e["mood"]] = mood_count.get(e["mood"], 0) + 1
            for t in e["tags"]:
                tag_count[t] = tag_count.get(t, 0) + 1
            total_words += len(e["content"].split())

        self.stats_box.delete("1.0", "end")
        self.stats_box.insert("end", f"Total Entries: {len(entries)}\n")
        self.stats_box.insert("end", f"Total Words Written: {total_words}\n\n")

        self.stats_box.insert("end", "Mood Frequency:\n")
        for mood, count in mood_count.items():
            self.stats_box.insert("end", f"  {mood}: {count}\n")

        self.stats_box.insert("end", "\nTag Frequency:\n")
        for tag, count in tag_count.items():
            self.stats_box.insert("end", f"  {tag}: {count}\n")


# ---------------------------------------------------------
# Page: Journal Manager (Multi‑Journal Support)
# ---------------------------------------------------------
class JournalManagerPage(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        ctk.CTkLabel(self, text="Manage Journals", font=("Arial", 24)).pack(pady=20)

        self.new_journal_entry = ctk.CTkEntry(self, placeholder_text="New Journal Name")
        self.new_journal_entry.pack(pady=10)

        ctk.CTkButton(self, text="Create Journal", command=self.create_journal).pack(pady=5)

        self.journal_list = ctk.CTkScrollableFrame(self, width=300, height=400)
        self.journal_list.pack(pady=20)

        self.refresh_list()

    def refresh_list(self):
        for widget in self.journal_list.winfo_children():
            widget.destroy()

        for file in os.listdir(DATA_FOLDER):
            if file.endswith(".json"):
                name = file[:-5]
                btn = ctk.CTkButton(
                    self.journal_list,
                    text=name,
                    command=lambda n=name: self.switch_journal(n)
                )
                btn.pack(pady=5)

    def create_journal(self):
        name = self.new_journal_entry.get().strip()
        if not name:
            return

        save_entries(name, [])
        self.new_journal_entry.delete(0, "end")
        self.refresh_list()

    def switch_journal(self, name):
        self.controller.current_journal = name
        self.controller.refresh_all_pages()


# ---------------------------------------------------------
# Main App
# ---------------------------------------------------------
class JournalApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Advanced Journal / Diary App")
        self.geometry("1100x700")

        self.current_journal = "default"
        save_entries("default", load_entries("default"))

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="Journal Menu", font=("Arial", 20)).pack(pady=20)

        # Container
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="right", fill="both", expand=True)

        self.pages = {}

        # Register pages
        self.add_page("New Entry", NewEntryPage)
        self.add_page("View Entries", ViewEntriesPage)
        self.add_page("Statistics", StatsPage)
        self.add_page("Manage Journals", JournalManagerPage)

        self.show_page("New Entry")

    def add_page(self, name, page_class):
        page = page_class(self.container, self)
        page.place(relwidth=1, relheight=1)
        self.pages[name] = page

        btn = ctk.CTkButton(self.sidebar, text=name, command=lambda n=name: self.show_page(n))
        btn.pack(pady=5, fill="x")

    def show_page(self, name):
        self.pages[name].show()

    def refresh_all_pages(self):
        for page in self.pages.values():
            if hasattr(page, "refresh_entries"):
                page.refresh_entries()
            if hasattr(page, "refresh_stats"):
                page.refresh_stats()


if __name__ == "__main__":
    app = JournalApp()
    app.mainloop()