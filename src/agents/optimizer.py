import os
from src.state import AgentState
from src.llm.factory import get_llm
from src.prompts.optimizer_prompt import RESUME_OPTIMIZE_PROMPT, OPTIMIZATION_SUMMARY_PROMPT
from src.tools.file_ops import save_document_tool
from rich.console import Console

console = Console()


def optimizer_agent(state: AgentState):
    """Optimize the resume and generate an optimization summary."""
    logs = []
    llm = get_llm()

    console.print("[bold blue][Optimizer Agent] Initializing the language model...[/bold blue]")
    logs.append("[Optimizer Agent] Model initialized.")

    console.print("[cyan][Optimizer Agent] Optimizing the resume content. This may take a moment...[/cyan]")
    logs.append("[Optimizer Agent] Starting resume optimization...")

    try:
        optimize_prompt = RESUME_OPTIMIZE_PROMPT.format(
            job_name=state["job_name"],
            job_age=state["job_age"],
            technology_stack=state["technology_stack"],
            resume_content=state["original_resume_text"],
        )

        optimized_response = llm.invoke(optimize_prompt)
        optimized_text = optimized_response.content
        logs.append("[Optimizer Agent] Resume optimization completed.")
        console.print("[green][Optimizer Agent] Resume optimization completed.[/green]")
    except Exception as e:
        error_msg = f"[Optimizer Agent] Error: resume optimization failed - {str(e)}"
        console.print(f"[bold red]{error_msg}[/bold red]")
        logs.append(error_msg)
        return {"logs": logs}

    console.print("[cyan][Optimizer Agent] Generating the optimization summary...[/cyan]")
    logs.append("[Optimizer Agent] Generating summary...")

    try:
        summary_prompt = OPTIMIZATION_SUMMARY_PROMPT.format(
            original_resume=state["original_resume_text"],
            optimized_resume=optimized_text,
            job_name=state["job_name"],
        )

        summary_response = llm.invoke(summary_prompt)
        summary_text = summary_response.content
        logs.append("[Optimizer Agent] Summary generation completed.")
        console.print("[green][Optimizer Agent] Summary generation completed.[/green]")
    except Exception as e:
        error_msg = f"[Optimizer Agent] Error: summary generation failed - {str(e)}"
        console.print(f"[bold red]{error_msg}[/bold red]")
        logs.append(error_msg)
        summary_text = "Error generating summary."

    out_dir = os.path.join(state["work_dir"], "Optimized_Output")

    msg_save = f"[Optimizer Agent] Saving the summary to {out_dir}..."
    console.print(f"[cyan]{msg_save}[/cyan]")
    logs.append(msg_save)

    save_document_tool.invoke(
        {"content": optimized_text, "file_path": os.path.join(out_dir, "optimized_resume_intermediate.md")}
    )
    save_document_tool.invoke({"content": summary_text, "file_path": os.path.join(out_dir, "optimization_summary.md")})

    return {
        "optimized_resume_text": optimized_text,
        "optimization_summary": summary_text,
        "progress": ["Resume Optimized", "Summary Generated"],
        "logs": logs,
    }
