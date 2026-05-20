import os
import concurrent.futures
from rich.console import Console
from src.state import AgentState
from src.llm.factory import get_llm
from src.prompts.optimizer_prompt import SELF_INTRO_PROMPT, INTERVIEW_QUESTIONS_TEMPLATE
from src.tools.file_ops import save_document_tool
from src.conf import SELF_INTRO_LENGTH, TOTAL_INTERVIEW_QUESTIONS, QUESTIONS_PER_BATCH

console = Console()


def generate_batch(batch_config, job_name, optimized_resume, technology_stack):
    """Generate one batch of interview questions."""
    llm = get_llm()
    start = batch_config["start"]
    end = batch_config["end"]
    q_type = batch_config["type"]

    try:
        prompt = INTERVIEW_QUESTIONS_TEMPLATE.format(
            job_name=job_name,
            optimized_resume=optimized_resume,
            technology_stack=technology_stack,
            question_type=q_type,
            num_questions=end - start + 1,
            start_index=start,
            end_index=end,
            focus_area=batch_config["focus"],
        )
        response = llm.invoke(prompt)
        return {
            "success": True,
            "start": start,
            "end": end,
            "type": q_type,
            "content": response.content,
        }
    except Exception as e:
        return {
            "success": False,
            "start": start,
            "end": end,
            "error": str(e),
        }


def interviewer_agent(state: AgentState):
    """Generate a self-introduction and interview questions."""
    logs = []
    llm = get_llm()

    msg_start = "[Interviewer Agent] Starting interview preparation tasks..."
    console.print(f"[bold blue]{msg_start}[/bold blue]")
    logs.append(msg_start)

    msg_intro = f"[Interviewer Agent] Generating a professional self-introduction (about {SELF_INTRO_LENGTH} words)..."
    console.print(f"[cyan]{msg_intro}[/cyan]")
    logs.append(msg_intro)

    try:
        intro_prompt = SELF_INTRO_PROMPT.format(
            optimized_resume=state["optimized_resume_text"],
            job_age=state["job_age"],
            technology_stack=state["technology_stack"],
            self_intro_length=SELF_INTRO_LENGTH,
        )
        intro_response = llm.invoke(intro_prompt)
        intro_text = intro_response.content

        msg_intro_done = "[Interviewer Agent] Self-introduction generated."
        console.print(f"[green]{msg_intro_done}[/green]")
        logs.append(msg_intro_done)

    except Exception as e:
        error_msg = f"[Interviewer Agent] Error: self-introduction generation failed - {str(e)}"
        console.print(f"[bold red]{error_msg}[/bold red]")
        logs.append(error_msg)
        intro_text = "Error generating self introduction."

    questions_full_text = "# Interview Question Bank\n\n"

    total_qs = TOTAL_INTERVIEW_QUESTIONS
    per_batch = QUESTIONS_PER_BATCH
    batches_config = []
    current_q = 1

    project_qs_count = max(per_batch, int(total_qs * 0.1))
    project_qs_count = (project_qs_count // per_batch) * per_batch
    if project_qs_count == 0:
        project_qs_count = per_batch

    for _ in range(0, project_qs_count, per_batch):
        if current_q > total_qs:
            break
        end_q = min(current_q + per_batch - 1, total_qs)
        batches_config.append(
            {
                "start": current_q,
                "end": end_q,
                "type": "Project Deep-Dive Questions",
                "focus": "Ask detailed questions about the candidate's specific projects, technical choices, major challenges, and solutions.",
            }
        )
        current_q = end_q + 1

    basic_qs_count = int(total_qs * 0.3)
    basic_qs_count = (basic_qs_count // per_batch) * per_batch
    for _ in range(0, basic_qs_count, per_batch):
        if current_q > total_qs:
            break
        end_q = min(current_q + per_batch - 1, total_qs)
        batches_config.append(
            {
                "start": current_q,
                "end": end_q,
                "type": "Fundamental Skills Questions",
                "focus": "Test language fundamentals, common libraries, core concepts, and underlying principles.",
            }
        )
        current_q = end_q + 1

    adv_qs_count = int(total_qs * 0.3)
    adv_qs_count = (adv_qs_count // per_batch) * per_batch
    for _ in range(0, adv_qs_count, per_batch):
        if current_q > total_qs:
            break
        end_q = min(current_q + per_batch - 1, total_qs)
        batches_config.append(
            {
                "start": current_q,
                "end": end_q,
                "type": "Advanced Skills Questions",
                "focus": "Assess advanced features, tooling, architecture tradeoffs, and best practices.",
            }
        )
        current_q = end_q + 1

    while current_q <= total_qs:
        end_q = min(current_q + per_batch - 1, total_qs)
        batches_config.append(
            {
                "start": current_q,
                "end": end_q,
                "type": "Scenario Design and Architecture Questions",
                "focus": "Cover high-concurrency systems, high availability, framework internals, and business scenario design.",
            }
        )
        current_q = end_q + 1

    total_batches = len(batches_config)
    msg_batch_start = (
        f"[Interviewer Agent] Generating {total_qs} interview questions across {total_batches} batch(es)..."
    )
    console.print(f"[cyan]{msg_batch_start}[/cyan]")
    logs.append(msg_batch_start)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_batch = {
            executor.submit(
                generate_batch,
                batch,
                state["job_name"],
                state["optimized_resume_text"],
                state["technology_stack"],
            ): batch
            for batch in batches_config
        }

        for future in concurrent.futures.as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                data = future.result()
                results.append(data)
                if data["success"]:
                    msg_batch_done = (
                        f"[Interviewer Agent] Batch complete: Q{data['start']}-Q{data['end']}."
                    )
                    console.print(f"[green]{msg_batch_done}[/green]")
                else:
                    msg_batch_err = (
                        f"[Interviewer Agent] Error: batch Q{batch['start']}-Q{batch['end']} failed - {data.get('error')}"
                    )
                    console.print(f"[bold red]{msg_batch_err}[/bold red]")
                    logs.append(msg_batch_err)
            except Exception as exc:
                msg_exc = (
                    f"[Interviewer Agent] Error: batch Q{batch['start']}-Q{batch['end']} raised an exception - {exc}"
                )
                console.print(f"[bold red]{msg_exc}[/bold red]")
                logs.append(msg_exc)

    results.sort(key=lambda x: x["start"])

    current_section = ""
    for res in results:
        if not res.get("success"):
            questions_full_text += f"\n\n**[Error generating Q{res['start']}-Q{res['end']}]**\n\n"
            continue

        if res["type"] != current_section:
            questions_full_text += f"## {res['type']}\n\n"
            current_section = res["type"]

        questions_full_text += res["content"] + "\n\n"

    msg_all_done = "[Interviewer Agent] All interview questions generated."
    console.print(f"[bold green]{msg_all_done}[/bold green]")
    logs.append(msg_all_done)

    out_dir = os.path.join(state["work_dir"], "Optimized_Output")

    msg_save = f"[Interviewer Agent] Saving outputs to {out_dir}..."
    console.print(f"[cyan]{msg_save}[/cyan]")
    logs.append(msg_save)

    save_document_tool.invoke({"content": intro_text, "file_path": os.path.join(out_dir, "self_introduction.md")})
    save_document_tool.invoke({"content": questions_full_text, "file_path": os.path.join(out_dir, "interview_questions.md")})

    return {
        "self_intro": intro_text,
        "interview_questions": questions_full_text,
        "progress": ["Self Introduction Generated", f"Interview Questions Generated ({total_qs} Qs)"],
        "logs": logs,
    }
