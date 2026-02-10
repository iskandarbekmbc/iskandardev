import sqlite3
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from xml.sax.saxutils import escape

DB_PATH = "zikr_desktop.db"


@dataclass
class ZikrItem:
    id: int
    name: str
    text: str
    target_count: int


class ZikrRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS zikr (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                text TEXT NOT NULL,
                target_count INTEGER NOT NULL CHECK(target_count > 0),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zikr_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                current_count INTEGER NOT NULL DEFAULT 0,
                UNIQUE(zikr_id, day),
                FOREIGN KEY(zikr_id) REFERENCES zikr(id) ON DELETE CASCADE
            )
            """
        )
        self.conn.commit()

    def list_zikr(self) -> list[ZikrItem]:
        rows = self.conn.execute(
            "SELECT id, name, text, target_count FROM zikr ORDER BY created_at DESC"
        ).fetchall()
        return [ZikrItem(row["id"], row["name"], row["text"], row["target_count"]) for row in rows]

    def add_zikr(self, name: str, text: str, target_count: int) -> None:
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            "INSERT INTO zikr(name, text, target_count, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (name.strip(), text.strip(), target_count, now, now),
        )
        self.conn.commit()

    def update_zikr(self, zikr_id: int, name: str, text: str, target_count: int) -> None:
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            "UPDATE zikr SET name=?, text=?, target_count=?, updated_at=? WHERE id=?",
            (name.strip(), text.strip(), target_count, now, zikr_id),
        )
        self.conn.commit()

    def delete_zikr(self, zikr_id: int) -> None:
        self.conn.execute("DELETE FROM daily_progress WHERE zikr_id=?", (zikr_id,))
        self.conn.execute("DELETE FROM zikr WHERE id=?", (zikr_id,))
        self.conn.commit()

    def get_progress(self, zikr_id: int, day: str | None = None) -> int:
        day = day or date.today().isoformat()
        row = self.conn.execute(
            "SELECT current_count FROM daily_progress WHERE zikr_id=? AND day=?",
            (zikr_id, day),
        ).fetchone()
        return row["current_count"] if row else 0

    def set_progress(self, zikr_id: int, count: int, day: str | None = None) -> None:
        day = day or date.today().isoformat()
        self.conn.execute(
            """
            INSERT INTO daily_progress(zikr_id, day, current_count)
            VALUES (?, ?, ?)
            ON CONFLICT(zikr_id, day)
            DO UPDATE SET current_count=excluded.current_count
            """,
            (zikr_id, day, max(0, count)),
        )
        self.conn.commit()


def write_simple_xlsx(headers: list[str], rows: list[list[str]], output_path: str) -> None:
    def column_name(index: int) -> str:
        name = ""
        while index > 0:
            index, rem = divmod(index - 1, 26)
            name = chr(65 + rem) + name
        return name

    def build_sheet_xml() -> str:
        all_rows = [headers] + rows
        row_xml_parts: list[str] = []
        for row_idx, row_values in enumerate(all_rows, start=1):
            cell_xml_parts: list[str] = []
            for col_idx, value in enumerate(row_values, start=1):
                ref = f"{column_name(col_idx)}{row_idx}"
                safe_value = escape(str(value))
                cell_xml_parts.append(
                    f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{safe_value}</t></is></c>'
                )
            row_xml_parts.append(f'<row r="{row_idx}">' + "".join(cell_xml_parts) + "</row>")

        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData>'
            + "".join(row_xml_parts)
            + "</sheetData></worksheet>"
        )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>'
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        '</Relationships>'
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Zikrlar" sheetId="1" r:id="rId1"/></sheets>'
        '</workbook>'
    )

    workbook_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '</Relationships>'
    )

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as xlsx:
        xlsx.writestr("[Content_Types].xml", content_types_xml)
        xlsx.writestr("_rels/.rels", rels_xml)
        xlsx.writestr("xl/workbook.xml", workbook_xml)
        xlsx.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        xlsx.writestr("xl/worksheets/sheet1.xml", build_sheet_xml())


class ZikrForm(tk.Toplevel):
    def __init__(self, parent, on_save, item: ZikrItem | None = None):
        super().__init__(parent)
        self.title("Zikr qo'shish" if item is None else "Zikrni tahrirlash")
        self.geometry("500x420")
        self.resizable(False, False)
        self.on_save = on_save
        self.item = item

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Nomi:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.name_var = tk.StringVar(value=item.name if item else "")
        ttk.Entry(self, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=10, pady=8)

        ttk.Label(self, text="Miqdor (kunlik):").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.target_var = tk.StringVar(value=str(item.target_count) if item else "33")
        ttk.Entry(self, textvariable=self.target_var).grid(row=1, column=1, sticky="ew", padx=10, pady=8)

        ttk.Label(self, text="Zikr matni:").grid(row=2, column=0, sticky="nw", padx=10, pady=8)
        self.text_widget = tk.Text(self, height=14, wrap="word")
        self.text_widget.grid(row=2, column=1, sticky="nsew", padx=10, pady=8)
        if item:
            self.text_widget.insert("1.0", item.text)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=1, sticky="e", padx=10, pady=8)
        ttk.Button(button_frame, text="Saqlash", command=self._save).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Bekor qilish", command=self.destroy).pack(side="left", padx=4)

    def _save(self):
        name = self.name_var.get().strip()
        text = self.text_widget.get("1.0", "end").strip()
        target_text = self.target_var.get().strip()

        if not name:
            messagebox.showerror("Xatolik", "Zikr nomi kiritilishi shart.")
            return
        if not text:
            messagebox.showerror("Xatolik", "Zikr matni kiritilishi shart.")
            return
        if not target_text.isdigit() or int(target_text) <= 0:
            messagebox.showerror("Xatolik", "Miqdor musbat butun son bo'lishi kerak.")
            return

        self.on_save(name, text, int(target_text))
        self.destroy()


class ZikrDesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kundalik Zikrlar")
        self.geometry("960x600")
        self.repo = ZikrRepository()
        self.selected_id: int | None = None

        self._build_ui()
        self.refresh_list()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self, padding=10)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Zikrlarim", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")

        self.tree = ttk.Treeview(left, columns=("name", "target", "progress"), show="headings", height=20)
        self.tree.heading("name", text="Nomi")
        self.tree.heading("target", text="Miqdor")
        self.tree.heading("progress", text="Bugun")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("target", width=80, anchor="center")
        self.tree.column("progress", width=120, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        btns = ttk.Frame(left)
        btns.grid(row=2, column=0, sticky="ew")
        ttk.Button(btns, text="+ Yangi", command=self.add_dialog).pack(side="left", padx=4)
        ttk.Button(btns, text="Tahrirlash", command=self.edit_dialog).pack(side="left", padx=4)
        ttk.Button(btns, text="O'chirish", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(btns, text="Excelga export", command=self.export_to_excel).pack(side="left", padx=4)

        right = ttk.Frame(self, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        self.title_var = tk.StringVar(value="Zikr tanlang")
        ttk.Label(right, textvariable=self.title_var, font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")

        self.progress_var = tk.StringVar(value="Progress: 0/0")
        ttk.Label(right, textvariable=self.progress_var, font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=6)

        self.text_display = tk.Text(right, wrap="word", state="disabled")
        self.text_display.grid(row=2, column=0, sticky="nsew")

        quick = ttk.Frame(right)
        quick.grid(row=3, column=0, sticky="e", pady=8)
        ttk.Button(quick, text="+1", command=lambda: self.increment(1)).pack(side="left", padx=4)
        ttk.Button(quick, text="+5", command=lambda: self.increment(5)).pack(side="left", padx=4)
        ttk.Button(quick, text="Reset (0)", command=self.reset_progress).pack(side="left", padx=4)

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        items = self.repo.list_zikr()
        for item in items:
            current = self.repo.get_progress(item.id)
            progress = f"{min(current, item.target_count)}/{item.target_count}"
            self.tree.insert("", "end", iid=str(item.id), values=(item.name, item.target_count, progress))

    def export_to_excel(self):
        items = self.repo.list_zikr()
        if not items:
            messagebox.showinfo("Eslatma", "Export qilish uchun zikrlar mavjud emas.")
            return

        day = date.today().isoformat()
        rows: list[list[str]] = []
        for item in items:
            current = self.repo.get_progress(item.id, day)
            rows.append(
                [
                    item.name,
                    item.text,
                    str(item.target_count),
                    str(min(current, item.target_count)),
                    f"{min(current, item.target_count)}/{item.target_count}",
                    day,
                ]
            )

        output_path = filedialog.asksaveasfilename(
            title="Excel faylni saqlash",
            defaultextension=".xlsx",
            initialfile=f"zikr-export-{day}.xlsx",
            filetypes=[("Excel fayl", "*.xlsx")],
        )

        if not output_path:
            return

        try:
            write_simple_xlsx(
                headers=["Nomi", "Zikr matni", "Kunlik miqdor", "Bugungi sanoq", "Progress", "Sana"],
                rows=rows,
                output_path=output_path,
            )
            messagebox.showinfo("Muvaffaqiyat", f"Excel export tayyor: {output_path}")
        except Exception as exc:
            messagebox.showerror("Xatolik", f"Exportda xatolik yuz berdi: {exc}")

    def _on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        self.selected_id = int(selected[0])
        self.show_selected()

    def _get_selected_item(self) -> ZikrItem | None:
        if self.selected_id is None:
            return None
        for item in self.repo.list_zikr():
            if item.id == self.selected_id:
                return item
        return None

    def show_selected(self):
        item = self._get_selected_item()
        if not item:
            return
        current = self.repo.get_progress(item.id)
        self.title_var.set(item.name)
        self.progress_var.set(f"Progress: {min(current, item.target_count)}/{item.target_count}")
        self.text_display.configure(state="normal")
        self.text_display.delete("1.0", "end")
        self.text_display.insert("1.0", item.text)
        self.text_display.configure(state="disabled")

    def add_dialog(self):
        def on_save(name: str, text: str, target: int):
            self.repo.add_zikr(name, text, target)
            self.refresh_list()

        ZikrForm(self, on_save)

    def edit_dialog(self):
        item = self._get_selected_item()
        if not item:
            messagebox.showinfo("Eslatma", "Avval ro'yxatdan zikr tanlang.")
            return

        def on_save(name: str, text: str, target: int):
            self.repo.update_zikr(item.id, name, text, target)
            current = self.repo.get_progress(item.id)
            if current > target:
                self.repo.set_progress(item.id, target)
            self.refresh_list()
            self.show_selected()

        ZikrForm(self, on_save, item=item)

    def delete_selected(self):
        item = self._get_selected_item()
        if not item:
            messagebox.showinfo("Eslatma", "Avval ro'yxatdan zikr tanlang.")
            return
        if messagebox.askyesno("Tasdiqlash", f"'{item.name}' zikrini o'chirasizmi?"):
            self.repo.delete_zikr(item.id)
            self.selected_id = None
            self.title_var.set("Zikr tanlang")
            self.progress_var.set("Progress: 0/0")
            self.text_display.configure(state="normal")
            self.text_display.delete("1.0", "end")
            self.text_display.configure(state="disabled")
            self.refresh_list()

    def increment(self, step: int):
        item = self._get_selected_item()
        if not item:
            messagebox.showinfo("Eslatma", "Avval ro'yxatdan zikr tanlang.")
            return
        current = self.repo.get_progress(item.id)
        new_value = min(item.target_count, current + step)
        self.repo.set_progress(item.id, new_value)
        self.refresh_list()
        self.show_selected()

    def reset_progress(self):
        item = self._get_selected_item()
        if not item:
            messagebox.showinfo("Eslatma", "Avval ro'yxatdan zikr tanlang.")
            return
        self.repo.set_progress(item.id, 0)
        self.refresh_list()
        self.show_selected()


if __name__ == "__main__":
    app = ZikrDesktopApp()
    app.mainloop()
