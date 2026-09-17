# MiniMind

MiniMind is a lightweight, fully private conversational AI assistant fine-tuned on top of `Qwen/Qwen2.5-0.5B-Instruct` using Low-Rank Adaptation (LoRA). Built for edge environments and resource-constrained systems, it delivers zero-latency local inference through an interactive CLI and an asynchronous FastAPI backend without any third-party cloud API dependencies.

---

## Key Features

- **100% Offline & Private**: All inference and data operations run strictly on your machine without external API calls or tracking.
- **Efficient Fine-Tuning (PEFT / LoRA)**: Custom adapter training targeting key attention projection layers (`q_proj`, `v_proj`, `k_proj`, `o_proj`) for minimal memory footprint.
- **Dual Inference Interfaces**:
  - **Terminal CLI**: Interactive conversational loop with history retention and clean session handling.
  - **FastAPI Backend**: Async REST API complete with automated Swagger (`/docs`) interactive documentation and CORS support.
- **Hardware Agnostic**: Optimized to run smooth inference on mid-range laptop CPUs (using 32-bit floats) and high-speed execution with CUDA/FP16 on NVIDIA GPUs.
- **Weight Fusion**: Includes standalone LoRA merge scripts to bake adapter weights directly into the base model for standalone checkpoint deployment or export to formats like GGUF/Ollama.

---

## Project Architecture

```text
MiniMind/
├── app/
│   ├── api.py              # FastAPI REST server with streaming-ready endpoints
│   └── cli.py              # Real-time multi-turn terminal chat interface
├── data/
│   ├── train.jsonl         # Supervised fine-tuning (SFT) conversation pairs
│   └── val.jsonl           # Validation dataset for loss evaluation
├── models/
│   ├── checkpoints/        # Intermediate training checkpoints
│   ├── final_adapter/      # Trained LoRA adapters & tokenizer configuration
│   └── merged_minimind/    # Standalone fused base + LoRA model weights
├── src/
│   ├── dataset.py          # Custom Hugging Face dataset loader & preprocessor
│   ├── inference.py        # Text generation engine with chat-template parsing
│   ├── merge.py            # LoRA adapter fusion & export script
│   └── train.py            # Modular SFTTrainer pipeline with CPU/CUDA fallback
├── requirements.txt        # Pinned Python package dependencies
└── README.md               # Project documentation

```

---

## Technical Specifications

| Parameter | Specification |
| --- | --- |
| **Base Architecture** | Qwen 2.5 (0.5 Billion Parameters, Instruct variant) |
| **Fine-Tuning Method** | Supervised Fine-Tuning (SFT) with LoRA |
| **LoRA Hyperparameters** | Rank ($r$) = 8, Alpha ($\alpha$) = 16, Dropout = 0.05 |
| **Target Modules** | `q_proj`, `k_proj`, `v_proj`, `o_proj` |
| **Max Sequence Length** | 256 to 512 tokens |
| **Inference Framework** | PyTorch, Hugging Face `transformers`, `peft` |
| **Recommended Hardware** | 8 GB+ RAM (CPU mode) or 4 GB+ VRAM (GPU mode) |

---

## Installation & Setup

### 1. Clone & Set Up Environment

```powershell
# Clone the repository
git clone [https://github.com/dbaidya811/MiniMind.git](https://github.com/dbaidya811/MiniMind.git)
cd MiniMind

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# (Linux / macOS: source venv/bin/activate)

# Install required dependencies
pip install -r requirements.txt

```

---

## Dataset Format

Data is structured in standard ChatML/Hugging Face multi-turn JSONL format under `data/train.jsonl` and `data/val.jsonl`:

```json
{"messages": [{"role": "system", "content": "You are MiniMind, a helpful and lightweight personal AI assistant."}, {"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello! I am MiniMind. How can I help you today?"}]}
{"messages": [{"role": "system", "content": "You are MiniMind, a helpful and lightweight personal AI assistant."}, {"role": "user", "content": "What is MiniMind?"}, {"role": "assistant", "content": "MiniMind is a fine-tuned lightweight local language model."}]}

```

---

## Model Training

### Option A: Local CPU/GPU Training

Run the training pipeline directly from your local terminal:

```powershell
python src/train.py

```

### Option B: Cloud GPU Acceleration (Google Colab T4)

For faster training times (~1-2 minutes):

1. Create a Google Colab notebook and set the runtime to **T4 GPU**.
2. Install dependencies:
```bash
!pip install -q torch transformers datasets peft trl accelerate

```


3. Run the SFT training loop with your dataset.
4. Compress the generated adapter:
```python
import shutil
shutil.make_archive("final_adapter", "zip", "final_adapter")

```


5. Download and extract `final_adapter.zip` into your local `MiniMind/models/final_adapter/` directory.

---

## Running the Application

### 1. Interactive CLI Mode

Launch the chat session in your console:

```powershell
python app/cli.py

```

```text
========================================
MiniMind Terminal Chat (Type 'exit' to quit)
========================================

You: Who made you?
MiniMind: I was trained and fine-tuned by my creator as the MiniMind model.

```

### 2. FastAPI Web Server

Start the REST API server on `localhost:8000`:

```powershell
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

```

* **Interactive API Documentation**: Open `http://127.0.0.1:8000/docs` in your browser.
* **REST Endpoint**: `POST /chat`

**Example Request Payload:**

```json
{
  "messages": [
    {"role": "system", "content": "You are MiniMind, a helpful AI assistant."},
    {"role": "user", "content": "Explain API endpoints in one line."}
  ],
  "max_tokens": 100,
  "temperature": 0.7
}

```

---

## Merging Adapter Weights (Optional)

To fuse the LoRA weights permanently into the base model for faster inference or conversion to GGUF:

```powershell
python src/merge.py

```

The unified standalone model will be exported to `models/merged_minimind/`.

---

## Roadmap

* [ ] Add GGUF quantization support (Q4_K_M / Q8_0) for direct llama.cpp execution.
* [ ] Implement token-by-token streaming responses in CLI and FastAPI via Server-Sent Events (SSE).
* [ ] Build a lightweight web UI using React and Tailwind CSS.

---

## License

This project is licensed under the **MIT License**.
