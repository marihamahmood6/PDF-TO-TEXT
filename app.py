import pymupdf
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD


# ==================================================
# VARIABLES
# ==================================================

extracted_text = ""


# ==================================================
# EXTRACT TEXT FROM PDF
# ==================================================

def extract_text(pdf_path):
    """Extract text from a PDF."""

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


# ==================================================
# PROCESS PDF
# ==================================================

def process_pdf(pdf_path):
    """Process the selected PDF."""

    global extracted_text

    # Remove curly brackets from drag-and-drop paths
    pdf_path = pdf_path.strip("{}")

    # Check if the file is a PDF
    if not pdf_path.lower().endswith(".pdf"):
        messagebox.showerror(
            "Invalid File",
            "Please select a PDF file."
        )
        return

    # Extract text
    text = extract_text(pdf_path)

    # Check if text was found
    if not text.strip():
        messagebox.showwarning(
            "No Text Found",
            "No text could be extracted from this PDF."
        )
        return

    # Store extracted text
    extracted_text = text

    # Display extracted text
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, text)

    # Get file name
    file_name = pdf_path.replace("\\", "/").split("/")[-1]

    # Display file name
    file_label.config(
        text=f"Loaded: {file_name}"
    )


# ==================================================
# BROWSE PDF
# ==================================================

def browse_pdf():
    """Open file browser and select a PDF."""

    file_path = filedialog.askopenfilename(
        title="Select PDF",
        filetypes=[
            ("PDF Files", "*.pdf"),
            ("All Files", "*.*")
        ]
    )

    if file_path:
        process_pdf(file_path)


# ==================================================
# DRAG AND DROP
# ==================================================

def drop_pdf(event):
    """Handle drag and drop PDF."""

    file_path = event.data

    # Remove brackets added by drag and drop
    if file_path.startswith("{") and file_path.endswith("}"):
        file_path = file_path[1:-1]

    process_pdf(file_path)


# ==================================================
# EXPORT AS TXT
# ==================================================

def export_as_txt():
    """Export extracted text as a TXT file."""

    if not extracted_text.strip():
        messagebox.showwarning(
            "Nothing to Export",
            "Please upload a PDF first."
        )
        return

    # Ask user where to save the TXT file
    save_path = filedialog.asksaveasfilename(
        title="Export as TXT",
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
                "Export Successful",
                "Your text file has been exported successfully!"
            )

        except Exception as e:

            messagebox.showerror(
                "Export Error",
                f"Could not export the text file:\n{e}"
            )


# ==================================================
# CLEAR
# ==================================================

def clear_text():
    """Clear the extracted text."""

    global extracted_text

    extracted_text = ""

    text_box.delete("1.0", tk.END)

    file_label.config(
        text="No PDF selected"
    )


# ==================================================
# APPLICATION WINDOW
# ==================================================

root = TkinterDnD.Tk()

root.title("PDF to Text Converter")

root.geometry("900x700")

root.minsize(700, 550)


# ==================================================
# TITLE
# ==================================================

title = tk.Label(
    root,
    text="PDF TO TEXT",
    font=("Arial", 24, "bold")
)

title.pack(
    pady=(25, 5)
)


# ==================================================
# SUBTITLE
# ==================================================

subtitle = tk.Label(
    root,
    text="Convert your PDF into editable text",
    font=("Arial", 11)
)

subtitle.pack(
    pady=(0, 20)
)


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
    padx=60,
    pady=(0, 15)
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
    font=("Arial", 11, "bold"),
    padx=30,
    pady=10,
    cursor="hand2"
)

browse_button.pack(
    pady=(0, 10)
)


# ==================================================
# FILE NAME
# ==================================================

file_label = tk.Label(
    root,
    text="No PDF selected",
    font=("Arial", 10)
)

file_label.pack(
    pady=(0, 10)
)


# ==================================================
# TEXT AREA
# ==================================================

text_box = tk.Text(
    root,
    wrap=tk.WORD,
    font=("Consolas", 11),
    padx=10,
    pady=10
)

text_box.pack(
    fill="both",
    expand=True,
    padx=60,
    pady=(0, 15)
)


# ==================================================
# BUTTON FRAME
# ==================================================

button_frame = tk.Frame(root)

button_frame.pack(
    pady=(0, 25)
)


# ==================================================
# CLEAR BUTTON
# ==================================================

clear_button = tk.Button(
    button_frame,
    text="Clear",
    command=clear_text,
    font=("Arial", 11, "bold"),
    padx=30,
    pady=10,
    cursor="hand2"
)

clear_button.pack(
    side="left",
    padx=8
)


# ==================================================
# EXPORT AS TXT BUTTON
# ==================================================

export_button = tk.Button(
    button_frame,
    text="Export as TXT",
    command=export_as_txt,
    font=("Arial", 11, "bold"),
    padx=30,
    pady=10,
    bg="#FF69B4",
    fg="white",
    activebackground="#FF1493",
    activeforeground="white",
    cursor="hand2"
)

export_button.pack(
    side="left",
    padx=8
)


# ==================================================
# START APPLICATION
# ==================================================

root.mainloop()
