import fitz  # PyMuPDF
import os
import logging

logging.basicConfig(level=logging.INFO)


def verify_pdf_content(pdf_path):
    print(f"Verifying PDF: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return False

    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()

        print("\n--- Extracted Text Content ---")
        print(text)
        print("------------------------------\n")

        keywords = ["Alex", "Hello", "world", "Resume Test"]
        missing = [keyword for keyword in keywords if keyword not in text]

        if not missing:
            print("SUCCESS: All expected keywords were found. No mojibake detected.")
            return True

        print(f"FAILURE: Missing keywords: {missing}. Rendering issues may still be present.")
        return False

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(project_root, "utils", "test_output_fpdf2.pdf")
    verify_pdf_content(pdf_path)
