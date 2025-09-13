import requests
import json
import os
import base64
from make_png_from_dicom import change_to_png

BASE_URL = "http://88.248.132.97:3333/lisapi/api/v1/Radiology/getPatientPacsImages"

# Set a default path to a sample JSON file (update this path as needed)
path = "received_data/patient_id_unknown/sample_patient.json"  # Default; replace with a real path if available
patient_id = 0

def get_patient(patient_id: int):
    """Fetch PACS image info for a given patient ID"""
    url = f"{BASE_URL}?patientId={patient_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def save_patient_data(data: dict, base_folder="received_data"):
    """Save patient JSON and all radiology images into patient folder"""
    global path

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

    # Update the global path to the new JSON file
    json_filename = f"{name}_{surname}_id_{pid}.json"
    json_path = os.path.join(patient_folder, json_filename)
    path = json_path  # Update global path

    # --- Save JSON ---
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

    # --- Convert DICOM to PNG if needed ---
    try:
        dcm_files = [f for f in os.listdir(patient_folder) if f.lower().endswith(".dcm")]
        if dcm_files:
            print(f"Found {len(dcm_files)} DICOM files. Starting conversion...")
            change_to_png(pid)
            print("Conversion complete.")
    except Exception as e:
        print(f"Error converting DICOM files: {e}")

    return patient_folder

def analyze_json():
    """
    Open JSON file and return all data except 'radiologyImages'.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Copy everything except "radiologyImages"
    result = {k: v for k, v in data.items() if k != "radiologyImages"}

    return result


def setup(path_to_instructions="first_text.txt"):
    try:
        with open(path_to_instructions, "r", encoding="utf-8") as f:
            prompt = f.read().strip()
        return prompt
    except FileNotFoundError:
        raise FileNotFoundError("")
    except Exception as e:
        raise RuntimeError("")


instructions = setup()