import os
import pydicom
import numpy as np
from PIL import Image

def dicom_to_png(input_folder, output_folder):
    # Make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".dcm"):
            dicom_path = os.path.join(input_folder, filename)
            try:
                # Read DICOM
                dcm = pydicom.dcmread(dicom_path)
                pixel_array = dcm.pixel_array

                # Normalize pixel values to 0–255 (8-bit grayscale)
                image = (pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array)) * 255.0
                image = image.astype(np.uint8)

                # Output filename (replace .dcm with .png)
                output_filename = os.path.splitext(filename)[0] + ".png"
                output_path = os.path.join(output_folder, output_filename)

                # Save as PNG
                Image.fromarray(image).save(output_path)
                print(f"Saved: {output_path}")
            except Exception as e:
                print(f"Could not convert {filename}: {e}")

def path(folder = "received_data\\"):
    name = input("Enter id: ")
    full_name = f"{folder}patient_id_{name}"
    try:
        return full_name
    except Exception as e:
        print("File was not succesfully found", e)

if __name__ == "__main__":
    input_folder = "dicom_files"       # change this to your DICOM folder
    output_folder = "dicom_png_output" # folder for PNGs
    input_folder = path()
    if os.path.exists(input_folder):
        dicom_to_png(input_folder, output_folder = input_folder)
    else:
        print("Folder not found")