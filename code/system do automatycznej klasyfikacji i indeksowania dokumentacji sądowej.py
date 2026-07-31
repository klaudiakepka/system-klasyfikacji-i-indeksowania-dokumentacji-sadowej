import tkinter as tk
import sqlite3
from Document import Document

try:
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
except sqlite3.Error:
    print("database error")

def update_data(new_list):
    new_list.clear()
    try:
        cursor.execute("SELECT * FROM documents")
        rows = cursor.fetchall()
        for row in rows:
            new_list[row[0]] = Document(row)
    except sqlite3.Error:
        print("database error")

root = tk.Tk()
root.geometry("1000x600+200+100")

try:
    searchIcon = tk.PhotoImage(file="searchIcon.png")
except Exception:
    searchIcon = '🔍'

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

button_frame = tk.Frame(root, pady=10, padx=20, bg="lightpink")
right_frame = tk.Frame(root, bg='lightgreen', pady=10)
left_frame = tk.Frame(root, bg='lightblue')

button_frame.grid(row=0, column=1, sticky='nsew')
left_frame.grid(row=1, column=0, sticky='nsew')
right_frame.grid(row=1, column=1, sticky='nsew')

add_button = tk.Button(button_frame, text="add", width=10)
remove_button = tk.Button(button_frame, text='remove', width=10)
search_frame = tk.Frame(button_frame, bg='white')
search_entry = tk.Entry(search_frame, width=20, bd=0)
search_button = tk.Button(search_frame, bd=0, bg='white',
                          image=searchIcon if isinstance(searchIcon, tk.PhotoImage) else None,
                          text="" if isinstance(searchIcon, tk.PhotoImage) else searchIcon)

add_button.pack(side='right', padx=(10, 0))
remove_button.pack(side='right', padx=(0, 10))
search_frame.pack(side='left')
search_entry.pack(side='right')
search_button.pack(side='left')

left_canvas = tk.Canvas(left_frame, highlightthickness=0, bg="blue")
filter_frame = tk.Frame(left_canvas, bg="lightblue")

left_canvas.pack(pady=20, padx=20, fill="both", expand=True)
left_canvas.create_window(0,0, window=filter_frame, anchor="nw")
filter_frame.bind("<Configure>", lambda e: left_canvas.config(width=e.width))






right_canvas = tk.Canvas(right_frame, highlightthickness=0, bg="lightgreen")
right_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=right_canvas.yview)
list_frame = tk.Frame(right_canvas, bg="lightgreen")

right_scrollbar.pack(side="right", fill='y', padx=(0, 5))
right_canvas.pack(fill="both", expand=True, padx=20)
right_canvas.configure(yscrollcommand=right_scrollbar.set)
list_id = right_canvas.create_window((0, 0), window=list_frame, anchor="nw")
list_frame.bind("<Configure>", lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all")))
right_canvas.bind("<Configure>", lambda e: right_canvas.itemconfig(list_id, width=e.width))

doc_list = {}
update_data(doc_list)
for doc in doc_list:
    doc_list[doc].doc_block(list_frame)

def remove():
    removed = []
    for doc in doc_list:
        if doc_list[doc].selected():
            removed.append(doc_list[doc].destroy())
    for name in removed:
        del doc_list[name]

remove_button.config(command=remove)

root.mainloop()