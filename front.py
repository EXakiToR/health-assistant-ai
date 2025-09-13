import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from request_create_json import get_patient, save_patient_data

def on_submit():
    patient_id = entry.get().strip()
    if not patient_id.isdigit():
        messagebox.showerror("Error", "Please enter a numeric patient ID.")
        return

    try:
        data = get_patient(int(patient_id))
        folder = save_patient_data(data)
        messagebox.showinfo("Success", f"Patient {patient_id} imported successfully.\nSaved in: {folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import patient {patient_id}.\n\n{e}")

# --- UI Setup ---
root = ttk.Window(themename="cosmo")
root.title("Patient Importer")
root.geometry("400x200")

label = ttk.Label(root, text="Enter Patient ID:", font=("Segoe UI", 12))
label.pack(pady=10)

entry = ttk.Entry(root, font=("Segoe UI", 12))
entry.pack(pady=5, padx=20, fill="x")

button = ttk.Button(root, text="Import Patient Data", bootstyle="primary", command=on_submit)
button.pack(pady=15)

root.mainloop()