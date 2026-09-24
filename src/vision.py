import os
import torch
from PIL import Image
from transformers import pipeline, logging as hf_logging

hf_logging.set_verbosity_error()

class VisionEngine:
    def __init__(self, model_id: str = "nlpconnect/vit-gpt2-image-captioning"):
        self.device = 0 if torch.cuda.is_available() else -1
        # Lightweight ~400MB pipeline, standard HuggingFace native architecture
        self.captioner = pipeline(
            "image-to-text",
            model=model_id,
            device=self.device
        )

    def describe_or_answer(self, image_path: str, prompt: str = "") -> str:
        clean_path = image_path.strip().strip('"').strip("'")
        if not os.path.exists(clean_path):
            return f"Error: Image not found at path '{clean_path}'"

        try:
            image = Image.open(clean_path).convert("RGB")
            # Downscale for ultra-fast inference
            image.thumbnail((512, 512))
            
            result = self.captioner(image, max_new_tokens=64)
            if result and len(result) > 0:
                caption = result[0].get("generated_text", "").strip()
                return f"This image shows: {caption.capitalize()}."
            return "Unable to describe image."
        except Exception as e:
            return f"Vision error: {str(e)}"