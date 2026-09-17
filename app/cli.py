import sys
import os

# src folder path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.inference import MiniMindEngine

def run_cli():
    bot = MiniMindEngine()
    history = [{"role": "system", "content": "You are MiniMind, a helpful and lightweight personal AI assistant."}]
    
    print("=" * 40)
    print("MiniMind Terminal Chat (Type 'exit' to quit)")
    print("=" * 40)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting MiniMind...")
                break

            history.append({"role": "user", "content": user_input})
            reply = bot.generate(history)
            print(f"\nMiniMind: {reply}")
            history.append({"role": "assistant", "content": reply})
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    run_cli()