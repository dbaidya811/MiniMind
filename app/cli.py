import sys
import os
import io

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["DIFFUSERS_NO_PROGRESS_BAR"] = "1"

import time
import json
import re
import threading
import itertools
from pathlib import Path
from contextlib import contextmanager

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown
from rich.live import Live

try:
    from transformers.utils import logging as hf_logging
    hf_logging.set_verbosity_error()
except ImportError:
    pass

try:
    from diffusers.utils import logging as diffusers_logging
    diffusers_logging.set_verbosity_error()
except ImportError:
    pass

from src.inference import MiniMindEngine
from src.vision import VisionEngine
from src.image_gen import ImageGenerator
from src.system_tools import SystemTools
from src.search_tool import WebSearchTool

console = Console()

BANNER_TEXT = """
 ███╗   ███╗██╗███╗   ██╗██╗███╗   ███╗██╗███╗   ██╗██████╗ 
 ████╗ ████║██║████╗  ██║██║████╗ ████║██║████╗  ██║██╔══██╗
 ██╔████╔██║██║██╔██╗ ██║██║██╔████╔██║██║██╔██╗ ██║██║  ██║
 ██║╚██╔╝██║██║██║╚██╗██║██║██║╚██╔╝██║██║██║╚██╗██║██║  ██║
 ██║ ╚═╝ ██║██║██║ ╚████║██║██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
 ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ 
"""

SYSTEM_PROMPT = (
    "You are MiniMind, an autonomous, lightweight, and fully local multimodal AI assistant. "
    "You were created and developed by Deep Baidya, a software developer and BCA student at Greater Kolkata College of Engineering and Management (GKCEM). "
    "When asked 'who created you', 'who made you', or about your origin, ALWAYS state clearly and proudly that you were created and built by Deep Baidya. "
    "Never claim to be created by Alibaba, Alibaba Cloud, OpenAI, or any third-party company. "
    "Maintain an executive, sharp, objective, and technically grounded tone in all responses. "
    "Always format source code inside markdown code blocks with proper syntax identifiers."
)

INTENT_ROUTER_PROMPT = """You are the internal intent router for MiniMind AI.
Analyze the user's input and classify the intent into one of the following JSON schemas:

1. Create a Word document, Excel spreadsheet, PowerPoint presentation, or text file:
{"action": "create_file", "file_type": "word"|"excel"|"ppt"|"text", "filename": "<clean_short_name_without_extension>", "topic": "<subject_to_write_about>"}

2. Generate or paint an image:
{"action": "paint", "prompt": "<visual prompt only>"}

3. Inspect/Analyze an image:
{"action": "vision", "path": "<file_path>", "question": "<question or describe>"}

4. Open an application (vscode, chrome, notepad, calculator, etc.):
{"action": "launch_app", "app": "<app_name>"}

5. Show directory contents:
{"action": "list_dir", "path": "<directory path or downloads>"}

6. Normal conversational chat or general questions:
{"action": "chat"}

Respond ONLY with valid JSON.
User Input: """


@contextmanager
def single_line_status(message: str, success_message: str = None):
    done = False
    spinner_cycle = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    orange_color = "\033[38;5;208m"
    cyan_color = "\033[1;36m"
    reset_color = "\033[0m"

    def spin():
        while not done:
            sys.stdout.write(f"\r\033[K{orange_color}{next(spinner_cycle)} {message}{reset_color}")
            sys.stdout.flush()
            time.sleep(0.08)

    thread = threading.Thread(target=spin, daemon=True)
    thread.start()

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    buffer = io.StringIO()

    try:
        sys.stderr = buffer
        yield
    finally:
        done = True
        thread.join()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        display_done = success_message if success_message else f"{message} (Completed)"
        sys.stdout.write(f"\r\033[K{cyan_color}✦{reset_color} {orange_color}{display_done}{reset_color}\n")
        sys.stdout.flush()


def print_banner():
    console.clear()
    banner = Text(BANNER_TEXT, style="bold #d97757")
    welcome_panel = Panel(
        banner,
        title="[bold #d97757] MiniMind Autonomous AI [/]",
        subtitle="[dim]Zero Command Mode | Multimodal Edge Agent[/]",
        border_style="#d97757",
        padding=(0, 2),
    )
    console.print(welcome_panel)


def route_user_intent(engine: MiniMindEngine, user_input: str) -> dict:
    lower = user_input.lower().strip()

    code_triggers = [
        "write a python", "write python", "python code", "write code",
        "write a code", "writed a python", "code for", "script to",
        "program to", "write a script", "write an algorithm", "solve"
    ]
    if any(k in lower for k in code_triggers):
        return {"action": "chat"}

    if any(k in lower for k in ["ppt", "pptx", "powerpoint", "presentation", "slide"]):
        count_match = re.search(r"(\d+)\s*(?:slides?|pages?)", lower)
        slide_count = int(count_match.group(1)) if count_match else 5

        topic = re.sub(
            r"\b(\d+\s*(?:slides?|pages?)|create|created|make|generate|a|an|the|ppt|pptx|powerpoint|presentation|slides?|in|on|about|for|to)\b",
            " ",
            lower
        )
        topic = re.sub(r"\s+", " ", topic).strip() or "presentation"
        clean_name = re.sub(r"[^\w\s-]", "", topic).strip().replace(" ", "_")[:30] or "presentation"
        return {"action": "create_file", "file_type": "ppt", "filename": clean_name, "topic": topic, "slide_count": slide_count}

    if any(k in lower for k in ["word document", "doc file", "docx file", "msword", "word file", "word"]):
        topic = re.sub(r"\b(create|created|make|generate|a|an|the|word|doc|docx|file|document|msword|in|on|about|for|to)\b", " ", lower)
        topic = re.sub(r"\s+", " ", topic).strip() or "document"
        clean_name = re.sub(r"[^\w\s-]", "", topic).strip().replace(" ", "_")[:30] or "document"
        return {"action": "create_file", "file_type": "word", "filename": clean_name, "topic": topic}

    if any(k in lower for k in ["excel", "xlsx", "sheet", "spreadsheet", "csv"]):
        topic = re.sub(r"\b(create|created|make|generate|a|an|the|excel|file|sheet|spreadsheet|csv|in|on|about|for|to)\b", " ", lower)
        topic = re.sub(r"\s+", " ", topic).strip() or "dataset"
        clean_name = re.sub(r"[^\w\s-]", "", topic).strip().replace(" ", "_")[:30] or "dataset"
        return {"action": "create_file", "file_type": "excel", "filename": clean_name, "topic": topic}

    if "create a text file" in lower or "save to text file" in lower or "create a txt file" in lower:
        topic = re.sub(r"\b(create|save|a|an|the|text|txt|file|to|on|about|for)\b", " ", lower)
        topic = re.sub(r"\s+", " ", topic).strip() or "notes"
        clean_name = re.sub(r"[^\w\s-]", "", topic).strip().replace(" ", "_")[:30] or "notes"
        return {"action": "create_file", "file_type": "text", "filename": clean_name, "topic": topic}

    img_match = re.search(
        r"([a-zA-Z]:\\[^\s*?\"<>|]+\.(?:png|jpg|jpeg|webp)|(?:[a-zA-Z0-9_\-\\/.]+\.(?:png|jpg|jpeg|webp)))",
        user_input,
        re.IGNORECASE
    )
    if img_match and not any(lower.startswith(w) for w in ["paint", "generate", "create", "draw"]):
        img_path = img_match.group(1)
        question = user_input.replace(img_path, "").strip() or "Describe this image in detail."
        return {"action": "vision", "path": img_path, "question": question}

    read_match = re.search(
        r"([a-zA-Z]:\\[^\s*?\"<>|]+\.(?:txt|md|csv|json)|(?:[a-zA-Z0-9_\-\\/.]+\.(?:txt|md|csv|json)))",
        user_input,
        re.IGNORECASE
    )
    if read_match and not any(lower.startswith(w) for w in ["update", "write", "create"]):
        return {"action": "read_file", "path": read_match.group(1)}

    prompt = [{"role": "user", "content": INTENT_ROUTER_PROMPT + user_input}]
    raw_response = ""
    for chunk, _ in engine.generate_stream(prompt, max_new_tokens=90, temperature=0.1):
        raw_response += chunk

    try:
        clean_json_str = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if clean_json_str:
            json_string = clean_json_str.group(0)
            json_string = re.sub(r'\\(?!["\\/bfnrt])', r'\\\\', json_string)
            return json.loads(json_string)
    except Exception:
        pass

    return {"action": "chat"}


def run_cli():
    print_banner()

    with single_line_status("Initializing MiniMind Engine...", "MiniMind Engine Ready"):
        bot = MiniMindEngine()

    vision_engine = None
    image_gen_engine = None
    downloads_path = str(SystemTools.get_downloads_dir())

    history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            user_input = console.input("[bold #8cbdd6]You[/] [dim]>[/] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                console.print("\n[bold #d97757]Shutting down MiniMind... Goodbye![/]\n")
                break

            if user_input.lower() == "clear":
                print_banner()
                history = [{"role": "system", "content": SYSTEM_PROMPT}]
                continue

            with single_line_status("Understanding intent..."):
                intent = route_user_intent(bot, user_input)

            # =================================================================
            # ACTION: Create Document with Single-Pass Fast CoT & Deep Web RAG
            # =================================================================
            if intent.get("action") == "create_file":
                file_type = str(intent.get("file_type", "text")).lower()
                raw_filename = intent.get("filename", "document")
                topic = intent.get("topic", user_input)
                slide_count = intent.get("slide_count", 5)

                clean_name = re.sub(r"[^\w\s-]", "", raw_filename).strip().replace(" ", "_")[:35] or "document"

                # Step 1: Deep Web Retrieval
                search_query = f"{topic} overview architecture statistics mechanisms"
                with single_line_status(f"Conducting deep web retrieval for '{topic}'...", "Deep Web Intel Retrieved"):
                    web_context = WebSearchTool.search_web(search_query, max_results=5)

                # Step 2: Content Generation with Single-Pass CoT
                with single_line_status(f"Synthesizing insights & generating {file_type.upper()} asset...", "Asset Compiled"):
                    if any(x in file_type for x in ["ppt", "powerpoint", "slide"]):
                        fast_cot_prompt = [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": (
                                f"Web Knowledge Context:\n{web_context}\n\n"
                                f"Create a technical, fact-dense {slide_count}-slide presentation specification for: '{topic}'.\n\n"
                                "Instructions:\n"
                                "1. First, think concisely inside <thought> ... </thought> tags (plan 4 key technical pillars, verified numbers, and 2 visual image prompts).\n"
                                "2. Then, immediately output a valid JSON array of slide objects: [ { ... }, { ... } ]\n"
                                "JSON Structure per slide:\n"
                                "- 'title': Specific technical slide title\n"
                                "- 'summary': 1-2 sentence executive highlight\n"
                                "- 'points': Array of 3 specific technical mechanics\n"
                                "- 'image_prompt': Short vivid prompt (include visual prompt ONLY for slide 1 and slide 2, leave empty for others)\n"
                                "- 'chart_type': 'bar' OR 'pie' OR 'none' (use 'bar' or 'pie' if the slide contains metrics/trends)\n\n"
                                "Slide 1 must be the Cover slide. Output valid JSON right after </thought>."
                            )}
                        ]
                        
                        raw_output = ""
                        for token_chunk, _ in bot.generate_stream(fast_cot_prompt, max_new_tokens=2200, temperature=0.2):
                            raw_output += token_chunk

                        # Strip thought tags
                        clean_json_text = re.sub(r"<thought>.*?</thought>", "", raw_output, flags=re.DOTALL).strip()
                        slides_data = []
                        try:
                            json_match = re.search(r"\[\s*\{.*\}\s*\]", clean_json_text, re.DOTALL)
                            if json_match:
                                slides_data = json.loads(json_match.group(0))
                        except Exception:
                            slides_data = []

                        if not slides_data:
                            slides_data = [
                                {
                                    "title": topic.title(),
                                    "summary": f"Strategic analysis and operational blueprint for {topic}.",
                                    "points": ["Architectural Principles", "Performance Metrics", "Implementation Pipeline"],
                                    "image_prompt": f"cinematic 3d render of {topic}, dark studio lighting, 8k",
                                    "chart_type": "none"
                                },
                                {
                                    "title": "System Architecture & Core Workflow",
                                    "summary": "Key functional mechanics and data pipeline.",
                                    "points": [
                                        "Modular architecture ensures minimal latency and maximum scalability.",
                                        "Data validation protocols enforce strict grounding and integrity.",
                                        "Enterprise-grade execution pipelines optimized for throughput."
                                    ],
                                    "image_prompt": "",
                                    "chart_type": "bar"
                                }
                            ]

                        if image_gen_engine is None:
                            try:
                                image_gen_engine = ImageGenerator()
                            except Exception:
                                image_gen_engine = None

                        res = SystemTools.create_ppt_structured(
                            filename=f"{clean_name}.pptx",
                            slides_data=slides_data,
                            image_generator=image_gen_engine,
                            topic=topic
                        )

                    elif any(x in file_type for x in ["word", "doc"]):
                        doc_prompt = [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": (
                                f"Web Knowledge Context:\n{web_context}\n\n"
                                f"Write an exhaustive, publication-grade executive whitepaper on: '{topic}'.\n\n"
                                "First think concisely inside <thought> ... </thought> tags, then produce the markdown document.\n"
                                "FORMAT REQUIREMENTS:\n"
                                "# Document Title\n"
                                "> Executive Summary (Callout paragraph)\n\n"
                                "## 1. Architectural & Theoretical Foundations\n"
                                "Comprehensive breakdown with deep real-world technical explanations.\n\n"
                                "## 2. Core Functional Mechanisms & Workflows\n"
                                "- Point 1: Deep technical mechanic.\n"
                                "- Point 2: Implementation pipeline.\n\n"
                                "## 3. Real-World Case Studies & Industry Applications\n"
                                "Concrete statistics, verified implementations, and measurable outcomes.\n\n"
                                "## 4. Strategic Outlook & Future Roadmap\n"
                                "Summary of future trajectory.\n\n"
                                "Begin output now:"
                            )}
                        ]
                        raw_output = ""
                        for token_chunk, _ in bot.generate_stream(doc_prompt, max_new_tokens=2500, temperature=0.2):
                            raw_output += token_chunk

                        clean_doc = re.sub(r"<thought>.*?</thought>", "", raw_output, flags=re.DOTALL).strip()
                        res = SystemTools.create_word_file(f"{clean_name}.docx", clean_doc)

                    elif any(x in file_type for x in ["excel", "xls", "sheet"]):
                        excel_prompt = [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": (
                                f"Web Knowledge Context:\n{web_context}\n\n"
                                f"Create an accurate, strictly factual CSV dataset for: '{topic}'.\n\n"
                                "STRICT FACT-CHECKING RULES:\n"
                                "1. Ground Truth Reality: Ensure real-world accuracy (e.g., India, USA, Germany, France, South Korea, China DO actively use and deploy 5G; never report false 'no' values for deployed tech).\n"
                                "2. Start directly with the header row on line 1. No introduction.\n"
                                "3. Make columns informative (e.g., Country, 4G Deployment, 5G Status/Adoption, Primary Providers/Launch Year).\n"
                                "4. Provide 12 to 18 verified, distinct rows.\n"
                                "5. Output raw comma-separated CSV lines only. No markdown fences (```)."
                            )}
                        ]
                        content_draft = ""
                        for token_chunk, _ in bot.generate_stream(excel_prompt, max_new_tokens=2048, temperature=0.1):
                            content_draft += token_chunk
                        res = SystemTools.create_excel_file(f"{clean_name}.xlsx", content_draft)

                    else:
                        res = SystemTools.update_or_create_file(f"{clean_name}.txt", web_context, mode="w")

                if res.get("status") == "error":
                    console.print(f"[red]Error saving file: {res.get('message', 'Unknown error')}[/red]\n")
                    continue

                saved_path = res.get("path", "Unknown path")
                console.print()
                console.rule("[bold #d97757]MiniMind (File Engine)[/]", style="#d97757")
                console.print("[bold green]✔ File created successfully in Downloads![/]")
                console.print(f"[bold #8cbdd6]File Path:[/] {saved_path}\n")
                console.rule(style="#d97757")
                console.print()
                continue

            # ACTION: Paint / Image Generation
            if intent.get("action") == "paint":
                prompt = intent.get("prompt", "a futuristic landscape")
                if image_gen_engine is None:
                    with single_line_status("Loading SD-Turbo Generator weights...", "Image Generator Loaded"):
                        image_gen_engine = ImageGenerator()

                with single_line_status(f"Generating image for: '{prompt}'..."):
                    t_start = time.perf_counter()
                    saved_path = image_gen_engine.generate(prompt)
                    t_elapsed = time.perf_counter() - t_start

                console.print()
                console.rule("[bold #d97757]MiniMind (Painter)[/]", style="#d97757")
                console.print("[bold green]Image generated and saved to your Downloads![/]")
                console.print(f"[bold #8cbdd6]File Path:[/] {saved_path}")
                console.rule(f"[dim]Time: {t_elapsed:.2f}s[/]", style="#d97757")
                console.print()
                continue

            # ACTION: Vision Analysis
            if intent.get("action") == "vision":
                img_path = intent.get("path", "")
                question = intent.get("question", "Describe what you see in this image.")

                if not os.path.isabs(img_path):
                    resolved_path = Path(downloads_path) / img_path
                    if resolved_path.exists():
                        img_path = str(resolved_path)

                if not os.path.exists(img_path):
                    console.print(f"[red]Error: Image file not found at: {img_path}[/]\n")
                    continue

                if vision_engine is None:
                    with single_line_status("Loading Vision Engine weights...", "Vision Engine Loaded"):
                        vision_engine = VisionEngine()

                with single_line_status(f"Analyzing {img_path}..."):
                    t_start = time.perf_counter()
                    answer = vision_engine.describe_or_answer(img_path, question)
                    t_elapsed = time.perf_counter() - t_start

                console.print()
                console.rule("[bold #d97757]MiniMind (Vision)[/]", style="#d97757")
                console.print(answer)
                console.rule(f"[dim]Time: {t_elapsed:.2f}s[/]", style="#d97757")
                console.print()
                continue

            # ACTION: Read Local Text File
            if intent.get("action") == "read_file":
                res = SystemTools.read_file(intent.get("path", ""))
                if res.get("status") == "success":
                    console.print()
                    console.rule(f"[bold #d97757]{res.get('path', '')}[/]", style="#d97757")
                    console.print(res.get("content", ""))
                    console.rule(style="#d97757")
                    console.print()
                else:
                    console.print(f"[red]{res.get('message', 'Failed to read file')}[/red]\n")
                continue

            # ACTION: Launch Application
            if intent.get("action") == "launch_app":
                res = SystemTools.launch_app(intent.get("app", ""))
                color = "bold green" if res.get("status") == "success" else "red"
                console.print(f"[{color}]{res.get('message', '')}[/{color}]\n")
                continue

            # ACTION: List Folder Items
            if intent.get("action") == "list_dir":
                res = SystemTools.list_directory(intent.get("path"))
                if res.get("status") == "success":
                    table = Table(title=f"Directory: {res.get('path')}", border_style="#d97757")
                    table.add_column("Type", style="bold #8cbdd6")
                    table.add_column("Name")
                    table.add_column("Size", justify="right", style="dim")
                    for it in res.get("items", []):
                        sz = f"{it['size_bytes']} B" if it["type"] == "file" else "-"
                        table.add_row(it["type"], it["name"], sz)
                    console.print(table)
                    console.print()
                else:
                    console.print(f"[red]{res.get('message', 'Failed to inspect directory')}[/red]\n")
                continue

            # Conversational Chat Flow
            if any(k in user_input.lower() for k in ["latest", "recent", "news", "who is", "what is", "price of"]):
                with single_line_status("Gathering latest data from web...", "Information Retrieved"):
                    live_info = WebSearchTool.search_web(user_input, max_results=2)
                if live_info:
                    history.append({"role": "system", "content": f"Contextual Web Intel:\n{live_info}"})

            history.append({"role": "user", "content": user_input})
            accumulated_response = ""
            latest_stats = {"tokens": 0, "time_sec": 0.0, "speed": 0.0}

            console.print()
            console.rule("[bold #d97757]MiniMind[/]", style="#d97757")

            with Live(console=console, refresh_per_second=12) as live:
                for token_chunk, stats in bot.generate_stream(history, max_new_tokens=4096):
                    accumulated_response += token_chunk
                    latest_stats = stats
                    live.update(Markdown(accumulated_response) if accumulated_response.strip() else Text("..."))

            stats_info = f"[dim]Tokens: {latest_stats['tokens']} | Time: {latest_stats['time_sec']:.2f}s | Speed: {latest_stats['speed']:.2f} tok/s[/]"
            console.rule(stats_info, style="#d97757")
            console.print()

            history.append({"role": "assistant", "content": accumulated_response})

        except KeyboardInterrupt:
            console.print("\n\n[bold #d97757]Process interrupted by user.[/]\n")
            break


if __name__ == "__main__":
    run_cli()