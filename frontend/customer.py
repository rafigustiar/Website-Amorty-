# frontend/customer.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from backend.db import get_connection
from backend.utils import generate_custom_id

class CustomerApp(tk.Tk):
    def __init__(self, customer_id):
        super().__init__()
        self.customer_id = customer_id
        self.title(f"Aplikasi Customer - ID: {customer_id}")
        self.geometry("1000x600")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.add_menu_tab()
        self.add_meja_tab()
        self.add_pesanan_tab()

    def add_menu_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Daftar Menu")
        tree = ttk.Treeview(frame, columns=('ID_Menu', 'Nama_Menu', 'Harga_Menu', 'Kategori'), show='headings')
        for col in tree['columns']:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill='both', expand=True)
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT ID_Menu, Nama_Menu, Harga_Menu, Kategori FROM MENU")
            for row in cur.fetchall():
                tree.insert('', 'end', values=row)
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data menu: {e}")

        def pesan_menu():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Pilih Menu", "Silakan pilih menu yang ingin dipesan.")
                return
            id_menu = tree.item(selected[0])['values'][0]
            meja_popup = tk.Toplevel(self)
            meja_popup.title("Pilih Meja")
            tk.Label(meja_popup, text="Pilih Meja:").pack(pady=5)
            meja_var = tk.StringVar()
            meja_combo = ttk.Combobox(meja_popup, textvariable=meja_var, state='readonly')

            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT ID_Meja FROM MEJA WHERE Status_Meja = 'KOSONG'")
                meja_list = [row[0] for row in cur.fetchall()]
                cur.close()
                conn.close()
            except Exception as e:
                meja_list = []
                messagebox.showerror("Error", f"Gagal mengambil data meja: {e}")

            meja_combo['values'] = meja_list
            meja_combo.pack(pady=5)
            if meja_list:
                meja_combo.current(0)

            def submit_pesanan():
                if not meja_var.get():
                    messagebox.showwarning("Pilih Meja", "Pilih meja terlebih dahulu!")
                    return
                id_meja = meja_var.get()
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    id_pesanan = generate_custom_id('PESANAN', 'ID_Pesanan', 'PES')
                    waktu = datetime.datetime.now()
                    cur.execute(
                        "INSERT INTO PESANAN (ID_Pesanan, ID_Customer, ID_Meja, ID_Menu, Waktu_Pesanan, ID_Karyawan) VALUES (:1, :2, :3, :4, :5, :6)",
                        [id_pesanan, self.customer_id, id_meja, id_menu, waktu, None]
                    )
                    cur.execute("UPDATE MEJA SET Status_Meja='DIPESAN' WHERE ID_Meja=:1", [id_meja])
                    conn.commit()
                    cur.close()
                    conn.close()
                    messagebox.showinfo("Sukses", "Pesanan berhasil dibuat!")
                    meja_popup.destroy()
                    self.refresh_pesanan_tab()
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal membuat pesanan: {e}")

            tk.Button(meja_popup, text="Pesan", command=submit_pesanan).pack(pady=10)

        btn_pesan = tk.Button(frame, text="Pesan Menu", command=pesan_menu)
        btn_pesan.pack(pady=8)

    def add_meja_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Daftar Meja")
        tree = ttk.Treeview(frame, columns=('ID_Meja', 'Nomor_Meja', 'Status_Meja'), show='headings')
        for col in tree['columns']:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill='both', expand=True)
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT ID_Meja, Nomor_Meja, Status_Meja FROM MEJA")
            for row in cur.fetchall():
                tree.insert('', 'end', values=row)
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data meja: {e}")

    def add_pesanan_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Pesanan Saya")
        tree = ttk.Treeview(frame, columns=('ID_Pesanan', 'ID_Customer', 'Waktu_Pesanan'), show='headings')
        for col in tree['columns']:
            tree.heading(col, text=col)
            tree.column(col, width=180)
        tree.pack(fill='both', expand=True)
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT ID_Pesanan, ID_Customer, Waktu_Pesanan
                FROM PESANAN
                WHERE ID_Customer = :1 OR Customer_ID_Customer = :1
            """, [self.customer_id])
            for row in cur.fetchall():
                tree.insert('', 'end', values=row)
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data pesanan: {e}")

    def refresh_pesanan_tab(self):
        for idx in range(len(self.notebook.tabs())):
            if self.notebook.tab(idx, option="text") == "Pesanan Saya":
                pesanan_frame = self.notebook.nametowidget(self.notebook.tabs()[idx])
                for widget in pesanan_frame.winfo_children():
                    widget.destroy()
                self.add_pesanan_tab()
                break
