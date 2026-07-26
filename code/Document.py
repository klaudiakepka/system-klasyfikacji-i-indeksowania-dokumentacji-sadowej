import tkinter as tk

class Document:
    def __init__(self, row):
        self.name = row[0]
        self.syg_akt = row[1]
        self.type = row[2]
        self.date = row[3]
        self.skarzacy = row[4]
        self.przeciwny = row[5]
        self.sad =  row[6]
        self.desc = row[7]
        self.attached = row[8]
        self.flag = row[9]

    def doc_block(self,parent_name):
        block = tk.Frame(parent_name)
        name = tk.Label(block, text=self.name)
        block.pack(fill='x', pady=(10, 0))
        name.pack(side="left", pady=5)