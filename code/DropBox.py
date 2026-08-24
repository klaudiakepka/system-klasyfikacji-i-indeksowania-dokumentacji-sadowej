import time
import threading
import tkinter as tk
from tkinterdnd2 import DND_FILES

class Spinner(tk.Canvas):
    def __init__(self, parent, size=100, thickness=10):
        super().__init__(parent, width=size, height=size, bg="#e8e8e8", highlightthickness=0)
        self.size = size
        self.thickness = thickness
        self.angle = 0
        self._running = False
        self._after_id = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._tick()

    def stop(self):
        self._running = False
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.delete("all")

    def _tick(self):
        if not self._running:
            return
        self.delete("all")
        pad = self.thickness
        self.create_arc(pad, pad, self.size - pad, self.size - pad, start=self.angle, extent=100,style="arc",
                        width=self.thickness, outline="lightgreen")
        self.angle = (self.angle - 12) % 360
        self._after_id = self.after(25, self._tick)


class DropBox(tk.Frame):
    min_sec = 1

    def __init__(self, parent, on_drop, text="Przetwarzanie...", size=(300, 300)):
        bg = "#e8e8e8"
        super().__init__(parent, width=size[0], height=size[1], bg=bg, highlightbackground="grey", highlightthickness=2)
        self.pack_propagate(False)
        self.on_drop = on_drop
        self.on_error = None
        self.processing = False
        self.idle_label = tk.Label(self, text="Add document", bg=bg, fg="#666666", font=("", 13))
        self.idle_label.pack(expand=True)
        self.frame = tk.Frame(self, bg=bg)
        self.spinner = Spinner(self.frame)
        self.spinner.pack(pady=(0, 8))
        tk.Label(self.frame, text=text, bg=bg, fg="#666666").pack()

        for widget in (self, self.idle_label):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop)
            widget.dnd_bind("<<DropEnter>>", self._on_drag)
            widget.dnd_bind("<<DropLeave>>", self._on_leave)

    def _on_drag(self, event):
        if not self.processing:
            self.config(highlightthickness=3)

    def _on_leave(self, event):
        if not self.processing:
            self.config(highlightthickness=2)

    def _on_drop(self, event):
        self.config(highlightthickness=2)
        if self.processing:
            return
        files = self.tk.splitlist(event.data)
        if files:
            self._start(list(files))

    def _start(self, files):
        self.processing = True
        self.idle_label.pack_forget()
        self.frame.pack(expand=True)
        self.spinner.start()
        threading.Thread(target=self._run, args=(files,), daemon=True).start()

    def _run(self, files):
        start_time = time.monotonic()
        error = None
        try:
            self.on_drop(files)
        except Exception as exc:
            error = exc

        elapsed = time.monotonic() - start_time
        if elapsed < self.min_sec:
            time.sleep(self.min_sec - elapsed)

        self.after(0, self._finish, error)

    def _finish(self, error):
        self.spinner.stop()
        self.frame.pack_forget()
        self.idle_label.pack(expand=True)
        self.processing = False

        if error is not None:
            if self.on_error:
                self.on_error(error)
            else:
                print(f"[DropZone] błąd w on_drop: {error}")