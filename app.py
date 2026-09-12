import io
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
 
import pymupdf
import pytesseract
from PIL import Image
 
# Point pytesseract at your Tesseract install (Windows path shown below).
# On macOS/Linux, tesseract is usually already on PATH, so this line can be
# commented out or wrapped as done here.
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
 
TESSERACT_AVAILABLE = True
try:
    pytesseract.get_tesseract_version()
except Exception:
    TESSERACT_AVAILABLE = False
 
 
class PDFConverterApp:
 
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Text Converter")
        self.root.geometry("700x600")
        self.root.minsize(500, 450)
 
        self.pdf_path = None
        self.extracted_text = ""
        self.cancel_requested = False
        self.worker_thread = None
 
        self._build_ui()
 
        if not TESSERACT_AVAILABLE:
            self.ocr_var.set(False)
            self.ocr_check.config(state="disabled")
            self.status_label.config(
                text="Tesseract not found - OCR disabled", fg="red"
            )
 
    # ---------- UI ----------
    def _build_ui(self):
        top_frame = tk.Frame(self.root, padx=10, pady=10)
        top_frame.pack(fill="x")
 
        self.browse_btn = tk.Button(
            top_frame, text="Browse PDF...", command=self.browse_pdf, width=14
        )
        self.browse_btn.pack(side="left", padx=(0, 8))
 
        self.file_label = tk.Label(
            top_frame, text="No file selected", anchor="w", fg="gray"
        )
        self.file_label.pack(side="left", fill="x", expand=True)
 
        # Options row (OCR toggle)
        options_frame = tk.Frame(self.root, padx=10)
        options_frame.pack(fill="x")
 
        self.ocr_var = tk.BooleanVar(value=True)
        self.ocr_check = tk.Checkbutton(
            options_frame,
            text="Use OCR for scanned pages / images in PDF",
            variable=self.ocr_var,
        )
        self.ocr_check.pack(side="left")
 
        # Middle: text preview
        mid_frame = tk.Frame(self.root, padx=10)
        mid_frame.pack(fill="both", expand=True, pady=(6, 0))
 
        self.text_area = tk.Text(mid_frame, wrap="word")
        scrollbar = tk.Scrollbar(mid_frame, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        self.text_area.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
 
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(6, 0))
 
        # Bottom: action buttons
        btn_frame = tk.Frame(self.root, padx=10, pady=10)
        btn_frame.pack(fill="x")
 
        self.convert_btn = tk.Button(
            btn_frame, text="Convert", command=self.start_conversion,
            width=12, state="disabled"
        )
        self.convert_btn.pack(side="left", padx=(0, 8))
 
        self.cancel_btn = tk.Button(
            btn_frame, text="Cancel", command=self.cancel_conversion,
            width=12, state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=(0, 8))
 
        self.export_btn = tk.Button(
            btn_frame, text="Export as .txt", command=self.export_text,
            width=14, state="disabled"
        )
        self.export_btn.pack(side="left")
 
        self.status_label = tk.Label(btn_frame, text="", fg="gray")
        self.status_label.pack(side="right")
 
    # ---------- Actions ----------
    def browse_pdf(self):
        path = filedialog.askopenfilename(
            title="Select a PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not path:
            return
        self.pdf_path = path
        self.file_label.config(text=os.path.basename(path), fg="black")
        self.text_area.delete("1.0", tk.END)
        self.export_btn.config(state="disabled")
        self.convert_btn.config(state="normal")
        self.status_label.config(text="Ready to convert", fg="gray")
 
    def start_conversion(self):
        if not self.pdf_path:
            messagebox.showwarning("No file", "Please select a PDF file first.")
            return
 
        self.cancel_requested = False
        self.text_area.delete("1.0", tk.END)
        self.extracted_text = ""
 
        self.browse_btn.config(state="disabled")
        self.convert_btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.status_label.config(text="Converting...", fg="gray")
        self.progress.start(10)
 
        self.worker_thread = threading.Thread(target=self._convert_worker, daemon=True)
        self.worker_thread.start()
 
    def _convert_worker(self):
        try:
            doc = pymupdf.open(self.pdf_path)
            chunks = []
            total_pages = len(doc)
            use_ocr = self.ocr_var.get() and TESSERACT_AVAILABLE
 
            for i, page in enumerate(doc):
                if self.cancel_requested:
                    self.root.after(0, self._on_cancelled)
                    doc.close()
                    return
 
                self.root.after(
                    0, self._update_status, f"Reading page {i + 1}/{total_pages}..."
                )
                page_text = page.get_text().strip()
                has_images = len(page.get_images(full=True)) > 0
 
                if use_ocr:
                    if not page_text:
                        # Scenario: image-only / fully scanned page -> OCR the
                        # whole rendered page.
                        self.root.after(
                            0, self._update_status,
                            f"OCR page {i + 1}/{total_pages} (scanned page)...",
                        )
                        page_text = self._ocr_full_page(page)
                    elif has_images:
                        # Scenario: mixed page -> keep the real text layer and
                        # additionally OCR any embedded images for extra text.
                        self.root.after(
                            0, self._update_status,
                            f"OCR images on page {i + 1}/{total_pages}...",
                        )
                        image_text = self._ocr_embedded_images(doc, page)
                        if image_text:
                            page_text = f"{page_text}\n{image_text}"
                    # else: plain text page, nothing more to do.
 
                chunks.append(page_text)
 
            doc.close()
            full_text = "\n\n".join(chunks)
            self.root.after(0, self._on_conversion_done, full_text)
 
        except Exception as e:
            self.root.after(0, self._on_conversion_error, str(e))
 
    def _ocr_full_page(self, page, zoom=2.0):
        """Render a page to an image and OCR it. Used for pages that have
        no extractable text layer at all (e.g. scanned documents)."""
        try:
            matrix = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix, colorspace=pymupdf.csRGB)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            return pytesseract.image_to_string(img).strip()
        except Exception:
            return ""
 
    def _ocr_embedded_images(self, doc, page):
        """Extract each embedded image on a page and OCR it individually.
        Used for pages that already have a text layer but also contain
        pictures (e.g. a screenshot or photo with text in it)."""
        texts = []
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                img_obj = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                text = pytesseract.image_to_string(img_obj).strip()
                if text:
                    texts.append(text)
            except Exception:
                continue
        return "\n".join(texts)
 
    def _update_status(self, msg):
        self.status_label.config(text=msg, fg="gray")
 
    def _on_conversion_done(self, text):
        self.extracted_text = text
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", text)
 
        self.progress.stop()
        self.browse_btn.config(state="normal")
        self.convert_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.export_btn.config(state="normal")
        self.status_label.config(text="Done.", fg="gray")
 
    def _on_cancelled(self):
        self.progress.stop()
        self.browse_btn.config(state="normal")
        self.convert_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        self.status_label.config(text="Cancelled.", fg="gray")
 
    def _on_conversion_error(self, error_msg):
        self.progress.stop()
        self.browse_btn.config(state="normal")
        self.convert_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        self.status_label.config(text="Error.", fg="red")
        messagebox.showerror("Conversion failed", error_msg)
 
    def cancel_conversion(self):
        self.cancel_requested = True
        self.status_label.config(text="Cancelling...", fg="gray")
 
    def export_text(self):
        if not self.extracted_text:
            messagebox.showwarning("Nothing to export", "Convert a PDF first.")
            return
 
        save_path = filedialog.asksaveasfilename(
            title="Save as .txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not save_path:
            return
 
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.extracted_text)
            self.status_label.config(text=f"Exported to {save_path}", fg="gray")
            messagebox.showinfo("Exported", f"Text saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))
 
 
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFConverterApp(root)
    root.mainloop()
 