"""
Split prompts for section-based resume optimization.
"""
from src.conf import SELF_INTRO_LENGTH

# 0. Resume title
TITLE_PROMPT = """
You are a professional resume editor.
Generate a polished English title for the resume.

Source content:
{resume_content}

Requirements:
1. Output exactly: "Professional Resume".
2. Output plain text only.
3. Do not include Markdown symbols such as #.
"""

# 1. Personal information
PERSONAL_INFO_PROMPT = """
You are a professional data extraction specialist.
Extract the candidate's personal information from the source content and normalize it into a valid JSON block.

Source content:
{resume_content}

Requirements:
1. Output a single valid JSON object wrapped in a ```json code block.
2. Translate all extracted values to English when translation is natural and accurate.
3. Use these English keys whenever the information is available:
   - Name
   - Gender
   - Age
   - Phone
   - Email
   - Degree
   - Current Location
   - Hometown
   - Birth Date
   - Salary Expectation
   - Open to Work
   - Years of Experience
   - Target Role
4. Set "Target Role" to "{job_name}".
5. Set "Years of Experience" to "{job_age}" if the source content does not clearly provide a better value.
6. Do not invent facts that are not supported by the source content, except for the explicit Target Role and fallback Years of Experience above.
7. Output only the Markdown JSON block and nothing else.
"""

# 2. Professional skills
SKILLS_PROMPT = """
You are a technical recruiter and resume editor.
Rewrite the candidate's professional skills section in English based on the target role and highlighted technology stack.

Target role: {job_name}
Priority tech stack: {technology_stack}
Source content:
{resume_content}

Requirements:
1. Output in English only.
2. Use a strict Markdown unordered list.
3. Every line must start with "- ".
4. Keep each bullet to a single line.
5. Merge overlapping content from sections such as skills, strengths, and technology stack.
6. Remove duplicate ideas while preserving the strongest technical signals.
7. Use precise wording that reflects proficiency, such as "Expert in", "Proficient in", or "Familiar with".
8. Output only the skills content and do not include a "## Professional Skills" heading.
"""

# 3. Certifications
CERTIFICATE_PROMPT = """
You are a professional resume editor.
Identify certifications, awards, or language credentials from the source content and format them cleanly in English.

Source content:
{resume_content}

Requirements:
1. Extract certifications, qualifications, awards, and language credentials when present.
2. If a certificate is present but the year is missing, use "{default_cert_date}".
3. If a certificate is present but the issuing organization is missing, use "{default_cert_org}".
4. Format each item as:
   Certificate Name | Year | Issuing Organization
5. Output only the certification lines with no heading.
6. If no relevant information exists, output exactly: None
"""

# 4. Work experience
WORK_EXP_PROMPT = """
You are a professional resume editor.
Extract and format the candidate's work experience in English.

Source content:
{resume_content}

Requirements:
1. Sort entries in reverse chronological order.
2. Output one role per line.
3. Use this exact format for each line:
   Job Title | Company Name | Date Range
4. Translate the content to English.
5. Do not add explanations, bullets, headings, or extra commentary.
"""

# 5. Education
EDUCATION_PROMPT = """
You are a professional resume editor.
Extract and format the candidate's education history in English.

Source content:
{resume_content}

Requirements:
1. Sort entries in reverse chronological order.
2. Output one education entry per line.
3. Recommended format:
   Date Range | School Name | Major | Degree
4. Translate the content to English.
5. Do not add explanations or extra commentary.
"""

# 6. Project experience
PROJECT_EXP_PROMPT = """
You are a senior technical interviewer and resume editor.
Extract the candidate's project experience from the source content, then refine it for the target role in English.

Target role: {job_name}
Priority tech stack: {technology_stack}
Source content:
{resume_content}

Requirements:
1. Output in English only.
2. Each project must start with a third-level Markdown title:
   ### Project Name
3. Each project must contain these four labels exactly:
   Project Description:
   Tech Stack:
   Responsibilities:
   Highlights:
4. Keep "Project Description" and "Tech Stack" on a single line after the colon.
5. Use English commas in "Tech Stack".
6. Under "Responsibilities" and "Highlights", use numbered lines beginning with "1. ".
7. Improve clarity and technical depth, but do not invent new projects or false experience.
8. Output only the project experience content and do not include a "## Project Experience" heading.
"""

# 7. Professional summary
SELF_EVAL_PROMPT = """
You are a senior career coach.
Write an English professional summary that fits the candidate's resume closely.

Optimized resume summary:
{optimized_sections_summary}

Requirements:
1. Aim for about {SELF_INTRO_LENGTH} words.
2. Output a single plain-text paragraph in English.
3. Do not use bullet points, numbering, indentation, or line breaks.
4. Summarize the candidate's core strengths, technical focus, professional style, and fit for the target role.
5. Output only the paragraph and nothing else.
"""
