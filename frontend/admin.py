# frontend/admin.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime
from backend.db import get_connection
from backend.utils import generate_custom_id, get_prefix_for_table

class CafeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Aplikasi Cafe Billiard')
        self.geometry('1200x700')
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        self.tabs = {}
        self.create_tabs()

    def create_tabs(self):
        tables = [
            ('CUSTOMER', ['ID_Customer', 'Nama_Customer', 'Kontak_Customer']),
            ('KARYAWAN', ['ID_Karyawan', 'Nama_Karyawan', 'Tanggal_Masuk', 'Gaji']),
            ('MEJA', ['ID_Meja', 'Nomor_Meja', 'Status_Meja', 'ID_Karyawan']),
            ('MENU', ['ID_Menu', 'Nama_Menu', 'Harga_Menu', 'Kategori']),
            ('PESANAN', ['ID_Pesanan', 'ID_Customer', 'ID_Karyawan', 'Waktu_Pesanan', 'ID_Menu', 'ID_Meja']),
            ('PEMBAYARAN', ['ID_Pembayaran', 'ID_Transaksi', 'Metode_Pembayaran', 'Jumlah_Bayar', 'Tanggal_Pembayaran']),
            ('RESERVASI', ['ID_Reservasi', 'ID_Customer', 'ID_Meja', 'Tanggal_Reservasi', 'Waktu_Mulai', 'Waktu_Selesai', 'Status_Reservasi']),
            ('TRANSAKSI', ['ID_Transaksi', 'ID_Pesanan', 'Total_Harga', 'Tanggal_Transaksi', 'ID_Karyawan']),
        ]

        for table, fields in tables:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=table)
            self.tabs[table] = TableTab(tab, table, fields)

class TableTab:
    def __init__(self, parent, table_name, fields):
        self.parent = parent
        self.table_name = table_name
        self.fields = fields
        self.entries = {}
        self.comboboxes = {}
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        input_frame = tk.Frame(self.parent)
        input_frame.pack(fill="x", padx=10, pady=5)

        for idx, field in enumerate(self.fields):
            tk.Label(input_frame, text=field).grid(row=0, column=idx, padx=5, pady=2)

            if self.table_name == "MENU" and field == "Kategori":
                cb = ttk.Combobox(input_frame, width=15, state="readonly")
                cb['values'] = ["Makanan", "Minuman"]
                cb.current(0)
                cb.grid(row=1, column=idx, padx=5, pady=2)
                self.comboboxes[field] = cb

            elif "tanggal" in field.lower() or "waktu" in field.lower():
                entry = DateEntry(input_frame, date_pattern="dd-mm-yyyy", width=12)
                entry.grid(row=1, column=idx, padx=5, pady=2)
                self.entries[field] = entry

            elif self.is_fk_field(field):
                cb = ttk.Combobox(input_frame, width=15)
                cb.grid(row=1, column=idx, padx=5, pady=2)
                self.comboboxes[field] = cb

            elif idx == 0:
                tk.Label(input_frame, text="(Auto)").grid(row=1, column=idx, padx=5, pady=2)
                self.entries[field] = None

            else:
                entry = tk.Entry(input_frame, width=15)
                entry.grid(row=1, column=idx, padx=5, pady=2)
                self.entries[field] = entry

        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_frame, text="Tambah", command=self.add_data).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit", command=self.edit_data).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Hapus", command=self.delete_data).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_data).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.parent, columns=self.fields, show="headings")
        for field in self.fields:
            self.tree.heading(field, text=field)
            self.tree.column(field, width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def is_fk_field(self, field):
        fk_patterns = [
            "_ID_Karyawan", "_ID_Customer", "_ID_Meja", "_ID_Menu",
            "_ID_Pesanan", "_ID_Transaksi", "_ID_Pembayaran"
        ]
        return any(pattern in field for pattern in fk_patterns) or (
            field.startswith("ID_") and field != self.fields[0]
        )

    def get_fk_values(self, field):
        fk_map = {
            "ID_Karyawan": ("KARYAWAN", "ID_Karyawan"),
            "ID_Customer": ("CUSTOMER", "ID_Customer"),
            "ID_Meja": ("MEJA", "ID_Meja"),
            "ID_Menu": ("MENU", "ID_Menu"),
            "ID_Pesanan": ("PESANAN", "ID_Pesanan"),
            "ID_Transaksi": ("TRANSAKSI", "ID_Transaksi"),
        }

        if field in fk_map:
            table, col = fk_map[field]
            conn = get_connection()
            if not conn:
                return []
            try:
                cur = conn.cursor()
                cur.execute(f"SELECT {col} FROM {table}")
                values = [str(row[0]) for row in cur.fetchall()]
                cur.close()
                return values
            except Exception as e:
                print(f"Error fetching FK values for {field} from {table}: {e}")
                return []
            finally:
                conn.close()
        return []

    def load_data(self):
        for field, cb in self.comboboxes.items():
            if self.table_name == "MENU" and field == "Kategori":
                cb["values"] = ["Makanan", "Minuman"]
                if not cb.get():
                    cb.set("Makanan")
            else:
                cb["values"] = self.get_fk_values(field)
                if cb["values"]:
                    cb.set(cb["values"][0])

        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(f"SELECT * FROM {self.table_name}")
                for row in cur.fetchall():
                    self.tree.insert("", "end", values=row)
                cur.close()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memuat data dari {self.table_name}: {e}")
            finally:
                conn.close()

    def get_form_values(self):
        data = []
        for field in self.fields:
            if "tanggal" in field.lower() or "waktu" in field.lower():
                data.append(self.entries[field].get())
            elif field in self.comboboxes:
                data.append(self.comboboxes[field].get())
            elif self.entries[field] is not None:
                data.append(self.entries[field].get())
            else:
                data.append("")
        return data

    def add_data(self):
        data = self.get_form_values()
        for i, field in enumerate(self.fields):
            if ("tanggal" in field.lower() or "waktu" in field.lower()) and data[i]:
                try:
                    data[i] = datetime.datetime.strptime(data[i], "%d-%m-%Y")
                except ValueError:
                    messagebox.showerror("Format Tanggal/Waktu Salah",
                                        f"Kolom {field} harus dalam format dd-mm-yyyy (misal 23-10-2024).")
                    return
        id_field = self.fields[0]
        prefix = get_prefix_for_table(self.table_name)
        data[0] = generate_custom_id(self.table_name, id_field, prefix)

        if any(value == "" for value in data[1:]):
            messagebox.showwarning("Peringatan", "Semua kolom (kecuali ID) harus diisi.")
            return

        placeholders = ",".join(f":{i+1}" for i in range(len(data)))
        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(f"INSERT INTO {self.table_name} VALUES ({placeholders})", data)
                conn.commit()
                cur.close()
                messagebox.showinfo("Sukses", f"Data berhasil ditambahkan!\nID: {data[0]}")
                self.load_data()
                for entry in self.entries.values():
                    if entry:
                        entry.delete(0, tk.END)
                for cb in self.comboboxes.values():
                    if cb["values"]:
                        cb.set(cb["values"][0])
            except Exception as e:
                messagebox.showerror("Error", f"Gagal tambah data: {e}")
            finally:
                conn.close()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        for idx, field in enumerate(self.fields):
            if field in self.comboboxes:
                self.comboboxes[field].set(values[idx])
            elif self.entries[field] is not None:
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, values[idx])

    def edit_data(self):
        data = self.get_form_values()
        update_values = data[1:] + [data[0]]
        set_clause = ", ".join(f"{f} = :{i+1}" for i, f in enumerate(self.fields[1:]))

        pk_value = None
        if self.entries.get(self.fields[0]):
            pk_value = self.entries[self.fields[0]].get()
        elif self.comboboxes.get(self.fields[0]):
            pk_value = self.comboboxes[self.fields[0]].get()

        if not pk_value:
            messagebox.showwarning("Peringatan", "Pilih data yang ingin diedit.")
            return

        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(f"UPDATE {self.table_name} SET {set_clause} WHERE {self.fields[0]} = :{len(self.fields)}", tuple(update_values))
                conn.commit()
                cur.close()
                self.load_data()
                messagebox.showinfo("Sukses", "Data berhasil diupdate.")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal update data: {e}")
            finally:
                conn.close()

    def delete_data(self):
        pk_value = None
        if self.entries.get(self.fields[0]):
            pk_value = self.entries[self.fields[0]].get()
        elif self.comboboxes.get(self.fields[0]):
            pk_value = self.comboboxes[self.fields[0]].get()

        if not pk_value:
            messagebox.showwarning("Peringatan", "Pilih data yang akan dihapus.")
            return

        if not messagebox.askyesno("Konfirmasi", f"Yakin hapus data ID {pk_value}?"):
            return

        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(f"DELETE FROM {self.table_name} WHERE {self.fields[0]} = :1", [pk_value])
                conn.commit()
                cur.close()
                self.load_data()
                messagebox.showinfo("Sukses", "Data berhasil dihapus.")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal hapus data: {e}")
            finally:
                conn.close()
