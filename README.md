# Multi-Agent Resume Optimization and Interview Prep System

This project is a command-line resume workflow built with **LangGraph** and **LangChain**. It takes a raw resume file from the local `data/` directory, routes the request to a role-specific technology stack profile, generates an improved English resume section by section, renders the output to PDF and optionally DOCX, and then creates interview-preparation materials such as a self-introduction and interview questions.

The repository is designed for practical, local use:
- Put a resume file in `data/`
- Configure an LLM provider in `.env`
- Run `python main.py`
- Collect the generated files from `Optimized_Output/`

## What This Project Does

The app automates the following flow:

1. Detect the newest resume file in `data/`
2. Extract text from `PDF`, `DOCX`, or legacy `DOC`
3. Ask for the target role and years of experience
4. Match the role to a technology stack profile
5. Generate English resume sections with role-aware prompts
6. Assemble the final Markdown resume
7. Render a polished PDF and, when applicable, a DOCX
8. Generate:
   - a professional self-introduction
   - an interview question bank
9. Optionally save optimized sections into a local memory store for reuse

## Key Features

- **Section-based optimization**
  The resume is generated section by section instead of as one large prompt.

- **Role-aware routing**
  The target role is matched against technology stack profiles such as Python backend, Java backend, frontend, DevOps, SRE, testing, product, and LLM-oriented roles.

- **Multiple LLM backends**
  The app supports:
  - DashScope / Qwen
  - DeepSeek via OpenAI-compatible API
  - OpenAI

- **English output pipeline**
  The current prompts and section assembly pipeline are configured to generate English resume content.

- **Memory-enhanced generation**
  Previously optimized sections can be cached locally and reused when the same source content and context are seen again.

- **PDF rendering**
  The app renders a structured PDF using ReportLab-based formatting tuned for resume-style output.

- **DOCX resilience**
  DOCX extraction works even if `docx2txt` is not installed, thanks to a built-in XML fallback parser.

## Current Behavior and Assumptions

- The app automatically selects the **newest** `PDF`, `DOCX`, or `DOC` file in `data/`.
- Resume output is generated in **English**.
- Source resumes may still be Chinese or mixed-language.
- The app is most comfortable on **Windows**, especially when handling legacy `.doc` files, because `.doc` conversion depends on Microsoft Word automation through `pywin32`.
- The app is interactive and expects terminal prompts for:
  - target role
  - years of experience
  - optional memory save/update decisions

## Project Structure

```text
.
├── .env
├── .gitignore
├── README.md
├── architecture_design.md
├── main.py
├── requirements.txt
├── data/
│   ├── memory_store/
│   ├── technology_stack/
│   ├── resume.docx
│   └── resume_unoptimized_source.md
├── fonts/
├── Optimized_Output/
├── src/
│   ├── agents/
│   ├── llm/
│   ├── memory/
│   ├── prompts/
│   ├── tools/
│   ├── conf.py
│   ├── graph.py
│   ├── route.py
│   └── state.py
└── utils/
```

## Main Components

### `main.py`

The CLI entrypoint. It is responsible for:
- loading environment variables
- selecting the newest resume file from `data/`
- asking the user for job metadata
- loading the technology stack profile
- running the LangGraph workflow
- printing generated file paths
- handling post-run interactive memory management

### `src/graph.py`

Defines the workflow order:

1. `extractor`
2. `title`
3. `personal_info`
4. `skills`
5. `certificate`
6. `work_experience`
7. `education`
8. `project_experience`
9. `self_evaluation`
10. `assembler`
11. `layout_expert`
12. `interviewer`

### `src/agents/`

Key agent modules:

- `extractor.py`
  Reads resume text from local files.

- `section_agents.py`
  Generates individual resume sections and assembles the final Markdown output.

- `layout_expert.py`
  Renders the final PDF or DOCX.

- `interviewer.py`
  Generates the self-introduction and interview questions.

- `optimizer.py` and `structure_optimizer.py`
  Legacy / alternate optimization paths still present in the repo.

### `src/tools/`

- `file_ops.py`
  Handles resume loading, DOC conversion, DOCX parsing, saving text files, and DOCX generation.

- `pdf_generator.py`
  Converts structured Markdown into a styled PDF using ReportLab.

- `pdf_ops.py`
  Thin wrapper around the current PDF generator.

### `src/llm/factory.py`

Resolves provider and model configuration from `.env` and returns a compatible chat client.

### `src/memory/manager.py`

Stores optimized sections on disk by hashing:
- the original content
- the section key
- the generation context, such as job name and technology stack

## Technology Stack Profiles

Role routing uses the text files in `data/technology_stack/`.

Current profiles include:

- `python_backend.txt`
- `java_backend.txt`
- `java_llm.txt`
- `llm_app_dev.txt`
- `llm_product_manager.txt`
- `llm_testing.txt`
- `frontend.txt`
- `devops.txt`
- `sre.txt`
- `test_dev.txt`
- `testing_manual.txt`
- `product_manager.txt`

The router uses:
- rule-based matching first
- LLM-based semantic matching second

If no profile is matched confidently, it falls back to `technology_stack.txt` when available.

## Installation

### Prerequisites

Recommended environment:

- Python 3.10 or newer
- Windows for best compatibility with `.doc` conversion
- Internet access to your configured LLM provider

Optional but useful:

- Microsoft Word, if you need automatic `.doc` to `.docx` conversion
- An isolated virtual environment or Conda environment

### Install Dependencies

```bash
pip install -r requirements.txt
```

If you are using Conda, a typical setup might look like:

```bash
conda create -n resume-agent python=3.13
conda activate resume-agent
pip install -r requirements.txt
```

## Configuration

All runtime configuration lives in `.env`.

### Supported Provider Styles

The app accepts two configuration styles:

1. **Provider name**
   Example:

   ```ini
   LLM_PROVIDER=dashscope
   DASHSCOPE_MODEL=qwen3.5-flash
   ```

2. **Direct model name**
   Example:

   ```ini
   LLM_PROVIDER=qwen3.5-flash
   ```

Both resolve correctly in the current codebase.

### DashScope / Qwen Example

```ini
LLM_PROVIDER=qwen3.5-flash
DASHSCOPE_MODEL=qwen3.5-flash
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_USE_COMPATIBLE_MODE=true
DASHSCOPE_TEMPERATURE=0
```

Notes:
- The project currently defaults to the **OpenAI-compatible DashScope endpoint** for Qwen models.
- This is intentional because some Qwen 3.5 models may return a `url error` when called through the older native route.
- If your key is region-specific, you may need the international endpoint:
  `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

### DeepSeek Example

```ini
LLM_PROVIDER=deepseek
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_TEMPERATURE=0
```

### OpenAI Example

```ini
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key
OPENAI_TEMPERATURE=0
```

### Important Security Note

Do **not** commit real API keys to version control.

If a real key has already been written into `.env`, rotate it immediately in the provider console and replace it with a new secret that is stored safely outside public version history.

## Input Resume Handling

Place your resume file inside the `data/` directory.

Supported input formats:

- `.pdf`
- `.docx`
- `.doc`

### Selection Rule

If more than one candidate file exists, the app chooses the **most recently modified** file.

### DOCX Parsing Behavior

For `.docx` files, the app tries:

1. `Docx2txtLoader`
2. a built-in OOXML XML extraction fallback

This means the app can still read DOCX files even if `docx2txt` is unavailable.

### Legacy `.doc` Behavior

For `.doc` files, the app:

1. tries to convert the file to `.docx`
2. reads the temporary `.docx`
3. deletes the temporary converted file

This path requires:
- Microsoft Word
- `pywin32`

## Quick Start

1. Install dependencies.
2. Configure `.env`.
3. Place a resume file in `data/`.
4. Run:

   ```bash
   python main.py
   ```

5. Enter:
   - target role
   - years of experience
6. Wait for the workflow to complete.
7. Review files in `Optimized_Output/`.

## Sample Input Files Included

The repository currently includes:

- `data/resume.docx`
- `data/resume_unoptimized_source.md`

These are useful for testing the end-to-end flow without sourcing a separate resume file first.

## Output Files

The main generated files are written to `Optimized_Output/`.

Typical outputs:

- `optimized_resume.md`
- `Optimized_Resume.pdf`
- `Optimized_Resume.docx` when the DOCX rendering path is used
- `optimization_summary.md`
- `self_introduction.md`
- `interview_questions.md`
- `extracted_content.txt`

Intermediate section PDFs are written to:

```text
Optimized_Output/intermediate/
```

Examples:

- `skills_optimized.pdf`
- `project_experience_optimized.pdf`
- `self_evaluation_optimized.pdf`

## Memory System

The app includes a local memory mechanism that can reuse previously optimized sections.

Memory files live in:

```text
data/memory_store/
```

Each entry is keyed by a hash of:

- the original resume content
- the section key
- the generation context

Generation context may include:

- target role
- technology stack
- section summary for self-evaluation

### Memory Behavior

- Memory is enabled by default.
- The app does **not** automatically save all new generations.
- At the end of a run, the user can choose which sections to save.
- Existing memory entries can be overwritten interactively.

## PDF Rendering Notes

PDF generation uses ReportLab with the font configured in:

- `src/conf.py`
- `fonts/`

Current default font:

- `simhei.ttf`

The renderer supports:

- title formatting
- section headers
- two-column personal information layout
- table-like work experience alignment
- project sublabel normalization
- first-line indentation for the professional summary

## Developer Notes

### Useful Utility Scripts

The `utils/` folder contains several validation and experimentation scripts, including:

- `validate_graph.py`
- `verify_pdf_style.py`
- `verify_final_layout.py`
- `verify_final_layout_v2.py`
- `verify_final_layout_v3.py`
- `verify_fpdf2.py`
- `verify_pdf_content.py`
- `test_pdf_fpdf2.py`
- `test_pdf_generator.py`

These are helpful when adjusting PDF layout, typography, or extraction behavior.

### Code Areas Most Likely To Need Changes

- `src/prompts/`
  Prompt wording, output style, role-specific instructions

- `src/route.py`
  Role matching and technology stack routing

- `src/llm/factory.py`
  Provider resolution, model selection, endpoint compatibility

- `src/tools/file_ops.py`
  Resume loading, DOCX fallback extraction, DOC conversion

- `src/tools/pdf_generator.py`
  Layout logic, spacing, styling, table alignment

- `src/conf.py`
  Output defaults, memory toggles, PDF sizes, summary length

## Troubleshooting

### `Unsupported LLM_PROVIDER`

Cause:
- `LLM_PROVIDER` is set to a value the factory does not understand

Fix:
- Use one of:
  - `dashscope`
  - `deepseek`
  - `openai`
  - a direct model name such as `qwen3.5-flash`, `deepseek-chat`, or `gpt-4o-mini`

### DashScope `url error`

Cause:
- Qwen 3.5 models are being called through the wrong DashScope route

Fix:
- Use:

  ```ini
  DASHSCOPE_USE_COMPATIBLE_MODE=true
  DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
  ```

- If needed, try the international endpoint:

  ```ini
  DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
  ```

### `No module named 'docx2txt'`

Cause:
- `docx2txt` is missing

Fix:
- The current code already includes a built-in fallback for `.docx` extraction
- No extra action is required unless the DOCX file itself is malformed

### `No API key found`

Cause:
- Neither `DASHSCOPE_API_KEY` nor `OPENAI_API_KEY` is set

Fix:
- Add the correct provider key to `.env`

### `.doc` conversion failure

Cause:
- Microsoft Word is not installed
- `pywin32` is not installed
- COM automation is blocked

Fix:
- Convert the file manually to `.docx`
- Or install / verify Microsoft Word and `pywin32`

### Empty or broken PDF output

Cause:
- Missing font file
- Markdown structure not matching the renderer assumptions
- Layout logic mismatch after prompt changes

Fix:
- Verify `fonts/simhei.ttf` exists
- Run the utility scripts in `utils/`
- Inspect the generated `optimized_resume.md`

### Network / connection errors

Cause:
- No outbound network access
- Wrong provider base URL
- Firewall or proxy issues

Fix:
- Verify your network can reach the configured provider
- Check region-specific base URLs
- Confirm keys and endpoints match the selected provider

