import requests
import json
import os
import base64

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

def analyze_json(path: str, image: str):
    """
    Open JSON file and return all data except 'radiologyImages'.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
#sdfef
    # Copy everything except "radiologyImages"
    result = {k: v for k, v in data.items() if k != "radiologyImages"}

    return result

def analyze_description():
    return

def analyze_input():
    return

def main(xray):

    if xray == True:
        analyze_input()
    
    else:
        analyze_input()
