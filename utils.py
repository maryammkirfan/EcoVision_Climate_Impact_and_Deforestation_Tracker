"""
utils.py — Data loading, transforms, and shared class-name/statistics
constants. This is the single place that defines how raw EuroSAT
images become model-ready tensors, so Day 1's notebook, Day 2's
training, and Day 4's Streamlit app can never accidentally use
different normalization or resizing and get inconsistent results.
"""

import torch
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
IMAGE_SIZE = 224


def get_eval_transform() -> transforms.Compose:
    """Deterministic preprocessing: resize + normalize, no augmentation.
    Used for validation, test, and single-image inference — anywhere
    the output needs to be reproducible."""
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


def get_train_transform() -> transforms.Compose:
    """Training-only preprocessing with augmentation. Vertical AND
    horizontal flips are both included because satellite imagery has
    no fixed orientation, unlike most photographic datasets."""
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(0.5),
        transforms.RandomVerticalFlip(0.5),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


def denormalize(tensor: torch.Tensor) -> torch.Tensor:
    """Reverses ImageNet normalization for visualization/display."""
    mean = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
    std = torch.tensor(IMAGENET_STD).view(3, 1, 1)
    return (tensor * std + mean).clamp(0, 1)


def get_dataloaders(root: str = "./data", batch_size: int = 32, seed: int = 42):
    """Rebuilds the exact same train/val/test split used throughout
    the project (70/15/15, seeded) and returns three DataLoaders plus
    the class name list. Centralizing this means Day 3's error
    analysis and any future retraining run are guaranteed to evaluate
    on the SAME test images Day 2 reported numbers for."""
    raw_dataset = datasets.EuroSAT(root=root, download=True, transform=None)
    class_names = raw_dataset.classes
    n_total = len(raw_dataset)
    n_train = int(0.70 * n_total)
    n_val = int(0.15 * n_total)
    n_test = n_total - n_train - n_val

    generator = torch.Generator().manual_seed(seed)
    train_idx, val_idx, test_idx = torch.utils.data.random_split(
        range(n_total), [n_train, n_val, n_test], generator=generator
    )

    train_set = Subset(datasets.EuroSAT(root=root, transform=get_train_transform()), train_idx.indices)
    val_set = Subset(datasets.EuroSAT(root=root, transform=get_eval_transform()), val_idx.indices)
    test_set = Subset(datasets.EuroSAT(root=root, transform=get_eval_transform()), test_idx.indices)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True)
    val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)

    return train_loader, val_loader, test_loader, class_names