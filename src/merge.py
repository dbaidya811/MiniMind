import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
ADAPTER_DIR = "models/final_adapter"
MERGED_DIR = "models/merged_minimind"

def merge_lora():
    print("Loading base model and LoRA adapter...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    model = PeftModel.from_pretrained(base, ADAPTER_DIR)
    
    print("Merging weights...")
    merged_model = model.merge_and_unload()

    os.makedirs(MERGED_DIR, exist_ok=True)
    merged_model.save_pretrained(MERGED_DIR)
    tokenizer.save_pretrained(MERGED_DIR)
    print(f"Standalone merged model saved to: {MERGED_DIR}")

if __name__ == "__main__":
    merge_lora()