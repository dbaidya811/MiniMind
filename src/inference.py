import sys
import os
import time
from pathlib import Path
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

class MiniMindEngine:
    def __init__(
        self,
        model_path: str = "models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
        repo_id: str = "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        filename: str = "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        n_ctx: int = 4096,
        n_threads: int = 6
    ):
        self.model_path = Path(model_path)
        self.repo_id = repo_id
        self.filename = filename
        
        # 1. Check if model exists locally; if not, download automatically
        self._ensure_model_exists()

        # 2. Initialize the Llama engine
        self.llm = Llama(
            model_path=str(self.model_path),
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False
        )

    def _ensure_model_exists(self):
        """Checks if local model exists; if not, downloads directly into models/ directory."""
        if not self.model_path.exists():
            print(f"\n[MiniMind Engine] Model not found locally at '{self.model_path}'.")
            print(f"[MiniMind Engine] Downloading {self.filename} from Hugging Face hub...")
            
            # Create models/ directory if it does not exist
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file into models/ folder
            downloaded_file = hf_hub_download(
                repo_id=self.repo_id,
                filename=self.filename,
                local_dir=str(self.model_path.parent),
                local_dir_use_symlinks=False
            )
            print(f"[MiniMind Engine] Download complete! Model saved to: {downloaded_file}\n")

    def generate_stream(self, messages: list, max_new_tokens: int = 2048, temperature: float = 0.3):
        """
        Yields chunks of text as they are generated, along with generation metrics.
        """
        start_time = time.perf_counter()
        token_count = 0

        response_stream = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=temperature,
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