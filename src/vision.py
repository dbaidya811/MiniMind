import os
import torch
from PIL import Image
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    AutoConfig,
    PreTrainedModel,
    GenerationMixin,
    GenerationConfig,
)

# Descriptor patch for tied weights key handling
class _TiedKeysPatch:
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get("_patched_all_tied_weights_keys", {})

    def __set__(self, instance, value):
        instance.__dict__["_patched_all_tied_weights_keys"] = value

setattr(PreTrainedModel, "all_tied_weights_keys", _TiedKeysPatch())


class VisionEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = "vikhyatk/moondream2"
        self.revision = "2024-08-26"

        config = AutoConfig.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            revision=self.revision,
        )

        config.pad_token_id = 50256
        if hasattr(config, "text_config"):
            config.text_config.pad_token_id = 50256
            config.text_config.rope_scaling = None

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            revision=self.revision,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            config=config,
            trust_remote_code=True,
            revision=self.revision,
            torch_dtype=torch.float32,
        )

        # Patch GenerationMixin and generation_config
        text_model = getattr(self.model, "text_model", None)
        targets = [self.model]
        if text_model is not None:
            targets.append(text_model)

        for target in targets:
            cls = target.__class__
            if not issubclass(cls, GenerationMixin):
                target.__class__ = type(
                    f"Patched_{cls.__name__}",
                    (cls, GenerationMixin),
                    {},
                )
            if not hasattr(target, "generation_config") or target.generation_config is None:
                target.generation_config = GenerationConfig.from_model_config(config)

        if self.device == "cuda":
            self.model = self.model.to("cuda")

        self.model.eval()

    def describe_or_answer(self, image_path: str, prompt: str = "Describe this image.") -> str:
        clean_path = image_path.strip().strip('"').strip("'")
        if not os.path.exists(clean_path):
            return f"Error: Image not found at path '{clean_path}'"

        try:
            image = Image.open(clean_path).convert("RGB")
            with torch.no_grad():
                enc_image = self.model.encode_image(image)
                answer = self.model.answer_question(enc_image, prompt, self.tokenizer)
            return str(answer).strip()
        except Exception as e:
            return f"Error processing image: {str(e)}"