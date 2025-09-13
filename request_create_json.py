import requests
import json
import os
import base64
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk 

BASE_URL = "http://88.248.132.97:3333/lisapi/api/v1/Radiology/getPatientPacsImages"

def get_patient(patient_id: int):
    """Fetch PACS image info for a given patient ID"""
    url = f"{BASE_URL}?patientId={patient_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def save_patient_data(data: dict, base_folder="received_data"):
    """Save patient JSON and all radiology images into patient folder"""

    if "patient" not in data:
        print("No patient field in response")
        return None

    patient = data["patient"]

    pid = patient.get("id", "unknown")
    name = patient.get("name", "unknown").replace(" ", "_")
    surname = patient.get("surname", "unknown").replace(" ", "_")

    # Create folder for patient
    patient_folder = os.path.join(base_folder, f"patient_id_{pid}")
    os.makedirs(patient_folder, exist_ok=True)

    # --- Save JSON ---
    json_filename = f"{name}_{surname}_id_{pid}.json"
    json_path = os.path.join(patient_folder, json_filename)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved patient JSON to {json_path}")

    # --- Save Images ---
    if "radiologyImages" in data:
        for study in data["radiologyImages"]:
            for file_info in study.get("files", []):
                file_name = file_info.get("fileName", "output.png")
                file_data = file_info.get("fileData")

                try:
                    file_bytes = base64.b64decode(file_data)
                    file_path = os.path.join(patient_folder, file_name)

                    with open(file_path, "wb") as img_file:
                        img_file.write(file_bytes)

                    print(f"Saved image: {file_path}")
                except Exception as e:
                    print(f"Error saving {file_name}: {e}")

    return patient_folder

# ---------------- UI WRAPPER ----------------
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