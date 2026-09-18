import sys
import os
import time
from colorama import init, Fore, Style

init(autoreset=True)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.inference import MiniMindEngine
from src.vision import VisionEngine
from src.image_gen import ImageGenerator

ORANGE = "\033[38;2;217;119;87m"
CYAN_SOFT = "\033[38;2;140;190;214m"
GRAY = "\033[90m"

BANNER_TEXT = rf"""{ORANGE}
 ███╗   ███╗██╗███╗   ██╗██╗███╗   ███╗██╗███╗   ██╗██████╗ 
 ████╗ ████║██║████╗  ██║██║████╗ ████║██║████╗  ██║██╔══██╗
 ██╔████╔██║██║██╔██╗ ██║██║██╔████╔██║██║██╔██╗ ██║██║  ██║
 ██║╚██╔╝██║██║██║╚██╗██║██║██║╚██╔╝██║██║██║╚██╗██║██║  ██║
 ██║ ╚═╝ ██║██║██║ ╚████║██║██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
 ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ 
{Style.RESET_ALL}"""

WELCOME_BOX = rf"""{ORANGE}
 ┌────────────────────────────────────────┐
 │  * Welcome to MiniMind Local AI        │
 └────────────────────────────────────────┘{Style.RESET_ALL}"""

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def run_cli():
    clear_screen()
    print(WELCOME_BOX)
    print(BANNER_TEXT)
    
    print(f"{ORANGE}[*] Initializing MiniMind Text Engine...{Style.RESET_ALL}")
    bot = MiniMindEngine()
    
    vision_engine = None
    image_gen_engine = None

    history = [
        {"role": "system", "content": "You are MiniMind, a helpful and lightweight personal AI assistant."}
    ]

    print(f"\n{ORANGE}┌─────────────────────────────────────────────────────────┐")
    print(f"│ MiniMind CLI Active. Type 'exit' or 'quit' to close.   │")
    print(f"│ Commands:                                               │")
    print(f"│   /vision <path> <question> : Ask about an image        │")
    print(f"│   /paint <prompt>           : Generate a new image      │")
    print(f"└─────────────────────────────────────────────────────────┘{Style.RESET_ALL}\n")

    while True:
        try:
            user_input = input(f"{CYAN_SOFT}You > {Style.RESET_ALL}").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print(f"\n{ORANGE}Shutting down MiniMind... Goodbye!{Style.RESET_ALL}")
                break

            # Vision Command
            if user_input.startswith("/vision"):
                parts = user_input.split(maxsplit=2)
                if len(parts) < 2:
                    print(f"{ORANGE}Usage: /vision <image_path> [question]{Style.RESET_ALL}\n")
                    continue
                
                img_path = parts[1]
                question = parts[2] if len(parts) > 2 else "Describe this image."

                if vision_engine is None:
                    print(f"{ORANGE}[*] Loading Vision Engine...{Style.RESET_ALL}")
                    vision_engine = VisionEngine()

                print(f"\n{ORANGE}MiniMind (Vision) > {Style.RESET_ALL}", end="", flush=True)
                t_start = time.perf_counter()
                ans = vision_engine.describe_or_answer(img_path, question)
                t_elapsed = time.perf_counter() - t_start
                print(f"{ans}")
                print(f"{GRAY}[Time: {t_elapsed:.2f}s]{Style.RESET_ALL}\n")
                continue

            # Paint Command
            if user_input.startswith("/paint"):
                prompt = user_input.replace("/paint", "", 1).strip()
                if not prompt:
                    print(f"{ORANGE}Usage: /paint <prompt>{Style.RESET_ALL}\n")
                    continue

                if image_gen_engine is None:
                    print(f"{ORANGE}[*] Loading Image Generator...{Style.RESET_ALL}")
                    image_gen_engine = ImageGenerator()

                print(f"\n{ORANGE}MiniMind (Painter) > {Style.RESET_ALL}Generating image for '{prompt}'...")
                t_start = time.perf_counter()
                saved_path = image_gen_engine.generate(prompt)
                t_elapsed = time.perf_counter() - t_start
                print(f"{ORANGE}MiniMind (Painter) > {Style.RESET_ALL}Image saved to: {saved_path}")
                print(f"{GRAY}[Time: {t_elapsed:.2f}s]{Style.RESET_ALL}\n")
                continue

            # Standard Chat Inference
            history.append({"role": "user", "content": user_input})
            print(f"\n{ORANGE}MiniMind > {Style.RESET_ALL}", end="", flush=True)
            
            reply, stats = bot.generate(history)
            print(reply)
            print(f"{GRAY}[Tokens: {stats['tokens']} | Time: {stats['time_sec']:.2f}s | Speed: {stats['speed']:.2f} tokens/s]{Style.RESET_ALL}\n")
            
            history.append({"role": "assistant", "content": reply})

        except KeyboardInterrupt:
            print(f"\n\n{ORANGE}Process terminated.{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    run_cli()