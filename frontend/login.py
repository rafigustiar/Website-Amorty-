# frontend/login.py
import tkinter as tk
from tkinter import messagebox
from backend.db import get_connection
from frontend.admin import CafeApp
from frontend.customer import CustomerApp

class LoginPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login Aplikasi Cafe Billiard")
        self.geometry("400x250")

        tk.Label(self, text="Pilih Peran").pack(pady=10)
        self.role_var = tk.StringVar(value="Admin")
        tk.Radiobutton(self, text="Admin", variable=self.role_var, value="Admin").pack()
        tk.Radiobutton(self, text="Customer", variable=self.role_var, value="Customer").pack()

        self.user_label = tk.Label(self, text="Username / ID Customer")
        self.user_label.pack(pady=5)
        self.user_entry = tk.Entry(self)
        self.user_entry.pack()

        self.pass_label = tk.Label(self, text="Password")
        self.pass_entry = tk.Entry(self, show="*")

        self.pass_label.pack(pady=5)
        self.pass_entry.pack()

        tk.Button(self, text="Login", command=self.handle_login).pack(pady=10)

        self.role_var.trace("w", self.toggle_password_field)

    def toggle_password_field(self, *args):
        if self.role_var.get() == "Customer":
            self.pass_label.pack_forget()
            self.pass_entry.pack_forget()
        else:
            self.pass_label.pack(pady=5)
            self.pass_entry.pack()

    def handle_login(self):
        role = self.role_var.get()
        username = self.user_entry.get()
        password = self.pass_entry.get()

        if role == "Admin":
            if username == "admin" and password == "admin":
                self.destroy()
                app = CafeApp()
                app.mainloop()
            else:
                messagebox.showerror("Login Gagal", "Username atau password admin salah.")
        else:  # Customer
            if self.verify_customer(username):
                messagebox.showinfo("Login Berhasil", f"Selamat datang Customer ID: {username}")
                self.destroy()
                app = CustomerApp(username)
                app.mainloop()
            else:
                messagebox.showerror("Login Gagal", "ID Customer tidak ditemukan.")

    def verify_customer(self, customer_id):
        conn = None
        try:
            conn = get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM CUSTOMER WHERE ID_Customer = :1", [customer_id])
                count = cur.fetchone()[0]
                cur.close()
                return count > 0
        except Exception as e:
            messagebox.showerror("Database Error", f"Gagal verifikasi ID Customer: {e}")
        finally:
            if conn:
                conn.close()
        return False
