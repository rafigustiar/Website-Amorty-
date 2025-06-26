# backend/utils.py
from .db import get_connection

def get_prefix_for_table(table):
    return {
        'CUSTOMER': 'CUS',
        'MEJA': 'MJ',
        'MENU': 'MN',
        'PESANAN': 'PES',
        'PEMBAYARAN': 'PB',
        'RESERVASI': 'RSV',
        'TRANSAKSI': 'TRX',
        'KARYAWAN': 'KAR',
    }.get(table.upper(), 'ID')

def generate_custom_id(table, id_field, prefix):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"SELECT MAX(TO_NUMBER(REGEXP_SUBSTR({id_field}, '\\d+'))) FROM {table} WHERE {id_field} LIKE '{prefix}%'"
        )
        result = cur.fetchone()[0]
        next_number = 1 if result is None else result + 1
        cur.close()
        return f"{prefix}{next_number}"
    except Exception as e:
        print(f"Gagal generate ID untuk {table}: {e}")
    finally:
        if conn:
            conn.close()
    return None
