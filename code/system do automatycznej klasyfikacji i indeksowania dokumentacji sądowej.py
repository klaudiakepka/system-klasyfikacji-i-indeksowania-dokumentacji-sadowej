import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from Document import Document
from AutoEntry import AutoEntry
from DropBox import DropBox

class TkinterDnD_CTk(TkinterDnD.Tk, ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

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
    return '.'

name_var = ctk.StringVar()
flag_var = ctk.StringVar(value="all")
attached_var = ctk.StringVar(value="all")
start_date_var = ctk.StringVar()
end_date_var = ctk.StringVar()
court_var = ctk.StringVar()
sides_var = ctk.StringVar()
doctype_var = ctk.StringVar()

def apply_filters(event = None):
    filters = {}

    name = name_var.get().strip()
    if name:
        filters["name"] = name
    flag = flag_var.get()
    if flag == "yes":
        filters["flag"] = True
    elif flag == "no":
        filters["flag"] = False
    attached = attached_var.get()
    if attached == "yes":
        filters["attached"] = True
    elif attached == "no":
        filters["attached"] = False

    start_date = start_date_var.get()
    if start_date:
        filters["start_date"] = start_date
    end_date = end_date_var.get()
    if end_date:
        filters["end_date"] = end_date

    court = court_var.get().strip()
    if court:
        filters["court"] = court
    side = sides_var.get().strip()
    if side:
        filters["side"] = side
    doctype = doctype_var.get().strip()
    if doctype:
        filters["doctype"] = doctype

    refresh(**filters)

main_top = tk.Frame(top_frame, bg=bg1)
new_button = tk.Button(main_top, text="new", width=10, command=lambda n="add": view(n))
remove_button_m = tk.Button(main_top, text='remove', width=10, command=remove)
search_frame = tk.Frame(main_top, bg='white')
search_entry = ctk.CTkEntry(search_frame, textvariable=name_var, placeholder_text="tytuł pliku", border_width=0)
search_entry.bind("<Return>", apply_filters)
search_button = tk.Button(search_frame, bd=0, bg='white', text='🔍', command=apply_filters)
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

def filter_block(parent, title):
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

def toggle(clicked, var, yes_var, no_var):
    if clicked == "yes" and yes_var.get() == 1:
        no_var.set(0)
        var.set("yes")
    elif clicked == "no" and no_var.get() == 1:
        yes_var.set(0)
        var.set("no")
    else:
        var.set("all")

flag_yes_var = ctk.IntVar(value=0)
flag_no_var = ctk.IntVar(value=0)
flag_filter = filter_block(filter_frame, "flag")
flag_yes = ctk.CTkCheckBox(flag_filter, text="Tak", variable=flag_yes_var, fg_color=bg3, text_color="black",
                           command=lambda: toggle("yes", flag_var, flag_yes_var, flag_no_var))
flag_no = ctk.CTkCheckBox(flag_filter, text="Nie", variable=flag_no_var, fg_color=bg3, text_color="black",
                          command=lambda: toggle("no", flag_var, flag_yes_var, flag_no_var))
flag_yes.pack()
flag_no.pack()

att_yes_var = ctk.IntVar(value=0)
att_no_var = ctk.IntVar(value=0)
att_filter = filter_block(filter_frame, "attachments")
att_yes = ctk.CTkCheckBox(att_filter, variable=att_yes_var, text="Tak", fg_color=bg3,
                        command=lambda: toggle("yes", attached_var, att_yes_var, att_no_var))
att_no = ctk.CTkCheckBox(att_filter, variable=att_no_var, text="Nie", fg_color=bg3,
                        command=lambda: toggle("no", attached_var, att_yes_var, att_no_var))
att_yes.pack()
att_no.pack()

def clear_date():
    start_date_entry.config(state='normal')
    start_date_entry.delete(0, 'end')
    start_date_entry.config(state='readonly')

    end_date_entry.config(state='normal')
    end_date_entry.delete(0, 'end')
    end_date_entry.config(state='readonly')

date_filter = filter_block(filter_frame, "data")
input_block = tk.Frame(date_filter, bg=bg3)
start_date_entry = DateEntry(input_block, width=9, font=('Inter', 8), locale='pl_PL', showweeknumbers=False,
                             showothermonthdays=False, state="readonly")
end_date_entry = DateEntry(input_block, width=9, font=('Helvetica', 8), locale='pl_PL', showweeknumbers=False,
                           showothermonthdays=False, state="readonly")
spacing = tk.Label(input_block, text='-', bg=bg3)
clear_button = tk.Button(date_filter, text="clear", command=clear_date)
input_block.pack(expand=True)
start_date_entry.pack(side="left")
spacing.pack(side="left")
end_date_entry.pack(side="left")
clear_button.pack(anchor='w', pady=(5,0), padx=5)
clear_date()

court_filter = filter_block(filter_frame, "sąd")
court_search = AutoEntry(court_filter, Document.dist_courts(), textvariable=court_var)
court_search.pack()

side_filter = filter_block(filter_frame, "strona sporu")
side_search = AutoEntry(side_filter, Document.dist_sides(), textvariable=sides_var)
side_search.pack()

doctype_filter = filter_block(filter_frame, "typ")
doctype_search = AutoEntry(doctype_filter, Document.dist_types(), textvariable=doctype_var)
doctype_search.pack()

filter_button = ctk.CTkButton(filter_frame, text="filter", command=apply_filters)
filter_button.pack(anchor='e')
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

def doc_block_build(doc, parent):
    def _toggle_flag():
        doc.toggle_flag()
        flag_button.configure(text_color="red" if doc.flag else "gray")

    doc_block = ctk.CTkFrame(parent)
    main_button = ctk.CTkButton(doc_block, text=doc.name, anchor='w', command=lambda n="edit": view(n))
    flag_button = ctk.CTkButton(doc_block, text="⚑", width=30, text_color="red" if doc.flag else "gray",
                                command=_toggle_flag)
    checkbox = ctk.CTkCheckBox(doc_block, text="", width=0)
    doc_block.pack(fill='x', padx=2)
    main_button.pack(side="left", fill='x', expand=True)
    flag_button.pack(side="right")
    checkbox.pack(side="right")

    return doc_block

def refresh(**filters):
    for child in main_right.winfo_children():
        child.destroy()

    documents = Document.load(**filters)
    if not documents:
        empty_label = ctk.CTkLabel(main_right, text="brak dokumentów spełniających kryteria")
        empty_label.pack(expand=True, fill='x')
        return
    for document in documents:
        block = doc_block_build(document, main_right)
#----------------------------------------------------------------------------------------------------------------------------

add_right = ctk.CTkScrollableFrame(right_frame, fg_color=bg2)
ai_switch = ctk.CTkSwitch(add_right, text="auto fill", text_color="black")
name_label = tk.Label(add_right, text="nazwa", bg=bg2, font=("", 10, "bold"))
name_entry = tk.Entry(add_right)
syg_akt_label = tk.Label(add_right, text="sygnatura akt", bg=bg2, font=("", 10, "bold"))
syg_akt_entry = tk.Entry(add_right)
doctype_label = tk.Label(add_right, text="typ", bg=bg2, font=("", 10, "bold"))
doctype_entry = tk.Entry(add_right)
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
doctype_label.pack(anchor='w')
doctype_entry.pack(fill='x', pady=(0, 10))
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
refresh()
root.mainloop()