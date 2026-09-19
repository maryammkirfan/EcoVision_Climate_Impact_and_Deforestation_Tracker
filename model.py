"""
model.py — Model architecture definitions.

Kept separate from training/inference logic so that ANY script (
training, error analysis, Streamlit app, Docker container) imports 
the exact same architecture code instead of each copy-pasting a
slightly different version that could silently drift.
"""

import torch.nn as nn
from torchvision import models


class SimpleCNN(nn.Module):
    """From-scratch baseline used only to measure the value transfer
    learning adds over training with random initialization."""

    def __init__(self, num_classes: int):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def build_resnet50(num_classes: int, pretrained: bool = True) -> nn.Module:
    """ResNet-50 with a frozen ImageNet backbone and a new head sized
    to num_classes. pretrained=False is used when reloading saved
    weights, since the weights themselves supply the values."""
    weights = models.ResNet50_Weights.IMAGENET1K_V2 if pretrained else None
    model = models.resnet50(weights=weights)
    for param in model.parameters():
        param.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def build_mobilenetv3(num_classes: int, pretrained: bool = True) -> nn.Module:
    """MobileNetV3-Small with a frozen ImageNet backbone and a new
    head sized to num_classes."""
    weights = models.MobileNet_V3_Small_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.mobilenet_v3_small(weights=weights)
    for param in model.parameters():
        param.requires_grad = False
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, num_classes)
    return model


# Single source of truth mapping a saved model's name (as written into
# day2_model_comparison.csv) to the function that rebuilds its
# architecture. inference.py and day3_error_analysis.py both use this
# instead of maintaining their own copy of the mapping.
MODEL_BUILDERS = {
    "resnet50": build_resnet50,
    "mobilenetv3": build_mobilenetv3,
    "baseline_cnn": lambda num_classes, pretrained=False: SimpleCNN(num_classes),
}


def build_model(name: str, num_classes: int, pretrained: bool = True) -> nn.Module:
    if name not in MODEL_BUILDERS:
        raise ValueError(f"Unknown model name '{name}'. Options: {list(MODEL_BUILDERS)}")
    return MODEL_BUILDERS[name](num_classes, pretrained=pretrained)