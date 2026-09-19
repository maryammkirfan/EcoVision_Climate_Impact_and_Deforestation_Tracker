"""
inference.py — Load trained weights and classify a single image.

This is the exact code path Streamlit app and Docker
container will call. It is deliberately independent of the training
loop and the full dataset — it only needs model.pt, a class name list,
and one image, because that is all a deployed app will ever have.
"""

import json
from pathlib import Path

import torch
from PIL import Image

from model import build_model
from utils import get_eval_transform

DEFAULT_MODEL_PATH = "model.pt"
DEFAULT_METADATA_PATH = "model_metadata.json"


def load_model(model_path: str = DEFAULT_MODEL_PATH, metadata_path: str = DEFAULT_METADATA_PATH):
    """Loads the saved model together with the metadata Day 2 should
    write alongside it (architecture name + class list), so this
    function never has to guess or hardcode which architecture won."""
    with open(metadata_path) as f:
        metadata = json.load(f)

    model = build_model(metadata["model_name"], num_classes=len(metadata["class_names"]), pretrained=False)
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    return model, metadata["class_names"]


def predict(image: Image.Image, model: torch.nn.Module, class_names: list[str], top_k: int = 2):
    """Runs one PIL image through the model and returns the top_k
    (class_name, probability) predictions, sorted highest first.

    top_k=2 by default rather than 1, deliberately: Day 3's error
    analysis showed specific classes get confused with each other, so
    the app surfaces the runner-up prediction too, which is more
    honest about model uncertainty than a single label would be.
    """
    transform = get_eval_transform()
    tensor = transform(image.convert("RGB")).unsqueeze(0)  # add batch dim

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0)

    top_probs, top_indices = torch.topk(probs, k=top_k)
    return [
        (class_names[idx], prob.item())
        for idx, prob in zip(top_indices.tolist(), top_probs)
    ]


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python inference.py <path_to_image>")
        sys.exit(1)

    model, class_names = load_model()
    image = Image.open(sys.argv[1])
    results = predict(image, model, class_names)

    print(f"Predictions for {sys.argv[1]}:")
    for class_name, prob in results:
        print(f"  {class_name:25s} {prob:.1%}")