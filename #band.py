#band
import tkinter as tk
from tkinter import messagebox, filedialog
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class BandMember:
    def __init__(self, name, height, waist, seat, in_use=False):
        self.name = name
        self.height = float(height)
        self.waist = float(waist)
        self.seat = float(seat)
        self.in_use = in_use

    def __str__(self):
        status = " (In Use)" if self.in_use else ""
        return f"{self.name}{status} - Height: {self.height}, Waist: {self.waist}, Seat: {self.seat}"

class UniformApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Marching Band Uniform Manager")
        self.members = []
        self.last_match = []

        # New variable for checkbox
        self.hide_checked_out = tk.BooleanVar(value=False)

        # Input fields
        tk.Label(root, text="Name").grid(row=0, column=0)
        tk.Label(root, text="Height").grid(row=0, column=1)
        tk.Label(root, text="Waist").grid(row=0, column=2)
        tk.Label(root, text="Seat").grid(row=0, column=3)

        self.name_entry = tk.Entry(root)
        self.height_entry = tk.Entry(root)
        self.waist_entry = tk.Entry(root)
        self.seat_entry = tk.Entry(root)

        self.name_entry.grid(row=1, column=0)
        self.height_entry.grid(row=1, column=1)
        self.waist_entry.grid(row=1, column=2)
        self.seat_entry.grid(row=1, column=3)

        tk.Button(root, text="Add Member", command=self.add_member).grid(row=1, column=4)

        # Sort and help buttons
        tk.Button(root, text="Sort by Height", command=lambda: self.sort_members("height")).grid(row=2, column=0)
        tk.Button(root, text="Sort by Waist", command=lambda: self.sort_members("waist")).grid(row=2, column=1)
        tk.Button(root, text="Sort by Seat", command=lambda: self.sort_members("seat")).grid(row=2, column=2)
        tk.Button(root, text="Help / Guide", command=self.show_help).grid(row=2, column=4)

        # Search fields
        tk.Label(root, text="Search Height / Waist / Seat").grid(row=3, column=0, columnspan=3)
        self.search_height = tk.Entry(root, width=10)
        self.search_waist = tk.Entry(root, width=10)
        self.search_seat = tk.Entry(root, width=10)
        self.search_height.grid(row=4, column=0)
        self.search_waist.grid(row=4, column=1)
        self.search_seat.grid(row=4, column=2)

        # Min/max filters
        self.min_height = tk.Entry(root, width=10)
        self.max_height = tk.Entry(root, width=10)
        self.min_waist = tk.Entry(root, width=10)
        self.max_waist = tk.Entry(root, width=10)
        self.min_seat = tk.Entry(root, width=10)
        self.max_seat = tk.Entry(root, width=10)

        tk.Label(root, text="Min Height").grid(row=5, column=0)
        tk.Label(root, text="Max Height").grid(row=5, column=1)
        self.min_height.grid(row=6, column=0)
        self.max_height.grid(row=6, column=1)

        tk.Label(root, text="Min Waist").grid(row=5, column=2)
        tk.Label(root, text="Max Waist").grid(row=5, column=3)
        self.min_waist.grid(row=6, column=2)
        self.max_waist.grid(row=6, column=3)

        tk.Label(root, text="Min Seat").grid(row=5, column=4)
        tk.Label(root, text="Max Seat").grid(row=5, column=5)
        self.min_seat.grid(row=6, column=4)
        self.max_seat.grid(row=6, column=5)

        # Match + count
        tk.Button(root, text="Find Match", command=self.find_match).grid(row=7, column=0)
        tk.Label(root, text="Matches to Show").grid(row=7, column=1)
        self.match_count = tk.StringVar(root)
        self.match_count.set("7")
        tk.OptionMenu(root, self.match_count, "1", "3", "5", "7", "10").grid(row=7, column=2)

        # New Hide Checked Out checkbox
        tk.Checkbutton(root, text="Hide Checked Out", variable=self.hide_checked_out).grid(row=7, column=3)

        # Results list
        self.result_list = tk.Listbox(root, width=100)
        self.result_list.grid(row=8, column=0, columnspan=6, pady=10)

        # File + export buttons
        tk.Button(root, text="Save to CSV", command=self.save_to_csv).grid(row=9, column=0)
        tk.Button(root, text="Load from CSV", command=self.load_from_csv).grid(row=9, column=1)
        tk.Button(root, text="Export Match (Text)", command=self.export_match_txt).grid(row=9, column=2)
        tk.Button(root, text="Export Match (PDF)", command=self.export_match_pdf).grid(row=9, column=3)

        # Check Out / Return button
        tk.Button(root, text="Check Out / Return", command=self.toggle_checked_out).grid(row=9, column=4)
    def add_member(self):
        try:
            name = self.name_entry.get()
            height = float(self.height_entry.get())
            waist = float(self.waist_entry.get())
            seat = float(self.seat_entry.get())
            self.members.append(BandMember(name, height, waist, seat))
            self.clear_entries()
            self.display_members()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers.")

    def clear_entries(self):
        for entry in [self.name_entry, self.height_entry, self.waist_entry, self.seat_entry]:
            entry.delete(0, tk.END)

    def display_members(self):
        self.result_list.delete(0, tk.END)
        for member in self.members:
            self.result_list.insert(tk.END, str(member))

    def sort_members(self, key):
        self.members.sort(key=lambda m: getattr(m, key))
        self.display_members()

    def find_match(self):
        try:
            h = float(self.search_height.get())
            w = float(self.search_waist.get())
            s = float(self.search_seat.get())
            count = int(self.match_count.get())
            hide_in_use = self.hide_checked_out.get()

            def within_range(m):
                checks = [
                    (self.min_height.get(), lambda v: m.height >= float(v)),
                    (self.max_height.get(), lambda v: m.height <= float(v)),
                    (self.min_waist.get(), lambda v: m.waist >= float(v)),
                    (self.max_waist.get(), lambda v: m.waist <= float(v)),
                    (self.min_seat.get(), lambda v: m.seat >= float(v)),
                    (self.max_seat.get(), lambda v: m.seat <= float(v)),
                ]
                for val, cond in checks:
                    if val != "":
                        try:
                            if not cond(val):
                                return False
                        except ValueError:
                            return False
                return True

            filtered = [m for m in self.members if within_range(m) and (not hide_in_use or not m.in_use)]

            if not filtered:
                filtered = self.members[:] if not hide_in_use else []

            def closeness(m):
                return abs(m.height - h) + abs(m.waist - w) + abs(m.seat - s)

            sorted_members = sorted(filtered, key=closeness)
            top_matches = sorted_members[:count]
            self.last_match = top_matches

            self.result_list.delete(0, tk.END)
            self.result_list.insert(tk.END, f"Top {count} Closest Matches:")

            for idx, match in enumerate(top_matches):
                score = closeness(match)
                display_text = str(match)
                self.result_list.insert(tk.END, display_text)

                if match.in_use:
                    color = "#dddddd"  # gray
                elif score <= 2:
                    color = "#c8facc"  # green
                elif score <= 5:
                    color = "#fff6aa"  # yellow
                else:
                    color = "#ffcccc"  # red

                self.result_list.itemconfig(idx + 1, bg=color)

        except ValueError:
            messagebox.showerror("Invalid Input", "Enter valid numbers in the search fields.")

    def toggle_checked_out(self):
        selected = self.result_list.curselection()
        if not selected or selected[0] == 0:
            messagebox.showwarning("Select Uniform", "Select a uniform to check out/return.")
            return
        index = selected[0] - 1
        if 0 <= index < len(self.last_match):
            member = self.last_match[index]
            member.in_use = not member.in_use
            self.find_match()

    def save_to_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Height", "Waist", "Seat", "InUse"])
            for m in self.members:
                writer.writerow([m.name, m.height, m.waist, m.seat, int(m.in_use)])
        messagebox.showinfo("Saved", "CSV file saved.")

    def load_from_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        try:
            with open(path, "r") as f:
                reader = csv.DictReader(f)
                self.members.clear()
                for row in reader:
                    self.members.append(BandMember(
                        row["Name"],
                        row["Height"],
                        row["Waist"],
                        row["Seat"],
                        row.get("InUse", "0") == "1"
                    ))
            self.display_members()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

    def export_match_txt(self):
        if not self.last_match:
            messagebox.showwarning("No Matches", "Run a search first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return
        with open(path, "w") as f:
            f.write("Filtered Match Results:\n")
            for m in self.last_match:
                f.write(str(m) + "\n")
        messagebox.showinfo("Exported", "Text file created.")

    def export_match_pdf(self):
        if not self.last_match:
            messagebox.showwarning("No Matches", "Run a search first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not path:
            return
        c = canvas.Canvas(path, pagesize=letter)
        text = c.beginText(50, 750)
        text.setFont("Helvetica", 12)
        text.textLine("Filtered Match Results:")
        text.textLine("")
        for m in self.last_match:
            text.textLine(str(m))
        c.drawText(text)
        c.save()
        messagebox.showinfo("Exported", "PDF file created.")

    def show_help(self):
        guide = (
            "📘 Marching Band Uniform Manager - User Guide\n\n"
            "➕ Add Uniform: Fill in name, height, waist, seat → 'Add Member'.\n\n"
            "🔍 Find Matches: Enter desired size → 'Find Match'.\n"
            "✔️ Results are color-coded:\n"
            "• Green = best fit\n• Yellow = medium fit\n• Red = loose fit\n"
            "• Gray = uniform is in use\n\n"
            "📤 Export / Save: Use the buttons to save/load/export your data.\n\n"
            "🔒 'Check Out / Return': Select a result and click this button to mark a uniform as in use or returned.\n"
            "👁️ 'Hide Checked Out': Hide unavailable uniforms from match results."
        )
        messagebox.showinfo("Help / User Guide", guide)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = UniformApp(root)
    root.mainloop()
