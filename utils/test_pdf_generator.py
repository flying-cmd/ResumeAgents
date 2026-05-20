import os
import logging
import markdown
import shutil
import tempfile
from xhtml2pdf import pisa
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_pdf_generation_safe_path():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    original_font_path = os.path.join(project_root, "fonts", "simhei.ttf")
    output_path = os.path.join(project_root, "utils", "test_output_safe.pdf")

    print(f"Original Font Path: {original_font_path}")
    if not os.path.exists(original_font_path):
        print("Error: Font file not found.")
        return

    try:
        tmp_fd, tmp_font_path = tempfile.mkstemp(suffix=".ttf")
        os.close(tmp_fd)
        shutil.copy2(original_font_path, tmp_font_path)
        print(f"Font copied to temporary path: {tmp_font_path}")
    except Exception as e:
        print(f"Error copying font to a temp location: {e}")
        return

    font_family = "SimHeiSafe"

    try:
        pdfmetrics.registerFont(TTFont(font_family, tmp_font_path))
        pdfmetrics.registerFont(TTFont(f"{font_family}-Bold", tmp_font_path))
        pdfmetrics.registerFont(TTFont(f"{font_family}-Italic", tmp_font_path))
        pdfmetrics.registerFont(TTFont(f"{font_family}-BoldItalic", tmp_font_path))

        addMapping(font_family, 0, 0, font_family)
        addMapping(font_family, 1, 0, f"{font_family}-Bold")
        addMapping(font_family, 0, 1, f"{font_family}-Italic")
        addMapping(font_family, 1, 1, f"{font_family}-BoldItalic")

        print(f"Successfully registered font '{font_family}' from the temporary path.")
    except Exception as e:
        print(f"Error registering font: {e}")
        if os.path.exists(tmp_font_path):
            os.unlink(tmp_font_path)
        return

    markdown_content = """
# Resume Test - Safe Path

## Personal Information
- Name: Alex Chen
- Role: Python Engineer

## Skills
- **Programming Languages**: Python, JavaScript, Go
- *Frameworks*: Django, Flask, React
- ***Combined Formatting***: Bold and Italic

## Details
This document verifies PDF generation with a temporary font file path.

Code Block:
```python
def hello():
    print("Hello, world")
```
    """

    html_content = markdown.markdown(markdown_content, extensions=["extra", "codehilite"])

    css_style = f"""
    <style>
        html, body {{
            font-family: '{font_family}', sans-serif;
            font-size: 12pt;
        }}

        h1, h2, h3 {{
            font-family: '{font_family}';
            font-weight: bold;
        }}

        code {{
            font-family: '{font_family}';
        }}

        pre {{
            font-family: '{font_family}';
            background-color: #f0f0f0;
            padding: 10px;
        }}

        strong, b {{
            font-family: '{font_family}';
            font-weight: bold;
        }}

        em, i {{
            font-family: '{font_family}';
            font-style: italic;
        }}
    </style>
    """

    final_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        {css_style}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    print(f"Generating PDF to: {output_path}")
    try:
        with open(output_path, "wb") as result_file:
            pisa_status = pisa.CreatePDF(final_html, dest=result_file, encoding="utf-8")

        if pisa_status.err:
            print(f"Error generating PDF: {pisa_status.err}")
        else:
            print("PDF generation completed successfully.")
            print(f"Check output at: {output_path}")

    except Exception as e:
        print(f"Exception: {e}")
    finally:
        if os.path.exists(tmp_font_path):
            try:
                os.unlink(tmp_font_path)
                print("Temporary font file cleaned up.")
            except Exception:
                pass
