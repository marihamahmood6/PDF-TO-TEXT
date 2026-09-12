import pymupdf
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD


# Store extracted text
extracted_text = ""


def extract_text(pdf_path):
    """Extract text from PDF."""

    try:
        doc = pymupdf.open(pdf_path)

        text = ""

        for page in doc:
            text += page.get_text()
            text += "\n"

        doc.close()

        return text

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Could not read PDF:\n{e}"
        )

        return ""


def process_pdf(pdf_path):
    """Process the selected PDF."""

    global extracted_text

    # Remove { } added by drag and drop
    pdf_path = pdf_path.strip("{}")

    # Check file type
    if not pdf_path.lower().endswith(".pdf"):
        messagebox.showerror(
            "Invalid File",
            "Please select a PDF file."
        )
        return

    # Extract text
    text = extract_text(pdf_path)

    if not text.strip():
        messagebox.showwarning(
            "No Text Found",
            "No text could be extracted from this PDF."
        )
        return

    # Store extracted text
    extracted_text = text

    # Display text
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, text)

    # Show filename
    file_label.config(
        text=f"Loaded: {pdf_path.split('/')[-1]}"
    )


def browse_pdf():
    """Open file browser."""

    file_path = filedialog.askopenfilename(
        title="Select PDF",
        filetypes=[
            ("PDF Files", "*.pdf"),
            ("All Files", "*.*")
        ]
    )

    if file_path:
        process_pdf(file_path)


def drop_pdf(event):
    """Handle drag and drop."""

    file_path = event.data

    # Remove { } if present
    if file_path.startswith("{") and file_path.endswith("}"):
        file_path = file_path[1:-1]

    process_pdf(file_path)


def download_text():
    """Save extracted text as TXT file."""

    if not extracted_text.strip():
        messagebox.showwarning(
            "Nothing to Download",
            "Please upload a PDF first."
        )
        return

    save_path = filedialog.asksaveasfilename(
        title="Save Text File",
        defaultextension=".txt",
        filetypes=[
            ("Text Files", "*.txt")
        ]
    )

    if save_path:

        try:
            with open(
                save_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(extracted_text)

            messagebox.showinfo(
                "Success",
                "Text file saved successfully!"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Could not save file:\n{e}"
            )


def clear_text():
    """Clear the text area."""

    global extracted_text

    extracted_text = ""

    text_box.delete("1.0", tk.END)

    file_label.config(
        text="No PDF selected"
    )


# ==================================================
# CREATE APPLICATION
# ==================================================

root = TkinterDnD.Tk()

root.title("PDF to Text Converter")

root.geometry("900x650")

root.minsize(700, 500)


# ==================================================
# TITLE
# ==================================================

title = tk.Label(
    root,
    text="PDF TO TEXT",
    font=("Arial", 24, "bold")
)

title.pack(pady=(20, 5))


subtitle = tk.Label(
    root,
    text="Convert your PDF into editable text",
    font=("Arial", 11)
)

subtitle.pack(pady=(0, 20))


# ==================================================
# DRAG & DROP AREA
# ==================================================

drop_area = tk.Label(
    root,
    text="Drag & Drop PDF Here\n\nor\n\nClick Browse PDF",
    font=("Arial", 16),
    relief="groove",
    borderwidth=2,
    height=8
)

drop_area.pack(
    fill="x",
    padx=50
)


# Enable drag and drop
drop_area.drop_target_register(DND_FILES)

drop_area.dnd_bind(
    "<<Drop>>",
    drop_pdf
)


# ==================================================
# BROWSE BUTTON
# ==================================================

browse_button = tk.Button(
    root,
    text="Browse PDF",
    command=browse_pdf,
    font=("Arial", 11),
    padx=20,
    pady=8
)

browse_button.pack(pady=15)


# ==================================================
# FILE NAME
# ==================================================

file_label = tk.Label(
    root,
    text="No PDF selected",
    font=("Arial", 10)
)

file_label.pack()


# ==================================================
# TEXT BOX
# ==================================================

text_box = tk.Text(
    root,
    wrap=tk.WORD,
    font=("Consolas", 11)
)

text_box.pack(
    fill="both",
    expand=True,
    padx=50,
    pady=15
)


# ==================================================
# BUTTONS
# ==================================================

button_frame = tk.Frame(root)

button_frame.pack(pady=15)


# Clear button
clear_button = tk.Button(
    button_frame,
    text="Clear",
    command=clear_text,
    font=("Arial", 11),
    padx=25,
    pady=8
)

clear_button.pack(
    side="left",
    padx=10
)


# Download button
download_button = tk.Button(
    button_frame,
    text="Download TXT",
    command=download_text,
    font=("Arial", 11),
    padx=25,
    pady=8
)

download_button.pack(
    side="left",
    padx=10
)


# ==================================================
# START APPLICATION
# ==================================================

root.mainloop()