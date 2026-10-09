"""
Minimal wrapper to run the working vlookup_filter pipeline with a simple file browser.
Usage: python run_vlookup.py
Select input Excel file, optionally change sheet name, choose output path, then click Run.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

try:
    from ghFiles.pycodes.IMAdb.NominaCreator import load_and_filter_data, group_by_professor, generate_payroll_for_professors, export_nomina_single_workbook
except Exception as e:
    load_and_filter_data = group_by_professor = generate_payroll_for_professors = export_nomina_single_workbook = None
    IMPORT_ERR = e
else:
    IMPORT_ERR = None

class RunVLookupApp:
    def __init__(self, root):
        self.root = root
        root.title('Run VLOOKUP Filter')
        root.geometry('520x200')
        
        frame = ttk.Frame(root, padding=12)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text='Input Excel file:').grid(row=0, column=0, sticky='w')
        self.input_label = ttk.Label(frame, text='(none)', foreground='gray')
        self.input_label.grid(row=0, column=1, sticky='w', padx=8)
        ttk.Button(frame, text='Browse...', command=self.browse_input).grid(row=0, column=2)
        
        ttk.Label(frame, text='Sheet name:').grid(row=1, column=0, sticky='w', pady=(8,0))
        self.sheet_var = tk.StringVar(value='Tradicional')
        self.sheet_entry = ttk.Entry(frame, textvariable=self.sheet_var, width=32)
        self.sheet_entry.grid(row=1, column=1, sticky='w', padx=8, pady=(8,0))
        
        ttk.Label(frame, text='Output file:').grid(row=2, column=0, sticky='w', pady=(8,0))
        self.output_label = ttk.Label(frame, text='Will ask on Run', foreground='gray')
        self.output_label.grid(row=2, column=1, sticky='w', padx=8, pady=(8,0))
        
        self.status = ttk.Label(frame, text='Ready', foreground='blue')
        self.status.grid(row=4, column=0, columnspan=3, pady=(12,0))
        
        run_btn = ttk.Button(frame, text='Run', command=self.run)
        run_btn.grid(row=3, column=1, pady=(12,0))
        
        self.input_path = None

    def browse_input(self):
        path = filedialog.askopenfilename(title='Select Excel file', filetypes=[('Excel', '*.xlsx *.xls'), ('All', '*.*')])
        if not path:
            return
        self.input_path = path
        self.input_label.config(text=os.path.basename(path), foreground='black')
        self.status.config(text='File selected', foreground='green')

    def run(self):
        if IMPORT_ERR:
            messagebox.showerror('Import error', f'Could not import vlookup_filter: {IMPORT_ERR}')
            return
        if not self.input_path:
            messagebox.showwarning('No input', 'Please select an input Excel file first')
            return

        sheet = self.sheet_var.get().strip() or 'Tradicional'
        out = filedialog.asksaveasfilename(title='Save nómina as', defaultextension='.xlsx', filetypes=[('Excel', '*.xlsx')], initialfile='nomina_por_profesor.xlsx')
        if not out:
            return
        try:
            self.status.config(text='Loading and filtering...', foreground='blue')
            df = load_and_filter_data(self.input_path, sheet)
            if df is None or df.empty:
                messagebox.showerror('No data', 'No active rows found in the selected sheet')
                self.status.config(text='No data', foreground='red')
                return
            self.status.config(text='Grouping...', foreground='blue')
            groups = group_by_professor(df)
            self.status.config(text='Generating payroll...', foreground='blue')
            nominas = generate_payroll_for_professors(groups)
            self.status.config(text='Exporting...', foreground='blue')
            export_nomina_single_workbook(nominas, out)
            self.status.config(text='Done', foreground='green')
            messagebox.showinfo('Done', f'Nómina exported to\n{out}')
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(tb)
            messagebox.showerror('Error', f'{e}\nSee console for details')
            self.status.config(text='Error', foreground='red')

if __name__ == '__main__':
    root = tk.Tk()
    app = RunVLookupApp(root)
    root.mainloop()
