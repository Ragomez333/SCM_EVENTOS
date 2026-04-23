import sqlite3
from datetime import datetime

DB_NAME = "citas.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            horario TEXT NOT NULL,
            estado TEXT NOT NULL,
            creada_en TEXT NOT NULL,
            actualizada_en TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def guardar_cita(horario: str):
    conn = sqlite3.connect(DB_NAME)
    ahora = datetime.now().isoformat()
    conn.cursor().execute(
        "INSERT INTO citas (horario, estado, creada_en, actualizada_en) VALUES (?, ?, ?, ?)",
        (horario, "activa", ahora, ahora)
    )
    conn.commit()
    conn.close()

def cancelar_cita_db(horario: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE citas SET estado='cancelada', actualizada_en=? WHERE horario=? AND estado='activa'",
        (datetime.now().isoformat(), horario)
    )
    afectadas = cursor.rowcount
    conn.commit()
    conn.close()
    return afectadas > 0

def listar_citas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT horario, estado, creada_en, actualizada_en FROM citas ORDER BY creada_en DESC")
    filas = cursor.fetchall()
    conn.close()
    return [{"horario": f[0], "estado": f[1], "creada_en": f[2], "actualizada_en": f[3]} for f in filas]