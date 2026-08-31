import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from datetime import datetime
import os
import tempfile
from pathlib import Path
from Document import Document
from AutoEntry import AutoEntry
from DropBox import DropBox
class TkinterDnD_CTk(TkinterDnD.Tk, ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

root = TkinterDnD_CTk()
ctk.set_appearance_mode("Light")
root.geometry("1000x650+200+100")
root.bind("<Button-1>", lambda e: None if isinstance(e.widget, tk.Entry) else root.focus())
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

ctk.ThemeManager.theme["CTkButton"]["text_color"] = "black"
bg1 = "lightpink"
bg2 = "lightgreen"
bg3 = "lightblue"

top_frame = ctk.CTkFrame(root, fg_color=bg1)
right_frame = ctk.CTkFrame(root, fg_color=bg2)
left_frame = ctk.CTkFrame(root, fg_color=bg3)
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
        error_label.configure(text="")
        clear_add_form()
        refresh()
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

main_top = ctk.CTkFrame(top_frame, fg_color=bg1)
new_button = ctk.CTkButton(main_top, text="new", width=30, command=lambda n="add": view(n))
remove_button_m = ctk.CTkButton(main_top, text='remove', width=30)
search_frame = ctk.CTkFrame(main_top, fg_color='white')
search_entry = ctk.CTkEntry(search_frame, textvariable=name_var, border_width=0, fg_color="white")
search_entry.bind("<Return>", apply_filters)
search_button = ctk.CTkButton(search_frame, border_width=0, fg_color='white', text='🔍', command=apply_filters, width=5)
main_top.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
new_button.pack(side='right', padx=(10, 0))
remove_button_m.pack(side='right', padx=(0, 10))
search_frame.pack(side='left')
search_entry.pack(side='right')
search_button.pack()
#----------------------------------------------------------------------------------------------------------------------------

def add():
    name = name_entry.get().strip()
    syg_akt = syg_akt_entry.get().strip()
    doctype = doctype_entry.get().strip()
    date = date_entry.get()
    side1 = side1_entry.get().strip()
    side2 = side2_entry.get().strip()
    court = court_entry.get().strip()
    desc = desc_entry.get("1.0", "end-1c").strip()

    if not name or not syg_akt:
        error_label.configure(text="nie wprowadzono nazwy lub sygnatury akt")
        return False
    data = {"name": name, "syg_akt": syg_akt}

    path = current_file["path"]
    if path:
        ext = current_file["ext"]
        if not name.lower().endswith(ext.lower()):
            name += ext

        new_path = os.path.join(os.path.dirname(path), name)
        if os.path.normcase(new_path) != os.path.normcase(path):
            if os.path.exists(new_path):
                error_label.configure(text="plik o takiej nazwie już istnieje")
                return False
            try:
                os.rename(path, new_path)
            except OSError as e:
                error_label.configure(text=f"nie udało się zmienić nazwy pliku: {e}")
                return False
            current_file["path"] = new_path
    data.update({"attached": 1})

    if doctype:
        data.update({"doctype": doctype})
    if date:
        try:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            data.update({"date": date})
        except ValueError:
            error_label.configure(text="niepoprawnie wpisana data")
            return False
    if side1:
        data.update({"skarzacy": side1})
    if side2:
        data.update({"przeciwny": side2})
    if court:
        data.update({"sad": court})
    if desc:
        data.update({"desc": desc})

    error_label.configure(text=Document.add(**data))
    clear_add_form()

add_top = ctk.CTkFrame(top_frame, fg_color=bg1)
cancel_button_a = ctk.CTkButton(add_top, text="cancel", width=10, command=lambda n="main": view(n))
add_label = ctk.CTkLabel(add_top, text="Dodaj nowy dokumet", font=("",15), fg_color=bg1)
add_button = ctk.CTkButton(add_top, text="add", width=10, command=add)
add_top.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
cancel_button_a.pack(side="left")
add_label.pack(side="left", expand=True)
add_button.pack(side="right")
#----------------------------------------------------------------------------------------------------------------------------

edit_top = ctk.CTkFrame(top_frame, fg_color=bg1)
remove_button_e = ctk.CTkButton(edit_top, text="remove", width=10)
save_button = ctk.CTkButton(edit_top, text="save", width=10)
cancel_button_e = ctk.CTkButton(edit_top, text="cancel", width=10, command=lambda n="main": view(n))
edit_top.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
remove_button_e.pack(side="right", padx=(10,0))
save_button.pack(side="right", padx=(0,10))
cancel_button_e.pack(side="left")
#----------------------------------------------------------------------------------------------------------------------------



main_left = tk.Canvas(left_frame, highlightthickness=0, bg=bg3)
filter_frame = ctk.CTkFrame(main_left, fg_color=bg3)
main_left.grid(row=0, column=0, sticky="nesw", pady=20, padx=(10, 0))
main_left.create_window(0, 0, window=filter_frame, anchor="nw")
filter_frame.bind("<Configure>", lambda e: main_left.config(width=e.width))

def filter_block(parent, title):
    def toggle_visibility():
        if content.winfo_ismapped():
            content.pack_forget()
            header.configure(text=f"▶ {title}")
        else:
            content.pack(anchor="w", padx=(20,0), pady=(5,0), after=header)
            header.configure(text=f"▼ {title}")

    header = ctk.CTkButton(parent, text=f"▶ {title}", width=200, anchor="w", border_width=0, fg_color=bg3,
                       hover_color=bg3, command=toggle_visibility)
    header.pack()
    ttk.Separator(parent, orient="horizontal").pack(fill='x', padx=10, pady=5)
    content = ctk.CTkFrame(parent, fg_color=bg3)
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
        no_var.set(0)
        yes_var.set(0)

flag_yes_var = ctk.IntVar(value=0)
flag_no_var = ctk.IntVar(value=0)
flag_filter = filter_block(filter_frame, "flag")
flag_yes = ctk.CTkCheckBox(flag_filter, text="Tak", variable=flag_yes_var, fg_color=bg3,
                           command=lambda: toggle("yes", flag_var, flag_yes_var, flag_no_var))
flag_no = ctk.CTkCheckBox(flag_filter, text="Nie", variable=flag_no_var, fg_color=bg3,
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
    start_date_var.set("")
    end_date_var.set("")
date_filter = filter_block(filter_frame, "data")
input_block = ctk.CTkFrame(date_filter, fg_color=bg3)
start_date_entry = DateEntry(input_block, font=('Inter', 8), locale='pl_PL', showweeknumbers=False,
                             showothermonthdays=False, state="readonly", textvariable=start_date_var,
                             date_pattern='yyyy-mm-dd')
end_date_entry = DateEntry(input_block, font=('Helvetica', 8), locale='pl_PL', showweeknumbers=False,
                           showothermonthdays=False, state="readonly", textvariable=end_date_var,
                           date_pattern="yyyy-mm-dd")
spacing = ctk.CTkLabel(input_block, text='-', fg_color=bg3)
clear_button = ctk.CTkButton(date_filter, text="clear", command=clear_date)
input_block.pack(expand=True)
start_date_entry.pack(side="left")
spacing.pack(side="left", padx=5)
end_date_entry.pack(side="left")
clear_button.pack(anchor='w', pady=(5,0), padx=5)
clear_date()

court_filter = filter_block(filter_frame, "sąd")
court_search = AutoEntry(court_filter, Document.dist_courts(), textvariable=court_var, font=("", 12))
court_search.pack()

side_filter = filter_block(filter_frame, "strona sporu")
side_search = AutoEntry(side_filter, Document.dist_sides(), textvariable=sides_var, font=("", 12))
side_search.pack()

doctype_filter = filter_block(filter_frame, "typ")
doctype_search = AutoEntry(doctype_filter, Document.dist_types(), textvariable=doctype_var, font=("", 12))
doctype_search.pack()


def clear_filters():
    toggle("all", flag_var, flag_yes_var, flag_no_var)
    toggle("all", attached_var, att_yes_var, att_no_var)
    start_date_var.set("")
    end_date_var.set("")
    court_var.set("")
    sides_var.set("")
    doctype_var.set("")
    refresh()
button_frame = ctk.CTkFrame(filter_frame, fg_color=bg3)
use_filters = ctk.CTkButton(button_frame, text="filter", command=apply_filters, width=30)
clear_filters = ctk.CTkButton(button_frame, text="clear", command=clear_filters, width=30)
button_frame.pack(expand=True, fill='x')
use_filters.pack(side="right", padx=10)
clear_filters.pack(side="right")
#----------------------------------------------------------------------------------------------------------------------------

add_left = ctk.CTkFrame(left_frame, fg_color=bg3)

current_file = {"path": None, "ext": ""}
def on_file_drop(files):
    path = files[0]
    filename = os.path.basename(path)
    _, ext = os.path.splitext(filename)
    current_file["path"] = path
    current_file["ext"] = ext

    def fill_name():
        name_entry.delete(0, "end")
        name_entry.insert(0, filename)
    name_entry.after(0, fill_name)

drop_box_frame = ctk.CTkFrame(add_left, fg_color=bg3)
drop_box = DropBox(drop_box_frame, on_drop=on_file_drop)
drop_box_frame.pack(expand=True)
drop_box.pack(padx=20)
add_left.grid(row=0, column=0, sticky="nesw")
#----------------------------------------------------------------------------------------------------------------------------

edit_left = ctk.CTkFrame(left_frame, fg_color=bg3, width=400)
edit_left.grid(row=0, column=0, sticky="nesw")
#----------------------------------------------------------------------------------------------------------------------------



main_right = ctk.CTkScrollableFrame(right_frame, fg_color=bg2)
main_right.grid(row=0, column=0, sticky="nsew", padx=(20,0))

def doc_block_build(doc, parent):
    def _toggle_flag():
        doc.toggle_flag()
        flag_button.configure(text_color="red" if doc.flag else "gray")

    def view_class():
        def remove_doc(doc_class):
            doc_class.remove()
            view("main")

        def edit_doc(doc_class):
            name = name_entry.get().strip()
            syg_akt = syg_akt_entry.get().strip()
            doctype = doctype_entry.get().strip()
            date = date_entry.get()
            side1 = side1_entry.get().strip()
            side2 = side2_entry.get().strip()
            court = court_entry.get().strip()
            desc = desc_entry.get("1.0", "end-1c").strip()

            if not name or not syg_akt:
                error_label.configure(text="nie wprowadzono nazwy lub sygnatury akt")
                return False
            data = {"name": name, "syg_akt": syg_akt}
            if doctype:
                data.update({"doctype": doctype})
            if date:
                try:
                    date = datetime.strptime(date, "%Y-%m-%d").date()
                    data.update({"date": date})
                except ValueError:
                    error_label.configure(text="niepoprawnie wpisana data")
                    return False
            if side1:
                data.update({"skarzacy": side1})
            if side2:
                data.update({"przeciwny": side2})
            if court:
                data.update({"court": court})
            if desc:
                data.update({"desc": desc})
            error_label.configure(text=doc_class.change(**data))

        view("edit")
        fill_add_form(doc)
        remove_button_e.configure(command=lambda d=doc: remove_doc(d))
        save_button.configure(command=lambda d=doc: edit_doc(d))

    doc_block = ctk.CTkFrame(parent)
    main_button = ctk.CTkButton(doc_block, text=doc.name, anchor='w', command=view_class)
    flag_button = ctk.CTkButton(doc_block, text="⚑", width=30, text_color="red" if doc.flag else "gray",
                                command=_toggle_flag)
    checkbox = ctk.CTkCheckBox(doc_block, text="", width=0, command=lambda: doc.checkbox_state(checkbox.get()))
    doc_block.pack(fill='x', padx=2)
    main_button.pack(side="left", fill='x', expand=True)
    flag_button.pack(side="right")
    checkbox.pack(side="right")

def refresh(**filters):
    for child in main_right.winfo_children():
        child.destroy()

    documents = Document.load(**filters)
    if not documents:
        empty_label = ctk.CTkLabel(main_right, text="brak dokumentów spełniających kryteria")
        empty_label.pack(expand=True, fill='x')
        return
    for document in documents:
        doc_block_build(document, main_right)

    def remove():
        for doc in documents:
            doc.remove_check()
        refresh(**filters)
    remove_button_m.configure(command=remove)
#----------------------------------------------------------------------------------------------------------------------------

def clear_add_form():
    if name_entry.get():
        name_entry.delete(0, "end")
    if syg_akt_entry.get():
        syg_akt_entry.delete(0, "end")
    if doctype_entry.get():
        doctype_entry.delete(0, "end")
    if date_entry.get():
        date_entry.delete(0, "end")
    if side1_entry.get():
        side1_entry.delete(0, "end")
    if side2_entry.get():
        side2_entry.delete(0, "end")
    if court_entry.get():
        court_entry.delete(0, "end")
    if desc_entry.get("1.0", "end-1c"):
        desc_entry.delete("1.0", "end")
    current_file["path"] = None
    current_file["ext"] = ""

def fill_add_form(doc):
    name_entry.insert(0, doc.name)
    syg_akt_entry.insert(0, doc.syg_akt)
    doctype_entry.insert(0, doc.doctype or '')
    date_entry.insert(0, doc.date or '')
    side1_entry.insert(0, doc.skarzacy or '')
    side2_entry.insert(0, doc.przeciwny or '')
    court_entry.insert(0, doc.court or '')
    desc_entry.insert("1.0", doc.desc or '')

add_right = ctk.CTkScrollableFrame(right_frame, fg_color=bg2)
ai_switch = ctk.CTkSwitch(add_right, text="auto fill")
name_label = ctk.CTkLabel(add_right, text="nazwa", fg_color=bg2)
name_entry = ctk.CTkEntry(add_right)
syg_akt_label = ctk.CTkLabel(add_right, text="sygnatura akt", fg_color=bg2)
syg_akt_entry = ctk.CTkEntry(add_right)
doctype_label = ctk.CTkLabel(add_right, text="typ", fg_color=bg2)
doctype_entry = ctk.CTkEntry(add_right)
date_label = ctk.CTkLabel(add_right, text="data", fg_color=bg2)
date_entry = ctk.CTkEntry(add_right, placeholder_text="YYYY-MM-DD")
side1_label = ctk.CTkLabel(add_right, text="strona skarżąca", fg_color=bg2)
side1_entry = ctk.CTkEntry(add_right)
side2_label = ctk.CTkLabel(add_right, text="strona przeciwna", fg_color=bg2)
side2_entry = ctk.CTkEntry(add_right)
court_label = ctk.CTkLabel(add_right, text="sąd", fg_color=bg2)
court_entry = ctk.CTkEntry(add_right)
desc_label = ctk.CTkLabel(add_right, text="opis", fg_color=bg2)
desc_entry = ctk.CTkTextbox(add_right, height=70)
error_label = ctk.CTkLabel(add_right, text_color="red", text="", font=("", 15, "bold"))
add_right.grid(row=0, column=0, sticky="nsew", padx=(20,0))
name_label.pack(anchor='w')
name_entry.pack(fill='x', pady=(0,5))
syg_akt_label.pack(anchor='w')
syg_akt_entry.pack(fill='x', pady=(0,5))
doctype_label.pack(anchor='w')
doctype_entry.pack(fill='x', pady=(0,5))
date_label.pack(anchor='w')
date_entry.pack(fill='x', pady=(0,5))
side1_label.pack(anchor='w')
side1_entry.pack(fill='x', pady=(0,5))
side2_label.pack(anchor='w')
side2_entry.pack(fill='x', pady=(0,5))
court_label.pack(anchor='w')
court_entry.pack(fill='x', pady=(0,5))
desc_label.pack(anchor='w')
desc_entry.pack(fill='x', pady=(0,5))
error_label.pack(fill='x')
ai_switch.pack(anchor='w')
#----------------------------------------------------------------------------------------------------------------------------



view("main")
refresh()
root.mainloop()