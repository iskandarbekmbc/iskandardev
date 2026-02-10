import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

DATA_FILE = Path("kundalik_entries.json")
UPLOADS_DIR = Path("kundalik_uploads")


class KundalikApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Ish Kundaligi")
        self.root.geometry("1020x560")

        self.current_attachment: Path | None = None
        UPLOADS_DIR.mkdir(exist_ok=True)
        self.entries = self._load_entries()

        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        form = tk.Frame(self.root, padx=12, pady=10)
        form.pack(fill="x")

        tk.Label(form, text="Sana (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(form, textvariable=self.date_var, width=16).grid(row=0, column=1, padx=(6, 16), sticky="w")

        tk.Label(form, text="Loyiha / Mavzu:").grid(row=0, column=2, sticky="w")
        self.project_var = tk.StringVar()
        tk.Entry(form, textvariable=self.project_var, width=28).grid(row=0, column=3, padx=(6, 16), sticky="we")

        tk.Label(form, text="Sarflangan vaqt (soat):").grid(row=0, column=4, sticky="w")
        self.hours_var = tk.StringVar()
        tk.Entry(form, textvariable=self.hours_var, width=10).grid(row=0, column=5, padx=(6, 0), sticky="w")

        tk.Label(form, text="Qilingan ish tafsiloti:").grid(row=1, column=0, columnspan=6, pady=(12, 4), sticky="w")
        self.task_text = tk.Text(form, height=5, width=100)
        self.task_text.grid(row=2, column=0, columnspan=6, sticky="we")

        attachment_row = tk.Frame(form)
        attachment_row.grid(row=3, column=0, columnspan=6, sticky="we", pady=(10, 2))

        tk.Label(attachment_row, text="Yuklangan fayl:").pack(side="left")
        self.attachment_var = tk.StringVar(value="Fayl tanlanmagan")
        tk.Label(attachment_row, textvariable=self.attachment_var, fg="#0b5394").pack(side="left", padx=(8, 12))
        tk.Button(attachment_row, text="Fayl yuklash", command=self.pick_attachment, width=14).pack(side="left")
        tk.Button(attachment_row, text="Yuklangan faylni ochish", command=self.open_current_attachment, width=22).pack(side="left", padx=8)

        button_row = tk.Frame(form, pady=10)
        button_row.grid(row=4, column=0, columnspan=6, sticky="w")

        tk.Button(button_row, text="Saqlash", command=self.save_entry, width=14).pack(side="left")
        tk.Button(button_row, text="Tanlanganni o'chirish", command=self.delete_entry, width=20).pack(side="left", padx=8)
        tk.Button(button_row, text="Tanlangan yozuv faylini ochish", command=self.open_selected_entry_attachment, width=28).pack(side="left", padx=8)
        tk.Button(button_row, text="Tozalash", command=self.clear_form, width=12).pack(side="left")

        table_frame = tk.Frame(self.root, padx=12, pady=8)
        table_frame.pack(fill="both", expand=True)

        columns = ("date", "project", "hours", "task", "attachment")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.table.heading("date", text="Sana")
        self.table.heading("project", text="Loyiha")
        self.table.heading("hours", text="Soat")
        self.table.heading("task", text="Tafsilot")
        self.table.heading("attachment", text="Fayl")

        self.table.column("date", width=120, anchor="center")
        self.table.column("project", width=170)
        self.table.column("hours", width=90, anchor="center")
        self.table.column("task", width=420)
        self.table.column("attachment", width=180)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=y_scroll.set)

        self.table.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

        self.table.bind("<Double-1>", self._on_table_double_click)

    def _load_entries(self) -> list[dict]:
        if not DATA_FILE.exists():
            return []
        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    for entry in data:
                        entry.setdefault("attachment", "")
                    return data
        except json.JSONDecodeError:
            messagebox.showwarning("Ogohlantirish", "kundalik_entries.json fayli buzilgan. Yangi ro'yxat boshlandi.")
        return []

    def _save_entries(self) -> None:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(self.entries, file, ensure_ascii=False, indent=2)

    def _refresh_table(self) -> None:
        for item in self.table.get_children():
            self.table.delete(item)

        for idx, entry in enumerate(self.entries):
            attachment_name = Path(entry.get("attachment", "")).name if entry.get("attachment") else "-"
            self.table.insert(
                "",
                "end",
                iid=str(idx),
                values=(entry["date"], entry["project"], entry["hours"], entry["task"], attachment_name),
            )

    def _validate(self, date_text: str, project: str, hours_text: str, task: str) -> bool:
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Xato", "Sana formati noto'g'ri. Misol: 2026-01-31")
            return False

        if not project.strip():
            messagebox.showerror("Xato", "Loyiha / Mavzu maydoni bo'sh bo'lmasligi kerak.")
            return False

        if not task.strip():
            messagebox.showerror("Xato", "Qilingan ish tafsilotini kiriting.")
            return False

        try:
            hours = float(hours_text)
            if hours <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Xato", "Sarflangan vaqt musbat son bo'lishi kerak.")
            return False

        return True

    def pick_attachment(self) -> None:
        file_path = filedialog.askopenfilename(title="Fayl tanlang")
        if not file_path:
            return

        src = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_name = f"{timestamp}_{src.name}"
        dest_path = UPLOADS_DIR / dest_name

        try:
            shutil.copy2(src, dest_path)
        except OSError as error:
            messagebox.showerror("Xato", f"Faylni yuklashda xatolik: {error}")
            return

        self.current_attachment = dest_path
        self.attachment_var.set(dest_path.name)
        messagebox.showinfo("Muvaffaqiyat", "Fayl yuklandi va ushbu yozuvga biriktirildi.")

    def open_current_attachment(self) -> None:
        if not self.current_attachment:
            messagebox.showinfo("Ma'lumot", "Avval fayl yuklang yoki tanlang.")
            return
        self._open_file(self.current_attachment)

    def open_selected_entry_attachment(self) -> None:
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Ma'lumot", "Jadvaldan yozuv tanlang.")
            return

        entry = self.entries[int(selected[0])]
        attachment_path = entry.get("attachment")
        if not attachment_path:
            messagebox.showinfo("Ma'lumot", "Bu yozuvga fayl biriktirilmagan.")
            return

        self._open_file(Path(attachment_path))

    def _open_file(self, path: Path) -> None:
        if not path.exists():
            messagebox.showerror("Xato", "Fayl topilmadi. U o'chirilgan bo'lishi mumkin.")
            return

        try:
            if sys.platform.startswith("win"):
                subprocess.run(["cmd", "/c", "start", "", str(path)], check=False)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=False)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
        except OSError as error:
            messagebox.showerror("Xato", f"Faylni ochib bo'lmadi: {error}")

    def _on_table_double_click(self, _event: tk.Event) -> None:
        self.open_selected_entry_attachment()

    def save_entry(self) -> None:
        date_text = self.date_var.get().strip()
        project = self.project_var.get().strip()
        hours_text = self.hours_var.get().strip()
        task = self.task_text.get("1.0", "end").strip()

        if not self._validate(date_text, project, hours_text, task):
            return

        entry = {
            "date": date_text,
            "project": project,
            "hours": float(hours_text),
            "task": task,
            "attachment": str(self.current_attachment) if self.current_attachment else "",
        }
        self.entries.append(entry)
        self._save_entries()
        self._refresh_table()
        self.clear_form(reset_date=False)

    def delete_entry(self) -> None:
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Ma'lumot", "O'chirish uchun jadvaldan bir qator tanlang.")
            return

        idx = int(selected[0])
        self.entries.pop(idx)
        self._save_entries()
        self._refresh_table()

    def clear_form(self, reset_date: bool = True) -> None:
        if reset_date:
            self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.project_var.set("")
        self.hours_var.set("")
        self.task_text.delete("1.0", "end")
        self.current_attachment = None
        self.attachment_var.set("Fayl tanlanmagan")


if __name__ == "__main__":
    app_root = tk.Tk()
    KundalikApp(app_root)
    app_root.mainloop()
