import pymupdf

pdf_file = "Im so cool.pdf"

text_file = "output.txt"

doc = pymupdf.open(pdf_file)

with open(text_file, "w", encoding="utf-8") as f:

    for page in doc:

        text = page.get_text()

        f.write(text)

        f.write("\n")

doc.close()

print("PDF converted thanks!")