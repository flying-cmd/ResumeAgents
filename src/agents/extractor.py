import os
import glob
from src.state import AgentState
from src.tools.file_ops import read_resume_tool, save_document_tool
from rich.console import Console

console = Console()


def extractor_agent(state: AgentState):
    """Extract text from the resume file."""
    work_dir = state["work_dir"]
    data_dir = os.path.join(work_dir, "data")

    logs = []

    msg_start = f"[Extractor Agent] Scanning directory: {data_dir}..."
    console.print(f"[bold blue]{msg_start}[/bold blue]")
    logs.append(msg_start)

    pdfs = glob.glob(os.path.join(data_dir, "*.pdf"))
    docs = glob.glob(os.path.join(data_dir, "*.docx"))
    files = pdfs + docs

    file_ext = ""
    if files:
        file_ext = os.path.splitext(files[0])[1].lower()
        msg_detect = f"[Extractor Agent] Detected resume file: {os.path.basename(files[0])} ({file_ext})"
        console.print(f"[cyan]{msg_detect}[/cyan]")
        logs.append(msg_detect)

    console.print("[cyan][Extractor Agent] Reading the resume file...[/cyan]")
    result = read_resume_tool.invoke({"directory": data_dir})

    if result.startswith("Error"):
        msg_err = f"[Extractor Agent] Error: unable to extract resume content - {result}"
        console.print(f"[bold red]{msg_err}[/bold red]")
        logs.append(msg_err)
        return {
            "original_resume_text": "",
            "resume_file_extension": "",
            "progress": ["Extraction Failed"],
            "logs": logs,
        }

    msg_success = f"[Extractor Agent] Resume extracted successfully: {len(result)} characters."
    console.print(f"[green]{msg_success}[/green]")
    logs.append(msg_success)

    output_path = os.path.join(work_dir, "Optimized_Output", "extracted_content.txt")
    msg_save = f"[Extractor Agent] Saving extracted source text to {output_path}..."
    console.print(f"[cyan]{msg_save}[/cyan]")
    logs.append(msg_save)

    save_document_tool.invoke({"content": result, "file_path": output_path})

    return {
        "original_resume_text": result,
        "resume_file_extension": file_ext,
        "progress": ["Resume Extracted"],
        "logs": logs,
    }


# Workflow
# 1. Read the working directory from state.
# 2. Locate the data folder.
# 3. Search for PDF or DOCX resume files.
# 4. Detect the resume file extension.
# 5. Extract resume text with read_resume_tool.
# 6. Return a failure state if extraction fails.
# 7. Save the extracted text on success.
# 8. Return the extracted text, file extension, progress, and logs.
