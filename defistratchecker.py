import streamlit as st
import requests

# =======================
# CONFIG
# =======================

st.set_page_config(
    page_title="DEFI WALLET BACKTEST",
    layout="wide"
)

# =======================
# GLOBAL STYLES
# =======================

st.markdown("""
<style>

/* ----- Global ----- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #ffffff !important;
    color: #0f172a !important;
}

h1, h2, h3, h4 {
    color: #0f172a !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input {
    background-color: #f8fafc !important;
    color: #0f172a !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px;
}

/* Buttons (CTA GOLD) */
.stButton button {
    background: linear-gradient(135deg, #facc15, #f59e0b) !important;
    color: #000000 !important;
    font-weight: 700;
    border-radius: 14px;
    padding: 0.6em 1.6em;
    border: none;
    box-shadow: 0px 6px 20px rgba(250,204,21,0.35);
}

/* Cards */
.card {
    background: #ffffff;
    border-radius: 18px;
    padding: 26px;
    box-shadow: 0px 10px 30px rgba(15, 23, 42, 0.12);
    margin-bottom: 20px;
    border: 1px solid #e5e7eb;
}

/* Tables */
table {
    background-color: #ffffff !important;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
}
thead tr th {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
}
tbody tr td {
    color: #0f172a !important;
}

</style>
""", unsafe_allow_html=True)

# =======================
# HEADER BANNER
# =======================

st.markdown("""
<style>
.deFi-banner {
    background: linear-gradient(135deg, #0a0f1f 0%, #1e2761 40%, #4b1c7d 100%);
    padding: 25px 30px;
    border-radius: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 4px 18px rgba(0,0,0,0.45);
    margin-bottom: 25px;
}
.deFi-title-text {
    font-size: 36px;
    font-weight: 700;
    color: white !important;
}
.deFi-buttons a {
    color: white;
    font-size: 15px;
    font-weight: 600;
    text-decoration: none;
    padding: 8px 14px;
    border-radius: 12px;
    margin-left: 8px;
}
.krystal-btn { background-color: #06b6d4; }
.plusvalue-btn { background-color: #10b981; }
.telegram-btn { background-color: #6c5ce7; }
.formation-btn { background-color: #f59e0b; }
</style>

<div class="deFi-banner">
    <div class="deFi-title-text">DEFI WALLET BACKTEST</div>
    <div class="deFi-buttons">
        <a href="https://defi.krystal.app/referral?r=3JwR8YRQCRJT" target="_blank" class="krystal-btn">Krystal</a>
        <a href="https://plusvalueimposable.streamlit.app/" target="_blank" class="plusvalue-btn">Plus-value</a>
        <a href="https://t.me/Pigeonchanceux" target="_blank" class="telegram-btn">Telegram</a>
        <a href="https://shorturl.at/X3sYt" target="_blank" class="formation-btn">Formation</a>
    </div>
</div>
""", unsafe_allow_html=True)

# =======================
# DISCLAIMER
# =======================

st.markdown("""
<div style="
    background-color: #fff3cd;
    border-left: 6px solid #ffca2c;
    padding: 15px 20px;
    border-radius: 8px;
    color: #000;
    margin-bottom: 25px;
    font-size: 15px;
">
<b>⚠️ DISCLAIMER IMPORTANT</b><br><br>
L’analyse du wallet est <b>purement statistique et indicative</b>, réalisée en fonction du
<b>profil de risque sélectionné (SAFE / MID / DEGEN)</b>.<br>
Les montants saisis restent <b>uniquement en local dans le navigateur</b> et ne sont jamais stockés ou transmis à un serveur.<br>
Ces informations <b>ne constituent pas un conseil financier</b>.
</div>
""", unsafe_allow_html=True)

# =======================
# STRATEGIES
# =======================

STRATEGIES = {
    "SAFE": {
        "description": "Préservation du capital",
        "targets": {"hodl": 0.10, "lending": 0.60, "liquidity_pool": 0.10, "borrowing": 0.20},
        "threshold": 0.05
    },
    "MID": {
        "description": "Rendement équilibré",
        "targets": {"hodl": 0.05, "lending": 0.50, "liquidity_pool": 0.20, "borrowing": 0.25},
        "threshold": 0.05
    },
    "DEGEN": {
        "description": "Rendement agressif et risque très élevès",
        "targets": {"hodl": 0.10, "lending": 0.30, "liquidity_pool": 0.40, "borrowing": 0.20},
        "threshold": 0.10
    }
}

ASSETS = ["hodl", "lending", "liquidity_pool", "borrowing"]

def normalize(portfolio):
    total = sum(portfolio[a] for a in ASSETS)
    return {a: portfolio[a]/total if total > 0 else 0 for a in ASSETS}

def detect_actions(strategy, current):
    actions = []
    for asset in ASSETS:
        delta = current[asset] - strategy["targets"][asset]
        if delta > strategy["threshold"]:
            actions.append(f"REDUIRE {asset.upper()} de {delta:.1%}")
        elif delta < -strategy["threshold"]:
            actions.append(f"AUGMENTER {asset.upper()} de {-delta:.1%}")
    return actions

# =======================
# UI MANUEL
# =======================

left, right = st.columns([1,2])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Saisie manuelle des montants du wallet ($)")
    portfolio = {}
    for asset in ASSETS:
        portfolio[asset] = st.number_input(asset.upper(), min_value=0.0, value=0.0, step=100.0, format="%.2f")
    strategy_choice = st.radio("Profil de risque", list(STRATEGIES.keys()), horizontal=True)
    strategy = STRATEGIES[strategy_choice]
    st.info(strategy["description"])
    analyze = st.button("Analyser")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    if analyze:
        current = normalize(portfolio)
        actions = detect_actions(strategy, current)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Répartition du portefeuille")
        total_exposure = sum(portfolio[a] for a in ASSETS)
        st.write(f"Exposition totale : ${total_exposure:,.2f}")
        st.table({
            "Catégorie": [a.upper() for a in ASSETS],
            "Actuel": [f"{current[a]:.1%}" for a in ASSETS],
            "Cible": [f"{strategy['targets'][a]:.1%}" for a in ASSETS]
        })

        st.subheader("Actions recommandées")
        if actions:
            for a in actions:
                st.warning(a)
        else:
            st.success("Portefeuille aligné avec la stratégie")
        st.markdown('</div>', unsafe_allow_html=True)
