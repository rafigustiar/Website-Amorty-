# backend/db.py
import cx_Oracle
from tkinter import messagebox
from config import ORACLE_LIB_DIR, ORACLE_DSN, DB_USER, DB_PASS

def init_oracle_client():
    try:
        cx_Oracle.init_oracle_client(lib_dir=ORACLE_LIB_DIR)
    except cx_Oracle.Error as e:
        messagebox.showerror("Kesalahan Inisialisasi Oracle Client", str(e))
        exit()

def get_connection():
    try:
        return cx_Oracle.connect(user=DB_USER, password=DB_PASS, dsn=ORACLE_DSN)
    except cx_Oracle.Error as e:
        messagebox.showerror("Kesalahan Koneksi Database", str(e))
        return None
