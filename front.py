import os
import base64
import io
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, Text, Canvas, Frame, Toplevel
from PIL import Image, ImageTk
from pathlib import Path
import pyperclip  # pip install pyperclip

# Import backend functions
from request_create_json import get_patient, save_patient_data


def decode_image(file_info):
    file_data = file_info.get("fileData")
    if not file_data:
        return None
    try:
        file_bytes = base64.b64decode(file_data)
        return Image.open(io.BytesIO(file_bytes))
    except Exception:
        return None


def decode_image_from_path(file_path):
    try:
        return Image.open(file_path)
    except Exception:
        return None


class HealthcareApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("Healthcare AI Assistant")
        self.geometry("1000x700")

        self.patient_data = None
        self.xrays = []
        self.tk_preview = None
        self.image_thumbnails = {}
        self.selected_xray = None
        self.patient_folder = None

        # Patient ID input
        tb.Label(self, text="Enter Patient ID:", bootstyle=INFO).pack(pady=10)
        self.entry_id = tb.Entry(self, width=40)
        self.entry_id.pack(pady=5)

        tb.Button(self, text="Fetch Patient", bootstyle=SUCCESS, command=self.fetch_patient).pack(pady=10)

        # Scrollable workflow frame
        self.canvas = Canvas(self)
        self.scrollbar = tb.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # Frame inside canvas
        self.scrollable_frame = tb.Frame(self.canvas)

        # Create window with anchor="n" (north/centered)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="n"
        )

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"),
                width=self.scrollable_frame.winfo_width()  # match width
            )
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Keep content centered when resizing window
        def _center_content(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)

        self.canvas.bind("<Configure>", _center_content)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def fetch_patient(self):
        pid = self.entry_id.get().strip()
        if not pid:
            messagebox.showwarning("Input Error", "Please enter a patient ID")
            return

        try:
            self.patient_data = get_patient(pid)
            self.patient_folder = save_patient_data(self.patient_data)
            self.build_workflow()
            messagebox.showinfo("Success", "Patient data retrieved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch patient: {e}")

    def copy_relative_path(self, file_path, base_dir=None):
        file_path = Path(file_path).resolve()
        if base_dir is None:
            base_dir = Path.cwd()
        else:
            base_dir = Path(base_dir).resolve()
        try:
            relative_path = file_path.relative_to(base_dir)
            pyperclip.copy(str(relative_path))
            print(f"Copied to clipboard: {relative_path}")
            return str(relative_path)
        except ValueError:
            print("Error: File is not within the base directory")
            return None

    def build_workflow(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.xrays = []
        for study in self.patient_data.get("radiologyImages", []):
            for file_info in study.get("files", []):
                file_name = file_info.get("fileName", "unknown.png")
                self.xrays.append((file_name, file_info))

        if self.patient_folder and os.path.exists(self.patient_folder):
            for file_name in os.listdir(self.patient_folder):
                if file_name.lower().endswith(".png"):
                    file_path = os.path.join(self.patient_folder, file_name)
                    self.xrays.append((file_name, {"filePath": file_path}))

        if self.xrays:
            tb.Label(self.scrollable_frame, text="Select X-ray (click on an image):", bootstyle=PRIMARY).pack(pady=5)

            gallery_frame = Frame(self.scrollable_frame)
            gallery_frame.pack(pady=5)

            canvas = Canvas(gallery_frame, height=160)
            scrollbar = tb.Scrollbar(gallery_frame, orient="horizontal", command=canvas.xview)
            scrollable_frame = Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
            canvas.configure(xscrollcommand=scrollbar.set)

            def _on_mousewheel(event):
                canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

            canvas.bind_all("<Shift-MouseWheel>", _on_mousewheel)

            self.image_thumbnails = {}
            column_index = 0
            for i, (file_name, file_info) in enumerate(self.xrays):
                if file_name.lower().endswith('.dcm'):
                    continue

                img_frame = Frame(scrollable_frame)
                img_frame.grid(row=0, column=column_index, padx=10, pady=5)

                tb.Label(img_frame, text=file_name, bootstyle=SECONDARY).pack()

                img = decode_image_from_path(file_info["filePath"]) if "filePath" in file_info else decode_image(file_info)
                if img:
                    width, height = img.size
                    ratio = min(120/width, 100/height)
                    new_size = (int(width * ratio), int(height * ratio))
                    thumbnail = img.resize(new_size, Image.Resampling.LANCZOS)
                    tk_thumbnail = ImageTk.PhotoImage(thumbnail)
                    self.image_thumbnails[file_name] = (tk_thumbnail, img)

                    img_label = tb.Label(img_frame, image=tk_thumbnail, cursor="hand2")
                    img_label.pack()
                    img_label.bind("<Button-1>", lambda e, name=file_name: self.show_xray(name))

                column_index += 1

            canvas.pack(side="top", fill="x", expand=True)
            scrollbar.pack(side="bottom", fill="x")

            self.xray_preview = tb.Label(self.scrollable_frame, text="No X-ray selected", bootstyle=SECONDARY)
            self.xray_preview.pack(pady=10)

        tb.Label(self.scrollable_frame, text="Assumptions & Diagnosis:", bootstyle=PRIMARY).pack(pady=5)
        self.entry_assumptions = Text(self.scrollable_frame, height=6, width=80)
        self.entry_assumptions.pack(pady=5)

        tb.Label(self.scrollable_frame, text="Any questions about the patient? (optional):", bootstyle=PRIMARY).pack(pady=5)
        self.entry_questions = Text(self.scrollable_frame, height=4, width=80)
        self.entry_questions.pack(pady=5)

        tb.Button(self.scrollable_frame, text="Submit", bootstyle=SUCCESS, command=self.submit_data).pack(pady=15)

        # --- AI Output field ---
        tb.Label(self.scrollable_frame, text="AI Assistant Output:", bootstyle=PRIMARY).pack(pady=5)

        output_frame = Frame(self.scrollable_frame)
        output_frame.pack(pady=5, fill="both", expand=True)

        self.output_text = Text(output_frame, wrap="word", height=12, width=100)
        self.output_text.pack(side="left", fill="both", expand=True)

        v_scroll = tb.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        v_scroll.pack(side="right", fill="y")
        self.output_text.configure(yscrollcommand=v_scroll.set)


    def show_xray(self, selected_file):
        if not selected_file:
            self.xray_preview.config(image="", text="No X-ray selected")
            return

        chosen_file_info = next((f for n, f in self.xrays if n == selected_file), None)
        if chosen_file_info and selected_file in self.image_thumbnails:
            _, full_img = self.image_thumbnails[selected_file]
            self.preview_img = full_img

            width, height = full_img.size
            ratio = min(400/width, 400/height)
            new_size = (int(width * ratio), int(height * ratio))
            preview_img = full_img.resize(new_size, Image.Resampling.LANCZOS)
            self.tk_preview = ImageTk.PhotoImage(preview_img)

            self.xray_preview.config(image=self.tk_preview, text=f"Selected: {selected_file}")
            self.xray_preview.bind("<Button-1>", self.open_full_image)
            self.selected_xray = selected_file

    def open_full_image(self, event=None):
        if not hasattr(self, "preview_img") or self.preview_img is None:
            return

        top = Toplevel(self)
        top.title("Full Resolution X-ray")

        frame = Frame(top)
        frame.pack(fill="both", expand=True)

        v_scrollbar = tb.Scrollbar(frame, orient="vertical")
        h_scrollbar = tb.Scrollbar(frame, orient="horizontal")

        canvas = Canvas(frame, bg="black", yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.config(command=canvas.yview)
        h_scrollbar.config(command=canvas.xview)

        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        tk_full = ImageTk.PhotoImage(self.preview_img)
        canvas.create_image(0, 0, anchor="nw", image=tk_full)
        canvas.image = tk_full
        canvas.config(scrollregion=canvas.bbox("all"))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        img_width = self.preview_img.width
        img_height = self.preview_img.height

        if img_width > screen_width * 0.8 or img_height > screen_height * 0.8:
            top.geometry(f"{min(img_width, int(screen_width*0.8))}x{min(img_height, int(screen_height*0.8))}")
        else:
            top.geometry(f"{img_width}x{img_height}")

    def submit_data(self):
        assumptions = self.entry_assumptions.get("1.0", "end").strip()
        questions = self.entry_questions.get("1.0", "end").strip()
        
        print(assumptions, "           ", questions, "            ", self.selected_xray)
        selected_file = self.selected_xray

        if not assumptions:
            messagebox.showwarning("Input Error", "Please provide assumptions/diagnosis")
            return

        try:
            # Placeholder AI response
            ai_response = f"AI Analysis for {selected_file}:\nBased on your assumptions: {assumptions}\nAnd your questions: {questions}\n\nDiagnosis suggestion: This is a placeholder."
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", ai_response)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process data: {e}")
    

if __name__ == "__main__":
    app = HealthcareApp()
    app.mainloop()