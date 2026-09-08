import sqlite3
import os
from datetime import date

class Document:
    col = "name, syg_akt, type, date, skarzacy, przeciwny, sad, desc, attached, flag"
    path = "./data/data.db"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    _conn = sqlite3.connect(path)
    try:
        _conn.execute("""CREATE TABLE IF NOT EXISTS documents ("name" VARCHAR(255) NOT NULL PRIMARY KEY, 
            "syg_akt" VARCHAR(100) NOT NULL, "type" VARCHAR(50), "date" DATE,"skarzacy" VARCHAR(255), 
            "przeciwny" VARCHAR(255), "sad" VARCHAR(255), "desc" TEXT, "attached" BOOLEAN NOT NULL DEFAULT 0, 
            "flag" BOOLEAN NOT NULL DEFAULT 0)""")
        _conn.commit()
    finally:
        _conn.close()
    del _conn

    def __init__(self, row):
        self.name = row[0]
        self.syg_akt = row[1]
        self.doctype = row[2]
        self.date = row[3]
        self.skarzacy = row[4]
        self.przeciwny = row[5]
        self.court =  row[6]
        self.desc = row[7]
        self.attached = row[8]
        self.flag = row[9]
        self.to_remove = False

    @classmethod
    def load(cls, *, flag=None, attached=None, start_date=None, end_date=None, name=None, court=None,
             side=None, doctype=None, syg_akt=None):
        query = f"SELECT {cls.col} FROM documents WHERE 1=1"
        params = []

        if flag is not None:
            query += " AND flag = ?"
            params.append(int(flag))
        if attached is not None:
            query += " AND attached = ?"
            params.append(int(attached))
        if start_date and end_date:
            query += " AND date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        elif start_date:
            query += " AND date >= ?"
            params.append(start_date)
        elif end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if court:
            query += " AND sad LIKE ?"
            params.append(f"%{court}%")
        if side:
            query += " AND (skarzacy LIKE ? OR przeciwny LIKE ?)"
            params.extend([f"%{side}%", f"%{side}%"])
        if doctype:
            query += " AND type LIKE ?"
            params.append(f"%{doctype}%")
        if syg_akt:
            query += " AND syg_akt LIKE ?"
            params.append(f"%{syg_akt}%")
        query += " ORDER BY date DESC"

        conn = sqlite3.connect(cls.path)
        try:
            rows = conn.execute(query, params).fetchall()
        finally:
            conn.close()

        return [cls(row) for row in rows]

    @classmethod
    def dist_courts(cls):
        conn = sqlite3.connect(cls.path)
        try:
            rows = conn.execute("SELECT DISTINCT sad FROM documents ORDER BY sad").fetchall()
        finally:
            conn.close()
        return [row[0] for row in rows]

    @classmethod
    def dist_types(cls):
        conn = sqlite3.connect(cls.path)
        try:
            rows = conn.execute("SELECT DISTINCT type FROM documents ORDER BY type").fetchall()
        finally:
            conn.close()
        return [row[0] for row in rows]

    @classmethod
    def dist_sides(cls):
        conn = sqlite3.connect(cls.path)
        try:
            rows = conn.execute("SELECT skarzacy AS side FROM documents "
                                "UNION SELECT przeciwny FROM documents ORDER BY side;").fetchall()
        finally:
            conn.close()
        return [row[0] for row in rows]

    @classmethod
    def add(cls, name, syg_akt, doctype='', date=None, skarzacy='', przeciwny='', sad='', desc='', attached=0):
        conn = sqlite3.connect(cls.path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM documents WHERE name = ?", (name,))
            if cursor.fetchone() is not None:
                return "dokument o tej nazwie już istnieje"

            cursor.execute("INSERT INTO documents (name, syg_akt, type, date, skarzacy, przeciwny, "
                           "sad, desc, attached) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (name, syg_akt, doctype, date, skarzacy, przeciwny, sad, desc, attached))
            conn.commit()
        finally:
            conn.close()
        return ""

    def toggle_flag(self):
        self.flag = not self.flag
        conn = sqlite3.connect(Document.path)
        try:
            conn.execute("UPDATE documents SET flag = ? WHERE name = ?", (self.flag, self.name))
            conn.commit()
        finally:
            conn.close()

    def checkbox_state(self, state):
        self.to_remove = (state == 1)

    def remove_check(self):
        if self.to_remove:
            self.remove()

    def remove(self):
        conn = sqlite3.connect(Document.path)
        try:
            conn.execute("DELETE FROM documents WHERE name = ?", (self.name,))
            conn.commit()
        finally:
            conn.close()

    def change(self, name, syg_akt, doctype='', date='', skarzacy='', przeciwny='', court='', desc='', attached=0):
        conn = sqlite3.connect(Document.path)
        try:
            cursor = conn.cursor()
            changes = []
            params = []
            old_name = self.name

            if name != self.name:
                cursor.execute("SELECT 1 FROM documents WHERE name = ?", (name,))
                if cursor.fetchone() is not None:
                    return "dokument o tej nazwie już istnieje"
                changes.append("name = ?")
                params.append(name)
                self.name = name
            if syg_akt != self.syg_akt:
                changes.append("syg_akt = ?")
                params.append(syg_akt)
                self.syg_akt = syg_akt
            if doctype != self.doctype:
                changes.append("type = ?")
                params.append(doctype)
                self.doctype = doctype
            if date.isoformat() != self.date:
                changes.append("date = ?")
                params.append(date.isoformat())
                self.date = date.isoformat()
            if skarzacy != self.skarzacy:
                changes.append("skarzacy = ?")
                params.append(skarzacy)
                self.skarzacy = skarzacy
            if przeciwny != self.przeciwny:
                changes.append("przeciwny = ?")
                params.append(przeciwny)
                self.przeciwny = przeciwny
            if court != self.court:
                changes.append("sad = ?")
                params.append(court)
                self.court = court
            if desc != self.desc:
                changes.append("desc = ?")
                params.append(desc)
                self.desc = desc
            if attached == 1 and attached != self.attached:
                changes.append("attached = ?")
                params.append(attached)
                self.attached = attached
            params.append(old_name)

            if changes:
                cursor.execute(f"UPDATE documents SET {', '.join(changes)} WHERE name = ?", params)
                conn.commit()
        finally:
            conn.close()
        return ""

