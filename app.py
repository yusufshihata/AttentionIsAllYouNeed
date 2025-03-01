import os
import torch
import streamlit as st
import subprocess
from transformers import AutoTokenizer
from src.model import TransformerEncoder
from src.utils import load_checkpoint
from src.inference import predict
from src.lr_scheduler import TransformerScheduler

# Streamlit UI
st.set_page_config(page_title="IMDB Sentiment Analysis", layout="centered")
st.title("IMDB Sentiment Analysis")
st.write("Enter a movie review and get the predicted sentiment!")

# Model directory
MODEL_DIR = "./models"
MODEL_PATH = os.path.join(MODEL_DIR, "checkpoint_3.pth")

# Step 1: Download model from Kaggle if not present
if not os.path.exists(MODEL_PATH):
    st.info("Downloading model from Kaggle... (This may take a few moments)")
    os.makedirs(MODEL_DIR, exist_ok=True)

    try:
        subprocess.run(
            [
                "kaggle", "kernels", "output", "yusufshihata20069/sentiment-analysis-with-transformers",
                "-p", MODEL_DIR
            ],
            capture_output=True,
            text=True,
            check=True
        )
        st.success("Model downloaded successfully!")
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to download model: {e.stderr}")
        st.stop()

# Step 2: Load Tokenizer
st.info("Loading tokenizer...")
try:
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    st.success("Tokenizer loaded!")
except Exception as e:
    st.error(f"Failed to load tokenizer: {e}")
    st.stop()

# Step 3: Load Model
st.info("Loading model...")
try:
    model = TransformerEncoder(vocab_size=30522, d_model=768, num_heads=12, num_layers=6, d_ff=3072)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    scheduler = TransformerScheduler(optimizer=optimizer, d_model=768, warmup_steps=4000)
    load_checkpoint(MODEL_PATH, model, optimizer, scheduler)
    model.eval()
    device = "cpu"
    model.to(device)
    st.success("Model loaded!")
except Exception as e:
    st.error(f"Failed to load model: {e}")
    st.stop()

# Step 4: UI for Input
user_input = st.text_area("Enter a review:", "")

if st.button("Analyze Sentiment"):
    if user_input.strip():
        sentiment = predict(model, tokenizer, user_input)
        st.subheader(f"Predicted Sentiment: **{sentiment}**")
    else:
        st.warning("Please enter text before analyzing.")
