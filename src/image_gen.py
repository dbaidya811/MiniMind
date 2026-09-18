import os
import torch
from diffusers import AutoPipelineForText2Image

class ImageGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        # sd-turbo 1 step generation kore, tai CPU/local setup-e khub fast
        self.pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sd-turbo",
            torch_dtype=dtype
        )
        if self.device == "cuda":
            self.pipe.to("cuda")

    def generate(self, prompt: str, output_path: str = "outputs/generated.png") -> str:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image = self.pipe(
                prompt=prompt, 
                num_inference_steps=1, 
                guidance_scale=0.0
            ).images[0]
            
            image.save(output_path)
            return output_path
        except Exception as e:
            return f"Error generating image: {str(e)}"