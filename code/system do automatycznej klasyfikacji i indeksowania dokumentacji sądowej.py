import tkinter as tk
import sqlite3
from Document import Document

connection = sqlite3.connect("./data/data.db")
cursor = connection.cursor()
cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                name VARCHAR(100) NOT NULL UNIQUE PRIMARY KEY,
                syg_akt VARCHAR(40) NOT NULL,
                type VARCHAR(40),
                date DATE,
                skarzacy VARCHAR(100),
                przeciwny VARCHAR(100),
                sad VARCHAR(100),
                desc TEXT,
                attached BOOLEAN NOT NULL DEFAULT 0,
                flag BOOLEAN NOT NULL DEFAULT 0
            );""")

def update_data(list):
    list.clear()
    cursor.execute("SELECT * FROM documents")
    rows = cursor.fetchall()
    for row in rows:
        list[row[0]] = Document(row)

root = tk.Tk()
root.geometry("1000x600+200+100")

try:
    searchIcon = tk.PhotoImage(file="searchIcon.png")
except Exception as e:
    searchIcon = '🔍'

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

buttonFrame = tk.Frame(root, pady=10, padx=20)
rightFrame = tk.Frame(root, bg='lightgreen', pady=10, padx=30)
leftFrame = tk.Frame(root, bg='lightblue', width=200)

buttonFrame.grid(row=0, column=1, sticky='nsew')
leftFrame.grid(row=1, column=0, sticky='nsew')
rightFrame.grid(row=1, column=1, sticky='nsew')

addButton = tk.Button(buttonFrame, text="add", width=10)
removeButton = tk.Button(buttonFrame, text='remove', width=10)
searchFrame = tk.Frame(buttonFrame, bg='white')
searchEntry = tk.Entry(searchFrame, width=20, bd=0)
searchButton = tk.Button(searchFrame, bd=0, bg='white',
                         image=searchIcon if isinstance(searchIcon, tk.PhotoImage) else None,
                         text="" if isinstance(searchIcon, tk.PhotoImage) else searchIcon)

addButton.pack(side='right', padx=(10,0))
removeButton.pack(side='right', padx=(0,10))
searchFrame.pack(side='left')
searchEntry.pack(side='right')
searchButton.pack(side='left')

canvas = tk.Canvas(rightFrame)
scrollbar = tk.Scrollbar(rightFrame, orient="vertical", command=canvas.yview)
listFrame = tk.Frame(canvas, bg="pink")

scrollbar.pack(side="right", fill='y')
canvas.pack(fill="both", expand=True)
canvas.configure(yscrollcommand=scrollbar.set)

listFrame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
canvas.create_window((0, 0), window=listFrame, anchor="nw")

doc_list = {}
update_data(doc_list)
for doc in doc_list:
    doc_list[doc].doc_block(listFrame)

root.mainloop()