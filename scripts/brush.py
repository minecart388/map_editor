# brush.py
import tkinter as tk
import json
import os
from typing import List, Tuple, Dict
from .core import path
from .config import CFG

class CustomBrush:
    def __init__(self, name: str, size: int, matrix: List[List[bool]]):
        self.name = name
        self.size = size
        self.matrix = matrix
        self.offsets = self._compute_offsets()

    def _compute_offsets(self) -> List[Tuple[int, int]]:
        offsets = []
        half = (self.size - 1) // 2
        for y in range(self.size):
            for x in range(self.size):
                if self.matrix[y][x]:
                    offsets.append((x - half, y - half))
        return offsets

    def get_offsets(self) -> List[Tuple[int, int]]:
        return self.offsets

class BrushManager:
    def __init__(self):
        self.brush_dir = path("assets/brush", internal=False)
        os.makedirs(self.brush_dir, exist_ok=True)
        self.custom_brushes: Dict[str, CustomBrush] = {}
        self.standard_mode = True
        self.current_brush: CustomBrush = None
        self.load_custom_brushes()

    def load_custom_brushes(self):
        self.custom_brushes.clear()
        if not os.path.exists(self.brush_dir):
            return
        for fname in os.listdir(self.brush_dir):
            if fname.endswith(".json"):
                p = os.path.join(self.brush_dir, fname)
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        name = data.get("name", fname[:-5])
                        size = data.get("size", 1)
                        matrix = data.get("matrix", [[True]])
                        self.custom_brushes[name] = CustomBrush(name, size, matrix)
                except:
                    pass

    def save_custom_brush(self, brush: CustomBrush):
        p = os.path.join(self.brush_dir, brush.name + ".json")
        data = {"name": brush.name, "size": brush.size, "matrix": brush.matrix}
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        self.custom_brushes[brush.name] = brush

    def delete_custom_brush(self, name: str):
        if name in self.custom_brushes:
            if self.current_brush and self.current_brush.name == name:
                self.set_standard_mode()
            del self.custom_brushes[name]
            p = os.path.join(self.brush_dir, name + ".json")
            if os.path.exists(p):
                os.remove(p)

    def set_standard_mode(self):
        self.standard_mode = True
        self.current_brush = None

    def set_custom_brush(self, name: str):
        if name in self.custom_brushes:
            self.standard_mode = False
            self.current_brush = self.custom_brushes[name]

    def get_offsets(self, size: int) -> List[Tuple[int, int]]:
        if self.standard_mode or not self.current_brush:
            half = (size - 1) // 2
            return [(dx, dy) for dy in range(-half, half+1) for dx in range(-half, half+1)]
        return self.current_brush.get_offsets()

class BrushConfigWindow:
    def __init__(self, parent, brush_mgr: BrushManager, on_close=None):
        self.brush_mgr = brush_mgr
        self.on_close = on_close
        self.win = tk.Toplevel(parent)
        self.win.title("Настройка кисти")
        self.win.geometry("300x700")
        self.win.minsize(400, 500)
        self.win.transient(parent)
        self.win.grab_set()
        self.win.configure(bg=CFG.colors["BG_PANEL"])
        self.win.protocol("WM_DELETE_WINDOW", self._close)
        self.current_edit_brush = None
        self._build()
        self._apply_theme()

    def _build(self):
        colors = CFG.colors
        main = tk.Frame(self.win, bg=colors["BG_PANEL"])
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        mode_frame = tk.LabelFrame(main, text="Режим кисти", bg=colors["BG_PANEL"], fg=colors["TEXT"])
        mode_frame.pack(fill=tk.X, pady=5)
        self.mode_var = tk.StringVar(value="standard" if self.brush_mgr.standard_mode else "custom")
        rb_standard = tk.Radiobutton(mode_frame, text="Стандартная", variable=self.mode_var, value="standard",
                                     command=self._on_standard_mode, bg=colors["BG_PANEL"], fg=colors["TEXT"],
                                     selectcolor=colors["BG_PANEL"])
        rb_standard.pack(anchor=tk.W, padx=10, pady=2)
        rb_custom = tk.Radiobutton(mode_frame, text="Пользовательская", variable=self.mode_var, value="custom",
                                   command=self._on_custom_mode, bg=colors["BG_PANEL"], fg=colors["TEXT"],
                                   selectcolor=colors["BG_PANEL"])
        rb_custom.pack(anchor=tk.W, padx=10, pady=2)

        list_frame = tk.LabelFrame(main, text="Пользовательские кисти", bg=colors["BG_PANEL"], fg=colors["TEXT"])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        listbox_frame = tk.Frame(list_frame, bg=colors["BG_PANEL"])
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.brush_listbox = tk.Listbox(listbox_frame, bg=colors["BG_CANVAS"], fg=colors["TEXT"])
        self.brush_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.brush_listbox.bind("<<ListboxSelect>>", self._on_select_brush)
        self.brush_listbox.bind("<MouseWheel>", self._on_listbox_scroll)
        self.brush_listbox.bind("<Button-4>", self._on_listbox_scroll)
        self.brush_listbox.bind("<Button-5>", self._on_listbox_scroll)

        btn_list_frame = tk.Frame(list_frame, bg=colors["BG_PANEL"])
        btn_list_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_list_frame, text="Новая кисть", command=self._new_brush,
                  bg=colors["BUTTON"], fg=colors["TEXT"]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_list_frame, text="Удалить выбранную", command=self._delete_selected_brush,
                  bg=colors["BUTTON"], fg=colors["TEXT"]).pack(side=tk.LEFT, padx=5)

        edit_frame = tk.LabelFrame(main, text="Редактор кисти", bg=colors["BG_PANEL"], fg=colors["TEXT"])
        edit_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        edit_inner = tk.Frame(edit_frame, bg=colors["BG_PANEL"])
        edit_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        name_frame = tk.Frame(edit_inner, bg=colors["BG_PANEL"])
        name_frame.pack(fill=tk.X, pady=2)
        tk.Label(name_frame, text="Название:", bg=colors["BG_PANEL"], fg=colors["TEXT"]).pack(side=tk.LEFT, padx=5)
        self.brush_name_entry = tk.Entry(name_frame, bg=colors["BUTTON"], fg=colors["TEXT"])
        self.brush_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        size_frame = tk.Frame(edit_inner, bg=colors["BG_PANEL"])
        size_frame.pack(fill=tk.X, pady=2)
        tk.Label(size_frame, text="Размер (1-10):", bg=colors["BG_PANEL"], fg=colors["TEXT"]).pack(side=tk.LEFT, padx=5)

        size_controls = tk.Frame(size_frame, bg=colors["BG_PANEL"])
        size_controls.pack(side=tk.LEFT, padx=5)
        self.brush_size_var = tk.IntVar(value=3)
        self.brush_size_entry = tk.Entry(size_controls, textvariable=self.brush_size_var, width=5,
                                          bg=colors["BUTTON"], fg=colors["TEXT"])
        self.brush_size_entry.pack(side=tk.LEFT)
        self.brush_size_entry.bind("<KeyRelease>", self._on_size_entry_change)

        btn_size_down = tk.Button(size_controls, text="-", width=2, command=self._size_down,
                                  bg=colors["BUTTON"], fg=colors["TEXT"])
        btn_size_down.pack(side=tk.LEFT, padx=2)
        btn_size_up = tk.Button(size_controls, text="+", width=2, command=self._size_up,
                                bg=colors["BUTTON"], fg=colors["TEXT"])
        btn_size_up.pack(side=tk.LEFT, padx=2)

        self.canvas_frame = tk.Frame(edit_inner, bg=colors["BG_PANEL"], bd=2, relief=tk.SUNKEN)
        self.canvas_frame.pack(pady=5)
        self.grid_canvas = tk.Canvas(self.canvas_frame, width=200, height=200, bg=colors["BG_CANVAS"])
        self.grid_canvas.pack()
        self.grid_canvas.bind("<Button-1>", self._on_canvas_click)

        edit_buttons = tk.Frame(edit_inner, bg=colors["BG_PANEL"])
        edit_buttons.pack(fill=tk.X, pady=5)
        tk.Button(edit_buttons, text="Сохранить кисть", command=self._save_current_brush,
                  bg=colors["BUTTON"], fg=colors["TEXT"]).pack(side=tk.LEFT, padx=5)
        tk.Button(edit_buttons, text="Очистить форму", command=self._clear_matrix,
                  bg=colors["BUTTON"], fg=colors["TEXT"]).pack(side=tk.LEFT, padx=5)

        self._refresh_brush_list()
        self._clear_editor()
        if not self.brush_mgr.standard_mode and self.brush_mgr.current_brush:
            self.mode_var.set("custom")
            self._select_brush_by_name(self.brush_mgr.current_brush.name)

    def _on_listbox_scroll(self, event):
        if event.delta:
            self.brush_listbox.yview_scroll(int(-event.delta/120), "units")
        elif event.num == 4:
            self.brush_listbox.yview_scroll(-1, "units")
        elif event.num == 5:
            self.brush_listbox.yview_scroll(1, "units")
        return "break"

    def _size_up(self):
        val = self.brush_size_var.get()
        if val < 10:
            self.brush_size_var.set(val + 1)
            self._on_size_change()

    def _size_down(self):
        val = self.brush_size_var.get()
        if val > 1:
            self.brush_size_var.set(val - 1)
            self._on_size_change()

    def _on_size_entry_change(self, event=None):
        try:
            val = int(self.brush_size_entry.get())
            if val < 1:
                val = 1
            elif val > 10:
                val = 10
            self.brush_size_var.set(val)
            self._on_size_change()
        except:
            pass

    def _refresh_brush_list(self):
        self.brush_listbox.delete(0, tk.END)
        for name in sorted(self.brush_mgr.custom_brushes.keys()):
            self.brush_listbox.insert(tk.END, name)

    def _on_select_brush(self, event):
        sel = self.brush_listbox.curselection()
        if sel:
            name = self.brush_listbox.get(sel[0])
            brush = self.brush_mgr.custom_brushes.get(name)
            if brush:
                self._load_brush_to_editor(brush)
                self.current_edit_brush = brush.name
                if self.mode_var.get() == "standard":
                    self.mode_var.set("custom")
                    self._on_custom_mode()
                else:
                    self.brush_mgr.set_custom_brush(name)
                    if self.on_close:
                        self.on_close()

    def _select_brush_by_name(self, name: str):
        for i in range(self.brush_listbox.size()):
            if self.brush_listbox.get(i) == name:
                self.brush_listbox.selection_clear(0, tk.END)
                self.brush_listbox.selection_set(i)
                self.brush_listbox.see(i)
                self._on_select_brush(None)
                break

    def _load_brush_to_editor(self, brush: CustomBrush):
        self.brush_name_entry.delete(0, tk.END)
        self.brush_name_entry.insert(0, brush.name)
        self.brush_size_var.set(brush.size)
        self.matrix = [row[:] for row in brush.matrix]
        self._draw_grid()

    def _new_brush(self):
        self._clear_editor()
        self.current_edit_brush = None

    def _delete_selected_brush(self):
        sel = self.brush_listbox.curselection()
        if sel:
            name = self.brush_listbox.get(sel[0])
            if self.brush_mgr.current_brush and self.brush_mgr.current_brush.name == name:
                self.brush_mgr.set_standard_mode()
                self.mode_var.set("standard")
                self._on_standard_mode()
            self.brush_mgr.delete_custom_brush(name)
            self._refresh_brush_list()
            if self.current_edit_brush == name:
                self._clear_editor()
                self.current_edit_brush = None

    def _clear_editor(self):
        self.brush_name_entry.delete(0, tk.END)
        self.brush_size_var.set(3)
        self._init_matrix(3)
        self._draw_grid()

    def _init_matrix(self, size: int):
        if size < 1:
            size = 1
        self.matrix = [[False]*size for _ in range(size)]
        self.matrix[size//2][size//2] = True

    def _on_size_change(self):
        sz = self.brush_size_var.get()
        if sz < 1:
            sz = 1
        if sz > 10:
            sz = 10
        self.brush_size_var.set(sz)
        old_size = len(self.matrix) if hasattr(self, 'matrix') else 0
        if sz != old_size:
            new_matrix = [[False]*sz for _ in range(sz)]
            min_size = min(sz, old_size)
            offset_new = (sz - min_size) // 2
            offset_old = (old_size - min_size) // 2 if old_size > 0 else 0
            for i in range(min_size):
                for j in range(min_size):
                    if old_size > 0 and i+offset_old < old_size and j+offset_old < old_size:
                        new_matrix[i+offset_new][j+offset_new] = self.matrix[i+offset_old][j+offset_old]
            self.matrix = new_matrix
        self._draw_grid()

    def _draw_grid(self):
        self.grid_canvas.delete("all")
        sz = self.brush_size_var.get()
        if sz < 1:
            return
        cw = max(2, 200 // sz)
        ch = max(2, 200 // sz)
        for i in range(sz):
            for j in range(sz):
                x1 = j*cw
                y1 = i*ch
                fill = CFG.colors["BUTTON"] if self.matrix[i][j] else CFG.colors["BG_CANVAS"]
                self.grid_canvas.create_rectangle(x1, y1, x1+cw, y1+ch, fill=fill, outline=CFG.colors["GRID"])
        for i in range(sz+1):
            self.grid_canvas.create_line(i*cw, 0, i*cw, 200, fill=CFG.colors["GRID"])
            self.grid_canvas.create_line(0, i*ch, 200, i*ch, fill=CFG.colors["GRID"])

    def _on_canvas_click(self, e):
        sz = self.brush_size_var.get()
        if sz <= 0:
            return
        cw = 200 // sz
        ch = 200 // sz
        col = e.x // cw
        row = e.y // ch
        if 0 <= row < sz and 0 <= col < sz:
            self.matrix[row][col] = not self.matrix[row][col]
            self._draw_grid()

    def _clear_matrix(self):
        sz = self.brush_size_var.get()
        self.matrix = [[False]*sz for _ in range(sz)]
        self._draw_grid()

    def _save_current_brush(self):
        name = self.brush_name_entry.get().strip()
        if not name:
            return
        sz = self.brush_size_var.get()
        brush = CustomBrush(name, sz, self.matrix)
        self.brush_mgr.save_custom_brush(brush)
        self._refresh_brush_list()
        self.current_edit_brush = name
        if self.mode_var.get() == "custom":
            self.brush_mgr.set_custom_brush(name)
            if self.on_close:
                self.on_close()

    def _on_standard_mode(self):
        self.brush_mgr.set_standard_mode()
        if self.on_close:
            self.on_close()

    def _on_custom_mode(self):
        if self.brush_listbox.size() > 0:
            sel = self.brush_listbox.curselection()
            if sel:
                name = self.brush_listbox.get(sel[0])
                self.brush_mgr.set_custom_brush(name)
            else:
                self.brush_listbox.selection_set(0)
                self.brush_listbox.see(0)
                name = self.brush_listbox.get(0)
                self.brush_mgr.set_custom_brush(name)
                self._on_select_brush(None)
        else:
            self.mode_var.set("standard")
            self.brush_mgr.set_standard_mode()
        if self.on_close:
            self.on_close()

    def _close(self):
        if self.on_close:
            self.on_close()
        self.win.destroy()

    def _apply_theme(self):
        colors = CFG.colors
        self.win.configure(bg=colors["BG_PANEL"])
        def apply(w):
            if isinstance(w, (tk.Frame, tk.LabelFrame)):
                w.configure(bg=colors["BG_PANEL"])
            elif isinstance(w, tk.Button):
                w.configure(bg=colors["BUTTON"], fg=colors["TEXT"])
            elif isinstance(w, tk.Label):
                w.configure(bg=colors["BG_PANEL"], fg=colors["TEXT"])
            elif isinstance(w, tk.Listbox):
                w.configure(bg=colors["BG_CANVAS"], fg=colors["TEXT"])
            elif isinstance(w, tk.Entry):
                w.configure(bg=colors["BUTTON"], fg=colors["TEXT"])
            elif isinstance(w, tk.Radiobutton):
                w.configure(bg=colors["BG_PANEL"], fg=colors["TEXT"], selectcolor=colors["BG_PANEL"])
            for c in w.winfo_children():
                apply(c)
        apply(self.win)