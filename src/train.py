import os
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

# Leverage available CPU threads
torch.set_num_threads(os.cpu_count() or 4)

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
OUTPUT_DIR = "models/final_adapter"

def train():
    has_cuda = torch.cuda.is_available()
    device = "cuda" if has_cuda else "cpu"
    print(f"Training device: {device}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load base model in float32 for CPU stability
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=torch.float32,
        device_map=None
    )

    # Load dataset
    dataset = load_dataset(
        "json",
        data_files={"train": "data/train.jsonl", "validation": "data/val.jsonl"}
    )

    # Lightweight LoRA setup for low CPU overhead
    peft_config = LoraConfig(
        r=4,
        lora_alpha=8,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # Optimized training arguments
    training_args = SFTConfig(
        output_dir="models/checkpoints",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate=3e-4,
        num_train_epochs=2,
        logging_steps=1,
        save_strategy="no",
        eval_strategy="no",
        use_cpu=True,
        max_length=64  # Short sequence length greatly accelerates attention computation
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        peft_config=peft_config,
        processing_class=tokenizer,
        args=training_args
    )

    print("Starting optimized CPU training...")
    trainer.train()

    # Save fine-tuned adapter weights
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"Training complete! Adapter saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    train()