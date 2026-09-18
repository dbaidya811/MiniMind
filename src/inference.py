import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

class MiniMindEngine:
    def __init__(self, base_model_id="Qwen/Qwen2.5-0.5B-Instruct", adapter_path="models/final_adapter"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_id)
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            torch_dtype=torch.float32,
            device_map="auto" if self.device == "cuda" else None
        )
        self.model = PeftModel.from_pretrained(base_model, adapter_path)
        self.model.eval()

    def generate(self, messages, max_new_tokens=256, temperature=0.7):
        # 1. Chat Template encode
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        input_token_count = model_inputs.input_ids.shape[1]

        # 2. Timing start
        start_time = time.perf_counter()

        with torch.no_grad():
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True if temperature > 0 else False,
                pad_token_id=self.tokenizer.eos_token_id
            )

        elapsed_time = time.perf_counter() - start_time

        # 3. Only new tokens extract
        output_ids = generated_ids[0][input_token_count:]
        generated_token_count = len(output_ids)
        response_text = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()

        stats = {
            "tokens": generated_token_count,
            "time_sec": elapsed_time,
            "speed": generated_token_count / elapsed_time if elapsed_time > 0 else 0.0
        }

        return response_text, stats