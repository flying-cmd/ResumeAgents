import os

# Resolve the project root directory.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Professional summary configuration.
SELF_INTRO_LENGTH = 200  # Target length for the professional summary.
SELF_INTRO_INDENT_CHARS = 2  # First-line indentation characters, handled in prompts rather than rendering.

# Memory module configuration.
ENABLE_MEMORY = True  # Enable memory-enhanced generation.
CLEAR_MEMORY_ON_START = False  # Clear saved memory entries on startup.
MEMORY_DIR = os.path.join(BASE_DIR, "data", "memory_store")  # Memory storage directory.

# Interview question generation configuration.
TOTAL_INTERVIEW_QUESTIONS = 1
QUESTIONS_PER_BATCH = 1

# PDF generation configuration.
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
PDF_FONT_NAME = "simhei.ttf"

# PDF style configuration.
PDF_TITLE_SIZE = 30
PDF_HEADER_SIZE = 20
PDF_SUBHEADER_SIZE = 16
PDF_PROJECT_SUBHEADER_SIZE = 14
PDF_BODY_FONT_SIZE = 12

PDF_TITLE_STYLE = "B"
PDF_HEADER_STYLE = "B"
PDF_SUBHEADER_STYLE = "B"
PDF_PROJECT_SUBHEADER_STYLE = "B"

PDF_LINE_HEIGHT = 10
PDF_LIST_INDENT = 8
PDF_SELF_INTRO_INDENT = 8  # mm

# Default personal information values.
DEFAULT_SALARY = "Negotiable"
DEFAULT_IS_RESIGNED = "Yes"

# Default certification values.
DEFAULT_CERT_DATE = "2017"
DEFAULT_CERT_ORG = "Issuing Authority"

# Section-specific configuration.
SECTION_CONFIGS = {
    "title": {
        "style": "B",
        "size": 30,
        "align": "C",
    },
    "personal_info": {
        # Reserved for future personal information formatting options.
    },
    "skills": {
        "force_list": False,
        "ident": False,
    },
    "certificate": {
        "force_list": False,
    },
    "work_experience": {
        "ident": False,
    },
    "project_experience": {
        "subheader_style": "B",
        "indent_description": True,
    },
    "self_introduction": {
        "length_limit": SELF_INTRO_LENGTH,
        "indent": True,
        "indent_size": 8,  # mm
    },
}
