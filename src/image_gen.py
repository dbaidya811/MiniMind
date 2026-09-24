import os
import time
from pathlib import Path
import torch
from diffusers import AutoPipelineForText2Image
from diffusers.utils import logging as diffusers_logging

# Suppress multi-line progress logs from diffusers
diffusers_logging.set_verbosity_error()


class ImageGenerator:
    def __init__(self, model_id: str = "stabilityai/sd-turbo"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32

        # Initialize SD-Turbo pipeline
        self.pipe = AutoPipelineForText2Image.from_pretrained(
            model_id,
            torch_dtype=self.dtype,
            variant="fp16" if self.device == "cuda" else None
        )
        self.pipe.to(self.device)

        # Disable internal progress bar to prevent multiline terminal pollution
        self.pipe.set_progress_bar_config(disable=True)

    def generate(self, prompt: str, output_path: str = None) -> str:
        try:
            # Default to the OS user's Downloads directory if no custom path is provided
            if not output_path:
                downloads_dir = Path.home() / "Downloads"
                downloads_dir.mkdir(parents=True, exist_ok=True)
                timestamp = int(time.time())
                output_path = str(downloads_dir / f"minimind_{timestamp}.png")
            else:
                target_dir = os.path.dirname(output_path)
                if target_dir:
                    os.makedirs(target_dir, exist_ok=True)

            # SD-Turbo single-step adversarial diffusion distillation (ADD)
            result = self.pipe(
                prompt=prompt,
                num_inference_steps=1,
                guidance_scale=0.0
            )
            image = result.images[0]

            image.save(output_path)
            return output_path
        except Exception as e:
            return f"Error generating image: {str(e)}"