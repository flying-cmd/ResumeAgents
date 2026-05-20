# Multi-Agent Resume Optimization System Architecture

## 1. Overview
This project is built on **LangGraph** and **LangChain**. It implements a multi-agent workflow that automates resume extraction, content optimization, PDF generation, and interview-preparation material creation. The system supports both DashScope-compatible and OpenAI-compatible language models and uses MCP-style tools for file operations.

## 2. Core Capabilities
1. **Resume Parsing**: Detect and extract plain text from PDF and Word resumes.
2. **Intelligent Optimization**: Tailor resume content to a target role and preferred technology stack with LLM support.
3. **Format Conversion**: Turn optimized Markdown into polished PDF and DOCX outputs.
4. **Interview Preparation**:
   - Generate a professional self-introduction.
   - Generate interview questions with detailed answers.
5. **Interactive Experience**: Provide a command-line interface with live progress updates.

## 3. Architecture
The system uses a **StateGraph** workflow. Agents share a common `AgentState` object and update it step by step.

### 3.1 Core Components
- **LangGraph**: Orchestrates the agent workflow.
- **LangChain**: Provides the model and tool abstractions used by the agents.
- **LLM Layer**: Wraps the selected model provider behind a unified interface.

### 3.2 Main Agents
1. **Extractor Agent**
   - Responsibility: Scan the data directory, detect the resume file, and extract text.
   - Tools: `read_resume_tool`, `save_document_tool`
   - Output: `original_resume_text`

2. **Section Agents**
   - Responsibility: Generate English resume sections such as title, personal information, skills, certifications, work experience, education, projects, and summary.
   - Tools: LLM, memory manager, `convert_markdown_to_pdf`
   - Output: `sections`

3. **Assembler Agent**
   - Responsibility: Combine optimized sections into the final resume Markdown and trigger PDF generation.
   - Tools: `convert_markdown_to_pdf`
   - Output: `optimized_resume_text`

4. **Layout Agent**
   - Responsibility: Render the final resume into PDF or DOCX depending on the detected input type.
   - Tools: `generate_pdf_tool`, `generate_docx_tool`
   - Output: rendered files in `Optimized_Output/`

5. **Interviewer Agent**
   - Responsibility: Generate the self-introduction and interview question bank.
   - Tools: LLM, `save_document_tool`
   - Output: `self_intro`, `interview_questions`

### 3.3 Data Flow
```mermaid
graph LR
    Start --> Extractor[Extractor Agent]
    Extractor --> Title[Title Agent]
    Title --> PersonalInfo[Personal Info Agent]
    PersonalInfo --> Skills[Skills Agent]
    Skills --> Certificates[Certificate Agent]
    Certificates --> Work[Work Experience Agent]
    Work --> Education[Education Agent]
    Education --> Projects[Project Experience Agent]
    Projects --> Summary[Professional Summary Agent]
    Summary --> Assembler[Assembler Agent]
    Assembler --> Layout[Layout Agent]
    Layout --> Interviewer[Interviewer Agent]
    Interviewer --> End
```

### 3.4 Tooling
The main tools live in `src/tools`:
- `read_resume_tool`: Extract resume text from PDF, DOCX, or DOC files.
- `read_tech_stack_tool`: Load the target technology stack profile from disk.
- `save_document_tool`: Save generated text output to disk.
- `generate_docx_tool`: Render Markdown as DOCX.
- `convert_markdown_to_pdf` / `generate_pdf_tool`: Render Markdown as PDF.

## 4. Project Structure
```text
.
├── .env
├── main.py
├── requirements.txt
├── architecture_design.md
├── data/
│   ├── memory_store/
│   └── technology_stack/
├── fonts/
├── src/
│   ├── agents/
│   ├── llm/
│   ├── memory/
│   ├── prompts/
│   ├── tools/
│   ├── conf.py
│   ├── graph.py
│   └── state.py
└── utils/
```

## 5. How To Run

### 5.1 Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.env`:
   ```ini
   LLM_PROVIDER=dashscope
   DASHSCOPE_API_KEY=your_key_here
   ```
   Or set `OPENAI_API_KEY` if you are using the OpenAI-compatible path.

### 5.2 Start the App
Run from the project root:
```bash
python main.py
```

### 5.3 Runtime Flow
1. The app detects a resume file in `data/`.
2. It asks for the target role and years of experience.
3. It routes the request to the best matching tech stack profile.
4. Agents generate optimized English resume sections.
5. The assembler creates the final Markdown and PDF.
6. The interviewer agent generates self-introduction and interview question outputs.
7. The app optionally offers interactive memory management at the end.
