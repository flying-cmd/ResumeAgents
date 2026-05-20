STRUCTURE_OPTIMIZE_PROMPT = """
You are a professional document layout strategist and resume architect.
Reorganize the optimized Markdown resume below so it becomes cleaner, more professional, and easier to render into PDF.

Input resume:
{resume_content}

Rules:
1. Title normalization:
   - Standardize the main title to **Professional Resume**.
   - Remove unrelated top-level descriptions.

2. Personal Information:
   - Place personal information under the second-level heading `## Personal Information`.
   - Preserve as much original information as possible.
   - Use English JSON keys such as "Name", "Gender", "Age", "Phone", "Email", "Current Location", "Degree", "Years of Experience", and "Target Role".

3. Professional Skills:
   - Merge related sections such as skills, strengths, and technology stack into one `## Professional Skills` section.
   - Remove duplicate ideas while keeping the strongest competitive signals.
   - Use Markdown bullet points.

4. Work Experience:
   - Sort entries in reverse chronological order.
   - Each title line must strictly follow:
     `Job Title | Company Name | Date Range`

5. Project Experience:
   - Sort projects in reverse chronological order when dates are available.
   - Use `### Project Name` for each project title.
   - The line immediately below the title should follow:
     `Job Title | Company Name | Date Range`
   - Use these English sublabels exactly:
     `Project Description:`
     `Tech Stack:`
     `Responsibilities:`
     `Highlights:`

6. Professional Summary:
   - Place it under `## Professional Summary`.
   - Output a single paragraph with no bullets.

Output example:

# Professional Resume

## Personal Information
```json
{{
  "Name": "Alex Chen",
  "Phone": "123-456-7890"
}}
```

## Professional Skills
- Skill one

## Work Experience
Senior Backend Engineer | Example Company | 2020-2023

## Project Experience
### Enterprise Knowledge Platform
Senior Backend Engineer | Example Company | 2020-2023
Project Description: ...
Tech Stack: ...
Responsibilities:
1. ...
Highlights:
1. ...
"""
