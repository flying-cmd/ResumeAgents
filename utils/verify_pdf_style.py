import os
import sys
import logging

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.tools.pdf_ops import generate_pdf_tool

logging.basicConfig(level=logging.INFO)


def verify_style():
    output_path = os.path.join(project_root, "utils", "test_style_output.pdf")

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
    "Target Role": "Senior Python Engineer"
}
```

## Professional Skills
- Expert in **Python** development with FastAPI and Django.
- Experienced with **Docker** and **Kubernetes** container platforms.
- Strong understanding of **microservices architecture** patterns.

## Work Experience
**Senior Software Engineer | Example Internet Company | 2020-2023**
- **Responsibilities:** Rebuilt the core transaction system and improved throughput by 50%.
- **Highlights:** Led a service-splitting initiative that broke a monolith into 12 microservices.

## Project Experience
### Enterprise Knowledge Platform
- **Project Description:** An intelligent Q&A system built on **RAG**.
- **Responsibilities:** Designed vector retrieval strategies and improved prompt engineering quality.

### Intelligent Customer Support Platform
- **Challenges:** Handled websocket connections under high concurrency.
- **Results:** Reached support for more than 100,000 long-lived connections on a single instance.

## Professional Summary
Ten years of engineering experience with a strong interest in solving complex technical problems.
"""

    print(f"Generating PDF to: {output_path}")
    try:
        result = generate_pdf_tool.invoke({"markdown_content": markdown_content, "output_path": output_path})
        print(f"Result: {result}")

        if "Successfully generated PDF" in result:
            print("Style generation completed successfully.")
            print(f"Please inspect {output_path} manually for font sizes, bold styling, and layout.")
    except Exception as e:
        print(f"Generation failed: {e}")


if __name__ == "__main__":
    verify_style()
