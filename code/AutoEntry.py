import tkinter as tk

class AutoEntry(tk.Entry):
    def __init__(self, master=None, suggestions=None, on_select=None, **kwargs):
        super().__init__(master, **kwargs)

        self.suggestions = suggestions or []
        self.max_results = 5
        self.on_select = on_select
        self.popup = None
        self.listbox = None

        self.bind("<KeyRelease>", self._key_release)
        self.bind("<Escape>", lambda e: self._hide())
        self.bind("<Down>", self._on_down)
        self.bind("<Return>", self._on_return)
        self.bind_all("<Button-1>", self._on_click, add="+")

    def _get_matches(self, text):
        if not text:
            return []
        text = text.lower()
        matches = [s for s in self.suggestions if text in s.lower()]
        return matches[: self.max_results]

    def _key_release(self, event):
        if event.keysym in ("Up", "Down", "Return", "Escape"):
            return

        text = self.get()
        matches = self._get_matches(text)
        if matches:
            self._show(matches)
        else:
            self._hide()

    def _on_down(self, event):
        if self.popup and self.listbox:
            self.listbox.focus_set()
            self.listbox.selection_set(0)

    def _on_return(self, event):
        self._select()

    def _show(self, matches):
        if self.popup is None:
            self.popup = tk.Toplevel(self)
            self.popup.wm_overrideredirect(True)
            self.popup.wm_attributes("-topmost", True)

            scroll = tk.Scrollbar(self.popup, orient="horizontal")
            scroll.pack(side="bottom", fill="x")
            self.listbox = tk.Listbox(self.popup, height=min(self.max_results, 8), xscrollcommand=scroll.set)
            self.listbox.pack(fill="both", expand=True)
            scroll.config(command=self.listbox.xview)

            self.listbox.bind("<ButtonRelease-1>", self._select)
            self.listbox.bind("<Return>", self._select)
            self.listbox.bind("<Escape>", lambda e: self._hide())

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        width = self.winfo_width()
        height = min(len(matches), 8) * 20 + 16
        self.popup.geometry(f"{width}x{height}+{x}+{y}")
        self.listbox.delete(0, tk.END)
        for item in matches:
            self.listbox.insert(tk.END, item)

        self.popup.deiconify()

    def _on_click(self, event):
        if not self.popup:
            return
        widget = event.widget
        if widget is self:
            return
        w = widget
        while w is not None:
            if w == self.popup:
                return
            w = w.master
        self._hide()

    def _hide(self):
        if self.popup is not None:
            self.popup.destroy()
            self.popup = None
            self.listbox = None

    def _select(self, event=None):
        if self.listbox:
            sel = self.listbox.curselection()
            if sel:
                self._choose(self.listbox.get(sel[0]))

    def _choose(self, value):
        self.delete(0, tk.END)
        self.insert(0, value)
        self._hide()
        self.focus_set()
        self.icursor(tk.END)
        if self.on_select:
            self.on_select(value)