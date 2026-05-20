import os
from fpdf import FPDF
import logging

logging.basicConfig(level=logging.INFO)


def test_fpdf2_generation():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    original_font_path = os.path.join(project_root, "fonts", "simhei.ttf")
    output_path = os.path.join(project_root, "utils", "test_output_fpdf2.pdf")

    print(f"Font Path: {original_font_path}")
    if not os.path.exists(original_font_path):
        print("Error: Font file not found.")
        return

    pdf = FPDF()
    pdf.add_page()

    try:
        pdf.add_font("SimHei", style="", fname=original_font_path)
        pdf.add_font("SimHei", style="B", fname=original_font_path)
        pdf.add_font("SimHei", style="I", fname=original_font_path)
        pdf.add_font("SimHei", style="BI", fname=original_font_path)
        print("Fonts registered successfully.")
    except Exception as e:
        print(f"Error registering font: {e}")
        return

    pdf.set_font("SimHei", size=14)

    markdown_text = """
# Resume Test (FPDF2 Version)

## Personal Information
- Name: **Alex Chen**
- Role: Python Engineer

## Skills
- **Programming Languages**: Python, JavaScript, Go
- *Frameworks*: Django, Flask, React
- ***Combined Formatting***: Bold and Italic

## Details
This document is used to verify PDF generation with **fpdf2**.
This is a simple rendering check for Markdown support.

Code Example:
    def hello():
        print("Hello, world")
    """

    try:
        pdf.multi_cell(w=0, h=10, txt=markdown_text, markdown=True)
        print("Content written to PDF.")
    except Exception as e:
        print(f"Error writing content: {e}")
        return

    try:
        pdf.output(output_path)
        print(f"PDF generated successfully at: {output_path}")
    except Exception as e:
        print(f"Error saving PDF: {e}")


if __name__ == "__main__":
    test_fpdf2_generation()
