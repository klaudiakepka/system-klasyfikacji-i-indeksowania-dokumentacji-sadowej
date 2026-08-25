import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
import sqlite3
from Document import Document
from AutoEntry import AutoEntry
from DropBox import DropBox

class TkinterDnD_CTk(TkinterDnD.Tk, ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

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

root = TkinterDnD_CTk()
root.geometry("1000x600+200+100")
root.bind_all("<Button-1>", lambda e: None if isinstance(e.widget, tk.Entry) else root.focus())
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

bg1 = "lightpink"
bg2 = "lightgreen"
bg3 = "lightblue"

top_frame = tk.Frame(root, pady=10, padx=20, bg=bg1)
right_frame = tk.Frame(root, bg=bg2, pady=10)
left_frame = tk.Frame(root, bg=bg3)
top_frame.grid(row=0, column=1, sticky='nsew')
top_frame.grid_rowconfigure(0, weight=1)
top_frame.grid_columnconfigure(0, weight=1)
right_frame.grid(row=1, column=1, sticky='nsew')
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_columnconfigure(0, weight=1)
left_frame.grid(row=1, column=0, sticky='nsew')
left_frame.grid_rowconfigure(0, weight=1)
left_frame.grid_columnconfigure(0, weight=1)

def view(name):
    if name == "main":
        top_frame.grid(column=1, columnspan=1)
        main_top.grid()
        main_right.grid()
        main_left.grid()
        add_top.grid_remove()
        add_right.grid_remove()
        add_left.grid_remove()
        edit_top.grid_remove()
        edit_left.grid_remove()
    elif name == "add":
        top_frame.grid(column=0, columnspan=2)
        add_top.grid()
        add_right.grid()
        add_left.grid()
        main_top.grid_remove()
        main_right.grid_remove()
        main_left.grid_remove()
        edit_top.grid_remove()
        edit_left.grid_remove()
    elif name == "edit":
        top_frame.grid(column=0, columnspan=2)
        edit_top.grid()
        add_right.grid()
        edit_left.grid()
        main_top.grid_remove()
        main_right.grid_remove()
        main_left.grid_remove()
        add_top.grid_remove()
        add_left.grid_remove()



#----------------------------------------------------------------------------------------------------------------------------

def remove():
    global doc
    removed = []
    for doc in doc_list:
        if doc_list[doc].selected():
            removed.append(doc_list[doc].destroy())
    for name in removed:
        del doc_list[name]

main_top = tk.Frame(top_frame, bg=bg1)
new_button = tk.Button(main_top, text="new", width=10, command=lambda n="add": view(n))
remove_button_m = tk.Button(main_top, text='remove', width=10, command=remove)
search_frame = tk.Frame(main_top, bg='white')
search_entry = tk.Entry(search_frame, width=20, bd=0)
search_button = tk.Button(search_frame, bd=0, bg='white', text='🔍')
main_top.grid(row=0, column=0, sticky="nsew")
new_button.pack(side='right', padx=(10, 0))
remove_button_m.pack(side='right', padx=(0, 10))
search_frame.pack(side='left')
search_entry.pack(side='right')
search_button.pack()
#----------------------------------------------------------------------------------------------------------------------------

add_top = tk.Frame(top_frame, bg=bg1)
cancel_button_a = tk.Button(add_top, text="cancel", width=10, command=lambda n="main": view(n))
add_label = tk.Label(add_top, text="Dodaj nowy dokumet", font=("",15), bg=bg1)
add_button = tk.Button(add_top, text="add", width=10)
add_top.grid(row=0, column=0, sticky="nsew")
cancel_button_a.pack(side="left")
add_label.pack(side="left", expand=True)
add_button.pack(side="right")
#----------------------------------------------------------------------------------------------------------------------------

edit_top = tk.Frame(top_frame, bg=bg1)
remove_button_e = tk.Button(edit_top, text="remove", width=10)
save_button = tk.Button(edit_top, text="save", width=10)
cancel_button_e = tk.Button(edit_top, text="cancel", width=10, command=lambda n="main": view(n))
edit_top.grid(row=0, column=0, sticky="nsew")
remove_button_e.pack(side="right", padx=(10,0))
save_button.pack(side="right", padx=(0,10))
cancel_button_e.pack(side="left")
#----------------------------------------------------------------------------------------------------------------------------



main_left = tk.Canvas(left_frame, highlightthickness=0, bg=bg3)
filter_frame = tk.Frame(main_left, bg=bg3)
main_left.grid(row=0, column=0, sticky="nesw", pady=20, padx=(10, 0))
main_left.create_window(0, 0, window=filter_frame, anchor="nw")
filter_frame.bind("<Configure>", lambda e: main_left.config(width=e.width))

def filter_section(parent, title):
    def toggle_visibility():
        if content.winfo_ismapped():
            content.pack_forget()
            header.config(text=f"▶ {title}")
        else:
            content.pack(anchor="w", padx=(20,0), pady=(5,0), after=header)
            header.config(text=f"▼ {title}")

    header = tk.Button(parent, text=f"▶ {title}", width=30, anchor="w", borderwidth=0, bg=bg3,
                       activebackground=bg3, command=toggle_visibility)
    header.pack()
    ttk.Separator(parent, orient="horizontal").pack(fill='x', padx=10, pady=5)
    content = tk.Frame(parent, bg=bg3)
    return content

flag_filter = filter_section(filter_frame, "flag")
flag_yes = tk.Checkbutton(flag_filter, text="Tak", bg=bg3, borderwidth=0)
flag_no = tk.Checkbutton(flag_filter, text="Nie", bg=bg3, borderwidth=0)
flag_yes.pack()
flag_no.pack()

att_filter = filter_section(filter_frame, "attachments")
att_yes = tk.Checkbutton(att_filter, text="Tak", bg=bg3, borderwidth=0)
att_no = tk.Checkbutton(att_filter, text="Nie", bg=bg3, borderwidth=0)
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
input_block = tk.Frame(date_filter, bg=bg3)
start_date = DateEntry(input_block, width=9, font=('Inter', 8), locale='pl_PL', showweeknumbers=False,
                       showothermonthdays=False, state="readonly")
end_date = DateEntry(input_block, width=9, font=('Helvetica', 8), locale='pl_PL', showweeknumbers=False,
                     showothermonthdays=False, state="readonly")
spacing = tk.Label(input_block, text='-', bg=bg3)
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
#----------------------------------------------------------------------------------------------------------------------------

add_left = tk.Frame(left_frame, bg=bg3)

def add_doc(filepaths):
    return

drop_box_frame = tk.Frame(add_left, bg=bg3)
drop_box = DropBox(drop_box_frame, on_drop=add_doc)
drop_box_frame.pack(expand=True)
drop_box.pack(padx=20)
add_left.grid(row=0, column=0, sticky="nesw")
#----------------------------------------------------------------------------------------------------------------------------

edit_left = tk.Frame(left_frame, bg=bg3, width=400)
edit_left.grid(row=0, column=0, sticky="nesw")
#----------------------------------------------------------------------------------------------------------------------------



main_right = ctk.CTkScrollableFrame(right_frame, fg_color=bg2)
main_right.grid(row=0, column=0, sticky="nsew", padx=(20,0))

doc_list = {}
for row in data:
    doc_list[row[0]] = Document(row)
for doc in doc_list:
    doc_list[doc].doc_block(main_right).config(command=lambda n="edit": view(n))
    ttk.Separator(main_right, orient="horizontal").pack(fill='x', pady=(0,5))
#----------------------------------------------------------------------------------------------------------------------------

add_right = ctk.CTkScrollableFrame(right_frame, fg_color=bg2)
ai_switch = ctk.CTkSwitch(add_right, text="auto fill", text_color="black")
name_label = tk.Label(add_right, text="nazwa", bg=bg2, font=("", 10, "bold"))
name_entry = tk.Entry(add_right)
syg_akt_label = tk.Label(add_right, text="sygnatura akt", bg=bg2, font=("", 10, "bold"))
syg_akt_entry = tk.Entry(add_right)
type_label = tk.Label(add_right, text="typ", bg=bg2, font=("", 10, "bold"))
type_entry = tk.Entry(add_right)
data_label = tk.Label(add_right, text="data", bg=bg2, font=("", 10, "bold"))
data_entry = tk.Entry(add_right)
strona1_label = tk.Label(add_right, text="strona skarżąca", bg=bg2, font=("", 10, "bold"))
strona1_entry = tk.Entry(add_right)
strona2_label = tk.Label(add_right, text="strona przeciwna", bg=bg2, font=("", 10, "bold"))
strona2_entry = tk.Entry(add_right)
court_label = tk.Label(add_right, text="sąd", bg=bg2, font=("", 10, "bold"))
court_entry = tk.Entry(add_right)
desc_label = tk.Label(add_right, text="opis", bg=bg2, font=("", 10, "bold"))
desc_entry = tk.Text(add_right, height=5)
add_right.grid(row=0, column=0, sticky="nsew", padx=(20,0))
name_label.pack(anchor='w')
name_entry.pack(fill='x', pady=(0,10))
syg_akt_label.pack(anchor='w')
syg_akt_entry.pack(fill='x', pady=(0,10))
type_label.pack(anchor='w')
type_entry.pack(fill='x', pady=(0,10))
data_label.pack(anchor='w')
data_entry.pack(fill='x', pady=(0,10))
strona1_label.pack(anchor='w')
strona1_entry.pack(fill='x', pady=(0,10))
strona2_label.pack(anchor='w')
strona2_entry.pack(fill='x', pady=(0,10))
court_label.pack(anchor='w')
court_entry.pack(fill='x', pady=(0,10))
desc_label.pack(anchor='w')
desc_entry.pack(fill='x', pady=(0,10))
ai_switch.pack(anchor='w')
#----------------------------------------------------------------------------------------------------------------------------



view("main")
root.mainloop()