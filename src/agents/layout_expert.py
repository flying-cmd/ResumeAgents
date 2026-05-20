import os
from src.state import AgentState
from src.tools.file_ops import generate_docx_tool
from src.tools.pdf_ops import generate_pdf_tool
from rich.console import Console

console = Console()


def layout_expert_agent(state: AgentState):
    """
    Render the final resume document (PDF or DOCX) from the structured Markdown.
    """
    logs = []
    console.print("[cyan][Layout Agent] Rendering the final resume file...[/cyan]")
    logs.append("[Layout Agent] Starting document rendering...")

    current_resume = state.get("optimized_resume_text", "")
    if not current_resume:
        msg = "[Layout Agent] Error: no structured resume content was found."
        console.print(f"[bold red]{msg}[/bold red]")
        logs.append(msg)
        return {"logs": logs}

    out_dir = os.path.join(state["work_dir"], "Optimized_Output")
    input_ext = state.get("resume_file_extension", ".pdf").lower()
    progress_msg = ""

    try:
        if input_ext == ".docx":
            docx_path = os.path.join(out_dir, "Optimized_Resume.docx")
            msg_doc = f"[Layout Agent] Word input detected. Generating DOCX: {docx_path}..."
            console.print(f"[cyan]{msg_doc}[/cyan]")
            logs.append(msg_doc)
            doc_result = generate_docx_tool.invoke({"markdown_content": current_resume, "output_path": docx_path})
            logs.append(f"[Layout Agent] {doc_result}")
            progress_msg = "Word Document Created"
        else:
            pdf_path = os.path.join(out_dir, "Optimized_Resume.pdf")
            msg_pdf = f"[Layout Agent] PDF input detected (or default fallback). Generating PDF: {pdf_path}..."
            console.print(f"[cyan]{msg_pdf}[/cyan]")
            logs.append(msg_pdf)
            pdf_result = generate_pdf_tool.invoke({"markdown_content": current_resume, "output_path": pdf_path})
            logs.append(f"[Layout Agent] {pdf_result}")
            progress_msg = "PDF Created"

        logs.append("[Layout Agent] File generation completed.")
        console.print("[green][Layout Agent] File generation completed.[/green]")

        return {
            "progress": ["Layout Rendered", progress_msg],
            "logs": logs,
        }

    except Exception as e:
        error_msg = f"[Layout Agent] Error: file generation failed - {str(e)}"
        console.print(f"[bold red]{error_msg}[/bold red]")
        logs.append(error_msg)
        return {"logs": logs}
