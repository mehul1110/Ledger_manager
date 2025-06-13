# Basic Tkinter App Structure
# This is the main entry point for your frontend GUI

import tkinter as tk
from PIL import Image, ImageTk

class BookkeepingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BAHI-KHATA App")
        self.root.geometry("900x600")
        self._last_size = (self.root.winfo_width(), self.root.winfo_height())
        self.set_background()
        self.create_widgets()
        self.root.bind('<Configure>', self._on_resize)

    def set_background(self):
        # Load and set a background image as a label covering the window, resizing dynamically
        try:
            width = self.root.winfo_width() or 900
            height = self.root.winfo_height() or 600
            img = Image.open("frontend/FACTSFANS121.jpeg")
            img = img.resize((width, height), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(img)
            if hasattr(self, 'bg_label') and self.bg_label.winfo_exists():
                self.bg_label.config(image=self.bg_photo)
            else:
                self.bg_label = tk.Label(self.root, image=self.bg_photo, borderwidth=0, highlightthickness=0)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower()
        except Exception as e:
            print(f"Background image error: {e}")

    def get_responsive_fonts(self):
        # Calculate and cache all font sizes based on window width
        width = self.root.winfo_width() or 900
        scale = width / 900
        self.fonts = {
            'title': ("Arial", max(int(25 * scale), 12)),
            'label': ("Arial", max(int(16 * scale), 10)),
            'entry': ("Arial", max(int(14 * scale), 10)),
            'button': ("Arial", max(int(14 * scale), 10)),
        }

    def create_widgets(self):
        # Clear the window before adding new widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background()
        self.get_responsive_fonts()
        title_font = self.fonts['title']
        tk.Label(self.root, text="Welcome to BAHI-KHATA App!", font=title_font, bg="white").pack(pady=30, fill='x')
        button_frame = tk.Frame(self.root, bg=None, highlightthickness=0, bd=0)
        button_frame.pack(pady=10)
        button_names = [
            ("Add Account", self.show_add_account_form),
            ("Add Receipt", self.show_add_receipt_form),
            ("Add Payment", self.show_add_payment_form),
            ("View Transactions", self.show_view_transactions_menu)
        ]
        btn_font = self.fonts['button']
        for i, (text, cmd) in enumerate(button_names):
            btn = tk.Button(
                button_frame,
                text=text,
                font=btn_font,
                width=30,
                height=2,
                relief='flat',
                bg='white',
                activebackground='#e0e0e0',
                bd=0,
                highlightthickness=0
            )
            if cmd:
                btn.config(command=cmd)
            btn.pack(pady=10)
        # Make the frame expand with the window
        self.root.update_idletasks()
        button_frame.config(width=self.root.winfo_width())

    def _on_resize(self, event):
        # Only redraw if the size has changed significantly
        new_size = (self.root.winfo_width(), self.root.winfo_height())
        if abs(new_size[0] - self._last_size[0]) > 5 or abs(new_size[1] - self._last_size[1]) > 5:
            self._last_size = new_size
            self.set_background()
            self.create_widgets()

    def show_main_menu(self):
        self.create_widgets()

    def show_add_receipt_form(self):
        # Clear the window before adding the form
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background()
        self.get_responsive_fonts()
        label_font = self.fonts['label']
        entry_font = self.fonts['entry']
        button_font = self.fonts['button']
        tk.Button(self.root, text="← Go Back", command=self.show_main_menu, font=button_font).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        tk.Label(self.root, text="From (account name):", font=label_font).grid(row=1, column=0, padx=10, pady=8, sticky='e')
        from_entry = tk.Entry(self.root, width=25, font=entry_font)
        from_entry.grid(row=1, column=1, padx=10, pady=8)

        tk.Label(self.root, text="Amount received:", font=label_font).grid(row=2, column=0, padx=10, pady=8, sticky='e')
        amount_entry = tk.Entry(self.root, width=25, font=entry_font)
        amount_entry.grid(row=2, column=1, padx=10, pady=8)

        tk.Label(self.root, text="Mode of payment:", font=label_font).grid(row=3, column=0, padx=10, pady=8, sticky='e')
        mop_var = tk.StringVar(value="Cash")
        mop_options = ["Cash", "Cheque", "Bank Transfer", "UPI"]
        mop_menu = tk.OptionMenu(self.root, mop_var, *mop_options)
        mop_menu.config(font=entry_font)
        mop_menu.grid(row=3, column=1, padx=10, pady=8, sticky='w')

        cheque_label = tk.Label(self.root, text="Cheque No (if cheque):", font=label_font)
        cheque_entry = tk.Entry(self.root, width=25, font=entry_font)
        cheque_label.grid_forget()
        cheque_entry.grid_forget()

        def on_mop_change(*args):
            if mop_var.get() == "Cheque":
                cheque_label.grid(row=4, column=0, padx=10, pady=8, sticky='e')
                cheque_entry.grid(row=4, column=1, padx=10, pady=8)
            else:
                cheque_label.grid_forget()
                cheque_entry.grid_forget()
        mop_var.trace_add('write', on_mop_change)

        tk.Label(self.root, text="Narration:", font=label_font).grid(row=5, column=0, padx=10, pady=8, sticky='e')
        narration_entry = tk.Entry(self.root, width=25, font=entry_font)
        narration_entry.grid(row=5, column=1, padx=10, pady=8)

        tk.Label(self.root, text="Transaction date (DD-MM-YYYY):", font=label_font).grid(row=6, column=0, padx=10, pady=8, sticky='e')
        date_entry = tk.Entry(self.root, width=25, font=entry_font)
        date_entry.grid(row=6, column=1, padx=10, pady=8)

        def submit(event=None):
            # Validation: highlight empty fields and do not submit
            entries = [from_entry, amount_entry, narration_entry, date_entry]
            labels = ["From (account name):", "Amount received:", "Narration:", "Transaction date (DD-MM-YYYY):"]
            if mop_var.get() == "Cheque":
                entries.insert(3, cheque_entry)
                labels.insert(3, "Cheque No (if cheque):")
            empty = False
            for entry in entries:
                if not entry.get().strip():
                    entry.config(bg="#ffe6e6")  # light red for missing
                    empty = True
                else:
                    entry.config(bg="white")
            if empty:
                return
            # ...existing code for submission...
            import sys
            import io
            import os
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from add_receipt import add_receipt
            # Collect values
            from_val = from_entry.get()
            amount_val = amount_entry.get()
            mop_val = mop_var.get()
            cheque_val = cheque_entry.get() if mop_val == "Cheque" else ''
            narration_val = narration_entry.get()
            date_val = date_entry.get()
            input_str = f"{from_val}\n{amount_val}\n{mop_val}\n{cheque_val}\n{narration_val}\n{date_val}\n"
            old_stdin = sys.stdin
            sys.stdin = io.StringIO(input_str)
            try:
                add_receipt()
                tk.Label(self.root, text="✅ Receipt and journal entries recorded!", fg="green", font=label_font).grid(row=8, columnspan=2, pady=10)
            except Exception as e:
                tk.Label(self.root, text=f"❌ Error: {e}", fg="red", font=label_font).grid(row=8, columnspan=2, pady=10)
            finally:
                sys.stdin = old_stdin
        tk.Button(self.root, text="Submit", command=submit, width=18, font=button_font).grid(row=7, columnspan=2, pady=15)
        # Focus order
        from_entry.bind('<Return>', lambda e: amount_entry.focus_set())
        amount_entry.bind('<Return>', lambda e: mop_menu.focus_set())
        mop_menu.bind('<Return>', lambda e: cheque_entry.focus_set() if mop_var.get() == 'Cheque' else narration_entry.focus_set())
        cheque_entry.bind('<Return>', lambda e: narration_entry.focus_set())
        narration_entry.bind('<Return>', lambda e: date_entry.focus_set())
        date_entry.bind('<Return>', lambda e: submit())

    def show_add_account_form(self):
        # Clear the window before adding the form
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background()
        self.get_responsive_fonts()
        label_font = self.fonts['label']
        entry_font = self.fonts['entry']
        button_font = self.fonts['button']
        tk.Button(self.root, text="← Go Back", command=self.show_main_menu, font=button_font).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        tk.Label(self.root, text="Account Name:", font=label_font).grid(row=1, column=0, padx=10, pady=10, sticky='e')
        name_entry = tk.Entry(self.root, font=entry_font)
        name_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Label(self.root, text="Account Type:", font=label_font).grid(row=2, column=0, padx=10, pady=10, sticky='e')
        type_entry = tk.Entry(self.root, font=entry_font)
        type_entry.grid(row=2, column=1, padx=10, pady=10)

        def submit(event=None):
            entries = [name_entry, type_entry]
            empty = False
            for entry in entries:
                if not entry.get().strip():
                    entry.config(bg="#ffe6e6")
                    empty = True
                else:
                    entry.config(bg="white")
            if empty:
                return
            # ...existing code for submission...
            import sys
            import io
            import os
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from add_account import add_account
            old_stdin = sys.stdin
            sys.stdin = io.StringIO(f"{name_entry.get()}\n{type_entry.get()}\n")
            try:
                add_account()
                tk.Label(self.root, text="✅ Account added!", fg="green", font=label_font).grid(row=4, columnspan=2, pady=10)
            except Exception as e:
                tk.Label(self.root, text=f"❌ Error: {e}", fg="red", font=label_font).grid(row=4, columnspan=2, pady=10)
            finally:
                sys.stdin = old_stdin
        tk.Button(self.root, text="Submit", command=submit, font=button_font, width=18).grid(row=3, columnspan=2, pady=15)
        # Focus order
        name_entry.bind('<Return>', lambda e: type_entry.focus_set())
        type_entry.bind('<Return>', lambda e: submit())

    def show_add_payment_form(self):
        # Clear the window before adding the form
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background()
        self.get_responsive_fonts()
        label_font = self.fonts['label']
        entry_font = self.fonts['entry']
        button_font = self.fonts['button']
        tk.Button(self.root, text="← Go Back", command=self.show_main_menu, font=button_font).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        tk.Label(self.root, text="To (account name):", font=label_font).grid(row=1, column=0, padx=10, pady=10, sticky='e')
        name_entry = tk.Entry(self.root, font=entry_font)
        name_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Label(self.root, text="Amount paid:", font=label_font).grid(row=2, column=0, padx=10, pady=10, sticky='e')
        amount_entry = tk.Entry(self.root, font=entry_font)
        amount_entry.grid(row=2, column=1, padx=10, pady=10)
        tk.Label(self.root, text="Mode of payment:", font=label_font).grid(row=3, column=0, padx=10, pady=10, sticky='e')
        mop_var = tk.StringVar(value="Cash")
        mop_options = ["Cash", "Cheque", "Bank Transfer", "UPI"]
        mop_menu = tk.OptionMenu(self.root, mop_var, *mop_options)
        mop_menu.config(font=entry_font)
        mop_menu.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        cheque_label = tk.Label(self.root, text="Cheque No (if cheque):", font=label_font)
        cheque_entry = tk.Entry(self.root, font=entry_font)
        cheque_label.grid_forget()
        cheque_entry.grid_forget()
        narration_entry = tk.Entry(self.root, font=entry_font)
        narration_entry.grid(row=5, column=1, padx=10, pady=10)
        date_entry = tk.Entry(self.root, font=entry_font)
        date_entry.grid(row=6, column=1, padx=10, pady=10)
        name_entry.bind('<Return>', lambda e: amount_entry.focus_set())
        amount_entry.bind('<Return>', lambda e: mop_menu.focus_set())
        mop_menu.bind('<Return>', lambda e: cheque_entry.focus_set() if mop_var.get() == 'Cheque' else narration_entry.focus_set())
        cheque_entry.bind('<Return>', lambda e: narration_entry.focus_set())
        narration_entry.bind('<Return>', lambda e: date_entry.focus_set())
        date_entry.bind('<Return>', lambda e: submit())

        def submit(event=None):
            entries = [name_entry, amount_entry, narration_entry, date_entry]
            if mop_var.get() == "Cheque":
                entries.insert(3, cheque_entry)
            empty = False
            for entry in entries:
                if not entry.get().strip():
                    entry.config(bg="#ffe6e6")
                    empty = True
                else:
                    entry.config(bg="white")
            if empty:
                return
            # ...existing code for submission...
            import sys
            import io
            import os
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from add_payment import add_payment
            old_stdin = sys.stdin
            sys.stdin = io.StringIO(f"{name_entry.get()}\n{amount_entry.get()}\n{mop_var.get()}\n{cheque_entry.get() if mop_var.get() == 'Cheque' else ''}\n{narration_entry.get()}\n{date_entry.get()}\n")
            try:
                add_payment()
                tk.Label(self.root, text="✅ Payment and journal entries recorded!", fg="green", font=label_font).grid(row=8, columnspan=2, pady=10)
            except Exception as e:
                tk.Label(self.root, text=f"❌ Error: {e}", fg="red", font=label_font).grid(row=8, columnspan=2, pady=10)
            finally:
                sys.stdin = old_stdin
        tk.Button(self.root, text="Submit", command=submit, font=button_font, width=18).grid(row=7, columnspan=2, pady=15)

    def show_view_transactions_menu(self):
        # Clear the window before adding the view options
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background()
        self.get_responsive_fonts()
        label_font = self.fonts['label']
        btn_font = self.fonts['button']
        tk.Button(self.root, text="← Go Back", command=self.show_main_menu, font=btn_font).pack(anchor='w', padx=10, pady=10)
        tk.Label(self.root, text="View Transactions", font=label_font, bg="white").pack(pady=20)
        option_frame = tk.Frame(self.root, bg=None, highlightthickness=0, bd=0)
        option_frame.pack(pady=10)
        options = [
            ("Receipts", self.show_receipts_view),
            ("Payments", self.show_payments_view),
            ("Accounts", self.show_accounts_view),
            ("Journal Entries", self.show_journal_entries_view)
        ]
        for text, cmd in options:
            btn = tk.Button(
                option_frame,
                text=text,
                font=btn_font,
                width=25,
                height=2,
                relief='flat',
                bg='white',
                activebackground='#e0e0e0',
                bd=0,
                highlightthickness=0,
                command=cmd
            )
            btn.pack(pady=10)

    def show_receipts_view(self):
        # Placeholder for receipts view
        self.show_placeholder_view("Receipts")

    def show_payments_view(self):
        # Placeholder for payments view
        self.show_placeholder_view("Payments")

    def show_accounts_view(self):
        # Placeholder for accounts view
        self.show_placeholder_view("Accounts")

    def show_journal_entries_view(self):
        # Placeholder for journal entries view
        self.show_placeholder_view("Journal Entries")

    def show_placeholder_view(self, name):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background()
        self.get_responsive_fonts()
        label_font = self.fonts['label']
        button_font = self.fonts['button']
        tk.Button(self.root, text="← Go Back", command=self.show_view_transactions_menu, font=button_font).pack(anchor='w', padx=10, pady=10)
        tk.Label(self.root, text=f"{name} view coming soon...", font=label_font, bg="white").pack(pady=40)

if __name__ == "__main__":
    root = tk.Tk()
    app = BookkeepingApp(root)
    root.mainloop()
