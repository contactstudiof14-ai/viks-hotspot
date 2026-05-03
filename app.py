import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt

st.set_page_config(page_title="Hot Spot AI Pro", layout="centered")

# ---------- STYLE ----------
st.markdown("""
<style>
.number {
    display:inline-block;
    padding:10px;
    margin:4px;
    border-radius:8px;
    background:#eef2f7;
    font-weight:bold;
}
.card {
    padding:12px;
    border-radius:12px;
    background:white;
    margin-bottom:12px;
    box-shadow:0px 2px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

st.title("🎯 Hot Spot AI Pro")

# ---------- SESSION ----------
if "tickets" not in st.session_state:
    st.session_state.tickets = []

# ---------- DATA ----------
def load_data(uploaded):
    if uploaded:
        df = pd.read_csv(uploaded)
        numbers = df.values.flatten()
    else:
        numbers = []
        for _ in range(1500):
            numbers.extend(random.sample(range(1,81),20))
    return numbers

# ---------- AI SCORING ----------
def compute_scores(numbers):
    series = pd.Series(numbers)

    freq = series.value_counts()
    recency = series[::-1].drop_duplicates().reset_index(drop=True)

    scores = {}
    for num in range(1,81):
        f = freq.get(num,0)
        r = 80 - recency[recency == num].index[0] if num in recency.values else 0
        scores[num] = f*0.7 + r*0.3

    df = pd.DataFrame(list(scores.items()), columns=["Number","Score"])
    df = df.sort_values(by="Score", ascending=False)

    return df

# ---------- GENERATOR ----------
def weighted_pick(df, n):
    numbers = df["Number"].tolist()
    weights = df["Score"].tolist()
    return random.choices(numbers, weights=weights, k=n)

def generate_ticket(df):
    while True:
        picks = list(set(weighted_pick(df, 10)))
        if len(picks)==10:
            picks = sorted(picks)
            if max(picks)-min(picks)>=20:
                return picks

def bullseye():
    return random.randint(1,80)

# ---------- UI ----------
uploaded = st.file_uploader("📊 Upload Hot Spot CSV (optional)")

num_tickets = st.slider("Number of Tickets",1,10,3)

if st.button("🎟️ Generate AI Tickets"):
    numbers = load_data(uploaded)
    df = compute_scores(numbers)

    st.session_state.tickets = []

    for _ in range(num_tickets):
        st.session_state.tickets.append((generate_ticket(df), bullseye()))

# ---------- DISPLAY ----------
for i,(ticket,bull) in enumerate(st.session_state.tickets):
    st.markdown('<div class="card">',unsafe_allow_html=True)

    st.markdown(f"**🎟️ Ticket {i+1}**")

    nums_html = "".join([f'<span class="number">{n}</span>' for n in ticket])
    st.markdown(nums_html,unsafe_allow_html=True)

    st.write(f"🎯 Bulls-eye: **{bull}**")

    st.markdown('</div>',unsafe_allow_html=True)

# ---------- CHART ----------
st.subheader("📊 Hot vs Cold Numbers")

if st.button("Show Chart"):
    numbers = load_data(uploaded)
    freq = pd.Series(numbers).value_counts().sort_values(ascending=False).head(15)

    fig, ax = plt.subplots()
    ax.bar(freq.index, freq.values)
    ax.set_title("Top 15 Hot Numbers")

    st.pyplot(fig)

st.caption("⚠️ For entertainment only. No guaranteed wins.")