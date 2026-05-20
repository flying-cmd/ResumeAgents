import os
import sys
import logging

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.tools.pdf_ops import generate_pdf_tool

logging.basicConfig(level=logging.INFO)


def verify_final_layout():
    output_path = os.path.join(project_root, "utils", "test_final_layout.pdf")

    markdown_content = """# Professional Resume

## Personal Information
```json
{
    "Name": "Alex Wang",
    "Age": "32",
    "Gender": "Male",
    "Degree": "Bachelor's Degree",
    "Phone": "13800138000",
    "Email": "alex.wang@example.com",
    "Years of Experience": "10 years",
    "Target Role": "Senior Python Developer"
}
```

## Professional Skills
- Expert in **Python** development with FastAPI and Django.

## Work Experience
Senior Software Engineer | Example Internet Company | 2020.06 - 2023.12
Python Developer | Example Technology Ltd. | 2022.08 - 2024.07
Python Developer | Example Software Co. | 2020.08 - 2022.06
Python Developer | Global IT Services | 2018.05 - 2020.06

## Project Experience
### Enterprise Knowledge Platform
Senior Software Engineer | Example Internet Company | 2020.06 - 2023.12
- **Project Description:** An intelligent Q&A platform based on **RAG**.
- **Tech Stack:** **LangChain**, **Milvus**, **FastAPI**, **Redis**
- **Responsibilities:**
    - 1. Prepared data pipelines and indexing for a large-scale vector database.
    - 2. Designed retrieval strategies with multi-path recall.
- **Highlights:**
    - Improved retrieval accuracy from 60% to 90%.

## Professional Summary
Ten years of development experience with strong distributed-systems design skills and deep interest in production AI applications.
"""

    print(f"Generating PDF to: {output_path}")
    try:
        result = generate_pdf_tool.invoke({"markdown_content": markdown_content, "output_path": output_path})
        print(f"Result: {result}")

        if "Successfully generated PDF" in result:
            print("Final layout verification completed successfully.")
            print(f"Please inspect {output_path} manually.")
            print("Checklist:")
            print("1. Work experience columns should align vertically.")
            print("2. Project sublabels should align left without stray bullets.")
            print("3. The professional summary should preserve first-line indentation.")
    except Exception as e:
        print(f"Generation failed: {e}")


if __name__ == "__main__":
    verify_final_layout()
