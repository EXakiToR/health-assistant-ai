import os
import base64
import io
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, Text, Canvas, Frame, Toplevel
from PIL import Image, ImageTk
from pathlib import Path
import pyperclip  # pip install pyperclip

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import threading

selected_xray_global = None

import request_create_json as r
import perplexity_ai_client as pr


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

        tb.Button(self, text="Fetch Patient", bootstyle=SUCCESS, command=self.fetch_patient_async).pack(pady=10)

        # Scrollable workflow frame
        self.canvas = Canvas(self)
        self.scrollbar = tb.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # Frame inside canvas
        self.scrollable_frame = tb.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"),
                width=self.scrollable_frame.winfo_width()
            )
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Keep content centered when resizing
        def _center_content(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)

        self.canvas.bind("<Configure>", _center_content)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # --- NEW: Independent scroll binding for Text widgets ---
    def _bind_text_scroll(self, text_widget):
        def _on_mousewheel(event):
            text_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"  # stop main canvas from scrolling

        text_widget.bind("<Enter>", lambda e: text_widget.bind_all("<MouseWheel>", _on_mousewheel))
        text_widget.bind("<Leave>", lambda e: text_widget.bind_all("<MouseWheel>", self._on_mousewheel))

    # --- Async fetch wrapper ---
    def fetch_patient_async(self):
        pid = self.entry_id.get().strip()
        if not pid:
            messagebox.showwarning("Input Error", "Please enter a patient ID")
            return
        threading.Thread(target=lambda: self._safe_fetch(pid), daemon=True).start()

    def _safe_fetch(self, pid):
        try:
            self.patient_data = r.get_patient(pid)
            self.patient_folder = r.save_patient_data(self.patient_data)
            self.after(0, self.build_workflow)
            self.after(0, lambda: messagebox.showinfo("Success", "Patient data retrieved."))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch patient: {e}"))

    def copy_relative_path(self, file_path, base_dir=None):
        file_path = Path(file_path).resolve()
        base_dir = Path(base_dir).resolve() if base_dir else Path.cwd()
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

            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
            canvas.configure(xscrollcommand=scrollbar.set)

            canvas.bind_all("<Shift-MouseWheel>", lambda e: canvas.xview_scroll(int(-1 * (e.delta / 120)), "units"))

            self.image_thumbnails = {}
            column_index = 0
            for file_name, file_info in self.xrays:
                if file_name.lower().endswith('.dcm'):
                    continue

                img_frame = Frame(scrollable_frame)
                img_frame.grid(row=0, column=column_index, padx=10, pady=5)

                tb.Label(img_frame, text=file_name, bootstyle=SECONDARY).pack()

                img = decode_image_from_path(file_info["filePath"]) if "filePath" in file_info else decode_image(file_info)
                if img:
                    width, height = img.size
                    ratio = min(120 / width, 100 / height)
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

        # --- Assumptions input with scrollbar ---
        tb.Label(self.scrollable_frame, text="Assumptions & Diagnosis:", bootstyle=PRIMARY).pack(pady=5)
        assumptions_frame = Frame(self.scrollable_frame)
        assumptions_frame.pack(pady=5, fill="both", expand=True)

        self.entry_assumptions = Text(assumptions_frame, height=10, width=80, wrap="word")
        self.entry_assumptions.pack(side="left", fill="both", expand=True)

        assumptions_scroll = tb.Scrollbar(assumptions_frame, orient="vertical", command=self.entry_assumptions.yview)
        assumptions_scroll.pack(side="right", fill="y")
        self.entry_assumptions.configure(yscrollcommand=assumptions_scroll.set)
        self._bind_text_scroll(self.entry_assumptions)

        # --- Questions input with scrollbar ---
        tb.Label(self.scrollable_frame, text="Any questions about the patient? (optional):", bootstyle=PRIMARY).pack(pady=5)
        questions_frame = Frame(self.scrollable_frame)
        questions_frame.pack(pady=5, fill="both", expand=True)

        self.entry_questions = Text(questions_frame, height=8, width=80, wrap="word")
        self.entry_questions.pack(side="left", fill="both", expand=True)

        questions_scroll = tb.Scrollbar(questions_frame, orient="vertical", command=self.entry_questions.yview)
        questions_scroll.pack(side="right", fill="y")
        self.entry_questions.configure(yscrollcommand=questions_scroll.set)
        self._bind_text_scroll(self.entry_questions)

        tb.Button(self.scrollable_frame, text="Submit", bootstyle=SUCCESS, command=self.submit_data).pack(pady=15)

        tb.Label(self.scrollable_frame, text="AI Assistant Output:", bootstyle=PRIMARY).pack(pady=5)
        output_frame = Frame(self.scrollable_frame)
        output_frame.pack(pady=5, fill="both", expand=True)

        self.output_text = Text(output_frame, wrap="word", height=12, width=100)
        self.output_text.pack(side="left", fill="both", expand=True)

        v_scroll = tb.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        v_scroll.pack(side="right", fill="y")
        self.output_text.configure(yscrollcommand=v_scroll.set)

        tb.Button(self.scrollable_frame, text="Generate PDF Report", bootstyle=INFO,
                  command=self.generate_pdf_report).pack(pady=15)

    def show_xray(self, selected_file):
        if not selected_file:
            self.xray_preview.config(image="", text="No X-ray selected")
            return

        chosen_file_info = next((f for n, f in self.xrays if n == selected_file), None)
        if chosen_file_info and selected_file in self.image_thumbnails:
            _, full_img = self.image_thumbnails[selected_file]
            self.preview_img = full_img

            width, height = full_img.size
            ratio = min(400 / width, 400 / height)
            new_size = (int(width * ratio), int(height * ratio))
            preview_img = full_img.resize(new_size, Image.Resampling.LANCZOS)
            self.tk_preview = ImageTk.PhotoImage(preview_img)

            self.xray_preview.config(image=self.tk_preview, text=f"Selected: {selected_file}")
            self.xray_preview.bind("<Button-1>", self.open_full_image)
            self.selected_xray = selected_file

            global selected_xray_global
            selected_xray_global = self.selected_xray

    def open_full_image(self, event=None):
        if not hasattr(self, "preview_img") or self.preview_img is None:
            return
        top = Toplevel(self)
        top.title("Full Resolution X-ray")
        frame = Frame(top)
        frame.pack(fill="both", expand=True)

        canvas = Canvas(frame, bg="black")
        canvas.grid(row=0, column=0, sticky="nsew")
        tk_full = ImageTk.PhotoImage(self.preview_img)
        canvas.create_image(0, 0, anchor="nw", image=tk_full)
        canvas.image = tk_full
        canvas.config(scrollregion=canvas.bbox("all"))

    def submit_data(self):
        assumptions = self.entry_assumptions.get("1.0", "end").strip()
        questions = self.entry_questions.get("1.0", "end").strip()
        if not assumptions:
            messagebox.showwarning("Input Error", "Please provide assumptions/diagnosis")
            return
        if not self.selected_xray:
            messagebox.showwarning("Input Error", "Please select an X-ray")
            return

        image_path = os.path.join(r.image, self.selected_xray)
        prompt = {
            "requirements": r.instructions,
            "patient_data": r.analyze_json(),
            "opinion": assumptions,
            "question": questions
        }
        try:
            ai_response = pr.send_to_perplexity_ai(prompt, image_path)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", ai_response)
            self.bell()  # system beep instead of popup
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_pdf_report(self):
        if not self.patient_data or not self.selected_xray:
            messagebox.showwarning("Error", "Please fetch patient data and select an X-ray first.")
            return

        report_path = os.path.join(os.getcwd(), "Report_patient.pdf")
        try:
            c = canvas.Canvas(report_path, pagesize=A4)
            width, height = A4
            margin = 50
            y = height - margin

            def draw_wrapped_text(c, text, x, y, max_width, font="Helvetica", size=12, leading=14, spacing_after=10):
                """Draw text with word wrapping, return new y position."""
                from reportlab.pdfbase.pdfmetrics import stringWidth
                c.setFont(font, size)
                words = text.split()
                line = ""
                for word in words:
                    test_line = line + ("" if line == "" else " ") + word
                    if stringWidth(test_line, font, size) <= max_width:
                        line = test_line
                    else:
                        c.drawString(x, y, line)
                        y -= leading
                        if y < margin:  # start new page
                            c.showPage()
                            c.setFont(font, size)
                            y = height - margin
                        line = word
                if line:
                    c.drawString(x, y, line)
                    y -= leading
                return y - spacing_after

            # --- Report content ---
            c.setFont("Helvetica-Bold", 16)
            c.drawString(margin, y, "Healthcare AI Assistant Report")
            y -= 40

            if "id" in self.patient_data:
                y = draw_wrapped_text(c, f"Patient ID: {self.patient_data.get('id')}", margin, y, width-2*margin)
            if "name" in self.patient_data:
                y = draw_wrapped_text(c, f"Patient Name: {self.patient_data.get('name')}", margin, y, width-2*margin)
            if "anamnesis" in self.patient_data:
                y = draw_wrapped_text(c, f"Anamnesis: {self.patient_data.get('anamnesis')}", margin, y, width-2*margin)

            if "diagnoses" in self.patient_data:
                y = draw_wrapped_text(c, "Diagnoses:", margin, y, width-2*margin, font="Helvetica-Bold")
                for diag in self.patient_data["diagnoses"]:
                    diag_text = f"{diag.get('code', '')}: {diag.get('name', '')}"
                    y = draw_wrapped_text(c, diag_text, margin+20, y, width-2*margin)

            y = draw_wrapped_text(c, f"Assumptions/Diagnosis:\n{self.entry_assumptions.get('1.0', 'end').strip()}",
                                  margin, y, width-2*margin, spacing_after=20)

            y = draw_wrapped_text(c, f"Questions:\n{self.entry_questions.get('1.0', 'end').strip()}",
                                  margin, y, width-2*margin, spacing_after=20)

            y = draw_wrapped_text(c, "AI Analysis:", margin, y, width-2*margin,
                                  font="Helvetica-Bold", size=14, spacing_after=10)

            ai_text = self.output_text.get("1.0", "end").strip()
            y = draw_wrapped_text(c, ai_text, margin, y, width-2*margin, spacing_after=30)

            # --- Image on next page ---
            c.showPage()
            img_path = os.path.join(r.image, self.selected_xray)
            if os.path.exists(img_path):
                img = Image.open(img_path)
                aspect = img.height / img.width
                img_width = width - 2*margin
                img_height = img_width * aspect
                c.drawImage(img_path, margin, height - img_height - margin,
                            width=img_width, height=img_height, preserveAspectRatio=True)

            c.save()

            # Notify user: sound + popup
            self.bell()
            messagebox.showinfo("Report Ready", f"Report generated:\n{report_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")


if __name__ == "__main__":
    app = HealthcareApp()
    app.mainloop()
