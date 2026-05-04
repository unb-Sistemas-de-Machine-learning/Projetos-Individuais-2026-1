"""Model loading and identity.

Owns the pretrained model name, the label mapping, and the tokenization
defaults used everywhere in the project. Any code that needs to know "which
model are we using" should import from this module.
"""

from transformers import pipeline

MODEL_NAME = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
LABEL_MAP = {"POSITIVE": 1, "NEGATIVE": 0}
DEFAULT_MAX_LENGTH = 512


def build_classifier(device: int = -1, max_length: int = DEFAULT_MAX_LENGTH):
    """Construct the DistilBERT text-classification pipeline.

    Args:
        device: Torch device index. -1 forces CPU (the default for this project).
        max_length: Maximum input sequence length in tokens. DistilBERT has a
            hard architectural limit of 512; longer inputs are truncated.
    """
    return pipeline(
        "text-classification",
        model=MODEL_NAME,
        device=device,
        truncation=True,
        max_length=max_length,
    )
