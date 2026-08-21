import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import sqlite3
from Document import Document
from AutoEntry import AutoEntry

courts = []
sides = []
types = []
data = ""

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

    cursor.execute("SELECT DISTINCT sad FROM documents")
    courts_raw = cursor.fetchall()
    courts = [row[0] for row in courts_raw]

    cursor.execute("""SELECT DISTINCT skarzacy FROM documents UNION SELECT DISTINCT przeciwny FROM documents""")
    sides_raw = cursor.fetchall()
    sides = [row[0] for row in sides_raw]

    cursor.execute("SELECT DISTINCT type FROM documents")
    types_raw = cursor.fetchall()
    types = [row[0] for row in types_raw]

    cursor.execute("SELECT * FROM documents")
    data = cursor.fetchall()

    connection.close()
except sqlite3.Error:
    print("database error")

root = tk.Tk()
root.geometry("1000x600+200+100")
root.bind_all("<Button-1>", lambda e: None if isinstance(e.widget, tk.Entry) else root.focus())
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

top_frame = tk.Frame(root, pady=10, padx=20, bg="lightpink")
right_frame = tk.Frame(root, bg='lightgreen', pady=10)
left_frame = tk.Frame(root, bg='lightblue')
top_frame.grid(row=0, column=1, sticky='nsew')
top_frame.grid_rowconfigure(0, weight=1)
top_frame.grid_columnconfigure(0, weight=1)
right_frame.grid(row=1, column=1, sticky='nsew')
left_frame.grid(row=1, column=0, sticky='nsew')

def view(name):
    if name == "main":
        top_frame.grid(column=1, columnspan=1)
    else:
        top_frame.grid(column=0, columnspan=2)

    tk.Misc.tkraise(top_block[name])

top_block = {}

main_top = tk.Frame(top_frame, bg="lightpink")
new_button = tk.Button(main_top, text="new", width=10, command=lambda n="add": view(n))
remove_button_m = tk.Button(main_top, text='remove', width=10)
search_frame = tk.Frame(main_top, bg='white')
search_entry = tk.Entry(search_frame, width=20, bd=0)
search_button = tk.Button(search_frame, bd=0, bg='white', text='🔍')
main_top.grid(row=0, column=0, sticky="nsew")
new_button.pack(side='right', padx=(10, 0))
remove_button_m.pack(side='right', padx=(0, 10))
search_frame.pack(side='left')
search_entry.pack(side='right')
search_button.pack()
top_block["main"] = main_top

add_top = tk.Frame(top_frame, bg="lightpink")
cancel_button_a = tk.Button(add_top, text="cancel", width=10, command=lambda n="main": view(n))
add_label = tk.Label(add_top, text="add new document", font=("",15), bg="lightpink")
add_button = tk.Button(add_top, text="add", width=10)
add_top.grid(row=0, column=0, sticky="nsew")
cancel_button_a.pack(side="left")
add_label.pack(side="left", expand=True)
add_button.pack(side="right")
top_block["add"] = add_top

edit_top = tk.Frame(top_frame, bg="lightpink")
remove_button_e = tk.Button(edit_top, text="remove", width=10)
save_button = tk.Button(edit_top, text="save", width=10)
cancel_button_e = tk.Button(edit_top, text="cancel", width=10, command=lambda n="main": view(n))
edit_top.grid(row=0, column=0, sticky="nsew")
remove_button_e.pack(side="right", padx=(10,0))
save_button.pack(side="right", padx=(0,10))
cancel_button_e.pack(side="left")
top_block["edit"] = edit_top





left_canvas = tk.Canvas(left_frame, highlightthickness=0, bg="lightblue")
filter_frame = tk.Frame(left_canvas, bg="lightblue")
left_canvas.pack(pady=20, padx=(10,0), fill="both", expand=True)
left_canvas.create_window(0,0, window=filter_frame, anchor="nw")
filter_frame.bind("<Configure>", lambda e: left_canvas.config(width=e.width))

def filter_section(parent, title):
    def toggle_visibility():
        if content.winfo_ismapped():
            content.pack_forget()
            header.config(text=f"▶ {title}")
        else:
            content.pack(anchor="w", padx=(20,0), pady=(5,0), after=header)
            header.config(text=f"▼ {title}")

    header = tk.Button(parent, text=f"▶ {title}", width=30, anchor="w", borderwidth=0,bg="lightblue",
                       activebackground="lightblue", command=toggle_visibility)
    header.pack()
    ttk.Separator(parent, orient="horizontal").pack(fill='x', padx=10, pady=5)
    content = tk.Frame(parent, bg="lightblue")
    return content

flag_filter = filter_section(filter_frame, "flag")
flag_yes = tk.Checkbutton(flag_filter, text="Tak", bg="lightblue", borderwidth=0)
flag_no = tk.Checkbutton(flag_filter, text="Nie", bg="lightblue", borderwidth=0)
flag_yes.pack()
flag_no.pack()

att_filter = filter_section(filter_frame, "attachments")
att_yes = tk.Checkbutton(att_filter, text="Tak", bg="lightblue", borderwidth=0)
att_no = tk.Checkbutton(att_filter, text="Nie", bg="lightblue", borderwidth=0)
att_yes.pack()
att_no.pack()

def clear_date():
    start_date.config(state='normal')
    start_date.delete(0, 'end')
    start_date.config(state='readonly')

    end_date.config(state='normal')
    end_date.delete(0, 'end')
    end_date.config(state='readonly')

date_filter = filter_section(filter_frame, "data")
input_block = tk.Frame(date_filter, bg="lightblue")
start_date = DateEntry(input_block, width=9, font=('Inter', 8), locale='pl_PL', showweeknumbers=False,
                       showothermonthdays=False, state="readonly")
end_date = DateEntry(input_block, width=9, font=('Helvetica', 8), locale='pl_PL', showweeknumbers=False,
                     showothermonthdays=False, state="readonly")
spacing = tk.Label(input_block, text='-', bg="lightblue")
clear_button = tk.Button(date_filter, text="clear", command=clear_date)
input_block.pack(expand=True)
start_date.pack(side="left")
spacing.pack(side="left")
end_date.pack(side="left")
clear_button.pack(anchor='w', pady=(5,0), padx=5)
clear_date()

court_filter = filter_section(filter_frame, "sąd")
court_search = AutoEntry(court_filter, courts)
court_search.pack()

side_filter = filter_section(filter_frame, "strona sporu")
side_search = AutoEntry(side_filter, sides)
side_search.pack()

type_filter = filter_section(filter_frame, "typ")
type_search = AutoEntry(type_filter, types)
type_search.pack()

right_canvas = tk.Canvas(right_frame, highlightthickness=0, bg="lightgreen")
right_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=right_canvas.yview)
list_frame = tk.Frame(right_canvas)
right_scrollbar.pack(side="right", fill='y', padx=(0, 5))
right_canvas.pack(fill="both", expand=True, padx=20)
right_canvas.configure(yscrollcommand=right_scrollbar.set)
list_id = right_canvas.create_window((0, 0), window=list_frame, anchor="nw")
list_frame.bind("<Configure>", lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all")))
right_canvas.bind("<Configure>", lambda e: right_canvas.itemconfig(list_id, width=e.width))

doc_list = {}
for row in data:
    doc_list[row[0]] = Document(row)
for doc in doc_list:
    doc_list[doc].doc_block(list_frame)

def remove():
    global doc
    removed = []
    for doc in doc_list:
        if doc_list[doc].selected():
            removed.append(doc_list[doc].destroy())
    for name in removed:
        del doc_list[name]

remove_button_m.config(command=remove)



















view("edit")
root.mainloop()