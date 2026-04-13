# save_extractions.py
import fitz
import os
from pathlib import Path

input_folder = "data"
output_folder = "extractions"
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith(".pdf"):
        pdf = fitz.open(os.path.join(input_folder, filename))
        text = ""
        for page in pdf:
            text += page.get_text()
        pdf.close()

        output_file = os.path.join(output_folder, filename.replace(".pdf", ".txt"))
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Saved: {output_file}")