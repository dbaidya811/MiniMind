import sys
import os
import time
from pathlib import Path
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

class MiniMindEngine:
    def __init__(
        self,
        model_path: str = "models/qwen2.5-7b-instruct-q4_k_m.gguf",
        repo_id: str = "bartowski/Qwen2.5-7B-Instruct-GGUF",
        filename: str = "Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        n_ctx: int = 4096,
        n_threads: int = 8
    ):
        self.model_path = Path(model_path)
        self.repo_id = repo_id
        self.filename = filename
        
        # 1. Download model if missing locally
        self._ensure_model_exists()

        # 2. Initialize the local llama engine with tuned batch size for fast prompt processing
        self.llm = Llama(
            model_path=str(self.model_path),
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_batch=512,        # Prompt evaluation faster korar jonno batch size tuned
            verbose=False
        )

    def _ensure_model_exists(self):
        """Checks if local model exists; if not, downloads directly into models/ directory."""
        if not self.model_path.exists():
            print(f"\n[MiniMind Engine] Model not found locally at '{self.model_path}'.")
            print(f"[MiniMind Engine] Downloading {self.filename} from Hugging Face hub (7B Q4_K_M)...")
            
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            
            downloaded_file = hf_hub_download(
                repo_id=self.repo_id,
                filename=self.filename,
                local_dir=str(self.model_path.parent),
                local_dir_use_symlinks=False
            )

            # Match destination file naming if case differs
            downloaded_path = Path(downloaded_file)
            if downloaded_path.exists() and downloaded_path.resolve() != self.model_path.resolve():
                if self.model_path.exists():
                    self.model_path.unlink()
                downloaded_path.rename(self.model_path)

            print(f"[MiniMind Engine] Download complete! Model saved to: {self.model_path}\n")

    def generate_stream(self, messages: list, max_new_tokens: int = 2048, temperature: float = 0.2):
        """
        Yields chunks of text as they are generated, along with generation metrics.
        repeat_penalty is configured to strictly prevent repetitive hallucination loops.
        """
        start_time = time.perf_counter()
        token_count = 0

        response_stream = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=temperature,
            repeat_penalty=1.18,
            stream=True
        )

        for chunk in response_stream:
            delta = chunk["choices"][0].get("delta", {})
            content = delta.get("content", "")
            
            if content:
                token_count += 1
                elapsed = time.perf_counter() - start_time
                speed = token_count / elapsed if elapsed > 0 else 0.0
                
                stats = {
                    "tokens": token_count,
                    "time_sec": elapsed,
                    "speed": speed
                }
                yield content, stats