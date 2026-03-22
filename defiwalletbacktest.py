import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# =======================
# CONFIG
# =======================
st.set_page_config(page_title="LP BACKTEST ENGINE", layout="wide")

# =======================
# STYLE TERMINAL DARK
# =======================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0b0f0c !important;
    color: #00ff88 !important;
}

.card {
    background-color: #000;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #00ff88;
    margin-bottom: 20px;
    box-shadow: 0 0 15px rgba(0,255,150,0.1);
}

.title {
    font-family: monospace;
    font-size: 20px;
    margin-bottom: 10px;
}

.metric {
    font-size: 18px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🧪 LP BACKTEST ENGINE")

# =======================
# INPUTS
# =======================
col1, col2 = st.columns(2)

with col1:
    apr = st.number_input("APR (%)", value=20.0)
    il = st.number_input("Impermanent Loss (%)", value=5.0)
    fees = st.number_input("Fees (%)", value=10.0)

with col2:
    volatility = st.slider("Volatilité (%)", 0, 100, 50)
    duration = st.slider("Durée (jours)", 1, 365, 30)

run = st.button("▶ Lancer analyse")

# =======================
# ANALYSE
# =======================
if run:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Score IA LP
    score = (
        apr * 0.4 +
        fees * 0.3 -
        il * 0.2 -
        volatility * 0.1
    )

    score = max(0, min(100, score))

    st.markdown("### 🤖 Score IA LP")
    st.progress(int(score))

    # Interprétation
    if score > 70:
        st.success("🔥 Setup très performant (alpha)")
        level = "SAFE"
    elif score > 40:
        st.warning("⚖️ Setup équilibré")
        level = "MID"
    else:
        st.error("⚠️ Setup risqué")
        level = "DEGEN"

    st.markdown(f"**Niveau détecté : {level}**")

    # =======================
    # RADAR CHART (PLUS PETIT)
    # =======================
    labels = ["APR", "Fees", "IL", "Volatilité"]
    values = [apr, fees, il, volatility]

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    values = np.concatenate((values, [values[0]]))
    angles = np.concatenate((angles, [angles[0]]))

    fig = plt.figure(figsize=(3,3))  # 👈 plus petit
    ax = fig.add_subplot(111, polar=True)

    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    st.markdown("### 📊 Radar allocation")
    st.pyplot(fig)

    # =======================
    # RECOMMANDATIONS IA
    # =======================
    st.markdown("### 🧠 Recommandations IA")

    if il > 10:
        st.warning("Réduire l'exposition → IL trop élevée")

    if volatility > 70:
        st.warning("Marché très volatile → resserrer range LP")

    if apr < 15:
        st.info("APR faible → optimiser pool ou incentives")

    if fees > apr:
        st.success("Bonne capture de fees 👍")

    if score > 70:
        st.success("Stratégie optimisée 🔥")

    st.markdown('</div>', unsafe_allow_html=True)

# =======================
# DISCLAIMER
# =======================
st.markdown("""
<div class="card">
⚠️ DISCLAIMER  
Outil informatif uniquement  
Aucun conseil financier  
DYOR
</div>
""", unsafe_allow_html=True)
