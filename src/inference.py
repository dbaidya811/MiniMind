import time
from threading import Thread
from typing import Generator, Tuple, Dict, Any, List
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer,
    AutoConfig
)

class MiniMindEngine:
    def __init__(self, model_id: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = model_id

        # 32k context configuration
        self.config = AutoConfig.from_pretrained(self.model_id)
        self.config.max_position_embeddings = 32768
        if hasattr(self.config, "sliding_window"):
            self.config.sliding_window = 32768

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            model_max_length=32768,
            padding_side="right"
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            config=self.config,
            torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
            device_map="auto" if self.device == "cuda" else None,
            low_cpu_mem_usage=True
        )

        if self.device == "cuda":
            self.model = self.model.to("cuda")

        self.model.eval()

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
        prompt_text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        model_inputs = self.tokenizer(
            [prompt_text],
            return_tensors="pt",
            truncation=True,
            max_length=32768
        ).to(self.device)

        streamer = TextIteratorStreamer(
            self.tokenizer,
            timeout=60.0,
            skip_prompt=True,
            skip_special_tokens=True
        )

        generate_kwargs = dict(
            model_inputs,
            streamer=streamer,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True if temperature > 0.0 else False,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        )

        thread = Thread(target=self.model.generate, kwargs=generate_kwargs)
        thread.start()

        start_time = time.perf_counter()
        token_count = 0

        for new_text in streamer:
            token_count += 1
            elapsed = time.perf_counter() - start_time
            speed = token_count / elapsed if elapsed > 0 else 0.0

            stats = {
                "tokens": token_count,
                "time_sec": elapsed,
                "speed": speed
            }
            yield new_text, stats

        thread.join()