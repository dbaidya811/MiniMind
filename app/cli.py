import sys
import os
import time
import re
import pyperclip

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown
from rich.live import Live

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.inference import MiniMindEngine
from src.vision import VisionEngine
from src.image_gen import ImageGenerator

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
    "You are MiniMind, an autonomous, lightweight, and fully local AI assistant. "
    "You execute locally on the user's host machine as a private neural runtime. "
    "When asked about your identity or origin, state that you are MiniMind, an independent on-device AI system. "
    "Never claim to be developed by Alibaba, OpenAI, or any third-party corporation. "
    "Maintain an executive, sharp, objective, and technically grounded tone in all responses. "
    "Always format source code inside markdown code blocks with proper syntax identifiers."
)

def print_banner():
    console.clear()
    
    banner = Text(BANNER_TEXT, style="bold #d97757")
    welcome_panel = Panel(
        banner,
        title="[bold #d97757] MiniMind Local AI [/]",
        subtitle="[dim]Local Edge Intelligence | 32k Context Active[/]",
        border_style="#d97757",
        padding=(0, 2),
    )
    console.print(welcome_panel)

    menu = Table.grid(padding=(0, 2))
    menu.add_column(style="bold #8cbdd6")
    menu.add_column(style="dim")

    menu.add_row("/vision <image_path> [prompt]", "Analyze image and answer questions")
    menu.add_row("/paint <prompt>", "Generate image using SD-Turbo")
    menu.add_row("clear", "Clear terminal screen and reset chat")
    menu.add_row("exit / quit", "Terminate session")

    console.print(
        Panel(
            menu,
            title="[bold #73716b] Commands [/]",
            border_style="#34322d",
            padding=(0, 1),
        )
    )
    console.print()

def extract_and_copy_code(full_response: str):
    pattern = r"```(?:[a-zA-Z0-9_-]+)?\n(.*?)```"
    code_blocks = re.findall(pattern, full_response, re.DOTALL)

    if not code_blocks:
        return

    total_blocks = len(code_blocks)
    combined_code = "\n\n".join(block.strip() for block in code_blocks)

    prompt_text = Text()
    prompt_text.append(f"Code Block Detected ({total_blocks}) | ", style="bold #8cbdd6")
    prompt_text.append("Press ", style="dim")
    prompt_text.append("'c'", style="bold #d97757")
    prompt_text.append(" to copy to clipboard, or press ", style="dim")
    prompt_text.append("Enter", style="bold white")
    prompt_text.append(" to continue.", style="dim")

    console.print(
        Panel(
            prompt_text,
            border_style="#34322d",
            padding=(0, 2)
        )
    )

    try:
        choice = console.input("[bold #8cbdd6]Action[/] [dim]>[/] ").strip().lower()
        if choice == "c":
            pyperclip.copy(combined_code)
            console.print("[bold green]✔ Code copied to clipboard successfully![/]\n")
        else:
            console.print()
    except Exception as e:
        console.print(f"[dim red]Failed to access clipboard: {e}[/]\n")

def run_cli():
    print_banner()

    with console.status("[bold #d97757]Initializing MiniMind 32k Engine...[/]", spinner="dots"):
        bot = MiniMindEngine()

    vision_engine = None
    image_gen_engine = None

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

            # Vision Command
            if user_input.startswith("/vision"):
                parts = user_input.split(maxsplit=2)
                if len(parts) < 2:
                    console.print("[red]Usage: /vision <image_path> [question][/]\n")
                    continue

                img_path = parts[1]
                question = parts[2] if len(parts) > 2 else "Describe this image."

                if vision_engine is None:
                    with console.status("[bold #d97757]Loading Vision Engine...[/]", spinner="dots"):
                        vision_engine = VisionEngine()

                with console.status("[bold #d97757]Analyzing Image...[/]", spinner="dots"):
                    t_start = time.perf_counter()
                    answer = vision_engine.describe_or_answer(img_path, question)
                    t_elapsed = time.perf_counter() - t_start

                console.print(
                    Panel(
                        answer,
                        title="[bold #d97757]MiniMind (Vision)[/]",
                        subtitle=f"[dim]Time: {t_elapsed:.2f}s[/]",
                        border_style="#d97757",
                        padding=(1, 2),
                    )
                )
                console.print()
                continue

            # Paint Command
            if user_input.startswith("/paint"):
                prompt = user_input.replace("/paint", "", 1).strip()
                if not prompt:
                    console.print("[red]Usage: /paint <prompt>[/]\n")
                    continue

                if image_gen_engine is None:
                    with console.status("[bold #d97757]Loading Image Generator...[/]", spinner="dots"):
                        image_gen_engine = ImageGenerator()

                with console.status(f"[bold #d97757]Generating image for: '{prompt}'...[/]", spinner="dots"):
                    t_start = time.perf_counter()
                    saved_path = image_gen_engine.generate(prompt)
                    t_elapsed = time.perf_counter() - t_start

                output_text = Text()
                output_text.append("Image successfully generated!\n", style="bold green")
                output_text.append(f"Saved to: {saved_path}", style="#8cbdd6")

                console.print(
                    Panel(
                        output_text,
                        title="[bold #d97757]MiniMind (Painter)[/]",
                        subtitle=f"[dim]Time: {t_elapsed:.2f}s[/]",
                        border_style="#d97757",
                        padding=(1, 2),
                    )
                )
                console.print()
                continue

            # Text Streaming Output
            history.append({"role": "user", "content": user_input})
            accumulated_response = ""
            latest_stats = {"tokens": 0, "time_sec": 0.0, "speed": 0.0}

            def render_current_panel(text: str, stats: dict) -> Panel:
                content = Markdown(text) if text.strip() else Text("...")
                stats_line = (
                    f"[dim]Tokens: {stats['tokens']} | "
                    f"Time: {stats['time_sec']:.2f}s | "
                    f"Speed: {stats['speed']:.2f} tok/s[/]"
                )
                return Panel(
                    content,
                    title="[bold #d97757]MiniMind[/]",
                    subtitle=stats_line,
                    border_style="#d97757",
                    padding=(1, 2),
                )

            with Live(
                render_current_panel(accumulated_response, latest_stats),
                console=console,
                refresh_per_second=12
            ) as live:
                for token_chunk, stats in bot.generate_stream(history, max_new_tokens=4096):
                    accumulated_response += token_chunk
                    latest_stats = stats
                    live.update(render_current_panel(accumulated_response, latest_stats))

            history.append({"role": "assistant", "content": accumulated_response})
            console.print()

            # Trigger Code Block Copier
            extract_and_copy_code(accumulated_response)

        except KeyboardInterrupt:
            console.print("\n\n[bold #d97757]Process interrupted by user.[/]\n")
            break

if __name__ == "__main__":
    run_cli()