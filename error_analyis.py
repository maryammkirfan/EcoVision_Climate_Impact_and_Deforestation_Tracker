"""
EcoVision — Part A: Error Analysis

Standalone script for project-root execution. It reads the input comparison
CSV, loads the saved model and metadata, evaluates the test set, and saves
artifacts to disk without blocking on a GUI.
"""

from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import torch
from sklearn.metrics import classification_report, confusion_matrix

from model import build_model
from utils import denormalize, get_dataloaders

BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    comparison_path = BASE_DIR / "input" / "model_comparison.csv"
    if not comparison_path.exists():
        raise FileNotFoundError(f"Missing comparison file: {comparison_path}")

    comparison_df = pd.read_csv(comparison_path)
    best_row = comparison_df.loc[comparison_df["test_accuracy"].idxmax()]
    best_model_name = best_row["model"]
    print(f"Analyzing errors for: {best_model_name} (test accuracy {best_row['test_accuracy']:.4f})")

    metadata_path = BASE_DIR / "model_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing model metadata file: {metadata_path}")
    with metadata_path.open() as f:
        metadata = json.load(f)

    class_names = metadata["class_names"]
    model_name = metadata["model_name"]
    if model_name not in {"resnet50", "mobilenetv3", "baseline_cnn"}:
        raise ValueError(f"Unsupported model name in metadata: {model_name}")

    train_loader, val_loader, test_loader, class_names = get_dataloaders(
        root=str(BASE_DIR / "data"),
        batch_size=32,
        seed=42,
    )
    NUM_CLASSES = len(class_names)

    model = build_model(model_name, num_classes=NUM_CLASSES, pretrained=False)
    weights_path = BASE_DIR / "model.pt"
    if not weights_path.exists():
        raise FileNotFoundError(f"Missing model weights: {weights_path}")
    model.load_state_dict(torch.load(weights_path, map_location="cpu"))
    model.eval()

    all_images, all_true, all_pred, all_probs = [], [], [], []
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            preds = outputs.argmax(1)

            all_images.append(images.cpu())
            all_true.extend(labels.cpu().numpy())
            all_pred.extend(preds.cpu().numpy())
            all_probs.append(probs.cpu())

    all_images = torch.cat(all_images)
    all_probs = torch.cat(all_probs)

    cm = confusion_matrix(all_true, all_pred, normalize="true")
    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(cm, cmap="Greens", vmin=0, vmax=1)
    ax.set_xticks(range(NUM_CLASSES))
    ax.set_yticks(range(NUM_CLASSES))
    ax.set_xticklabels(class_names, rotation=45, ha="right")
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(f"Confusion matrix — {best_model_name} (row-normalized)")

    for i in range(NUM_CLASSES):
        for j in range(NUM_CLASSES):
            val = cm[i, j]
            ax.text(
                j,
                i,
                f"{val:.2f}",
                ha="center",
                va="center",
                color="white" if val > 0.5 else "black",
                fontsize=8,
            )

    plt.colorbar(im, ax=ax, fraction=0.046)
    plt.tight_layout()
    output_dir = BASE_DIR / "error_analysis_output"
    output_dir.mkdir(exist_ok=True)
    fig.savefig(output_dir / "confusion_matrix.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    report = classification_report(
        all_true,
        all_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )
    report_df = pd.DataFrame(report).transpose().round(3)
    print("Per-class performance:")
    print(report_df.to_string())
    report_df.to_csv(output_dir / "classification_report.csv")

    cm_counts = confusion_matrix(all_true, all_pred)
    confusions = []
    for i in range(NUM_CLASSES):
        for j in range(NUM_CLASSES):
            if i != j and cm_counts[i, j] > 0:
                confusions.append((class_names[i], class_names[j], int(cm_counts[i, j])))

    confusions.sort(key=lambda x: x[2], reverse=True)
    print("\nTop 5 confused class pairs (true -> predicted, count):")
    for true_c, pred_c, count in confusions[:5]:
        print(f"  {true_c:25s} -> {pred_c:25s} : {count} images")

    if confusions:
        top_true_name, top_pred_name, _ = confusions[0]
        top_true_idx = class_names.index(top_true_name)
        top_pred_idx = class_names.index(top_pred_name)

        mistake_indices = [
            i for i, (t, p) in enumerate(zip(all_true, all_pred))
            if t == top_true_idx and p == top_pred_idx
        ][:6]

        if mistake_indices:
            fig, axes = plt.subplots(1, len(mistake_indices), figsize=(3 * len(mistake_indices), 3.5))
            if len(mistake_indices) == 1:
                axes = [axes]
            for ax, idx in zip(axes, mistake_indices):
                img = denormalize(all_images[idx])
                confidence = all_probs[idx, top_pred_idx].item()
                ax.imshow(img.permute(1, 2, 0).numpy())
                ax.set_title(f"true: {top_true_name}\npred: {top_pred_name} ({confidence:.0%})", fontsize=8)
                ax.axis("off")
            plt.suptitle(f"Misclassified examples: {top_true_name} -> {top_pred_name}", y=1.05)
            plt.tight_layout()
            fig.savefig(output_dir / "misclassified_examples.png", dpi=150, bbox_inches="tight")
            plt.close(fig)

    print("\nError analysis artifacts saved:")
    print("  confusion_matrix.png")
    print("  classification_report.csv")
    print("  misclassified_examples.png")


if __name__ == "__main__":
    main()