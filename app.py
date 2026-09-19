"""
app.py — EcoVision Streamlit web app.

Run with: streamlit run app.py

This file deliberately contains almost no model logic of its own — it
calls load_model() and predict() from inference.py, the exact same
functions error analysis and any future CLI usage rely on.
That's the point of Day 3's refactor: the model-facing code path is
identical whether it's called from a script, an analysis notebook, or
a web UI, so there's no way for the deployed app to quietly behave
differently from what you measured and reported.
"""

import pandas as pd
import streamlit as st
from PIL import Image

from inference import load_model, predict

st.set_page_config(page_title="EcoVision", page_icon="🛰️", layout="centered")

st.markdown(
    """
    <style>
    :root {
        --leaf: #2f6b3f;
        --leaf-dark: #1f4d2c;
        --olive: #788447;
        --olive-light: #eef2df;
        --paper: #fbfdf8;
        --ink: #203126;
        --muted: #607064;
        --line: #dce7d7;
    }

    .stApp {
        background: linear-gradient(145deg, #f4f8ee 0%, #ffffff 48%, #f7faf3 100%);
        color: var(--ink);
    }

    .block-container {
        max-width: 980px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--leaf-dark) !important;
        letter-spacing: -0.02em;
    }

    p, label, .stCaption {
        color: var(--muted) !important;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(120deg, #e7f0dc 0%, #ffffff 62%, #f0f3df 100%);
        border: 1px solid #d2e1c9;
        border-radius: 24px;
        padding: 2.4rem 2.5rem 2.2rem;
        margin-bottom: 1.6rem;
        box-shadow: 0 16px 40px rgba(47, 107, 63, 0.10);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 170px;
        height: 170px;
        right: -48px;
        top: -58px;
        border: 24px solid rgba(120, 132, 71, 0.18);
        border-radius: 50%;
    }

    .eyebrow {
        color: var(--olive);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }

    .hero-title {
        color: var(--leaf-dark);
        font-size: 2.65rem;
        font-weight: 850;
        line-height: 1.05;
        margin: 0;
    }

    .hero-subtitle {
        color: #536557;
        font-size: 1.02rem;
        line-height: 1.65;
        max-width: 700px;
        margin: 0.9rem 0 0;
    }

    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.82);
        border: 2px dashed #a9be91;
        border-radius: 18px;
        padding: 0.75rem;
        box-shadow: 0 8px 24px rgba(47, 107, 63, 0.07);
    }

    [data-testid="stFileUploaderDropzone"] {
        background: #f8fbf5;
        border-radius: 12px;
    }

    [data-testid="stImage"] img {
        border: 1px solid var(--line);
        border-radius: 18px;
        box-shadow: 0 10px 26px rgba(31, 77, 44, 0.12);
    }

    .prediction-card, .empty-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.35rem 1.45rem;
        box-shadow: 0 10px 28px rgba(47, 107, 63, 0.08);
    }

    .card-label {
        color: var(--olive);
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .prediction-value {
        color: var(--leaf-dark);
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0.45rem 0 0.7rem;
    }

    .confidence-badge {
        display: inline-block;
        background: var(--olive-light);
        color: var(--leaf-dark);
        border: 1px solid #d5dfb8;
        border-radius: 999px;
        padding: 0.35rem 0.7rem;
        font-size: 0.84rem;
        font-weight: 750;
    }

    [data-testid="stProgress"] > div {
        background: #e7eddc;
        border-radius: 999px;
    }

    [data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, var(--olive), var(--leaf));
        border-radius: 999px;
    }

    [data-testid="stAlert"] {
        background: #f1f6e9;
        border: 1px solid #d5e2c5;
        border-radius: 14px;
        color: var(--leaf-dark);
    }

    hr {
        border: 0;
        border-top: 1px solid var(--line);
        margin: 1.8rem 0;
    }

    .model-footer {
        background: #f1f5e9;
        border: 1px solid #dce5cb;
        border-radius: 14px;
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.6;
        padding: 0.95rem 1.2rem;
        text-align: center;
    }

    .model-footer strong { color: var(--leaf-dark); }
    #MainMenu, footer { visibility: hidden; }
    header { background: transparent !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Cache the model load across reruns — Streamlit reruns this whole
# script top-to-bottom on every user interaction (every upload, every
# widget change). Without caching, model.pt would be reloaded from
# disk on every single click, which is slow and pointless since the
# weights never change during a session.
@st.cache_resource
def get_model():
    return load_model()

model, class_names = get_model()

# Read Day 2's own comparison table instead of hardcoding a model name
# and accuracy — if you retrain and a different backbone wins later,
# this caption stays correct without editing app.py by hand.
@st.cache_resource
def get_model_stats():
    df = pd.read_csv("input/model_comparison.csv")
    best = df.loc[df["test_accuracy"].idxmax()]
    return best["model"], best["test_accuracy"]

model_name, model_accuracy = get_model_stats()

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">AI for environmental monitoring</div>
        <div class="hero-title">🛰️ EcoVision</div>
        <p class="hero-subtitle">
            Turn satellite imagery into a clear land-cover signal for
            environmental monitoring, deforestation tracking, and land-use analysis.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Analyze a satellite image")
st.caption("Upload a JPG, JPEG, or PNG image patch to identify its land-cover category.")

uploaded_file = st.file_uploader(
    "Upload a satellite image (JPG or PNG)",
    type=["jpg", "jpeg", "png"],
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    col1, col2 = st.columns([1, 1.4])
    with col1:
        st.markdown('<div class="card-label">Input image</div>', unsafe_allow_html=True)
        st.image(image, caption="Uploaded satellite image", use_container_width=True)

    with col2:
        # top_k=2 is not cosmetic — Day 3's error analysis found the
        # model genuinely confuses specific class pairs (River/Highway
        # in particular). Showing only the top-1 label would hide that
        # uncertainty; showing the runner-up is a more honest
        # representation of what the model actually "thinks."
        results = predict(image, model, class_names, top_k=2)
        top_class, top_prob = results[0]

        st.markdown(
            f"""
            <div class="prediction-card">
                <div class="card-label">Model prediction</div>
                <div class="prediction-value">{top_class}</div>
                <span class="confidence-badge">✓ {top_prob:.1%} confidence</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(top_prob)

        if len(results) > 1:
            runner_up_class, runner_up_prob = results[1]
            st.caption(
                f"Second guess: {runner_up_class} ({runner_up_prob:.1%}) · "
                f"shown because this model's known confusions (see README) "
                f"mean a close runner-up is worth seeing, not hiding."
            )

    st.divider()
    st.markdown(
        f"""
        <div class="model-footer">
            <strong>Model:</strong> {model_name}
            &nbsp; · &nbsp; Transfer learning with a frozen ImageNet backbone
            &nbsp; · &nbsp; <strong>Dataset:</strong> EuroSAT
            &nbsp; · &nbsp; <strong>Test accuracy:</strong> {model_accuracy:.1%}
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="empty-card">
            <div style="font-size:2.1rem;">🌿</div>
            <h3 style="margin:0.35rem 0 0.2rem;">Ready to explore</h3>
            <p style="margin:0;">Your land-cover classification will appear here after you upload an image.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )