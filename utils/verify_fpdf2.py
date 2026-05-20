import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.pdf_generator import convert_markdown_to_pdf


def verify_fix():
    print("Starting PDF generation verification (ReportLab path)...")

    markdown_content = """
# Resume Generation Test

## Personal Information
- **Name**: Alex Chen
- **Role**: Senior Python Engineer
- **Phone**: 13800138000

## Professional Summary
Five years of Python development experience with strong Django and Flask skills.
Comfortable solving complex technical problems and collaborating across teams.

## Project Experience
### Intelligent Resume Generator
- **Role**: Core Developer
- **Description**: An LLM-powered resume optimization and generation tool.
- **Outcome**: Improved PDF generation stability and reduced text rendering issues.
    """

    output_path = os.path.join(os.path.dirname(__file__), "verify_output_fpdf2.pdf")

    if os.path.exists(output_path):
        os.remove(output_path)

    try:
        success = convert_markdown_to_pdf(markdown_content, output_path)

        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n[Success] PDF generated: {output_path}")
            print(f"File size: {file_size} bytes")
            if file_size > 1000:
                print("File size looks normal and content was likely written correctly.")
            else:
                print("[Warning] File is unexpectedly small and may be empty.")
        else:
            print("\n[Failure] PDF generation returned False or the file was not created.")

    except Exception as e:
        print(f"\n[Exception] An error occurred during verification: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    verify_fix()
