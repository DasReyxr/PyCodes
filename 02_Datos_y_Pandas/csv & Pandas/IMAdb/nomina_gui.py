"""
Simple GUI for Nómina Generation
Browse for Excel file and save with custom name
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

# Import from vlookup_filter
try:
    from ghFiles.pycodes.IMAdb.NominaCreator import (
        load_and_filter_data,
        group_by_professor,
        generate_payroll_for_professors,
        export_nomina_single_workbook
    )
    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False
    print(f"Import error: {e}")


class SimpleNominaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nómina Generator")
        self.root.geometry("500x250")
        self.root.resizable(False, False)
        
        self.excel_file = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup simple UI"""
        # Title
        title = ttk.Label(self.root, text="Nómina Generator", font=("Arial", 14, "bold"))
        title.pack(pady=20)
        
        # File selection
        file_frame = ttk.Frame(self.root)
        file_frame.pack(pady=10, padx=20, fill="x")
        
        ttk.Label(file_frame, text="Excel File:").grid(row=0, column=0, sticky="w", pady=5)
        self.file_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky="w", padx=10)
        
        browse_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_excel)
        browse_btn.grid(row=0, column=2, padx=5)
        
        # Output file
        ttk.Label(file_frame, text="Save As:").grid(row=1, column=0, sticky="w", pady=5)
        self.output_label = ttk.Label(file_frame, text="Will prompt when generating", foreground="gray")
        self.output_label.grid(row=1, column=1, sticky="w", padx=10)
        
        # Generate button
        generate_btn = ttk.Button(self.root, text="Generate Nómina", command=self.generate, width=20)
        generate_btn.pack(pady=20)
        
        # Status
        self.status = ttk.Label(self.root, text="Ready", foreground="blue")
        self.status.pack(pady=10)
    
    def browse_excel(self):
        """Browse for Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            self.excel_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=filename, foreground="black")
            self.status.config(text=f"Selected: {filename}", foreground="green")
    
    def generate(self):
        """Generate nómina workbook"""
        if not IMPORT_SUCCESS:
            messagebox.showerror("Error", "Required modules not found. Make sure vlookup_filter.py is in the same directory.")
            return
        
        if not self.excel_file:
            messagebox.showwarning("Warning", "Please select an Excel file first")
            return
        
        # Ask where to save
        output_path = filedialog.asksaveasfilename(
            title="Save Nómina As",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="Mes_Nomina.xlsx"
        )
        
        if not output_path:
            return
        
        try:
            self.status.config(text="Checking file and sheets...", foreground="blue")
            self.root.update()

            # Verify file is readable and detect sheet names
            try:
                xl = __import__('pandas').ExcelFile(self.excel_file)
                sheets = xl.sheet_names
            except Exception as se:
                raise RuntimeError(f"Could not read Excel file or detect sheets: {se}")

            # Prefer 'Tradicional' sheet, otherwise use first available
            sheet_to_use = 'Tradicional' if 'Tradicional' in sheets else sheets[0]
            self.status.config(text=f"Using sheet: {sheet_to_use}", foreground="blue")
            self.root.update()

            # Load and filter using the detected sheet
            df = load_and_filter_data(self.excel_file, sheet_to_use)

            if df is None or df.empty:
                messagebox.showerror("Error", "No active students found in the selected sheet")
                self.status.config(text="No data", foreground="red")
                return

            self.status.config(text="Grouping by professor...", foreground="blue")
            self.root.update()

            # Group
            groups = group_by_professor(df)

            self.status.config(text="Generating payroll...", foreground="blue")
            self.root.update()

            # Generate payroll (use existing function)
            if generate_payroll_for_professors:
                nominas = generate_payroll_for_professors(groups)
            else:
                raise RuntimeError("Payroll generation function is not available")

            self.status.config(text="Exporting to Excel...", foreground="blue")
            self.root.update()

            # Export
            export_nomina_single_workbook(nominas, output_path)

            self.status.config(text="Success!", foreground="green")
            messagebox.showinfo("Success", f"Nómina generated successfully!\n\n{output_path}")

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            # Show concise message and full traceback in details dialog
            messagebox.showerror("Error generating nómina", f"{e}\n\nSee console for details.")
            print("Error in SimpleNominaGUI.generate():", e)
            print(tb)
            self.status.config(text="Error", foreground="red")


def main():
    root = tk.Tk()
    app = SimpleNominaGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
