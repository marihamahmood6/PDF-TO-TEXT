import pymupdf
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD


# ==================================================
# COLOR PALETTE
# ==================================================

BG_MAIN = "#2E1A47"        # deep purple background
BG_PANEL = "#3D2463"       # slightly lighter purple for panels
ACCENT_PINK = "#FF3E9A"    # export button
ACCENT_BLUE = "#3EC6FF"    # browse button
ACCENT_RED = "#FF5C5C"     # clear button
TEXT_LIGHT = "#F5F0FF"
DROP_BG = "#4B2E7A"


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
# HOVER HELPERS
# ==================================================

def add_hover(widget, normal_color, hover_color):
    """Lighten/darken a button on hover for a nicer feel."""

    widget.bind("<Enter>", lambda e: widget.config(bg=hover_color))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal_color))


# ==================================================
# APPLICATION WINDOW
# ==================================================

root = TkinterDnD.Tk()

root.title("PDF to Text Converter")

root.geometry("850x620")

root.minsize(650, 500)

root.configure(bg=BG_MAIN)


# ==================================================
# TITLE
# ==================================================

title = tk.Label(
    root,
    text="PDF TO TEXT",
    font=("Arial", 26, "bold"),
    bg=BG_MAIN,
    fg=ACCENT_PINK
)

title.pack(
    pady=(15, 3)
)


# ==================================================
# SUBTITLE
# ==================================================

subtitle = tk.Label(
    root,
    text="Convert your PDF into editable text",
    font=("Arial", 11),
    bg=BG_MAIN,
    fg=TEXT_LIGHT
)

subtitle.pack(
    pady=(0, 10)
)


# ==================================================
# DRAG & DROP AREA
# ==================================================

drop_area = tk.Label(
    root,
    text="⬇  Drag & Drop PDF Here  ⬇\n\nor\n\nClick Browse PDF",
    font=("Arial", 16, "bold"),
    relief="ridge",
    borderwidth=3,
    height=5,
    bg=DROP_BG,
    fg=TEXT_LIGHT
)

drop_area.pack(
    fill="x",
    padx=60,
    pady=(0, 10)
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
    text="📂 Browse PDF",
    command=browse_pdf,
    font=("Arial", 11, "bold"),
    padx=30,
    pady=10,
    bg=ACCENT_BLUE,
    fg="white",
    activebackground="#1EA8E0",
    activeforeground="white",
    relief="flat",
    cursor="hand2"
)

browse_button.pack(
    pady=(0, 6)
)

add_hover(browse_button, ACCENT_BLUE, "#1EA8E0")


# ==================================================
# FILE NAME
# ==================================================

file_label = tk.Label(
    root,
    text="No PDF selected",
    font=("Arial", 10, "italic"),
    bg=BG_MAIN,
    fg=TEXT_LIGHT
)

file_label.pack(
    pady=(0, 6)
)


# ==================================================
# TEXT AREA
# ==================================================

text_box = tk.Text(
    root,
    wrap=tk.WORD,
    font=("Consolas", 11),
    padx=10,
    pady=10,
    bg=BG_PANEL,
    fg=TEXT_LIGHT,
    insertbackground=TEXT_LIGHT,
    relief="flat"
)

text_box.pack(
    fill="both",
    expand=True,
    padx=60,
    pady=(0, 10)
)


# ==================================================
# BUTTON FRAME (fixed height so buttons always stay visible)
# ==================================================

button_frame = tk.Frame(
    root,
    bg=BG_MAIN,
    height=60
)

button_frame.pack(
    side="bottom",
    fill="x",
    pady=(0, 12)
)

button_frame.pack_propagate(False)

# Centering sub-frame
inner_button_frame = tk.Frame(button_frame, bg=BG_MAIN)
inner_button_frame.pack(expand=True)


# ==================================================
# CLEAR BUTTON
# ==================================================

clear_button = tk.Button(
    inner_button_frame,
    text="🗑 Clear",
    command=clear_text,
    font=("Arial", 11, "bold"),
    padx=30,
    pady=10,
    bg=ACCENT_RED,
    fg="white",
    activebackground="#D94444",
    activeforeground="white",
    relief="flat",
    cursor="hand2"
)

clear_button.pack(
    side="left",
    padx=8
)

add_hover(clear_button, ACCENT_RED, "#D94444")


# ==================================================
# EXPORT AS TXT BUTTON
# ==================================================

export_button = tk.Button(
    inner_button_frame,
    text="⬇ Export as TXT",
    command=export_as_txt,
    font=("Arial", 11, "bold"),
    padx=30,
    pady=10,
    bg=ACCENT_PINK,
    fg="white",
    activebackground="#D8007E",
    activeforeground="white",
    relief="flat",
    cursor="hand2"
)

export_button.pack(
    side="left",
    padx=8
)

add_hover(export_button, ACCENT_PINK, "#D8007E")


# ==================================================
# START APPLICATION
# ==================================================

root.mainloop()