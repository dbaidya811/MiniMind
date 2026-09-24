![MiniMind Logo](public/image1.png)

<div align="center">

# 🧠 MiniMind

### Autonomous · Ultra-Fast · Fully Local Multimodal AI Edge Agent

**MiniMind** is a production-oriented AI assistant that runs **100% on your hardware** — no cloud, no API keys, no data ever leaves your machine. Feed it plain English and it will autonomously draft **executive PowerPoint decks**, **styled Excel workbooks**, **executive Word whitepapers**, **paint AI images locally**, **inspect images visually**, **answer from live web intel**, and even **launch your desktop apps** — all from a single rich terminal UI.

At its core sits a tuned **Qwen2.5-7B-Instruct (Q4_K_M GGUF)** engine powered by `llama-cpp-python` (`n_batch=512`, `repeat_penalty=1.18`) that runs a Chain-of-Thought (CoT) drafting loop over a **Deep Web RAG** pipeline — so every document, dataset, and answer is grounded in real evidence, not memory alone.

</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-4C9CDB)](https://www.python.org/)
[![LLM](https://img.shields.io/badge/LLM-Qwen2.5--7B--Instruct-6D28D9)](#-key-features)
[![Local](https://img.shields.io/badge/AI-100%25-Local-2EA043)](https://github.com/dbaidya811/MiniMind)
[![License](https://img.shields.io/badge/License-MIT-F39C12)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-0288D1)](https://github.com/dbaidya811/MiniMind)
[![PRs](https://img.shields.io/badge/PRs-Welcome-8B5CF6)](https://github.com/dbaidya811/MiniMind/pulls)

</div>

---

## 📑 Table of Contents

- [✨ Key Features](#-key-features)
- [🧠 System Architecture](#-system-architecture)
- [🖥 Hardware Requirements](#-hardware-requirements)
- [🧰 Tech Stack](#-tech-stack)
- [🚀 Installation & Setup](#installation--setup)
- [🎮 Quickstart & Usage](#quickstart--usage)
- [🖼 Sample Gallery](#-sample-gallery)
- [📁 Project Structure](#-project-structure)
- [🗺 Roadmap](#-roadmap)
- [👤 Author & Credits](#-author--credits)
- [📄 License](#-license)

---

## ✨ Key Features

### 🧠 Fully Local Edge LLM

- **Qwen2.5-7B-Instruct** quantized to **Q4_K_M GGUF** (≈ 4.4 GB) and served locally via `llama-cpp-python`.
- Prompt evaluation accelerated with tuned batching (`n_batch=512`) over an 8-thread, 4K-token context (`n_ctx=4096`).
- **Hallucination guardrail** — a tuned `repeat_penalty=1.18` suppresses repetitive loops and ghost tokens.
- **Zero-interaction auto-download** — on first run the model streams straight into `models/` from Hugging Face, no manual setup.

### 📑 Autonomous Multi-Format File Engine

Type one sentence → receive a finished, design-tuned office file in `~/Downloads`:

- **📽 Executive PowerPoint (`.pptx`)** — structured 16:9 decks rendered with `python-pptx`:
  - Cover slides with auto-generated **hero images** (SD-Turbo) on a navy/coral executive theme
  - Clean **rounded-card layouts** with automatic **two-column** content splits
  - **Auto-generated data charts** — dynamic **Bar & Pie charts** (Matplotlib) embedded from slide metrics
- **📊 Styled Excel (`.xlsx`)** — fact-checked CSV data compiled into a rich workbook via `openpyxl`:
  - Auto column widths, **navy-slate headers** with bold white type
  - **Zebra striping**, hairline borders, and automatic numeric typing (int / float)
- **📄 Executive Whitepapers (`.docx`)** — generated with `python-docx`:
  - Hierarchical heading system (H1 / H2 / H3) with custom 1-inch margins
  - **Callout quote paragraphs** (`>` executive summaries) and bulleted insight blocks
- **📝 Text (`.txt`)** — quick notes, configurations, and exportable snippets.

### 🕸 Deep Multi-Source RAG

- Direct **Wikipedia REST API** extraction as a factual background layer.
- **DuckDuckGo** web search for real-time snippets, listings, and current events.
- Retrieved intel is injected as *grounded context* before **Chain-of-Thought (CoT)** drafting — MiniMind writes from evidence it just fetched, not from memory alone.

### 🎨 Multimodal Vision & Creativity

- **👁 Local Vision Engine** — inspects local images with a lightweight (~400 MB) ViT-GPT2 image-to-text pipeline and describes any `.png / .jpg / .jpeg / .webp` file.
- **🖌 AI Image Painter** — high-speed local text-to-image via **SD-Turbo** (single-step adversarial diffusion distillation): one prompt → one image in seconds, saved straight to `~/Downloads`.

### 🖥 System & Desktop Tools (Zero Command)

- **App launcher** — open VS Code, Chrome, Notepad, Calculator, Explorer, and more from plain English.
- **File-system explorer** — render `~/Downloads` (or any folder) as a clean table with type, name, and size.
- **File reader** — print local `.txt / .md / .csv / .json` files directly into the conversation.

### ✨ Modern Terminal UI

- Built on **Rich**: styled panels, rule separators, and clean information tables.
- **Dynamic spinners** for every background task (RAG retrieval, engine warm-up, asset compilation).
- **Live generation metrics** — real-time streaming Markdown with `Tokens · Time · tok/s` readouts under every response.

---

## 🧠 System Architecture

```
                    ┌──────────────────────────────────────────────────┐
                    │           USER   (natural language prompt)       │
                    └────────────────────────┬─────────────────────────┘
                                             ▼
                    ┌──────────────────────────────────────────────────┐
                    │           INTENT ROUTER   (app/cli.py)           │
                    │   keyword rules  +  LLM intent JSON router       │
                    └───────┬────────────────────────────┬─────────────┘
                            ▼                            ▼
   ┌────────────────────────────────┐      ┌────────────────────────────────┐
   │         DEEP WEB RAG            │      │           LLM CORE              │
   │    (src/search_tool.py)         │      │     (src/inference.py)          │
   │   • Wikipedia REST API          │      │  Qwen2.5-7B-Instruct · GGUF     │
   │   • DuckDuckGo search           │      │  n_batch=512 · n_ctx=4096       │
   │   • Fact-grounded context intel │      │  repeat_penalty=1.18 · temp 0.2 │
   └───────────────┬────────────────┘      └───────────────┬────────────────┘
                   └──────────────────────────────────────▶│
                                                           ▼
                          ┌────────────────────────────────────────────────┐
                          │      SINGLE-PASS CHAIN-OF-THOUGHT SYNTHESIS     │
                          │   fact-grounded drafting · JSON slide specs     │
                          │   CSV datasets · markdown whitepapers           │
                          └───────┬────────────────────────────┬───────────┘
                                  ▼                            ▼
   ┌──────────────────────────────────────┐    ┌──────────────────────────────┐
   │      MULTI-FORMAT FILE ENGINE          │    │     MULTIMODAL ENGINES       │
   │   (src/system_tools.py)                │    │   🎨 SD-Turbo painter        │
   │   📽 PPTX · 📊 XLSX · 📄 DOCX · 📝 TXT │    │   👁 ViT-GPT2 vision         │
   │   themes · charts · styling            │    │   🖥 app launcher + file ts  │
   └──────────────────┬────────────────────┘    └──────────────┬───────────────┘
                      └────────────────────────────────────────▶
                                         ▼
                       ┌────────────────────────────────────────────────────┐
                       │            ~/Downloads  —  auto-export             │
                       └────────────────────────────────────────────────────┘
```

**Document-generation pipeline (per asset):**

1. **Retrieve** → Wikipedia REST + DuckDuckGo gather a grounded fact sheet (≤ 2,500 chars).
2. **Reason** → a single-pass CoT prompt plans pillars, statistics, and visuals inside `<thought>` tags.
3. **Render** → the file engine materializes the plan into a themed `.pptx`, a typed `.xlsx`, or a styled `.docx` (charts + hero images included) and saves it to `~/Downloads`.

---

## 🖥 Hardware Requirements

| Tier | RAM | CPU / GPU | Notes |
| :--- | :--- | :--- | :--- |
| **Minimum** (chat + RAG only) | 8 GB | 64-bit CPU with AVX2 | Usable; slower prompt evaluation on a 7B model |
| **⭐ Recommended** (full edge agent) | **16 GB** | 4+ cores · SSD · ~10 GB free disk | Full file engine + vision + painting |
| **Accelerated** (optional) | 6 GB+ VRAM | NVIDIA GPU (CUDA) | fp16 SD-Turbo → near-instant painting; optional LLM GPU offload |

> **Storage:** the Q4_K_M GGUF alone is ≈ **4.4 GB** (see `models/Qwen2.5-7B-Instruct-Q4_K_M.gguf`), plus ~1–2 GB for the vision + diffusion caches. Weights self-download on first use; everything stays on your machine.

---

## 🧰 Tech Stack

| Layer | Technology |
| :--- | :--- |
| Language / Runtime | Python 3.10+ |
| LLM Inference | `llama-cpp-python` · GGUF (Q4_K_M) |
| Edge LLM | Qwen2.5-7B-Instruct (`bartowski` GGUF, auto-download) |
| RAG & Web | `duckduckgo-search` · Wikipedia REST API |
| Documents & Visualization | `python-pptx` · `python-docx` · `openpyxl` · `matplotlib` |
| Computer Vision | Hugging Face `transformers` (ViT-GPT2 image-to-text pipeline) |
| Diffusion | `diffusers` · Stability AI **SD-Turbo** (single-step) |
| CLI & UX | `rich` · `pyperclip` · `colorama` |
| API Layer | `fastapi` · `uvicorn` · `pydantic` |
| Model I/O & Image | `huggingface-hub` · `pillow` · PyTorch |

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.10+** and `git`
- A 64-bit OS — Windows, Linux, or macOS (developed and tested on Windows)
- **16 GB RAM recommended** — see [Hardware Requirements](#-hardware-requirements)

### 1 — Clone the repository

```bash
git clone https://github.com/dbaidya811/MiniMind.git
cd MiniMind
```

### 2 — Create a virtual environment

```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

> `requirements.txt` already points at the **CPU wheel index** for `llama-cpp-python`. On an NVIDIA GPU you may optionally install the CUDA build (`pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124`) for faster LLM inference.

### 4 — Run MiniMind (model auto-downloads on first launch)

```bash
python app/cli.py
```

On the very first start, MiniMind detects that `models/Qwen2.5-7B-Instruct-Q4_K_M.gguf` is missing and **streams it down automatically from Hugging Face** (≈ 4.4 GB). Once the engine is ready you'll land in the interactive prompt.

### Alternative launchers

| Method | Command |
| :--- | :--- |
| Global npm CLI | `npm install -g minimind-ai` → `minimind` |
| Windows PATH helper | double-click `install_path.bat`, restart the terminal → `minimind` |
| Windows launcher | `minimind.cmd` |

---

## 🎮 Quickstart & Usage

### Interactive CLI

Run it and just talk — **no slash-commands to memorize**:

```bash
python app/cli.py
```

| You say… | MiniMind does… |
| :--- | :--- |
| `Create a 6-slide presentation on renewable energy` | Deep RAG → CoT → themed 16:9 `.pptx` with auto hero image + bar/pie charts |
| `Make an Excel sheet of 5G adoption by country` | Fact-checked CSV → styled `.xlsx` (navy headers, zebra striping, auto widths) |
| `Write a word document about transformer architecture` | Executive whitepaper `.docx` with callout summary + hierarchical headings |
| `paint a cyberpunk city at night` | SD-Turbo paints it in seconds → `.png` in Downloads |
| `What's in this image: C:\photos\render.png` | Local vision engine inspects & describes the image |
| `Open Chrome` / `list my downloads folder` | Zero-command app launcher / file-explorer table |
| `Who is Albert Einstein?` | Live web intel injected into context, then fact-grounded chat |
| `Write a Python script to sort a list...` | Code-focused chat with syntax-highlighted Markdown |

> Every generated asset is exported to `~/Downloads` — the CLI prints the absolute file path, and streams the live **Tokens · Time · tok/s** readout beneath each response.

### Programmatic API

```python
# 1) Streaming chat with live tok/s stats
from src.inference import MiniMindEngine

bot = MiniMindEngine()
for chunk, stats in bot.generate_stream(
    [{"role": "user", "content": "Explain edge AI in 3 bullets."}],
    max_new_tokens=512,
):
    print(chunk, end="")
print(f"\n\n{stats['tokens']} tokens · {stats['time_sec']:.2f}s · {stats['speed']:.2f} tok/s")
```

```python
# 2) One-shot document on demand
from src.system_tools import SystemTools

res = SystemTools.create_word_file(
    "edge_ai.docx",
    "# Edge AI\n> Executive summary…\n## Foundations\n- Local-first inference",
)
print(res["path"])   # C:\Users\<you>\Downloads\edge_ai.docx
```

```python
# 3) Image painting & local vision
from src.image_gen import ImageGenerator
from src.vision import VisionEngine

ImageGenerator().generate("a minimalist glass house in a forest", output_path="outputs/house.png")
vision = VisionEngine()
print(vision.describe_or_answer("outputs/house.png"))   # "This image shows: …"
```

### FastAPI REST Server

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs → <http://127.0.0.1:8000/docs>

```json
POST /chat
{
  "messages": [{"role": "user", "content": "What is 5G?"}],
  "max_tokens": 400,
  "temperature": 0.7
}
```

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello!"}],"max_tokens":100,"temperature":0.7}'
```

---

## 🖼 Sample Gallery

Real output images generated by the MiniMind multimodal engines:

<div align="center">

![Image Generation Sample](public/image2.png)

*Text-to-image generation via SD-Turbo*

| ![Painter Output — Cat](outputs/cat.png) | ![Painter Output — Dog](outputs/dog.png) |
| :---: | :---: |
| **Cat** | **Dog** |

</div>

---

## 📁 Project Structure

```
MiniMind/
├── app/
│   ├── cli.py                # Rich interactive CLI · intent router · agent loop
│   └── api.py                # FastAPI REST backend (POST /chat)
├── bin/
│   └── index.js              # Global `minimind` npm launcher
├── scripts/
│   └── install_deps.js       # npm postinstall pip installer
├── src/
│   ├── inference.py          # GGUF edge LLM (Qwen2.5-7B Q4_K_M) + streaming
│   ├── search_tool.py        # Wikipedia REST + DuckDuckGo Deep RAG
│   ├── system_tools.py       # PPTX / XLSX / DOCX / TXT file engine + desktop tools
│   ├── vision.py             # Local ViT-GPT2 image inspection
│   ├── image_gen.py          # SD-Turbo text-to-image painter
│   ├── code_executor.py      # Sandboxed Python snippet executor
│   ├── train.py              # LoRA SFT training (Qwen2.5-0.5B base)
│   ├── dataset.py            # ChatML dataset tooling
│   └── merge.py              # LoRA → base model weight fusion
├── models/                   # GGUF weights (auto-downloaded on first run)
├── data/                     # Training datasets (train.jsonl / val.jsonl, ChatML)
├── outputs/                  # Generated-media samples
├── public/                   # Static assets (logo / screenshots)
├── requirements.txt          # Python dependencies
├── minimind.cmd              # Windows launcher (venv-aware)
├── install_path.bat          # Registers MiniMind in the Windows user PATH
└── package.json              # npm packaging (minimind-ai)
```

---

## 🗺 Roadmap

- [x] CPU-first GGUF inference (Qwen2.5-7B · Q4_K_M)
- [ ] Token-streaming SSE / WebSocket in the FastAPI layer
- [ ] Lightweight web UI (React + Tailwind) with file previews
- [ ] Upgrade vision to a true VQA model (Moondream2 / Qwen2-VL) for open-ended image Q&A
- [ ] Persistent long-term memory via a local vector store (e.g., ChromaDB)
- [ ] Voice interface (local Whisper STT + edge TTS)
- [ ] GGUF export pipeline from LoRA fine-tunes (`train.py` → `merge.py` → GGUF)
- [ ] One-command cross-platform Docker / portable build

---

## 👤 Author & Credits

Built with ❤️ by **Deep Baidya** — Full-Stack Software Developer.

- 🐙 GitHub — [@dbaidya811](https://github.com/dbaidya811)
- 📦 npm — [`minimind-ai`](https://www.npmjs.com/package/minimind-ai) (optional global install)
- 💬 Issues & feature requests — [Open an issue](https://github.com/dbaidya811/MiniMind/issues)

**Standing on the shoulders of giants:** Qwen2.5 (Alibaba), `llama.cpp` / `llama-cpp-python`, Stability AI **SD-Turbo**, Hugging Face `transformers` & `diffusers`, and the Python OSS office stack (`python-pptx`, `python-docx`, `openpyxl`, `matplotlib`, `rich`).

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

**MiniMind** — your private, autonomous edge agent. 🧠 ⚡ 🔒
