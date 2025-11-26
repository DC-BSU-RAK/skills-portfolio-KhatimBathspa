# studentmanager.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
import json
from datetime import datetime


try:
    from reportlab.lib.pagesizes import letter  # type: ignore
    from reportlab.pdfgen import canvas as pdfcanvas  # type: ignore
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib  # type: ignore
    matplotlib.use("Agg")  # safe backend for saving, TkAgg used when embedding
    import matplotlib.pyplot as plt  # type: ignore
    from matplotlib.figure import Figure  # type: ignore
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

try:
    from PIL import Image, ImageTk  # type: ignore
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# Paths and constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MARKS_FILE = os.path.join(SCRIPT_DIR, "studentMarks.txt")
EXTRA_FILE = os.path.join(SCRIPT_DIR, "studentExtra.json")
USERS_FILE = os.path.join(SCRIPT_DIR, "users.json")

# LOGO PATHS
LOGO_PATHS = [
    "/mnt/data/2b0e4a23-bd83-42a1-a990-32e82bd6cb9d.png",
    os.path.join(SCRIPT_DIR, "university logo.png"),
    os.path.join(SCRIPT_DIR, "logo.png"),
    "image_395214.png"
]
LOGO_PATH = None
for p in LOGO_PATHS:
    if os.path.exists(p):
        LOGO_PATH = p
        break

OXFORD_BLUE = "#002147"
ACCENT = "#8A1538"
LIGHT_BG = "#f4f6f8"
ROW_EVEN = "#f4f4f4"
ROW_ODD = "#e9ecef"
HIGHEST_BG = "#d4edda"
LOWEST_BG = "#f8d7da"
HEADER_BG = "#dfe6e9"

# HELPER TO SET ICON ON ALL WINDOWS
def set_app_icon(window):
    """Sets the window icon to the university logo if available."""
    if PIL_AVAILABLE and LOGO_PATH and os.path.exists(LOGO_PATH):
        try:
            icon_img = Image.open(LOGO_PATH)
            # Window icons usually need to be small photoimages
            icon_photo = ImageTk.PhotoImage(icon_img)
            window.iconphoto(False, icon_photo)
            # Keep a reference to prevent garbage collection
            window._icon_ref = icon_photo
        except Exception:
            pass

def load_extra():
    if os.path.exists(EXTRA_FILE):
        try:
            with open(EXTRA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_extra(data):
    try:
        with open(EXTRA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        messagebox.showerror("Error", "Failed to save extra student details.")

class LoginWindow:
    """Larger, professional login window (600x400) using Oxford branding and logo."""
    def __init__(self, master, on_success):
        self.master = master
        self.on_success = on_success
        self.win = tk.Toplevel(master)
        self.win.title("Oxford University Student Manager - Login")
        self.win.geometry("600x400")
        self.win.resizable(False, False)
        self.win.configure(bg=OXFORD_BLUE)

        # SET ICON
        set_app_icon(self.win)

        self.win.grab_set()

        # Center content frame with light background
        content = tk.Frame(self.win, bg=LIGHT_BG, padx=18, pady=18)
        content.place(relx=0.5, rely=0.5, anchor="center")

        # Logo + Title row
        top_row = tk.Frame(content, bg=LIGHT_BG)
        top_row.pack(pady=(4,12), fill="x")
        if PIL_AVAILABLE and LOGO_PATH:
            try:
                logo_img = Image.open(LOGO_PATH)
                logo_img = logo_img.resize((88,88), Image.LANCZOS)
                self.login_logo = ImageTk.PhotoImage(logo_img)
                tk.Label(top_row, image=self.login_logo, bg=LIGHT_BG).pack(side="left", padx=(4,12))
            except Exception:
                tk.Label(top_row, text="Oxford", font=("Helvetica", 20, "bold"), bg=LIGHT_BG).pack(side="left", padx=(6,12))
        else:
            tk.Label(top_row, text="Oxford", font=("Helvetica", 20, "bold"), bg=LIGHT_BG).pack(side="left", padx=(6,12))

        title_frame = tk.Frame(top_row, bg=LIGHT_BG)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="Oxford University", font=("Helvetica", 16, "bold"), bg=LIGHT_BG).pack(anchor="w")
        tk.Label(title_frame, text="Student Manager Login", font=("Helvetica", 11), bg=LIGHT_BG).pack(anchor="w")

        # Input fields
        frm = tk.Frame(content, bg=LIGHT_BG)
        frm.pack(pady=6, fill="x")
        tk.Label(frm, text="Username", bg=LIGHT_BG, anchor="w").pack(fill="x", padx=8)
        self.user_ent = tk.Entry(frm, width=36, font=("Arial", 11))
        self.user_ent.pack(padx=8, pady=6)

        tk.Label(frm, text="Password", bg=LIGHT_BG, anchor="w").pack(fill="x", padx=8)
        self.pw_ent = tk.Entry(frm, show="*", width=36, font=("Arial", 11))
        self.pw_ent.pack(padx=8, pady=6)

        # Buttons row
        btn_row = tk.Frame(content, bg=LIGHT_BG)
        btn_row.pack(pady=(10,0))
        tk.Button(btn_row, text="Login", command=self.try_login, bg=ACCENT, fg="white", width=12).pack(side="left", padx=8)
        tk.Button(btn_row, text="Cancel", command=self.win.destroy, width=12).pack(side="left", padx=8)
        tk.Button(btn_row, text="Help", command=self.show_help, width=8).pack(side="left", padx=8)

        # small note
        tk.Label(content, text="Default: admin / oxford123", bg=LIGHT_BG, fg="gray20", font=("Arial",9)).pack(pady=(10,0))

        self.ensure_user_file()

    def ensure_user_file(self):
        if not os.path.exists(USERS_FILE):
            users = {"admin": {"password": "oxford123"}}
            try:
                with open(USERS_FILE, "w") as f:
                    json.dump(users, f)
            except:
                pass

    def try_login(self):
        user = self.user_ent.get().strip()
        pw = self.pw_ent.get()
        if not user or not pw:
            messagebox.showwarning("Missing", "Enter username and password.")
            return
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        except:
            users = {"admin": {"password": "oxford123"}}
        if user in users and users[user].get("password") == pw:
            self.win.destroy()
            self.on_success(user)
        else:
            messagebox.showerror("Failed", "Invalid username or password.")

    def show_help(self):
        messagebox.showinfo("Login Help", "Default admin credentials:\nusername: admin\npassword: oxford123\nYou may change users.json to add users.")

class StudentManager:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        root.title("Oxford University Student Manager")
        root.geometry("1200x860")
        root.configure(bg=LIGHT_BG)

        #  SET ICON FOR MAIN WINDOW
        set_app_icon(root)

        self.students = self.load_data()
        self.extra = load_extra()

        top = tk.Frame(root, bg=OXFORD_BLUE, pady=10)
        top.pack(fill="x")

        left = tk.Frame(top, bg=OXFORD_BLUE)
        left.pack(side="left", padx=12)
        if PIL_AVAILABLE and LOGO_PATH:
            try:
                img = Image.open(LOGO_PATH)
                img = img.resize((80,80), Image.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                tk.Label(left, image=self.logo_img, bg=OXFORD_BLUE).pack()
            except:
                tk.Label(left, text="Oxford", bg=OXFORD_BLUE, fg="white", font=("Helvetica", 18, "bold")).pack()
        else:
            tk.Label(left, text="Oxford", bg=OXFORD_BLUE, fg="white", font=("Helvetica", 18, "bold")).pack()

        tk.Label(top, text="Oxford University Student Manager", bg=OXFORD_BLUE, fg="white", font=("Helvetica", 20, "bold")).pack(side="left", padx=8)
        tk.Label(top, text=f"User: {self.user}", bg=OXFORD_BLUE, fg="white", font=("Arial",10)).pack(side="right", padx=12)

        search_frame = tk.Frame(root, bg=LIGHT_BG, pady=8)
        search_frame.pack(fill="x", padx=12)

        tk.Label(search_frame, text="Search Student:", bg=LIGHT_BG, font=("Arial", 11)).grid(row=0, column=0, sticky="w", padx=4)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=48, font=("Arial", 11))
        self.search_entry.grid(row=0, column=1, padx=6)
        self.search_entry.bind("<KeyRelease>", self.update_suggestions)

        search_btn = tk.Button(search_frame, text="Search", command=self.search_student, bg=ACCENT, fg="white", width=12)
        search_btn.grid(row=0, column=2, padx=6)
        clear_btn = tk.Button(search_frame, text="Clear Search", command=self.clear_search)
        clear_btn.grid(row=0, column=3, padx=6)

        self.listbox = tk.Listbox(search_frame, width=48, height=5)
        self.listbox.grid(row=1, column=1, padx=6, sticky="w")
        self.listbox.bind("<<ListboxSelect>>", self.select_suggestion)
        self.listbox.grid_remove()

        key_frame = tk.Frame(root, bg=LIGHT_BG)
        key_frame.pack(fill="x", padx=12, pady=6)
        tk.Label(key_frame, text="Key:", bg=LIGHT_BG, font=("Arial", 10, "bold")).pack(side="left")
        tk.Label(key_frame, text="Highest Score", bg=HIGHEST_BG, width=16).pack(side="left", padx=6)
        tk.Label(key_frame, text="Lowest Score", bg=LOWEST_BG, width=16).pack(side="left", padx=6)

        button_frame = tk.Frame(root, bg=LIGHT_BG, pady=6)
        button_frame.pack(fill="x", padx=12)

        btn_conf = {"width":16, "bg":OXFORD_BLUE, "fg":"white", "font":("Arial",10,"bold")}
        actions = [
            ("View All Records", self.view_all),
            ("View Individual", self.view_individual),
            ("Highest Score", self.highest),
            ("Lowest Score", self.lowest),
            ("Add Student", self.add_student),
            ("Update Student", self.update_student),
            ("Delete Student", self.delete_student),
            ("Statistics", self.show_stats),
            ("Export to PDF", self.export_pdf)
        ]
        for i,(label,cmd) in enumerate(actions):
            b = tk.Button(button_frame, text=label, command=cmd, **btn_conf)
            b.grid(row=0, column=i, padx=4, pady=4)

        sort_frame = tk.Frame(root, bg=LIGHT_BG)
        sort_frame.pack(fill="x", padx=12, pady=(4,0))
        tk.Label(sort_frame, text="Sort Records:", bg=LIGHT_BG).pack(side="left", padx=6)
        self.sort_choice = ttk.Combobox(sort_frame, values=["Ascending", "Descending"], state="readonly", width=12)
        self.sort_choice.current(0)
        self.sort_choice.pack(side="left")
        tk.Button(sort_frame, text="Sort", command=self.sort_records_from_dropdown, bg=ACCENT, fg="white").pack(side="left", padx=6)

        self.table_frame = tk.Frame(root, bg=LIGHT_BG)
        self.table_frame.pack(padx=12, pady=(8,6), fill="both", expand=True)

        cols = ("code","name","c1","c2","c3","exam","total","perc","grade")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col.title(), anchor="center", command=lambda _c=col: self.sort_by_column(_c))
            self.tree.column(col, anchor="center", width=100 if col!="name" else 260, minwidth=60)
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Arial", 10), rowheight=26, background=ROW_EVEN, fieldbackground=ROW_EVEN)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background=HEADER_BG)
        style.map("Treeview", background=[('selected', '#a6d0ff')])
        style.layout("Treeview", [('Treeview.treearea', {'sticky':'nswe'})])

        self.details_frame = tk.Frame(root, bg=LIGHT_BG, padx=12, pady=8, relief="groove", bd=0)
        self.details_frame.pack(fill="x", padx=12, pady=(2,12))
        self.details_title = tk.Label(self.details_frame, text="Student Details", bg=LIGHT_BG, font=("Arial", 11, "bold"))
        self.details_title.grid(row=0, column=0, sticky="w")
        self.details_widgets = {}
        for i, label in enumerate(["Email","DOB","Course"]):
            tk.Label(self.details_frame, text=label+":", bg=LIGHT_BG, anchor="w").grid(row=1+i, column=0, sticky="w", pady=2)
            val = tk.Label(self.details_frame, text="", bg=LIGHT_BG, anchor="w")
            val.grid(row=1+i, column=1, sticky="w", pady=2)
            self.details_widgets[label.lower()] = val

        self.view_all()
        self._col_sort_reverse = {}

    def load_data(self):
        if not os.path.exists(MARKS_FILE):
            messagebox.showwarning("Missing", f"{MARKS_FILE} not found. Starting with empty dataset.")
            return []
        students = []
        try:
            with open(MARKS_FILE, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            if not lines:
                return []
            # expecting first line = number of students, rest lines = records
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 6:
                    continue
                try:
                    students.append({
                        "code": parts[0],
                        "name": parts[1],
                        "c1": int(parts[2]),
                        "c2": int(parts[3]),
                        "c3": int(parts[4]),
                        "exam": int(parts[5])
                    })
                except:
                    continue
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read marks file: {e}")
        return students

    def save_data(self):
        # write file with count on first line (keeps same format)
        try:
            with open(MARKS_FILE, "w") as f:
                f.write(f"{len(self.students)}\n")
                for s in self.students:
                    f.write(f"{s['code']},{s['name']},{s['c1']},{s['c2']},{s['c3']},{s['exam']}\n")
            # ensure extra file is also saved
            save_extra(self.extra)
        except Exception as e:
            messagebox.showerror("Error", f"Failed saving to file: {e}")

    def clear_table(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

    def calc_total_perc_grade(self, s):
        total_course = s["c1"] + s["c2"] + s["c3"]
        total = total_course + s["exam"]
        perc = (total / 160) * 100
        grade = self.get_grade(perc)
        return total_course, total, perc, grade

    def get_grade(self, perc):
        if perc >= 70: return "A"
        elif perc >= 60: return "B"
        elif perc >= 50: return "C"
        elif perc >= 40: return "D"
        else: return "F"

    def insert_row(self, s, tag=None):
        total_course, total, perc, grade = self.calc_total_perc_grade(s)
        values = (s["code"], s["name"], s["c1"], s["c2"], s["c3"], s["exam"], total, f"{perc:.2f}", grade)
        # ensure iid is string
        self.tree.insert("", "end", values=values, tags=(tag if tag else ""), iid=str(s["code"]))

    def view_all(self):
        self.clear_table()
        if not self.students:
            return
        # Handle case where students list is empty before trying to find min/max
        if not self.students:
            avg = 0
            self.tree.insert("", "end", values=("", "Summary", "", "", "", "", "", f"Average: {avg:.2f}%", f"Students: {len(self.students)}"), tags=("summary",))
            return

        top_student = max(self.students, key=lambda x: x["c1"]+x["c2"]+x["c3"]+x["exam"])
        low_student = min(self.students, key=lambda x: x["c1"]+x["c2"]+x["c3"]+x["exam"])
        total_perc = 0
        for i, s in enumerate(self.students):
            total_course, total, perc, grade = self.calc_total_perc_grade(s)
            total_perc += perc
            if s == top_student:
                tag = "top"
            elif s == low_student:
                tag = "low"
            else:
                tag = "even" if i%2==0 else "odd"
            self.insert_row(s, tag)
        self.tree.tag_configure("even", background=ROW_EVEN)
        self.tree.tag_configure("odd", background=ROW_ODD)
        self.tree.tag_configure("top", background=HIGHEST_BG)
        self.tree.tag_configure("low", background=LOWEST_BG)
        avg = total_perc / len(self.students)
        # show a blank line and summary at end
        self.tree.insert("", "end", values=("", "", "", "", "", "", "", "", ""))
        self.tree.insert("", "end", values=("", "Summary", "", "", "", "", "", f"Average: {avg:.2f}%", f"Students: {len(self.students)}"), tags=("summary",))
        self.tree.tag_configure("summary", background=HEADER_BG, font=("Arial",10,"bold"))
        for k in self.details_widgets:
            self.details_widgets[k].config(text="")

    def display_single(self, s):
        # show just this student's row in table and populate details pane
        self.clear_table()
        self.insert_row(s)
        # Ensure tags are configured even for single row view
        self.tree.tag_configure("even", background=ROW_EVEN)
        self.tree.tag_configure("odd", background=ROW_ODD)
        self.tree.tag_configure("top", background=HIGHEST_BG)
        self.tree.tag_configure("low", background=LOWEST_BG)
        extras = self.extra.get(s["code"], {})
        self.details_widgets["email"].config(text=extras.get("email",""))
        self.details_widgets["dob"].config(text=extras.get("dob",""))
        self.details_widgets["course"].config(text=extras.get("course",""))

    def view_individual(self):
        if not self.students:
            messagebox.showerror("Error", "No students loaded.")
            return
        top = tk.Toplevel(self.root)
        top.title("View Individual Student")
        # Increased height to accommodate the listbox and button better
        top.geometry("520x340")
        top.configure(bg=LIGHT_BG)

        # --- SET ICON ---
        set_app_icon(top)

        # include logo on this popup too
        header = tk.Frame(top, bg=LIGHT_BG)
        header.pack(fill="x", pady=6)
        if PIL_AVAILABLE and LOGO_PATH:
            try:
                img = Image.open(LOGO_PATH)
                img = img.resize((60,60), Image.LANCZOS)
                logo = ImageTk.PhotoImage(img)
                tk.Label(header, image=logo, bg=LIGHT_BG).pack(side="left", padx=8)
                # keep reference
                top.logo = logo
            except:
                pass
        tk.Label(header, text="Search and Select Student:", bg=LIGHT_BG, font=("Arial",11,"bold")).pack(side="left", padx=6)

        # Search Bar and Listbox for selection
        search_frame = tk.Frame(top, bg=LIGHT_BG)
        search_frame.pack(pady=12, padx=12, fill="x")

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=50, font=("Arial", 11))
        search_entry.pack(side="top", pady=4, fill="x")

        listbox = tk.Listbox(search_frame, width=50, height=8) # Increased height
        listbox.pack(pady=4, fill="x")

        def update_listbox(event=None):
            typed = search_var.get().strip().lower()
            listbox.delete(0, tk.END)
            if not typed:
                # Show all students if search is empty
                matches = [f"{s['code']} - {s['name']}" for s in self.students]
            else:
                matches = [f"{s['code']} - {s['name']}" for s in self.students if typed in s['name'].lower() or typed in s['code'].lower()]

            for m in matches:
                listbox.insert(tk.END, m)

            if matches:
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(0) # Select the first result
                listbox.see(0) # Ensure the first item is visible

        search_entry.bind("<KeyRelease>", update_listbox)
        update_listbox() # Populate initially

        def select_student(event=None):
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Selection Missing", "Please select a student from the list.")
                return

            selected_text = listbox.get(selection[0])
            code_name_parts = selected_text.split(" - ", 1)
            if len(code_name_parts) < 2:
                messagebox.showerror("Error", "Invalid student format selected.")
                return

            student_code = code_name_parts[0].strip()

            # Find the student dictionary using the code
            selected_student = next((s for s in self.students if s["code"] == student_code), None)

            if selected_student:
                self.display_single(selected_student)
                top.destroy()
            else:
                messagebox.showerror("Error", "Could not find student data.")

        # Bind Enter key to select the highlighted student
        search_entry.bind("<Return>", select_student)
        listbox.bind("<Double-Button-1>", select_student)

        # This button is now clearly visible due to increased window size
        tk.Button(top, text="View Selected", command=select_student, bg=ACCENT, fg="white", width=18).pack(pady=8)


    def highest(self):
        if not self.students:
            messagebox.showerror("Error", "No students loaded.")
            return
        stu = max(self.students, key=lambda s: s["c1"]+s["c2"]+s["c3"]+s["exam"])
        self.display_single(stu)

    def lowest(self):
        if not self.students:
            messagebox.showerror("Error", "No students loaded.")
            return
        stu = min(self.students, key=lambda s: s["c1"]+s["c2"]+s["c3"]+s["exam"])
        self.display_single(stu)

    def update_suggestions(self, event):
        typed = self.search_var.get().strip().lower()
        # show inline suggestions (like Google) in the listbox under the input
        self.listbox.delete(0, tk.END)
        if not typed:
            self.listbox.grid_remove()
            return
        matches = [f"{s['code']} - {s['name']}" for s in self.students if typed in s['name'].lower() or typed in s['code'].lower()]
        for m in matches[:20]:
            self.listbox.insert(tk.END, m)
        if matches:
            self.listbox.grid()
        else:
            self.listbox.grid_remove()

    def select_suggestion(self, event):
        if not self.listbox.curselection():
            return
        sel = self.listbox.get(self.listbox.curselection())
        # set entry text to the code - name string (user asked for same behaviour)
        self.search_var.set(sel)
        # hide suggestions; user can press Search to display
        self.listbox.grid_remove()

    def search_student(self):
        q = self.search_var.get().strip().lower()
        # hide suggestions after search
        self.listbox.grid_remove()
        if not q:
            messagebox.showwarning("Empty", "Enter name or code to search.")
            return
        # we allow searching by "code - name" or part of name/code
        found = [s for s in self.students if q in s["name"].lower() or q in s["code"].lower() or q in f"{s['code']} - {s['name']}".lower()]
        if not found:
            messagebox.showinfo("Not found", "No matching student.")
            return
        self.display_single(found[0])

    def clear_search(self):
        self.search_var.set("")
        self.listbox.grid_remove()
        self.view_all()

    def sort_records_from_dropdown(self):
        choice = self.sort_choice.get()
        reverse = False if choice == "Ascending" else True
        self.students.sort(key=lambda s: s["c1"]+s["c2"]+s["c3"]+s["exam"], reverse=reverse)
        self.view_all()

    def sort_by_column(self, col):
        # called when clicking on column header; toggles sort
        reverse = self._col_sort_reverse.get(col, False)
        if col in ("c1","c2","c3","exam","total","perc"):
            if col in ("total","perc"):
                self.students.sort(key=lambda s: s["c1"]+s["c2"]+s["c3"]+s["exam"], reverse=not reverse)
            else:
                self.students.sort(key=lambda s: s.get(col,0), reverse=not reverse)
        elif col == "code":
            self.students.sort(key=lambda s: int(s["code"]) if s["code"].isdigit() else s["code"], reverse=not reverse)
        else:
            self.students.sort(key=lambda s: s.get(col,"").lower(), reverse=not reverse)
        self._col_sort_reverse[col] = not reverse
        self.view_all()

    def add_student(self):
        top = tk.Toplevel(self.root)
        top.title("Add Student - Oxford Manager")
        top.geometry("520x560")
        top.configure(bg=LIGHT_BG)

        # SET ICON
        set_app_icon(top)

        # header with logo
        hdr = tk.Frame(top, bg=LIGHT_BG)
        hdr.pack(fill="x", pady=6)
        if PIL_AVAILABLE and LOGO_PATH:
            try:
                img = Image.open(LOGO_PATH).resize((60,60), Image.LANCZOS)
                lg = ImageTk.PhotoImage(img)
                tk.Label(hdr, image=lg, bg=LIGHT_BG).pack(side="left", padx=8)
                top.logo = lg
            except:
                pass
        tk.Label(hdr, text="Add New Student", bg=LIGHT_BG, font=("Arial", 12, "bold")).pack(side="left", padx=6)

        fields = [("Code",""), ("Name",""), ("C1",""), ("C2",""), ("C3",""), ("Exam",""), ("Email",""), ("DOB (YYYY-MM-DD)",""), ("Course","")]
        entries = {}
        for lbl, val in fields:
            frame = tk.Frame(top, bg=LIGHT_BG)
            frame.pack(fill="x", padx=12, pady=6)
            tk.Label(frame, text=lbl+":", width=18, anchor="w", bg=LIGHT_BG).pack(side="left")
            ent = tk.Entry(frame, width=34)
            ent.pack(side="left")
            ent.insert(0, val)
            entries[lbl] = ent

        def save():
            try:
                code = entries["Code"].get().strip()
                if not code:
                    raise ValueError("Code required")
                name = entries["Name"].get().strip()
                c1 = int(entries["C1"].get()); c2 = int(entries["C2"].get()); c3 = int(entries["C3"].get()); exam = int(entries["Exam"].get())
                for v in (c1,c2,c3):
                    if not (0 <= v <= 20):
                        raise ValueError("Coursework marks 0-20")
                if not (0 <= exam <= 100):
                    raise ValueError("Exam must be 0-100")
                if any(s["code"]==code for s in self.students):
                    raise ValueError("Student code already exists")
                student = {"code":code, "name":name, "c1":c1, "c2":c2, "c3":c3, "exam":exam}
                self.students.append(student)
                extras = {"email": entries["Email"].get().strip(), "dob": entries["DOB (YYYY-MM-DD)"].get().strip(), "course": entries["Course"].get().strip()}
                if extras["email"] or extras["dob"] or extras["course"]:
                    self.extra[code] = extras
                    save_extra(self.extra)
                self.save_data()
                self.view_all()
                top.destroy()
            except Exception as e:
                messagebox.showerror("Invalid", str(e))

        tk.Button(top, text="Add Student", command=save, bg="#27ae60", fg="white", width=18).pack(pady=12)

    def delete_student(self):
        top = tk.Toplevel(self.root)
        top.title("Delete Student")
        top.geometry("620x450")
        top.configure(bg=LIGHT_BG)

        # SET ICON
        set_app_icon(top)

        hdr = tk.Frame(top, bg=LIGHT_BG)
        hdr.pack(fill="x", pady=6)
        if PIL_AVAILABLE and LOGO_PATH:
            try:
                img = Image.open(LOGO_PATH).resize((60,60), Image.LANCZOS)
                lg = ImageTk.PhotoImage(img)
                tk.Label(hdr, image=lg, bg=LIGHT_BG).pack(side="left", padx=8)
                top.logo = lg
            except:
                pass
        tk.Label(hdr, text="Delete Student", bg=LIGHT_BG, font=("Arial", 12, "bold")).pack(side="left", padx=6)

        tk.Label(top, text="Enter Student Code or Name:", bg=LIGHT_BG).pack(pady=8)
        q_ent = tk.Entry(top, width=68)
        q_ent.pack(pady=4)

        # Frame for Find and Delete Button
        btn_container = tk.Frame(top, bg=LIGHT_BG)
        btn_container.pack(pady=6)

        # Frame for Treeview
        search_results_frame = tk.Frame(top, bg=LIGHT_BG)
        search_results_frame.pack(pady=6, fill="both", expand=True)

        # Store reference to Treeview for deletion (will be created in find_and_show)
        self.tv_delete = None

        def find_and_show():
            q = q_ent.get().strip()

            # Clear and hide previous results
            for widget in search_results_frame.winfo_children():
                widget.destroy()

            if not q:
                result_lbl.config(text="Enter code or name.")
                self.delete_btn.pack_forget()
                self.tv_delete = None
                return

            matches = [s for s in self.students if q.lower() in s["code"].lower() or q.lower() in s["name"].lower()]

            if not matches:
                result_lbl.config(text="No matching student found.")
                self.delete_btn.pack_forget()
                self.tv_delete = None
                return

            # show matches in a Treeview for nicer UI
            cols = ("code","name","total","perc")
            tv = ttk.Treeview(search_results_frame, columns=cols, show="headings", height=6)
            for c in cols:
                tv.heading(c, text=c.title())
                tv.column(c, width=120 if c!="name" else 260, anchor="center")
            for s in matches:
                # Calculate total and percentage for display
                _, total, perc, _ = self.calc_total_perc_grade(s)
                # Use the student's code as the item ID (iid) for easy lookup in confirm_delete_student
                # Ensure iid is always string
                tv.insert("", "end", values=(s["code"], s["name"], total, f"{perc:.2f}%"), iid=str(s["code"]))

            tv.pack(side="left", fill="both", expand=True)
            scr = ttk.Scrollbar(search_results_frame, orient="vertical", command=tv.yview)
            scr.pack(side="right", fill="y")
            tv.configure(yscrollcommand=scr.set)

            # Store reference to the Treeview
            self.tv_delete = tv
            result_lbl.config(text=f"Found {len(matches)} matching student(s). Select one to delete.")
            self.delete_btn.pack(side="left", padx=6) # Repack/show the delete button

        # Find button
        tk.Button(btn_container, text="Find", command=find_and_show, bg=ACCENT, fg="white", width=18).pack(side="left", padx=6)

        # Delete button (defined outside but controlled here)
        self.delete_btn = tk.Button(btn_container, text="Delete Selected", command=lambda: self.confirm_delete_student(self.tv_delete, top), bg="#c0392b", fg="white", width=18)
        self.delete_btn.pack_forget() # Hide initially

        result_lbl = tk.Label(top, text="", bg=LIGHT_BG)
        result_lbl.pack(pady=6)


    def confirm_delete_student(self, treeview, window):
        if not treeview:
            messagebox.showwarning("Error", "No search results to delete from.")
            return

        sel = treeview.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a student to delete.")
            return

        # Robustly extract chosen code: prefer iid, else use first value column
        item = treeview.item(sel[0])
        chosen_code = None
        # item may have 'iid' stored as the ident; get from values if needed
        try:
            # item returns dict with keys like 'values'
            # some tkinter versions don't return iid here, so check values
            if item and item.get("values"):
                # first value is the code column
                chosen_code = str(item["values"][0])
        except Exception:
            chosen_code = None

        # fallback: sometimes sel[0] is the iid already
        if not chosen_code:
            try:
                chosen_code = str(sel[0])
            except Exception:
                chosen_code = None

        if not chosen_code:
            messagebox.showerror("Error", "Could not determine the student code from selection.")
            return

        # Find the student dictionary using the code from the item
        chosen_student = next((s for s in self.students if str(s["code"]) == chosen_code), None)

        if not chosen_student:
            messagebox.showerror("Error", "Could not identify student in main list.")
            return

        if not messagebox.askyesno("Confirm", f"Delete {chosen_student['name']} ({chosen_student['code']})?"):
            return

        # Perform deletion: Remove the dictionary object from the list
        try:
            self.students.remove(chosen_student)

            # Remove from extra details if it exists
            if chosen_code in self.extra:
                del self.extra[chosen_code]
                save_extra(self.extra)  # ensure extras are saved after deletion

            # Save data to both files immediately
            self.save_data()
            self.view_all() # Update the main display
            messagebox.showinfo("Deleted", "Student removed.")
            # clear tv reference
            try:
                # if window passed is the delete dialog, close it
                window.destroy()
            except Exception:
                pass
            self.tv_delete = None
        except ValueError:
             messagebox.showerror("Error", "Student not found in the list (unexpected internal error).")
        except Exception as e:
             messagebox.showerror("Error", f"Failed to complete deletion: {e}")


    def update_student(self):
        top = tk.Toplevel(self.root)
        top.title("Update Student")
        top.geometry("720x560")
        top.configure(bg=LIGHT_BG)

        # SET ICON
        set_app_icon(top)

        hdr = tk.Frame(top, bg=LIGHT_BG)
        hdr.pack(fill="x", pady=6)
        if PIL_AVAILABLE and LOGO_PATH:
            try:
                img = Image.open(LOGO_PATH).resize((60,60), Image.LANCZOS)
                lg = ImageTk.PhotoImage(img)
                tk.Label(hdr, image=lg, bg=LIGHT_BG).pack(side="left", padx=8)
                top.logo = lg
            except:
                pass
        tk.Label(hdr, text="Update Student", bg=LIGHT_BG, font=("Arial", 12, "bold")).pack(side="left", padx=6)

        tk.Label(top, text="Enter Student Code or Name to find:", bg=LIGHT_BG).pack(pady=8)
        q_ent = tk.Entry(top, width=68)
        q_ent.pack(pady=4)
        result_lbl = tk.Label(top, text="", bg=LIGHT_BG)
        result_lbl.pack(pady=6)

        def find_and_edit():
            q = q_ent.get().strip()
            if not q:
                result_lbl.config(text="Enter code or name.")
                return
            matches = [s for s in self.students if q.lower() in s["code"].lower() or q.lower() in s["name"].lower()]
            if not matches:
                result_lbl.config(text="No matching student found.")
                return
            # if more than one match present choices grid
            chosen = matches[0]
            if len(matches) > 1:
                # show a small chooser window
                choose = tk.Toplevel(top)
                choose.title("Choose Student")
                choose.geometry("600x300")
                tvc = ttk.Treeview(choose, columns=("code","name","total","perc"), show="headings", height=8)
                for c in ("code","name","total","perc"):
                    tvc.heading(c, text=c.title())
                    tvc.column(c, width=130 if c!="name" else 300)
                for s in matches:
                    total = s["c1"]+s["c2"]+s["c3"]+s["exam"]
                    perc = (total/160)*100
                    tvc.insert("", "end", values=(s["code"], s["name"], total, f"{perc:.2f}%"), iid=s["code"]) # Using code as iid
                tvc.pack(fill="both", expand=True)
                def choose_selected():
                    sel = tvc.selection()
                    if not sel:
                        messagebox.showwarning("Select", "Select a student.")
                        return
                    code = tvc.item(sel[0], "iid") # Get code from iid
                    chosen_local = next(x for x in matches if x["code"]==code)
                    choose.destroy()
                    populate_form(chosen_local)
                tk.Button(choose, text="Choose", command=choose_selected, bg=ACCENT, fg="white").pack(pady=6)
                return
            else:
                populate_form(chosen)

        # Clear any previously packed forms
        def clear_form_widgets():
            for widget in top.winfo_children():
                # Check for frames containing entry widgets (the form)
                if isinstance(widget, tk.Frame) and any(child.winfo_class() == "Entry" for child in widget.winfo_children()):
                    widget.destroy()
                # Check for the Save Changes button
                if isinstance(widget, tk.Button) and widget.cget("text") == "Save Changes":
                    widget.destroy()

        def populate_form(chosen):
            # Clear previous form elements if any
            clear_form_widgets()

            # big form to edit
            form = tk.Frame(top, bg=LIGHT_BG)
            form.pack(pady=8, fill="x", padx=8)
            labels = ["Code","Name","C1","C2","C3","Exam","Email","DOB (YYYY-MM-DD)","Course"]
            entries = {}
            extras = self.extra.get(chosen["code"], {})
            initial = {
                "Code": chosen["code"], "Name": chosen["name"], "C1": chosen["c1"], "C2": chosen["c2"], "C3": chosen["c3"], "Exam": chosen["exam"],
                "Email": extras.get("email",""), "DOB (YYYY-MM-DD)": extras.get("dob",""), "Course": extras.get("course","")
            }
            for lbl in labels:
                f = tk.Frame(form, bg=LIGHT_BG)
                f.pack(fill="x", padx=12, pady=4)
                tk.Label(f, text=lbl+":", width=18, anchor="w", bg=LIGHT_BG).pack(side="left")
                ent = tk.Entry(f, width=40)
                ent.pack(side="left")
                ent.insert(0, str(initial.get(lbl,"")))
                entries[lbl] = ent
            def save_changes():
                try:
                    new_code = entries["Code"].get().strip()
                    name = entries["Name"].get().strip()
                    c1 = int(entries["C1"].get()); c2 = int(entries["C2"].get()); c3 = int(entries["C3"].get()); exam = int(entries["Exam"].get())
                    if not (0<=c1<=20 and 0<=c2<=20 and 0<=c3<=20):
                        raise ValueError("Coursework marks 0-20")
                    if not (0<=exam<=100):
                        raise ValueError("Exam 0-100")
                    if new_code != chosen["code"] and any(s["code"]==new_code for s in self.students if s is not chosen):
                        # Ensure we check against *other* students only if the code changed
                        raise ValueError("Code already exists for another student")

                    # Store old code for extra data deletion
                    old_code = chosen["code"]

                    chosen["code"] = new_code
                    chosen["name"] = name
                    chosen["c1"] = c1; chosen["c2"] = c2; chosen["c3"] = c3; chosen["exam"] = exam

                    # Update/Save extra data
                    self.extra[new_code] = {"email": entries["Email"].get().strip(), "dob": entries["DOB (YYYY-MM-DD)"].get().strip(), "course": entries["Course"].get().strip()}

                    # if code changed, remove old extra entry
                    if new_code != old_code and old_code in self.extra:
                        del self.extra[old_code]

                    save_extra(self.extra)
                    self.save_data()
                    self.view_all()
                    top.destroy()
                except Exception as e:
                    messagebox.showerror("Invalid", str(e))
            tk.Button(top, text="Save Changes", command=save_changes, bg="#f39c12", fg="white", width=18).pack(pady=10)

        tk.Button(top, text="Find & Edit", command=find_and_edit, bg=ACCENT, fg="white", width=18).pack(pady=6)

    def show_stats(self):
        if not self.students:
            messagebox.showinfo("No data", "No students to analyse.")
            return
        totals = [s["c1"]+s["c2"]+s["c3"]+s["exam"] for s in self.students]
        percs = [(t/160)*100 for t in totals]
        avg = sum(percs)/len(percs)
        highest = max(percs); lowest = min(percs)

        stats_win = tk.Toplevel(self.root)
        stats_win.title("Statistics")
        stats_win.geometry("1100x680")
        stats_win.configure(bg=LIGHT_BG)

        # SET ICON
        set_app_icon(stats_win)

        topf = tk.Frame(stats_win, bg=LIGHT_BG)
        topf.pack(fill="x", padx=12, pady=8)
        tk.Label(topf, text=f"Average: {avg:.2f}%  Highest: {highest:.2f}%  Lowest: {lowest:.2f}%", bg=LIGHT_BG, font=("Arial",11,"bold")).pack(side="left")

        chart_type = tk.StringVar(value="hist")

        # Options: Histogram, Pie, or Both
        tk.Radiobutton(topf, text="Histogram", variable=chart_type, value="hist", bg=LIGHT_BG).pack(side="left", padx=6)
        tk.Radiobutton(topf, text="Pie Chart (grades)", variable=chart_type, value="pie", bg=LIGHT_BG).pack(side="left", padx=6)

        # OPTION FOR SEE BOTH
        tk.Radiobutton(topf, text="See Both (Side-by-Side)", variable=chart_type, value="both", bg=LIGHT_BG, fg=ACCENT, font=("Arial", 10, "bold")).pack(side="left", padx=10)

        canvas_frame = tk.Frame(stats_win, bg=LIGHT_BG)
        canvas_frame.pack(fill="both", expand=True, padx=12, pady=6)

        def draw_chart():
            for widget in canvas_frame.winfo_children():
                widget.destroy()
            if not MATPLOTLIB_AVAILABLE:
                tk.Label(canvas_frame, text="matplotlib not installed. Install it to view charts.", bg=LIGHT_BG).pack()
                return

            ctype = chart_type.get()

            # Prepare Data
            grades = [self.get_grade(p) for p in percs]
            # Use fixed order for grades
            grade_order = ["A", "B", "C", "D", "F"]
            labels = [g for g in grade_order if g in grades]
            counts = [grades.count(g) for g in labels]

            # Logic for "See Both"
            if ctype == "both":
                fig = Figure(figsize=(12,5), dpi=100)
                # subplot 1: Histogram
                ax1 = fig.add_subplot(121)
                ax1.hist(percs, bins=10)
                ax1.set_title("Distribution of Percentages")
                ax1.set_xlabel("Percentage")
                ax1.set_ylabel("Count")

                # subplot 2: Pie
                ax2 = fig.add_subplot(122)
                ax2.pie(counts, labels=labels, autopct="%1.1f%%", startangle=90)
                ax2.set_title("Grade Distribution")

            elif ctype == "hist":
                fig = Figure(figsize=(9,5))
                ax = fig.add_subplot(111)
                ax.hist(percs, bins=10)
                ax.set_title("Distribution of Percentages")
                ax.set_xlabel("Percentage")
                ax.set_ylabel("Count")
            else: # pie
                fig = Figure(figsize=(9,5))
                ax = fig.add_subplot(111)
                ax.pie(counts, labels=labels, autopct="%1.1f%%", startangle=90)
                ax.set_title("Grade Distribution")

            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            stats_win._current_fig = fig

        draw_chart_btn = tk.Button(topf, text="Draw Chart", command=draw_chart, bg=ACCENT, fg="white")
        draw_chart_btn.pack(side="left", padx=8)

        export_btn = tk.Button(topf, text="Export Chart to PDF", bg="#27ae60", fg="white")
        export_btn.pack(side="right", padx=8)

        def export_chart_to_pdf():
            if not hasattr(stats_win, "_current_fig"):
                messagebox.showwarning("No Chart", "Draw a chart before exporting.")
                return
            path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf"),("PNG","*.png")])
            if not path:
                return
            fig = stats_win._current_fig
            tmp_img = os.path.join(SCRIPT_DIR, f"__temp_chart_{datetime.now().timestamp():.0f}.png")
            fig.savefig(tmp_img, bbox_inches="tight")
            if path.lower().endswith(".pdf"):
                if not REPORTLAB_AVAILABLE:
                    messagebox.showwarning("reportlab missing", f"Saved chart image to {tmp_img}. Install reportlab to embed into PDF.")
                    return
                try:
                    c = pdfcanvas.Canvas(path, pagesize=letter)
                    w, h = letter
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(36, h-36, "Oxford University - Statistics Export")
                    # embed logo if available
                    if LOGO_PATH and os.path.exists(LOGO_PATH):
                        try:
                            c.drawImage(LOGO_PATH, w-120, h-80, width=72, height=72, mask='auto')
                        except:
                            pass
                    c.drawImage(tmp_img, 36, 80, width=w-72, preserveAspectRatio=True, mask='auto')
                    c.save()
                    os.remove(tmp_img)
                    messagebox.showinfo("Exported", f"PDF saved to {path}")
                except Exception as e:
                    messagebox.showerror("Error", f"PDF export failed: {e}")
            else:
                try:
                    os.replace(tmp_img, path)
                    messagebox.showinfo("Saved", f"Chart saved to {path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Save failed: {e}")

        export_btn.config(command=export_chart_to_pdf)

    def export_pdf(self):
        items = [i for i in self.tree.get_children() if self.tree.item(i)["values"] and self.tree.item(i)["values"][0]!=""]
        if not items:
            messagebox.showinfo("Empty", "No data to export.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf"),("CSV","*.csv")], title="Export")
        if not save_path:
            return
        if save_path.lower().endswith(".pdf"):
            if not REPORTLAB_AVAILABLE:
                messagebox.showwarning("ReportLab missing", "reportlab not installed. The app will save CSV instead.")
                save_path = os.path.splitext(save_path)[0] + ".csv"
            else:
                try:
                    c = pdfcanvas.Canvas(save_path, pagesize=letter)
                    width, height = letter
                    x = 36; y = height - 36
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(x, y, "Oxford University - Student Manager Export")
                    if LOGO_PATH and os.path.exists(LOGO_PATH):
                        try:
                            c.drawImage(LOGO_PATH, width-130, y-30, width=72, height=72, mask='auto')
                        except:
                            pass
                    c.setFont("Helvetica", 9)
                    y -= 40
                    headers = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
                    row_h = 14
                    # compute column x positions (simple layout)
                    col_x = [x, x+80, x+320, x+400, x+480, x+560, x+640, x+720, x+800] # Adjusted to give more space
                    for i,h in enumerate(headers):
                        c.drawString(col_x[i], y, h)
                    y -= row_h
                    for item in items:
                        vals = self.tree.item(item)["values"]
                        if y < 80:
                            c.showPage()
                            y = height - 36
                        for i,v in enumerate(vals):
                            c.drawString(col_x[i], y, str(v))
                        y -= row_h
                    c.save()
                    messagebox.showinfo("Exported", f"PDF saved to {save_path}")
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"PDF export failed: {e}")
                    return
        # fallback CSV
        try:
            with open(save_path, "w") as f:
                headers = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
                f.write(",".join(headers)+"\n")
                for item in items:
                    vals = [str(v) for v in self.tree.item(item)["values"]]
                    f.write(",".join(vals)+"\n")
            messagebox.showinfo("Saved", f"CSV saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

def main():
    root = tk.Tk()
    root.withdraw()
    def on_login_success(user):
        root.deiconify()
        StudentManager(root, user)
    LoginWindow(root, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    main()
