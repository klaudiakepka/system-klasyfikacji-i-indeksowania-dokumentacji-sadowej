import tkinter as tk
import sqlite3

def _db_query(query, param=None):
    try:
        connection = sqlite3.connect("./data/data.db")
        cursor = connection.cursor()
        cursor.execute(query, param)
        connection.commit()
        connection.close()
    except sqlite3.Error as e:
        print("database error")

class Document:
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

        self.block = None
        self.state = tk.BooleanVar()

    def doc_block(self,parent_name):
        def __toggle_flag():
            self.flag = not self.flag
            new_color = "red" if self.flag else "grey"
            flag_button.config(fg=new_color)
            _db_query("UPDATE documents SET flag=? WHERE name=?", (self.flag, self.name))

        self.block = tk.Frame(parent_name)
        name = tk.Label(self.block, text=self.name)
        checkbox = tk.Checkbutton(self.block, variable=self.state)
        color = "red" if self.flag else "grey"
        flag_button = tk.Button(self.block, text="⚑", font=("Arial", 12), fg=color, bd=0, relief="flat", command=__toggle_flag)

        self.block.pack(fill='x', pady=(10, 0))
        name.pack(side="left", pady=5)
        checkbox.pack(side="right")
        flag_button.pack(side="right")
        return self.block

    def selected(self):
        return self.state.get()

    def destroy(self):
        if self.block:
            self.block.destroy()
            _db_query("DELETE FROM documents WHERE name=?", (self.name,))
            return self.name