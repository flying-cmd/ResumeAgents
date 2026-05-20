import os
import sys
import logging

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.tools.pdf_ops import generate_pdf_tool

logging.basicConfig(level=logging.INFO)


def verify_final_layout_v3():
    output_path = os.path.join(project_root, "utils", "test_final_layout_v3.pdf")

    markdown_content = """# Professional Resume

## Personal Information
```json
{
    "Name": "Alex Wang",
    "Age": "32",
    "Gender": "Male",
    "Degree": "Bachelor's Degree"
}
```

## Professional Skills
- Proficient in Python and Java (already a bullet)
Experienced with Docker and Kubernetes (should be converted into a bullet)
- Expert in LangChain (already a bullet)

## Work Experience
Senior Software Engineer | Example Internet Company | 2020.06 - 2023.12
Python Developer | Example Technology Ltd. | 2022.08 - 2024.07

## Project Experience
### Enterprise Knowledge Platform
Senior Software Engineer | Example Internet Company | 2020.06 - 2023.12
**Project Description:** This RAG-based platform includes a deliberately long description to confirm the paragraph rendering and indentation behavior inside the PDF pipeline.
**Tech Stack:** Python, LangChain, Elasticsearch
**Responsibilities:**
1. Handled data cleaning.
2. Improved retrieval quality.
**Highlights:**
1. Increased retrieval accuracy.

### Test Project
**Project Description:** A short inline description.
**Responsibilities:**
- Responsibility one
- Responsibility two

## Professional Summary
The candidate has ten years of engineering experience.
They enjoy deep technical work and continuous improvement.
These lines should be merged into a single paragraph with first-line indentation only.
"""

    print(f"Generating PDF to: {output_path}")
    try:
        result = generate_pdf_tool.invoke({"markdown_content": markdown_content, "output_path": output_path})
        print(f"Result: {result}")

        if "Successfully generated PDF" in result:
            print("Verification V3 completed successfully.")
            print(f"Please inspect {output_path} manually.")
            print("Checklist:")
            print("1. All skill lines should appear as bullet points.")
            print("2. Work experience should align left with no indentation issues.")
            print("3. Project description formatting should remain stable.")
            print("4. The professional summary should become a single paragraph.")
    except Exception as e:
        print(f"Generation failed: {e}")


if __name__ == "__main__":
    verify_final_layout_v3()
