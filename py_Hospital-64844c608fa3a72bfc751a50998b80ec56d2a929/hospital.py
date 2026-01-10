import tkinter as tk
from tkinter import ttk, messagebox
import pymysql

class Hospital:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System")
        self.root.state('zoomed')
        self.root.configure(bg="#f4f6f8")

        # ================= STYLE =================
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background="#f4f6f8", font=("Segoe UI", 11))
        style.configure('Header.TLabel', font=("Segoe UI", 26, 'bold'))
        style.configure('TButton', font=("Segoe UI", 11), padding=8)
        style.configure('Card.TFrame', background="white", relief='ridge', borderwidth=2)
        style.configure('Treeview.Heading', font=("Segoe UI", 11, 'bold'))
        style.configure('Treeview', font=("Segoe UI", 10), rowheight=28)

        # ================= HEADER =================
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill='x')
        ttk.Label(header, text="Hospital Management System", style='Header.TLabel').pack(anchor='center')

        # ================= MAIN LAYOUT =================
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill='both', expand=True)

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)

        # ================= LEFT CARD (FORM) =================
        form = ttk.Frame(main, style='Card.TFrame', padding=20)
        form.grid(row=0, column=0, sticky='nsew', padx=(0, 15))

        ttk.Label(form, text="Admit Patient", font=("Segoe UI", 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

        labels = [
            "Patient ID", "Patient Name", "Blood Group",
            "Disease", "Health Points", "Medication", "Address"
        ]

        self.entries = []
        for i, text in enumerate(labels):
            ttk.Label(form, text=text).grid(row=i+1, column=0, sticky='w', pady=6)
            ent = ttk.Entry(form, width=25)
            ent.grid(row=i+1, column=1, pady=6)
            self.entries.append(ent)

        (self.idIn, self.nameIn, self.bgIn,
         self.desIn, self.hpIn, self.medIn, self.addrIn) = self.entries

        ttk.Button(form, text="Admit Patient", command=self.insertFun).grid(
            row=9, column=0, columnspan=2, pady=20, sticky='ew'
        )

        # ================= RIGHT CARD (DETAILS + TABLE) =================
        right = ttk.Frame(main, style='Card.TFrame', padding=20)
        right.grid(row=0, column=1, sticky='nsew')

        topBar = ttk.Frame(right)
        topBar.pack(fill='x', pady=10)

        ttk.Label(topBar, text="Patient ID").pack(side='left')
        self.pIdIn = ttk.Entry(topBar, width=15)
        self.pIdIn.pack(side='left', padx=10)

        ttk.Button(topBar, text="View", command=self.medicsFun).pack(side='left', padx=5)
        ttk.Button(topBar, text="Add Health Points", command=self.hPointFun).pack(side='left', padx=5)
        ttk.Button(topBar, text="Discharge", command=self.disFun).pack(side='left', padx=5)
        ttk.Button(topBar, text="Show All Patients", command=self.showAll).pack(side='left', padx=5)
        ttk.Button(topBar, text="Refresh", command=self.refreshTable).pack(side='left', padx=5)

        # ================= TABLE =================
        tableFrame = ttk.Frame(right)
        tableFrame.pack(fill='both', expand=True)

        scroll_y = ttk.Scrollbar(tableFrame, orient='vertical')
        scroll_y.pack(side='right', fill='y')

        self.table = ttk.Treeview(
            tableFrame,
            columns=("id","name","bgroup","disease","points","med","addr"),
            yscrollcommand=scroll_y.set,
            show='headings'
        )
        scroll_y.config(command=self.table.yview)

        headings = [
            ("id", "ID"), ("name", "Name"), ("bgroup", "Blood"),
            ("disease", "Disease"), ("points", "Points"),
            ("med", "Medication"), ("addr", "Address")
        ]

        for col, txt in headings:
            self.table.heading(col, text=txt)
            self.table.column(col, anchor='center', width=120)

        self.table.pack(fill='both', expand=True)

    # ================= DATABASE =================
    def dbFun(self):
        self.con = pymysql.connect(host="localhost", user="root", passwd="ismail", database="rec")
        self.cur = self.con.cursor()

    # ================= FUNCTIONS =================
    def insertFun(self):
        try:
            data = [e.get() for e in self.entries]
            if not data[0].isdigit() or not data[4].isdigit():
                raise ValueError("ID and Health Points must be numbers")

            self.dbFun()
            self.cur.execute(
                "INSERT INTO hospital VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (int(data[0]), data[1], data[2], data[3], int(data[4]), data[5], data[6])
            )
            self.con.commit()
            messagebox.showinfo("Success", "Patient admitted successfully")
            self.clear()
            self.con.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def showAll(self):
        """Show all patient records"""
        try:
            self.dbFun()
            self.cur.execute("SELECT * FROM hospital")
            rows = self.cur.fetchall()
            self.table.delete(*self.table.get_children())
            for row in rows:
                self.table.insert('', 'end', values=row)
            self.con.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refreshTable(self):
        """Clear table view"""
        self.table.delete(*self.table.get_children())

    def medicsFun(self):
        pid = self.pIdIn.get()
        if not pid.isdigit():
            return messagebox.showerror("Error", "Invalid Patient ID")

        self.dbFun()
        self.cur.execute("SELECT * FROM hospital WHERE id=%s", (pid,))
        row = self.cur.fetchone()
        self.table.delete(*self.table.get_children())
        if row:
            self.table.insert('', 'end', values=row)
        else:
            messagebox.showinfo("Info", "Patient not found")
        self.con.close()

    def hPointFun(self):
        win = tk.Toplevel(self.root)
        win.title("Add Health Points")
        win.geometry("300x180")
        win.resizable(False, False)

        ttk.Label(win, text="Enter Points", font=("Segoe UI", 12)).pack(pady=15)
        ent = ttk.Entry(win, width=20)
        ent.pack()

        def save():
            if not ent.get().isdigit():
                return messagebox.showerror("Error", "Invalid points")
            self.dbFun()
            self.cur.execute("UPDATE hospital SET h_points=h_points+%s WHERE id=%s", (ent.get(), self.pIdIn.get()))
            self.con.commit()
            self.con.close()
            win.destroy()
            self.medicsFun()

        ttk.Button(win, text="Update", command=save).pack(pady=20)

    def disFun(self):
        pid = self.pIdIn.get()
        if not pid.isdigit():
            return messagebox.showerror("Error", "Invalid Patient ID")
        self.dbFun()
        self.cur.execute("DELETE FROM hospital WHERE id=%s", (pid,))
        self.con.commit()
        self.con.close()
        self.table.delete(*self.table.get_children())
        messagebox.showinfo("Success", "Patient discharged")

    def clear(self):
        for e in self.entries:
            e.delete(0, 'end')

    def getPatientCount(self):
        """Return total number of patients"""
        self.dbFun()
        self.cur.execute("SELECT COUNT(*) FROM hospital")
        count = self.cur.fetchone()[0]
        self.con.close()
        return count

    def migrate(self):
        self.dbFun()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS hospital (
            id INT PRIMARY KEY,
            name VARCHAR(100),
            b_group VARCHAR(10),
            desease VARCHAR(100),
            h_points INT,
            medication VARCHAR(100),
            addr VARCHAR(255)
        )""")
        self.con.commit()
        self.con.close()

# ================= RUN =================
root = tk.Tk()
app = Hospital(root)
app.migrate()
root.mainloop()
