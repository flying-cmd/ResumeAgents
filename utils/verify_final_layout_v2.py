import os
import sys
import logging

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.tools.pdf_ops import generate_pdf_tool

logging.basicConfig(level=logging.INFO)


def verify_final_layout_v2():
    output_path = os.path.join(project_root, "utils", "test_final_layout_v2.pdf")

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
- Expert in **Python** development.

## Work Experience
Senior Software Engineer | Example Internet Company | 2020.06 - 2023.12
Python Developer | Example Technology Ltd. | 2022.08 - 2024.07

## Project Experience
### Enterprise Knowledge Platform
Senior Software Engineer | Example Internet Company | 2020.06 - 2023.12
1. **Project Description:** An intelligent Q&A system built with **RAG**.
2. **Responsibilities:** 1. Prepared data and indexing. 2. Improved retrieval strategy.
3. **Highlights:** Accuracy reached 90%.

## Professional Summary
Ten years of engineering experience with a strong interest in production AI systems.
"""

    print(f"Generating PDF to: {output_path}")
    try:
        result = generate_pdf_tool.invoke({"markdown_content": markdown_content, "output_path": output_path})
        print(f"Result: {result}")
        if "Successfully generated PDF" in result:
            print("Verification V2 completed successfully.")
    except Exception as e:
        print(f"Generation failed: {e}")


if __name__ == "__main__":
    verify_final_layout_v2()
