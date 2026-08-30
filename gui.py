"""
Modern Tkinter GUI for Python Calculator
Features a sleek dark theme, dual-line display, Standard/Scientific modes, Memory bar, History panel, and full keyboard navigation.
"""

import math
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
from calculator_engine import CalculatorEngine, CalculationError


# Theme Color Palette (Modern Slate / Glass Dark Theme)
THEME = {
    "bg_main": "#121316",
    "bg_display": "#1a1c23",
    "bg_memory": "#181a20",
    "bg_sidebar": "#16181e",
    "text_primary": "#ffffff",
    "text_secondary": "#9ca3af",
    "text_accent": "#38bdf8",
    "text_error": "#f87171",
    
    # Button colors
    "btn_num_bg": "#232733",
    "btn_num_hover": "#2f3545",
    "btn_num_fg": "#f3f4f6",

    "btn_op_bg": "#1e293b",
    "btn_op_hover": "#334155",
    "btn_op_fg": "#38bdf8",

    "btn_sci_bg": "#1e222d",
    "btn_sci_hover": "#2c3242",
    "btn_sci_fg": "#a5b4fc",

    "btn_action_bg": "#374151",
    "btn_action_hover": "#4b5563",
    "btn_action_fg": "#f9fafb",

    "btn_clear_bg": "#451a1a",
    "btn_clear_hover": "#5c2424",
    "btn_clear_fg": "#fca5a5",

    "btn_equals_bg": "#2563eb",
    "btn_equals_hover": "#1d4ed8",
    "btn_equals_fg": "#ffffff",

    "btn_mem_bg": "#14171f",
    "btn_mem_hover": "#1f2430",
    "btn_mem_fg": "#94a3b8",
    
    "border_color": "#2a2e3d",
}


class CalculatorGUI(tk.Tk):
    """Main Calculator GUI Application Window."""

    def __init__(self):
        super().__init__()
        self.title("Python Calculator")
        self.configure(bg=THEME["bg_main"])
        self.minsize(360, 560)
        
        # Engine state
        self.engine = CalculatorEngine(angle_mode="DEG")
        self.scientific_mode = False
        self.history_visible = False
        self.is_new_calculation = True

        # Center window on screen
        self._center_window(390, 590)

        # Build UI Components
        self._setup_layout()
        self._create_top_bar()
        self._create_display()
        self._create_memory_bar()
        self._create_keypad()
        self._create_history_sidebar()

        # Keyboard bindings
        self._bind_keyboard_shortcuts()

    def _center_window(self, width: int, height: int):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)  # Keypad area expands

    # ------------------ UI Creation ------------------ #

    def _create_top_bar(self):
        """Top bar with Mode Toggle (Standard/Scientific), Angle Mode (DEG/RAD), and History Button."""
        self.top_bar = tk.Frame(self, bg=THEME["bg_main"], padx=12, pady=8)
        self.top_bar.grid(row=0, column=0, sticky="ew")
        self.top_bar.columnconfigure(1, weight=1)

        # Mode button (Standard / Scientific)
        self.mode_btn = tk.Button(
            self.top_bar,
            text="Scientific",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["btn_op_bg"],
            fg=THEME["text_accent"],
            activebackground=THEME["btn_op_hover"],
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.toggle_scientific_mode,
        )
        self.mode_btn.pack(side="left", padx=2)

        # Angle mode button (DEG / RAD)
        self.angle_btn = tk.Button(
            self.top_bar,
            text=f"Mode: {self.engine.angle_mode}",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["btn_sci_bg"],
            fg=THEME["btn_sci_fg"],
            activebackground=THEME["btn_sci_hover"],
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.toggle_angle_mode,
        )
        self.angle_btn.pack(side="left", padx=6)

        # History toggle button
        self.hist_btn = tk.Button(
            self.top_bar,
            text="History",
            font=("Segoe UI", 9),
            bg=THEME["btn_op_bg"],
            fg=THEME["text_secondary"],
            activebackground=THEME["btn_op_hover"],
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.toggle_history_panel,
        )
        self.hist_btn.pack(side="right", padx=2)

    def _create_display(self):
        """Dual line display: Top line for ongoing expression/history, bottom for active input/result."""
        self.display_frame = tk.Frame(
            self,
            bg=THEME["bg_display"],
            highlightbackground=THEME["border_color"],
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        self.display_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=4)
        self.display_frame.columnconfigure(0, weight=1)

        # Top Expression / Formula Label
        self.expr_var = tk.StringVar(value="")
        self.expr_label = tk.Label(
            self.display_frame,
            textvariable=self.expr_var,
            font=("Segoe UI", 12),
            bg=THEME["bg_display"],
            fg=THEME["text_secondary"],
            anchor="e",
            justify="right",
        )
        self.expr_label.grid(row=0, column=0, sticky="ew")

        # Main Input / Result Display Label
        self.input_var = tk.StringVar(value="0")
        self.input_label = tk.Label(
            self.display_frame,
            textvariable=self.input_var,
            font=("Segoe UI", 26, "bold"),
            bg=THEME["bg_display"],
            fg=THEME["text_primary"],
            anchor="e",
            justify="right",
        )
        self.input_label.grid(row=1, column=0, sticky="ew", pady=(4, 0))

    def _create_memory_bar(self):
        """Memory function bar (MC, MR, M+, M-, MS)."""
        self.mem_frame = tk.Frame(self, bg=THEME["bg_main"], padx=12, pady=2)
        self.mem_frame.grid(row=2, column=0, sticky="ew")

        mem_buttons = [
            ("MC", self.mem_clear),
            ("MR", self.mem_recall),
            ("M+", self.mem_add),
            ("M-", self.mem_sub),
            ("MS", self.mem_store),
        ]

        for i, (text, cmd) in enumerate(mem_buttons):
            self.mem_frame.columnconfigure(i, weight=1)
            btn = tk.Button(
                self.mem_frame,
                text=text,
                font=("Segoe UI", 9, "bold"),
                bg=THEME["btn_mem_bg"],
                fg=THEME["btn_mem_fg"],
                activebackground=THEME["btn_mem_hover"],
                activeforeground="#ffffff",
                bd=0,
                relief="flat",
                pady=4,
                cursor="hand2",
                command=cmd,
            )
            btn.grid(row=0, column=i, sticky="ew", padx=2)

    def _create_keypad(self):
        """Main keypad container with grid layout."""
        self.keypad_frame = tk.Frame(self, bg=THEME["bg_main"], padx=12, pady=8)
        self.keypad_frame.grid(row=3, column=0, sticky="nsew")

        self._render_buttons()

    def _render_buttons(self):
        """Build buttons dynamically based on Standard vs Scientific mode."""
        # Clear existing buttons in keypad
        for widget in self.keypad_frame.winfo_children():
            widget.destroy()

        if self.scientific_mode:
            # Scientific Layout (6 columns x 6 rows)
            layout = [
                [
                    ("sin", "sci", lambda: self.insert_func("sin(")),
                    ("cos", "sci", lambda: self.insert_func("cos(")),
                    ("tan", "sci", lambda: self.insert_func("tan(")),
                    ("C", "clear", self.clear_all),
                    ("DEL", "clear", self.delete_backspace),
                    ("÷", "op", lambda: self.insert_text(" ÷ ")),
                ],
                [
                    ("asin", "sci", lambda: self.insert_func("asin(")),
                    ("acos", "sci", lambda: self.insert_func("acos(")),
                    ("atan", "sci", lambda: self.insert_func("atan(")),
                    ("(", "op", lambda: self.insert_text("(")),
                    (")", "op", lambda: self.insert_text(")")),
                    ("×", "op", lambda: self.insert_text(" × ")),
                ],
                [
                    ("x²", "sci", lambda: self.insert_text("^2")),
                    ("xʸ", "sci", lambda: self.insert_text("^")),
                    ("√", "sci", lambda: self.insert_func("sqrt(")),
                    ("7", "num", lambda: self.insert_text("7")),
                    ("8", "num", lambda: self.insert_text("8")),
                    ("9", "num", lambda: self.insert_text("9")),
                ],
                [
                    ("log", "sci", lambda: self.insert_func("log(")),
                    ("ln", "sci", lambda: self.insert_func("ln(")),
                    ("n!", "sci", lambda: self.insert_text("!")),
                    ("4", "num", lambda: self.insert_text("4")),
                    ("5", "num", lambda: self.insert_text("5")),
                    ("6", "num", lambda: self.insert_text("6")),
                ],
                [
                    ("π", "sci", lambda: self.insert_text("pi")),
                    ("e", "sci", lambda: self.insert_text("e")),
                    ("%", "op", lambda: self.insert_text("%")),
                    ("1", "num", lambda: self.insert_text("1")),
                    ("2", "num", lambda: self.insert_text("2")),
                    ("3", "num", lambda: self.insert_text("3")),
                ],
                [
                    ("±", "action", self.toggle_sign),
                    ("abs", "sci", lambda: self.insert_func("abs(")),
                    ("Ans", "sci", lambda: self.insert_text("ans")),
                    ("0", "num", lambda: self.insert_text("0")),
                    (".", "num", lambda: self.insert_text(".")),
                    ("=", "equals", self.calculate_result),
                ],
            ]
            
            # Place minus and plus operators in proper column
            # Replace 3rd and 4th row 6th column if needed
            layout[2].append(("-", "op", lambda: self.insert_text(" - ")))
            layout[3].append(("+", "op", lambda: self.insert_text(" + ")))
            # Clean layout rows to uniform 7 columns or 6 columns
        else:
            # Standard Layout (4 columns x 5 rows)
            layout = [
                [
                    ("C", "clear", self.clear_all),
                    ("DEL", "clear", self.delete_backspace),
                    ("%", "op", lambda: self.insert_text("%")),
                    ("÷", "op", lambda: self.insert_text(" ÷ ")),
                ],
                [
                    ("7", "num", lambda: self.insert_text("7")),
                    ("8", "num", lambda: self.insert_text("8")),
                    ("9", "num", lambda: self.insert_text("9")),
                    ("×", "op", lambda: self.insert_text(" × ")),
                ],
                [
                    ("4", "num", lambda: self.insert_text("4")),
                    ("5", "num", lambda: self.insert_text("5")),
                    ("6", "num", lambda: self.insert_text("6")),
                    ("-", "op", lambda: self.insert_text(" - ")),
                ],
                [
                    ("1", "num", lambda: self.insert_text("1")),
                    ("2", "num", lambda: self.insert_text("2")),
                    ("3", "num", lambda: self.insert_text("3")),
                    ("+", "op", lambda: self.insert_text(" + ")),
                ],
                [
                    ("±", "action", self.toggle_sign),
                    ("0", "num", lambda: self.insert_text("0")),
                    (".", "num", lambda: self.insert_text(".")),
                    ("=", "equals", self.calculate_result),
                ],
            ]

        # Configure columns and rows
        max_cols = max(len(row) for row in layout)
        for c in range(max_cols):
            self.keypad_frame.columnconfigure(c, weight=1)
        for r in range(len(layout)):
            self.keypad_frame.rowconfigure(r, weight=1)

        # Place buttons
        for r, row in enumerate(layout):
            for c, (text, btype, cmd) in enumerate(row):
                btn = self._make_button(text, btype, cmd)
                btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)

    def _make_button(self, text: str, btype: str, cmd) -> tk.Button:
        """Create styled button based on type."""
        style_map = {
            "num": (THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"], ("Segoe UI", 13, "bold")),
            "op": (THEME["btn_op_bg"], THEME["btn_op_hover"], THEME["btn_op_fg"], ("Segoe UI", 13, "bold")),
            "sci": (THEME["btn_sci_bg"], THEME["btn_sci_hover"], THEME["btn_sci_fg"], ("Segoe UI", 10, "bold")),
            "action": (THEME["btn_action_bg"], THEME["btn_action_hover"], THEME["btn_action_fg"], ("Segoe UI", 12, "bold")),
            "clear": (THEME["btn_clear_bg"], THEME["btn_clear_hover"], THEME["btn_clear_fg"], ("Segoe UI", 11, "bold")),
            "equals": (THEME["btn_equals_bg"], THEME["btn_equals_hover"], THEME["btn_equals_fg"], ("Segoe UI", 14, "bold")),
        }
        bg, hover_bg, fg, font = style_map.get(btype, style_map["num"])

        btn = tk.Button(
            self.keypad_frame,
            text=text,
            font=font,
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=cmd,
        )

        # Add hover effects
        def on_enter(e, b=btn, h=hover_bg):
            b["background"] = h

        def on_leave(e, b=btn, orig=bg):
            b["background"] = orig

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _create_history_sidebar(self):
        """Collapsible sidebar showing past calculations."""
        self.history_frame = tk.Frame(
            self,
            bg=THEME["bg_sidebar"],
            highlightbackground=THEME["border_color"],
            highlightthickness=1,
            padx=8,
            pady=8,
        )

        # History header
        head_frame = tk.Frame(self.history_frame, bg=THEME["bg_sidebar"])
        head_frame.pack(fill="x", pady=(0, 6))

        title = tk.Label(
            head_frame,
            text="History",
            font=("Segoe UI", 11, "bold"),
            bg=THEME["bg_sidebar"],
            fg=THEME["text_primary"],
        )
        title.pack(side="left")

        clear_btn = tk.Button(
            head_frame,
            text="Clear",
            font=("Segoe UI", 8),
            bg=THEME["btn_clear_bg"],
            fg=THEME["btn_clear_fg"],
            bd=0,
            relief="flat",
            padx=6,
            pady=2,
            cursor="hand2",
            command=self.clear_history,
        )
        clear_btn.pack(side="right")

        # Scrollable listbox for history items
        self.hist_listbox = tk.Listbox(
            self.history_frame,
            bg=THEME["bg_display"],
            fg=THEME["text_primary"],
            selectbackground=THEME["btn_op_hover"],
            selectforeground=THEME["text_accent"],
            font=("Segoe UI", 9),
            bd=0,
            highlightthickness=0,
        )
        self.hist_listbox.pack(fill="both", expand=True)
        self.hist_listbox.bind("<Double-Button-1>", self.on_history_select)

    # ------------------ Interaction Logic ------------------ #

    def insert_text(self, char: str):
        """Append text to the active display."""
        curr = self.input_var.get()
        if curr in ("0", "Error") or self.is_new_calculation:
            # If starting fresh with an operator, keep previous ans
            if char.strip() in ("+", "-", "×", "÷", "*", "/", "^", "%") and curr != "Error":
                self.input_var.set(curr + char)
            else:
                self.input_var.set(char)
            self.is_new_calculation = False
        else:
            self.input_var.set(curr + char)

    def insert_func(self, func_name: str):
        """Insert a function wrapper e.g. sin("""
        curr = self.input_var.get()
        if curr in ("0", "Error") or self.is_new_calculation:
            self.input_var.set(func_name)
            self.is_new_calculation = False
        else:
            self.input_var.set(curr + func_name)

    def clear_all(self):
        """Reset calculator display and state (AC)."""
        self.input_var.set("0")
        self.expr_var.set("")
        self.is_new_calculation = True

    def delete_backspace(self):
        """Delete last entered character."""
        curr = self.input_var.get()
        if curr in ("Error", "0") or len(curr) <= 1:
            self.input_var.set("0")
            self.is_new_calculation = True
        else:
            # If ends with spaces e.g. " + ", remove cleanly
            trimmed = curr.rstrip()
            if trimmed and trimmed[-1] in ("+", "-", "×", "÷", "*", "/"):
                self.input_var.set(curr[:curr.rfind(trimmed[-1])].rstrip())
            else:
                self.input_var.set(curr[:-1])

    def toggle_sign(self):
        """Toggle positive/negative sign of active input."""
        curr = self.input_var.get().strip()
        if curr in ("0", "Error"):
            return
        if curr.startswith("-"):
            self.input_var.set(curr[1:])
        else:
            self.input_var.set(f"-{curr}")

    def calculate_result(self):
        """Evaluate current expression using CalculatorEngine."""
        expr = self.input_var.get()
        if not expr or expr == "Error":
            return

        try:
            result = self.engine.evaluate(expr)
            formatted = CalculatorEngine.format_number(result)
            self.expr_var.set(f"{expr} =")
            self.input_var.set(formatted)
            self.is_new_calculation = True
            self._update_history_listbox()
        except CalculationError as err:
            self.expr_var.set(expr)
            self.input_var.set("Error")
            self.is_new_calculation = True
            messagebox.showwarning("Calculation Error", str(err), parent=self)
        except Exception as err:
            self.expr_var.set(expr)
            self.input_var.set("Error")
            self.is_new_calculation = True
            messagebox.showerror("Error", f"An unexpected error occurred:\n{err}", parent=self)

    # ------------------ Mode & Feature Toggles ------------------ #

    def toggle_scientific_mode(self):
        """Toggle between Standard and Scientific layouts."""
        self.scientific_mode = not self.scientific_mode
        if self.scientific_mode:
            self.mode_btn.configure(text="Standard", fg="#a5b4fc")
            self.geometry("560x620")
        else:
            self.mode_btn.configure(text="Scientific", fg=THEME["text_accent"])
            self.geometry("390x590")
        self._render_buttons()

    def toggle_angle_mode(self):
        """Toggle angle mode between DEG and RAD."""
        new_mode = self.engine.toggle_angle_mode()
        self.angle_btn.configure(text=f"Mode: {new_mode}")

    def toggle_history_panel(self):
        """Show or hide the calculation history panel."""
        self.history_visible = not self.history_visible
        if self.history_visible:
            self.hist_btn.configure(fg=THEME["text_accent"])
            self.history_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=(0, 10), pady=10)
            self.columnconfigure(1, weight=0, minsize=200)
            self._update_history_listbox()
        else:
            self.hist_btn.configure(fg=THEME["text_secondary"])
            self.history_frame.grid_forget()
            self.columnconfigure(1, weight=0, minsize=0)

    def _update_history_listbox(self):
        """Refresh items in history listbox."""
        self.hist_listbox.delete(0, tk.END)
        for item in reversed(self.engine.get_history()):
            res = CalculatorEngine.format_number(item["result"])
            self.hist_listbox.insert(tk.END, f"{item['expression']} = {res}")

    def on_history_select(self, event):
        """Load selected history result into input display."""
        selection = self.hist_listbox.curselection()
        if selection:
            item_text = self.hist_listbox.get(selection[0])
            if "=" in item_text:
                result_part = item_text.split("=")[-1].strip()
                self.input_var.set(result_part)
                self.is_new_calculation = True

    def clear_history(self):
        """Clear calculation history."""
        self.engine.clear_history()
        self.hist_listbox.delete(0, tk.END)

    # ------------------ Memory Operations ------------------ #

    def mem_clear(self):
        self.engine.memory_clear()
        self.expr_var.set("Memory Cleared")

    def mem_recall(self):
        val = self.engine.memory_recall()
        formatted = CalculatorEngine.format_number(val)
        self.input_var.set(formatted)
        self.is_new_calculation = True

    def mem_store(self):
        try:
            val = self.engine.evaluate(self.input_var.get())
            self.engine.memory_store(val)
            self.expr_var.set(f"Memory Stored: {CalculatorEngine.format_number(val)}")
        except Exception as e:
            messagebox.showwarning("Memory Error", str(e), parent=self)

    def mem_add(self):
        try:
            val = self.engine.evaluate(self.input_var.get())
            new_mem = self.engine.memory_add(val)
            self.expr_var.set(f"Memory M+: {CalculatorEngine.format_number(new_mem)}")
        except Exception as e:
            messagebox.showwarning("Memory Error", str(e), parent=self)

    def mem_sub(self):
        try:
            val = self.engine.evaluate(self.input_var.get())
            new_mem = self.engine.memory_subtract(val)
            self.expr_var.set(f"Memory M-: {CalculatorEngine.format_number(new_mem)}")
        except Exception as e:
            messagebox.showwarning("Memory Error", str(e), parent=self)

    # ------------------ Keyboard Support ------------------ #

    def _bind_keyboard_shortcuts(self):
        """Bind physical keyboard keys to calculator actions."""
        # Digits & dot
        for digit in "0123456789.":
            self.bind(f"<Key-{digit}>", lambda e, d=digit: self.insert_text(d))

        # Operators
        self.bind("<plus>", lambda e: self.insert_text(" + "))
        self.bind("<minus>", lambda e: self.insert_text(" - "))
        self.bind("<asterisk>", lambda e: self.insert_text(" × "))
        self.bind("<slash>", lambda e: self.insert_text(" ÷ "))
        self.bind("<percent>", lambda e: self.insert_text("%"))
        self.bind("<asciicircum>", lambda e: self.insert_text("^"))
        self.bind("<parenleft>", lambda e: self.insert_text("("))
        self.bind("<parenright>", lambda e: self.insert_text(")"))

        # Control keys
        self.bind("<Return>", lambda e: self.calculate_result())
        self.bind("<KP_Enter>", lambda e: self.calculate_result())
        self.bind("<equal>", lambda e: self.calculate_result())
        self.bind("<BackSpace>", lambda e: self.delete_backspace())
        self.bind("<Escape>", lambda e: self.clear_all())

        # Scientific key shortcuts
        self.bind("<s>", lambda e: self.insert_func("sin("))
        self.bind("<c>", lambda e: self.insert_func("cos("))
        self.bind("<t>", lambda e: self.insert_func("tan("))
        self.bind("<q>", lambda e: self.insert_func("sqrt("))
        self.bind("<l>", lambda e: self.insert_func("ln("))


def run_gui():
    """Start the Tkinter GUI Application."""
    app = CalculatorGUI()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
