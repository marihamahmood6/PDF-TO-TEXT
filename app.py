import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
 
import pymupdf
 
 
class PDFConverterApp:

    
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Text Converter")
        self.root.geometry("700x550")
        self.root.minsize(500, 400)
 
        self.pdf_path = None
        self.extracted_text = ""
        self.cancel_requested = False
        self.worker_thread = None
 
        self._build_ui()
 
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
 
        # Middle: text preview
        mid_frame = tk.Frame(self.root, padx=10)
        mid_frame.pack(fill="both", expand=True)
 
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
        self.file_label.config(text=path, fg="black")
        self.text_area.delete("1.0", tk.END)
        self.export_btn.config(state="disabled")
        self.convert_btn.config(state="normal")
        self.status_label.config(text="Ready to convert")
 
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
        self.status_label.config(text="Converting...")
        self.progress.start(10)
 
        self.worker_thread = threading.Thread(target=self._convert_worker, daemon=True)
        self.worker_thread.start()
 
    def _convert_worker(self):
        try:
            doc = pymupdf.open(self.pdf_path)
            chunks = []
            total_pages = len(doc)
 
            for i, page in enumerate(doc):
                if self.cancel_requested:
                    self.root.after(0, self._on_cancelled)
                    doc.close()
                    return
                chunks.append(page.get_text())
                self.root.after(0, self._update_status, f"Converting page {i+1}/{total_pages}...")
 
            doc.close()
            full_text = "\n".join(chunks)
            self.root.after(0, self._on_conversion_done, full_text)
 
        except Exception as e:
            self.root.after(0, self._on_conversion_error, str(e))
 
    def _update_status(self, msg):
        self.status_label.config(text=msg)
 
    def _on_conversion_done(self, text):
        self.extracted_text = text
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", text)
 
        self.progress.stop()
        self.browse_btn.config(state="normal")
        self.convert_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.export_btn.config(state="normal")
        self.status_label.config(text="Done.")
 
    def _on_cancelled(self):
        self.progress.stop()
        self.browse_btn.config(state="normal")
        self.convert_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        self.status_label.config(text="Cancelled.")
 
    def _on_conversion_error(self, error_msg):
        self.progress.stop()
        self.browse_btn.config(state="normal")
        self.convert_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        self.status_label.config(text="Error.")
        messagebox.showerror("Conversion failed", error_msg)
 
    def cancel_conversion(self):
        self.cancel_requested = True
        self.status_label.config(text="Cancelling...")
 
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
            self.status_label.config(text=f"Exported to {save_path}")
            messagebox.showinfo("Exported", f"Text saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))
 
 
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFConverterApp(root)
    root.mainloop()
 