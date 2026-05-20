import os
import re
import html
from rich.console import Console
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT

from src.conf import (
    FONTS_DIR,
    PDF_FONT_NAME,
    PDF_TITLE_SIZE,
    PDF_HEADER_SIZE,
    PDF_SUBHEADER_SIZE,
    PDF_BODY_FONT_SIZE,
    PDF_LINE_HEIGHT,
)

console = Console()

LEGACY_PERSONAL_INFO = "\u4e2a\u4eba\u4fe1\u606f"
LEGACY_WORK_EXPERIENCE = "\u804c\u4e1a\u7ecf\u5386"
LEGACY_EDUCATION = "\u6559\u80b2\u7ecf\u5386"
LEGACY_CERTIFICATIONS = "\u6280\u80fd\u8bc1\u4e66"
LEGACY_SKILLS = "\u4e13\u4e1a\u6280\u80fd"
LEGACY_PROJECT_EXPERIENCE = "\u9879\u76ee\u7ecf\u9a8c"
LEGACY_SUMMARY = "\u81ea\u6211\u8bc4\u4ef7"

LEGACY_PROJECT_DESCRIPTION = "\u9879\u76ee\u63cf\u8ff0"
LEGACY_TECH_STACK = "\u6280\u672f\u6808"
LEGACY_RESPONSIBILITIES = "\u804c\u8d23"
LEGACY_HIGHLIGHTS = "\u9879\u76ee\u4eae\u70b9"
LEGACY_PROJECT_PREFIX = "\u9879\u76ee"

PROJECT_FIELD_ALIASES = {
    LEGACY_PROJECT_DESCRIPTION: "Project Description",
    LEGACY_TECH_STACK: "Tech Stack",
    LEGACY_RESPONSIBILITIES: "Responsibilities",
    LEGACY_HIGHLIGHTS: "Highlights",
    "Project Description": "Project Description",
    "Tech Stack": "Tech Stack",
    "Responsibilities": "Responsibilities",
    "Highlights": "Highlights",
}


def register_fonts():
    """Register the fonts used during PDF rendering."""
    font_path = os.path.join(FONTS_DIR, PDF_FONT_NAME)
    if not os.path.exists(font_path):
        console.print(f"[red]Error: font file not found at {font_path}[/red]")
        return False

    try:
        pdfmetrics.registerFont(TTFont("SimHei", font_path))
        pdfmetrics.registerFont(TTFont("SimHei-Bold", font_path))
        return True
    except Exception as e:
        console.print(f"[red]Font registration failed: {e}[/red]")
        return False


def normalize_project_line(line: str) -> str:
    """Normalize legacy project field labels to the English label set."""
    for label, normalized in PROJECT_FIELD_ALIASES.items():
        for separator in (":", "\uff1a"):
            prefix = f"{label}{separator}"
            if line.startswith(prefix):
                remainder = line[len(prefix):].strip()
                return f"{normalized}: {remainder}".rstrip()
    return line


def convert_markdown_to_pdf(markdown_content: str, output_path: str) -> bool:
    """
    Convert Markdown content to PDF with ReportLab Platypus.
    This avoids the fpdf2 horizontal space issues seen in earlier versions.
    """
    if not register_fonts():
        return False

    try:
        styles = getSampleStyleSheet()

        style_body = ParagraphStyle(
            name="Body",
            fontName="SimHei",
            fontSize=PDF_BODY_FONT_SIZE,
            leading=PDF_LINE_HEIGHT * 1.6,
            firstLineIndent=0,
            alignment=TA_LEFT,
            spaceAfter=8,
        )

        style_title = ParagraphStyle(
            name="ResumeTitle",
            parent=style_body,
            fontSize=PDF_TITLE_SIZE,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName="SimHei-Bold",
        )

        style_h2 = ParagraphStyle(
            name="SectionHeader",
            parent=style_body,
            fontSize=PDF_HEADER_SIZE,
            fontName="SimHei-Bold",
            spaceBefore=25,
            spaceAfter=20,
        )

        style_h3 = ParagraphStyle(
            name="SubHeader",
            parent=style_body,
            fontSize=PDF_SUBHEADER_SIZE,
            fontName="SimHei-Bold",
            spaceBefore=15,
            spaceAfter=10,
        )

        style_indent = ParagraphStyle(
            name="IndentBody",
            parent=style_body,
            firstLineIndent=2 * PDF_BODY_FONT_SIZE,
            alignment=TA_JUSTIFY,
            leading=PDF_LINE_HEIGHT * 1.6,
        )

        style_list_content = style_body

        style_skill_content = ParagraphStyle(
            name="SkillContent",
            parent=style_body,
            leading=PDF_LINE_HEIGHT * 2.0,
            spaceAfter=5,
        )

        story = []
        lines = markdown_content.split("\n")
        i = 0
        current_section = None

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            if line.startswith("# "):
                story.append(Paragraph(line[2:].strip(), style_title))
                current_section = "title"

            elif line.startswith("## "):
                title_text = line[3:].strip()
                story.append(Spacer(1, 15))
                story.append(Paragraph(title_text, style_h2))
                story.append(Spacer(1, 5))

                if "Personal Information" in title_text or LEGACY_PERSONAL_INFO in title_text:
                    current_section = "personal_info"
                elif "Work Experience" in title_text or LEGACY_WORK_EXPERIENCE in title_text:
                    current_section = "work_experience"
                elif "Education" in title_text or LEGACY_EDUCATION in title_text:
                    current_section = "education"
                elif "Certification" in title_text or LEGACY_CERTIFICATIONS in title_text:
                    current_section = "certificate"
                elif "Professional Skills" in title_text or LEGACY_SKILLS in title_text:
                    current_section = "skills"
                elif "Project Experience" in title_text or LEGACY_PROJECT_EXPERIENCE in title_text:
                    current_section = "projects"
                elif "Professional Summary" in title_text or "Self Evaluation" in title_text or LEGACY_SUMMARY in title_text:
                    current_section = "self_eval"
                else:
                    current_section = "other"

            elif current_section == "personal_info":
                info_items = []
                while i < len(lines) and not lines[i].startswith("#"):
                    current_line = lines[i].strip()
                    if current_line:
                        current_line = current_line.replace("**", "").replace("- ", "").replace("*", "")
                        current_line = current_line.replace("\uff1a", ":")
                        if ":" in current_line:
                            info_items.append(current_line)
                    i += 1
                i -= 1

                table_data = []
                for idx in range(0, len(info_items), 2):
                    row = [Paragraph(info_items[idx], style_body)]
                    if idx + 1 < len(info_items):
                        row.append(Paragraph(info_items[idx + 1], style_body))
                    else:
                        row.append("")
                    table_data.append(row)

                if table_data:
                    table = Table(table_data, colWidths=["50%", "50%"])
                    table.setStyle(
                        TableStyle(
                            [
                                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                            ]
                        )
                    )
                    story.append(table)

            elif current_section in ["work_experience", "education", "certificate"]:
                if "|" in line:
                    parts = [part.strip() for part in line.replace("- ", "").split("|")]
                    if len(parts) >= 3:
                        col1 = Paragraph(f"<b>{parts[0]}</b>", style_body)
                        col2 = Paragraph(parts[1], style_body)
                        col3 = Paragraph(parts[2], ParagraphStyle("Right", parent=style_body, alignment=TA_RIGHT))

                        table = Table([[col1, col2, col3]], colWidths=["35%", "40%", "25%"])
                        table.setStyle(
                            TableStyle(
                                [
                                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                    ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                    ("RIGHTPADDING", (-1, -1), (-1, -1), 0),
                                ]
                            )
                        )
                        story.append(table)
                    elif len(parts) == 2:
                        col1 = Paragraph(f"<b>{parts[0]}</b>", style_body)
                        col2 = Paragraph(parts[1], ParagraphStyle("Right", parent=style_body, alignment=TA_RIGHT))
                        story.append(Table([[col1, col2]], colWidths=["50%", "50%"]))
                    else:
                        story.append(Paragraph(line, style_body))
                else:
                    story.append(Paragraph(line, style_body))

            elif current_section == "projects":
                line = normalize_project_line(line)
                clean_line = line.replace("**", "").replace("###", "").strip()
                clean_line = re.sub(r"^#+\s*", "", clean_line).strip()

                if any(clean_line.startswith(f"{label}:") for label in PROJECT_FIELD_ALIASES.values()):
                    parts = clean_line.split(":", 1)
                    if len(parts) == 2:
                        key = html.escape(parts[0].strip())
                        value = html.escape(parts[1].strip())

                        p_key = Paragraph(f"{key}: ", style_body)
                        p_val = Paragraph(value, style_body)

                        table = Table([[p_key, p_val]], colWidths=[25 * mm, None])
                        table.setStyle(
                            TableStyle(
                                [
                                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                ]
                            )
                        )
                        story.append(table)
                    else:
                        story.append(Paragraph(clean_line, style_body))

                elif line.startswith("###") or clean_line.startswith("Project") or clean_line.startswith(LEGACY_PROJECT_PREFIX):
                    story.append(Spacer(1, 5))
                    clean_line = clean_line.replace("\uff1a", " ").replace(":", " ")
                    story.append(Paragraph(clean_line, style_h3))

                elif line.strip().startswith("-") or re.match(r"^\d+\.", line.strip()):
                    match = re.match(r"^(\d+\.)", line.strip())
                    if match:
                        bullet_text = match.group(1)
                        content = line.strip()[len(bullet_text):].strip()
                    else:
                        bullet_text = "•"
                        content = line.strip().lstrip("-").strip()

                    content = html.escape(content)
                    bullet = Paragraph(bullet_text, style_body)
                    content_p = Paragraph(content, style_list_content)
                    table = Table([[bullet, content_p]], colWidths=[10 * mm, None])
                    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
                    story.append(table)
                else:
                    story.append(Paragraph(line, style_body))

            elif current_section == "self_eval":
                full_text = []
                while i < len(lines) and not lines[i].startswith("#"):
                    current_line = lines[i].strip()
                    if current_line:
                        full_text.append(current_line)
                    i += 1
                i -= 1

                text_block = " ".join(full_text).strip()
                if text_block:
                    story.append(Paragraph(text_block, style_indent))

            elif current_section == "skills":
                if line.startswith("- "):
                    content = line[2:].strip()
                    bullet = Paragraph("•", style_body)
                    paragraph = Paragraph(content, style_skill_content)
                    table = Table([[bullet, paragraph]], colWidths=[5 * mm, None])
                    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
                    story.append(table)
                else:
                    story.append(Paragraph(line, style_skill_content))

            else:
                story.append(Paragraph(line, style_body))

            i += 1

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )
        doc.build(story)

        console.print(f"[green]PDF generated successfully with ReportLab: {output_path}[/green]")
        return True

    except Exception as e:
        console.print(f"[bold red]Exception during PDF generation: {str(e)}[/bold red]")
        import traceback

        console.print(traceback.format_exc())
        import sys

        sys.exit(1)
