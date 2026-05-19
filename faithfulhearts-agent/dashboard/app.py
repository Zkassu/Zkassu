import json
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_FILE = ROOT / "data" / "amharic_examples.jsonl"
REPLIED_FILE = ROOT / "replied_ids.json"
ENV_FILE = ROOT / ".env"


def load_jsonl(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def load_replied_ids(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def load_env(path):
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


st.set_page_config(page_title="FaithfulHearts Agent", page_icon="🙏", layout="wide")
st.title("FaithfulHearts Agent Dashboard")

env = load_env(ENV_FILE)
examples = load_jsonl(EXAMPLES_FILE)
replied_ids = load_replied_ids(REPLIED_FILE)

col1, col2, col3 = st.columns(3)
col1.metric("Examples", len(examples))
col2.metric("Replied IDs", len(replied_ids))
col3.metric("Dry Run", env.get("DRY_RUN", "not set"))

st.subheader("Configuration")
safe_env = {
    "VIDEO_ID": env.get("VIDEO_ID", "not set"),
    "MAX_REPLIES_PER_DAY": env.get("MAX_REPLIES_PER_DAY", "not set"),
    "CLIENT_SECRETS_FILE": env.get("CLIENT_SECRETS_FILE", "not set"),
    "OPENAI_API_KEY": "set" if env.get("OPENAI_API_KEY") else "not set",
}
st.json(safe_env)

st.subheader("Prompt Examples")
if examples:
    df = pd.DataFrame(examples)
    categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
    selected = st.selectbox("Category", categories)
    if selected != "All":
        df = df[df["category"] == selected]
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("No examples found at data/amharic_examples.jsonl")

st.subheader("Recent Replied Comment IDs")
if replied_ids:
    st.dataframe(pd.DataFrame({"comment_id": replied_ids}), use_container_width=True, hide_index=True)
else:
    st.info("No replied_ids.json file yet. It will appear after the agent processes comments.")
