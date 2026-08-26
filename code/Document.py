import sqlite3

class Document:
    col = "name, syg_akt, type, date, skarzacy, przeciwny, sad, desc, attached, flag"
    path = "./data/data.db"

    def __init__(self, row):
        self.name = row[0]
        self.syg_akt = row[1]
        self.type = row[2]
        self.date = row[3]
        self.skarzacy = row[4]
        self.przeciwny = row[5]
        self.court =  row[6]
        self.desc = row[7]
        self.attached = row[8]
        self.flag = row[9]

    @classmethod
    def load(cls, *, name=None, court=None, date=None, flag=None):
        query = f"SELECT {cls.col} FROM documents WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if court:
            query += " AND sad LIKE ?"
            params.append(f"%{court}%")
        if date:
            query += " AND date LIKE ?"
            params.append(f"{date}%")
        if flag is not None:
            query += " AND flag = ?"
            params.append(int(flag))

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

    def toggle_flag(self):
        self.flag = not self.flag
        conn = sqlite3.connect(Document.path)
        try:
            conn.execute("UPDATE documents SET flag = ? WHERE name = ?", (self.flag, self.name))
            conn.commit()
        finally:
            conn.close()