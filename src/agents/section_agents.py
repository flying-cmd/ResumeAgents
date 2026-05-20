"""
Agents dedicated to optimizing specific resume sections with memory enhancement.
"""
import os
import json
import re
from rich.console import Console
from src.state import AgentState
from src.llm.factory import get_llm
from src.prompts.section_prompts import (
    TITLE_PROMPT,
    PERSONAL_INFO_PROMPT,
    SKILLS_PROMPT,
    CERTIFICATE_PROMPT,
    WORK_EXP_PROMPT,
    EDUCATION_PROMPT,
    PROJECT_EXP_PROMPT,
    SELF_EVAL_PROMPT,
)
from src.memory.manager import memory_manager
from src.conf import DEFAULT_SALARY, DEFAULT_IS_RESIGNED, SELF_INTRO_LENGTH, DEFAULT_CERT_DATE, DEFAULT_CERT_ORG
from src.tools.pdf_generator import convert_markdown_to_pdf

console = Console()

LEGACY_NAME = "\u59d3\u540d"
LEGACY_GENDER = "\u6027\u522b"
LEGACY_AGE = "\u5e74\u9f84"
LEGACY_PHONE = "\u7535\u8bdd"
LEGACY_EMAIL = "\u90ae\u7bb1"
LEGACY_DEGREE = "\u5b66\u5386"
LEGACY_LOCATION = "\u73b0\u5c45\u5730"
LEGACY_HOMETOWN = "\u7c4d\u8d2f"
LEGACY_BIRTH_DATE = "\u51fa\u751f\u5e74\u6708"
LEGACY_SALARY = "\u85aa\u8d44\u5f85\u9047"
LEGACY_RESIGNED = "\u662f\u5426\u79bb\u804c"
LEGACY_OPEN_TO_WORK = "\u804c\u4e1a\u72b6\u6001"
LEGACY_YOE = "\u5de5\u4f5c\u5e74\u9650"
LEGACY_TARGET_ROLE = "\u6c42\u804c\u610f\u5411"

LEGACY_PROJECT_DESCRIPTION = "\u9879\u76ee\u63cf\u8ff0"
LEGACY_TECH_STACK = "\u6280\u672f\u6808"
LEGACY_RESPONSIBILITIES = "\u804c\u8d23"
LEGACY_HIGHLIGHTS = "\u9879\u76ee\u4eae\u70b9"
LEGACY_PROJECT = "\u9879\u76ee"
LEGACY_NONE = "\u65e0"

PERSONAL_INFO_KEY_MAP = {
    LEGACY_NAME: "Name",
    LEGACY_GENDER: "Gender",
    LEGACY_AGE: "Age",
    LEGACY_PHONE: "Phone",
    LEGACY_EMAIL: "Email",
    LEGACY_DEGREE: "Degree",
    LEGACY_LOCATION: "Current Location",
    LEGACY_HOMETOWN: "Hometown",
    LEGACY_BIRTH_DATE: "Birth Date",
    LEGACY_SALARY: "Salary Expectation",
    LEGACY_RESIGNED: "Open to Work",
    LEGACY_OPEN_TO_WORK: "Open to Work",
    LEGACY_YOE: "Years of Experience",
    LEGACY_TARGET_ROLE: "Target Role",
}

PERSONAL_INFO_ORDER = [
    "Name",
    "Gender",
    "Age",
    "Phone",
    "Email",
    "Degree",
    "Target Role",
    "Current Location",
    "Hometown",
    "Birth Date",
    "Salary Expectation",
    "Open to Work",
    "Years of Experience",
]

PROJECT_LABEL_MAP = {
    LEGACY_PROJECT_DESCRIPTION: "Project Description",
    LEGACY_TECH_STACK: "Tech Stack",
    LEGACY_RESPONSIBILITIES: "Responsibilities",
    LEGACY_HIGHLIGHTS: "Highlights",
    "Project Description": "Project Description",
    "Tech Stack": "Tech Stack",
    "Responsibilities": "Responsibilities",
    "Highlights": "Highlights",
}


def contains_han(text: str) -> bool:
    """Return True when the text contains Han characters."""
    return bool(text and re.search(r"[\u4e00-\u9fff]", text))


def clean_text_spacing(text: str) -> str:
    """
    Normalize spacing in multilingual text:
    1. Remove spaces between Han characters.
    2. Remove spaces between Han characters and Latin letters or digits.
    3. Preserve normal spacing between pure English words.
    """
    if not text:
        return text

    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        if not line.strip():
            cleaned_lines.append(line)
            continue

        line = re.sub(r"([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])", r"\1\2", line)
        line = re.sub(r"([\u4e00-\u9fa5])\s+([^\u4e00-\u9fa5])", r"\1\2", line)
        line = re.sub(r"([^\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])", r"\1\2", line)

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def normalize_personal_info_data(data: dict) -> dict:
    """Convert legacy personal-info keys to the English key set."""
    normalized = {}
    for key, value in data.items():
        normalized_key = PERSONAL_INFO_KEY_MAP.get(key, key)
        normalized[normalized_key] = value
    return normalized


def normalize_project_label_line(line: str) -> str:
    """Convert legacy project field labels to their English equivalents."""
    for label, normalized in PROJECT_LABEL_MAP.items():
        for separator in (":", "\uff1a"):
            prefix = f"{label}{separator}"
            if line.startswith(prefix):
                remainder = line[len(prefix):].strip()
                return f"{normalized}: {remainder}".rstrip()
    return line


def _run_section_agent(state: AgentState, section_key: str, prompt_template: str, config_key: str) -> dict:
    """Run a generic section agent with memory support."""
    logs = []
    agent_name = f"Agent-{section_key}"
    console.print(f"[cyan][{agent_name}] Processing...[/cyan]")
    logs.append(f"[{agent_name}] Started processing.")

    original_resume = state.get("original_resume_text", "")
    job_name = state.get("job_name", "")
    tech_stack = state.get("technology_stack", "")

    memory_context = {"job_name": job_name, "technology_stack": tech_stack}

    if section_key == "self_evaluation":
        sections = state.get("sections", {})
        summary_str = json.dumps(sections, sort_keys=True, ensure_ascii=False)
        memory_context["sections_summary"] = summary_str

    cached_content = memory_manager.get_optimized_content(section_key, original_resume, memory_context)
    content = ""
    is_memory_hit = False

    if cached_content and contains_han(cached_content):
        msg = f"[{agent_name}] Legacy non-English memory detected. Regenerating this section in English."
        console.print(f"[yellow]{msg}[/yellow]")
        logs.append(msg)
        cached_content = None

    if cached_content:
        console.print(f"[green][{agent_name}] Memory hit. Skipping LLM generation.[/green]")
        logs.append(f"[{agent_name}] Memory hit.")
        content = cached_content
        is_memory_hit = True
    else:
        format_args = {
            "resume_content": original_resume,
            "job_name": job_name,
            "job_age": state.get("job_age", "3 years"),
            "technology_stack": tech_stack,
            "SELF_INTRO_LENGTH": SELF_INTRO_LENGTH,
            "default_cert_date": DEFAULT_CERT_DATE,
            "default_cert_org": DEFAULT_CERT_ORG,
        }

        if section_key == "self_evaluation":
            sections = state.get("sections", {})
            summary = "\n".join([f"--- {k} ---\n{v}" for k, v in sections.items() if v])
            format_args["optimized_sections_summary"] = summary

        try:
            prompt = prompt_template.format(**format_args)
            llm = get_llm()
            response = llm.invoke(prompt)
            content = response.content.strip()

            if section_key != "personal_info":
                if content.startswith("```markdown"):
                    content = content.replace("```markdown", "").replace("```", "").strip()
                elif content.startswith("```"):
                    content = content.replace("```", "").strip()

                content = clean_text_spacing(content)

            if section_key == "personal_info":
                try:
                    json_str = content
                    if json_str.startswith("```json"):
                        json_str = json_str.replace("```json", "", 1)
                    if json_str.startswith("```"):
                        json_str = json_str.replace("```", "", 1)
                    if json_str.endswith("```"):
                        json_str = json_str[:-3]
                    json_str = json_str.strip()

                    data = json.loads(json_str)
                    data = normalize_personal_info_data(data)

                    if not data.get("Salary Expectation"):
                        data["Salary Expectation"] = DEFAULT_SALARY
                    if not data.get("Open to Work"):
                        data["Open to Work"] = DEFAULT_IS_RESIGNED
                    if job_name:
                        data["Target Role"] = job_name

                    md_lines = []
                    for key in PERSONAL_INFO_ORDER:
                        if key in data and data[key]:
                            md_lines.append(f"{key}: {data[key]}")

                    for key, value in data.items():
                        if key not in PERSONAL_INFO_ORDER and value:
                            md_lines.append(f"{key}: {value}")

                    content = "\n".join(md_lines)

                except Exception as e:
                    console.print(f"[yellow]Warning: failed to parse or normalize personal info JSON: {e}[/yellow]")

            elif section_key == "skills":
                lines = [line.strip() for line in content.split("\n") if line.strip()]
                cleaned_lines = []
                for line in lines:
                    if not line.startswith("-"):
                        line = f"- {line}"
                    cleaned_lines.append(line)
                content = "\n".join(cleaned_lines)

            elif section_key == "self_evaluation":
                content = content.replace("\n", "").strip()
                content = clean_text_spacing(content)
                content = content.lstrip()

            elif section_key == "project_experience":
                lines = content.split("\n")
                cleaned_lines = []
                current_block = []

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    line = normalize_project_label_line(line)

                    if line.startswith("#"):
                        if current_block:
                            cleaned_lines.append("".join(current_block))
                            current_block = []
                        clean_title = line.replace("#", "").strip()
                        cleaned_lines.append(f"### {clean_title}")

                    elif any(line.startswith(f"{label}:") for label in PROJECT_LABEL_MAP.values()):
                        if current_block:
                            cleaned_lines.append("".join(current_block))
                            current_block = []
                        cleaned_lines.append(line)

                    elif re.match(r"^(\d+\.)", line) or line.startswith("-"):
                        if current_block:
                            cleaned_lines.append("".join(current_block))
                            current_block = []
                        cleaned_lines.append(line)
                    else:
                        current_block.append(line)

                if current_block:
                    cleaned_lines.append("".join(current_block))

                content = "\n".join(cleaned_lines)

            logs.append(f"[{agent_name}] Completed with LLM generation.")
            console.print(f"[green][{agent_name}] Completed.[/green]")

            debug_content = content[:500] + "..." if len(content) > 500 else content
            console.print(f"[dim]--- [{agent_name}] Generated content preview ---[/dim]")
            console.print(f"[dim]{debug_content}[/dim]")
            console.print("[dim]----------------------------------------------[/dim]")
            logs.append(f"[{agent_name}] Generated content preview: {debug_content}")

        except Exception as e:
            error_msg = f"[{agent_name}] Error: {str(e)}"
            console.print(f"[bold red]{error_msg}[/bold red]")
            logs.append(error_msg)
            return {"logs": logs}

    if content and section_key != "title":
        try:
            work_dir = state.get("work_dir", ".")
            intermediate_dir = os.path.join(work_dir, "Optimized_Output", "intermediate")
            os.makedirs(intermediate_dir, exist_ok=True)

            pdf_filename = f"{section_key}_optimized.pdf"
            pdf_path = os.path.join(intermediate_dir, pdf_filename)
            temp_md = f"# {section_key.replace('_', ' ').title()}\n\n{content}"

            convert_markdown_to_pdf(temp_md, pdf_path)
            logs.append(f"[{agent_name}] Saved intermediate PDF: {pdf_filename}")
        except Exception as e:
            console.print(f"[yellow]Warning: failed to generate the intermediate PDF for {section_key}: {e}[/yellow]")

    current_sections = state.get("sections", {})
    if current_sections is None:
        current_sections = {}

    current_sections[section_key] = content

    memory_hits = state.get("memory_hits", [])
    if is_memory_hit:
        memory_hits.append(section_key)

    return {
        "sections": current_sections,
        "memory_hits": memory_hits,
        "logs": logs,
    }


def title_agent(state: AgentState):
    return _run_section_agent(state, "title", TITLE_PROMPT, "title")


def personal_info_agent(state: AgentState):
    return _run_section_agent(state, "personal_info", PERSONAL_INFO_PROMPT, "personal_info")


def skills_agent(state: AgentState):
    return _run_section_agent(state, "skills", SKILLS_PROMPT, "skills")


def certificate_agent(state: AgentState):
    return _run_section_agent(state, "certificate", CERTIFICATE_PROMPT, "certificate")


def work_experience_agent(state: AgentState):
    return _run_section_agent(state, "work_experience", WORK_EXP_PROMPT, "work_experience")


def education_agent(state: AgentState):
    return _run_section_agent(state, "education", EDUCATION_PROMPT, "education")


def project_experience_agent(state: AgentState):
    return _run_section_agent(state, "project_experience", PROJECT_EXP_PROMPT, "project_experience")


def self_evaluation_agent(state: AgentState):
    return _run_section_agent(state, "self_evaluation", SELF_EVAL_PROMPT, "self_introduction")


def assembler_agent(state: AgentState):
    """Combine all optimized sections into the final resume."""
    logs = []
    console.print("[cyan][Assembler] Assembling the final resume...[/cyan]")

    sections = state.get("sections", {})

    title = sections.get("title", "Professional Resume")
    final_md = f"# {title}\n\n"

    personal_info = sections.get("personal_info", "")
    if personal_info:
        final_md += "## Personal Information\n"
        final_md += personal_info + "\n\n"

    skills = sections.get("skills", "")
    if skills:
        final_md += "## Professional Skills\n"
        final_md += skills + "\n\n"

    certifications = sections.get("certificate", "")
    if certifications and certifications.strip().lower() != "none" and certifications.strip() != LEGACY_NONE:
        final_md += "## Certifications\n"
        final_md += certifications + "\n\n"

    work_experience = sections.get("work_experience", "")
    if work_experience:
        final_md += "## Work Experience\n"
        final_md += work_experience + "\n\n"

    education = sections.get("education", "")
    if education:
        final_md += "## Education\n"
        final_md += education + "\n\n"

    project_experience = sections.get("project_experience", "")
    if project_experience:
        final_md += "## Project Experience\n"
        final_md += project_experience + "\n\n"

    professional_summary = sections.get("self_evaluation", "")
    if professional_summary:
        final_md += "## Professional Summary\n"
        final_md += professional_summary + "\n\n"

    output_dir = os.path.join(state.get("work_dir", "."), "Optimized_Output")
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "Optimized_Resume.pdf")

    try:
        if convert_markdown_to_pdf(final_md, pdf_path):
            logs.append(f"[Assembler] Resume PDF generated successfully: {pdf_path}")
            console.print("[green][Assembler] Resume PDF generated successfully.[/green]")
        else:
            logs.append("[Assembler] Resume PDF generation failed.")
            console.print("[red][Assembler] Resume PDF generation failed.[/red]")
    except Exception as e:
        console.print(f"[red]PDF generation error: {e}[/red]")
        logs.append(f"PDF generation error: {str(e)}")

    md_path = os.path.join(output_dir, "optimized_resume.md")
    with open(md_path, "w", encoding="utf-8") as file_obj:
        file_obj.write(final_md)

    return {
        "optimized_resume_text": final_md,
        "logs": logs,
    }
