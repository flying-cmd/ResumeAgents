import os
from rich.console import Console
from src.llm.factory import get_llm

console = Console()

ZH_LLM = "\u5927\u6a21\u578b"
ZH_FRONTEND = "\u524d\u7aef"
ZH_TEST_DEV = "\u6d4b\u8bd5\u5f00\u53d1"
ZH_QA_SHORT = "\u6d4b\u5f00"
ZH_TESTING = "\u6d4b\u8bd5"
ZH_SRE = "\u8fd0\u7ef4\u5f00\u53d1"
ZH_DEVOPS = "\u8fd0\u7ef4"
ZH_PRODUCT = "\u4ea7\u54c1"
ZH_BACKEND = "\u540e\u7aef"


def route_job_to_tech_stack(job_name: str, tech_stack_dir: str) -> str:
    """
    Route the user's target role to the most suitable technology stack file.
    A mix of rule-based matching and semantic matching is used.
    """
    job_lower = job_name.lower()

    rules = [
        # Java + LLM/AI
        (lambda j: "java" in j and (ZH_LLM in j or "llm" in j or "ai" in j), "java_llm.txt"),
        # Python + LLM/AI
        (lambda j: "python" in j and (ZH_LLM in j or "llm" in j or "ai" in j), "llm_app_dev.txt"),
        # General LLM/AI
        (lambda j: ZH_LLM in j or "llm" in j, "llm_app_dev.txt"),
        # Java backend
        (lambda j: "java" in j, "java_backend.txt"),
        # Python backend
        (lambda j: "python" in j, "python_backend.txt"),
        # Frontend
        (lambda j: ZH_FRONTEND in j or "frontend" in j or "vue" in j or "react" in j, "frontend.txt"),
        # Testing
        (lambda j: ZH_TEST_DEV in j or ZH_QA_SHORT in j, "test_dev.txt"),
        (lambda j: ZH_TESTING in j or "qa" in j, "testing_manual.txt"),
        # DevOps / SRE
        (lambda j: ZH_SRE in j or "sre" in j, "sre.txt"),
        (lambda j: ZH_DEVOPS in j or "devops" in j, "devops.txt"),
        # Product
        (lambda j: ZH_PRODUCT in j or "pm" in j or "product manager" in j, "product_manager.txt"),
        # Generic backend
        (lambda j: ZH_BACKEND in j and "python" not in j and "java" not in j, "java_backend.txt"),
    ]

    for matcher, filename in rules:
        if matcher(job_lower):
            console.print(f"[cyan]Route match:[/cyan] Rule hit -> {filename}")
            return filename

    console.print("[yellow]Route match:[/yellow] No rule hit. Trying semantic matching...")

    try:
        if not os.path.exists(tech_stack_dir):
            return "technology_stack.txt"

        files = [f for f in os.listdir(tech_stack_dir) if f.endswith(".txt")]
        if not files:
            return "technology_stack.txt"

        llm = get_llm()

        prompt = f"""
        You are a smart routing assistant.
        The user entered this target role: "{job_name}"

        The available technology stack files are:
        {", ".join(files)}

        Analyze the target role and choose the single best matching filename from the list.
        Output only the filename and nothing else.
        If you cannot determine a good match, output "technology_stack.txt".
        """

        response = llm.invoke(prompt)
        matched_file = response.content.strip()

        if matched_file in files:
            console.print(f"[green]Semantic match:[/green] LLM selected -> {matched_file}")
            return matched_file

        console.print(
            f"[red]Semantic match:[/red] LLM returned an invalid filename '{matched_file}'. Falling back to default."
        )

    except Exception as e:
        console.print(f"[bold red]Semantic match failed:[/bold red] {e}")

    return "technology_stack.txt"
