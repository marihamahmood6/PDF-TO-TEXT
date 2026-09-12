PDF to Text Converter
A Python desktop application that extracts text from PDFs and uses OCR for scanned pages and images.

Features
Extract text from PDFs
OCR scanned/image-based pages
Process PDFs containing text and images
Preview extracted text
Show conversion progress
Export text as `.txt`
Cancel conversion

Technologies
Python — Main language
Tkinter— GUI
PyMuPDF— PDF processing and text/image extraction
Pillow — Image processing
pytesseract — Python interface for Tesseract
Tesseract OCR — Text recognition
threading — Background processing

Installation
Install Python packages:
`py -m pip install pymupdf pillow pytesseract`
Install Tesseract OCR separately.
The application expects Tesseract at:
`C:\Program Files\Tesseract-OCR\tesseract.exe`
Usage
Run:
`py app.py`
Then select a PDF, enable OCR if needed, click **Convert**, and export the extracted text as a `.txt` file.


