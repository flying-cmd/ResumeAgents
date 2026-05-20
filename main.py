import os
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from src.graph import create_graph
from src.tools.file_ops import read_tech_stack_tool
from src.route import route_job_to_tech_stack
from src.memory.manager import memory_manager

console = Console()


def handle_interactive_memory(final_state):
    """Handle post-run interactive memory management."""
    console.print("\n" + "=" * 50)
    console.print("[bold cyan]Interactive Memory Management[/bold cyan]")
    console.print("=" * 50)

    sections = final_state.get("sections", {})
    if not sections:
        console.print("[yellow]No optimized sections were produced in this run. Skipping memory save.[/yellow]")
        return

    console.print("\nGenerated optimized sections:")
    for key in sections.keys():
        console.print(f"- {key}")

    console.print("\n[bold]Choose which sections to save to memory[/bold]")
    console.print("Enter section names separated by commas, for example: title, skills. Press Enter to skip.")

    user_input = Prompt.ask("Sections to save")

    if user_input.strip():
        selected_keys = [k.strip() for k in user_input.split(",") if k.strip()]

        for key in selected_keys:
            if key not in sections:
                console.print(f"[red]Section not found: {key}[/red]")
                continue

            original_content = final_state.get("original_resume_text", "")
            optimized_content = sections[key]

            current_context = {
                "job_name": final_state.get("job_name", ""),
                "technology_stack": final_state.get("technology_stack", ""),
            }

            if key == "self_evaluation":
                summary_str = json.dumps(sections, sort_keys=True, ensure_ascii=False)
                current_context["sections_summary"] = summary_str

            existing_content = memory_manager.get_optimized_content(key, original_content, current_context)
            should_save = True

            if existing_content:
                if existing_content == optimized_content:
                    console.print(f"[dim]Section [{key}] is unchanged. Skipping save.[/dim]")
                    continue

                should_save = Confirm.ask(
                    f"[yellow]A saved memory already exists for section [{key}]. Overwrite it?[/yellow]",
                    default=True,
                )

            if should_save:
                memory_manager.save_optimized_content(key, original_content, optimized_content, current_context)
                console.print(f"[green]Memory saved or updated for section [{key}].[/green]")
            else:
                console.print(f"[dim]Memory update canceled for section [{key}].[/dim]")

    if Confirm.ask("\nWould you like to open advanced memory maintenance (clean up or manual updates)?"):
        from utils.interactive_memory import interactive_mode

        interactive_mode()


def main():
    load_dotenv()
    work_dir = os.path.dirname(os.path.abspath(__file__))

    console.print(
        Panel.fit(
            "[bold blue]Multi-Agent Resume Optimization and Interview Prep System (LangGraph Edition)[/bold blue]"
        )
    )

    if not os.getenv("DASHSCOPE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        console.print(
            "[bold red]Error: No API key found. Please set DASHSCOPE_API_KEY or OPENAI_API_KEY in your .env file.[/bold red]"
        )
        return

    console.print("\n" + "=" * 50)
    console.print("[bold cyan]Enter the key job-search details[/bold cyan]")

    data_dir = os.path.join(work_dir, "data")
    resume_path = None

    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        candidates = [f for f in files if f.lower().endswith((".pdf", ".docx", ".doc"))]

        if candidates:
            # Choose the most recent file
            candidates.sort(
                key=lambda name: os.path.getmtime(os.path.join(data_dir, name)),
                reverse=True,
            )
            resume_path = os.path.join(data_dir, candidates[0])
            console.print(f"[green]Detected resume file automatically: {candidates[0]}[/green]")
        else:
            console.print(
                f"[red]Error: No valid resume file (.pdf, .docx, .doc) was found in {data_dir}.[/red]"
            )
            return
    else:
        console.print(f"[red]Error: Data directory does not exist: {data_dir}[/red]")
        return

    job_name = Prompt.ask(
        "Enter your [bold green]target role[/bold green] (for example: Python Backend Engineer)",
        default="Python Backend Engineer",
    )
    job_age = Prompt.ask(
        "Enter your [bold green]years of experience[/bold green] (for example: 3 years)",
        default="3 years",
    )
    console.print("=" * 50 + "\n")

    tech_stack_dir = os.path.join(work_dir, "data", "technology_stack")
    tech_file_name = route_job_to_tech_stack(job_name, tech_stack_dir)
    tech_stack_path = os.path.join(tech_stack_dir, tech_file_name)

    if not os.path.exists(tech_stack_path):
        tech_stack_path = os.path.join(work_dir, "data", tech_file_name)

    if not os.path.exists(tech_stack_path):
        tech_stack_path = os.path.join(work_dir, "data", "technology_stack.txt")

    console.print(f"[dim]Loading tech stack file: {os.path.basename(tech_stack_path)}[/dim]")

    tech_stack = read_tech_stack_tool.invoke(tech_stack_path)
    if tech_stack.startswith("Error"):
        console.print(f"[bold red]{tech_stack}[/bold red]")
        return

    console.print(f"\n[green]Loaded tech stack profile:[/green] {tech_stack[:50]}...")

    app = create_graph()
    initial_state = {
        "resume_path": resume_path,
        "job_name": job_name,
        "job_age": job_age,
        "technology_stack": tech_stack,
        "work_dir": work_dir,
        "original_resume_text": "",
        "optimized_resume_text": "",
        "sections": {},
        "progress": [],
        "logs": [],
    }

    final_state = None

    console.print("\n[bold yellow]Starting the agent workflow...[/bold yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task("Initializing system...", total=None)

        try:
            last_log_count = 0
            current_full_state = initial_state.copy()

            for event in app.stream(initial_state):
                for node_name, node_state in event.items():
                    current_full_state.update(node_state)

                    if "logs" in node_state and node_state["logs"]:
                        current_logs = node_state["logs"]
                        if len(current_logs) > last_log_count:
                            last_log_count = len(current_logs)

                    if "progress" in node_state and node_state["progress"]:
                        latest_update = node_state["progress"][-1]
                        progress.update(task_id, description=f"[green]Agent [{node_name}] completed: {latest_update}")
                    else:
                        progress.update(task_id, description=f"[cyan]Running: {node_name}...[/cyan]")

            final_state = current_full_state
            progress.update(task_id, completed=100, description="[bold green]All tasks completed.[/bold green]")

        except Exception as e:
            progress.update(task_id, description=f"[bold red]Execution failed: {str(e)}[/bold red]")
            console.print_exception()
            return

    output_dir = os.path.join(work_dir, "Optimized_Output")
    console.print("\n[bold]Generated files:[/bold]")
    console.print(f"- [blue]{os.path.join(output_dir, 'optimized_resume.md')}[/blue]")
    console.print(f"- [blue]{os.path.join(output_dir, 'Optimized_Resume.pdf')}[/blue]")
    console.print(f"- [blue]{os.path.join(output_dir, 'optimization_summary.md')}[/blue]")
    console.print(f"- [blue]{os.path.join(output_dir, 'self_introduction.md')}[/blue]")
    console.print(f"- [blue]{os.path.join(output_dir, 'interview_questions.md')}[/blue]")

    if final_state:
        handle_interactive_memory(final_state)


if __name__ == "__main__":
    main()


# Overall workflow
# Start
#   ↓
# Load .env
#   ↓
# Check API key
#   ↓
# Find the resume file in data/
#   ↓
# Ask for target role and years of experience
#   ↓
# Route the job name to the best matching tech stack file
#   ↓
# Read the tech stack file
#   ↓
# Create the LangGraph app
#   ↓
# Build the initial state
#   ↓
# Stream graph execution with a progress bar
#   ↓
# Collect the final state
#   ↓
# Print generated file paths
#   ↓
# Ask which optimized sections should be saved into memory
#   ↓
# Optional advanced memory maintenance
#   ↓
# End
