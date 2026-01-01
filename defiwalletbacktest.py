import streamlit as st
import requests
import pandas as pd

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
.stTextInput input,
.stNumberInput input {
    background-color: #f8fafc !important;
    color: #0f172a !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px;
}

/* Buttons */
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

/* Section titles */
.section-banner {
    background: linear-gradient(135deg, #0a0f1f 0%, #1e2761 40%, #4b1c7d 100%);
    padding: 16px 24px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 4px 18px rgba(0,0,0,0.35);
    margin: 35px 0 20px 0;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =======================
# HEADER BANNER
# =======================

st.markdown("""
<div class="deFi-banner" style="
    background: linear-gradient(135deg, #0a0f1f 0%, #1e2761 40%, #4b1c7d 100%);
    padding: 25px 30px;
    border-radius: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 4px 18px rgba(0,0,0,0.45);
    margin-bottom: 25px;">
    <div style="font-size:36px;font-weight:700;color:white;">
        DEFI WALLET BACKTEST
    </div>
</div>
""", unsafe_allow_html=True)

# =======================
# SECTION TITLE FUNCTION
# =======================

def section_title(title):
    st.markdown(f"""
    <div class="section-banner">
        <div class="section-title">{title}</div>
    </div>
    """, unsafe_allow_html=True)

# =======================
# STRATEGIES
# =======================

STRATEGIES = {
    "SAFE": {
        "description": "Préservation du capital",
        "targets": {"hodl": 0.15, "lending": 0.70, "liquidity_pool": 0.10, "borrowing": 0.05},
        "threshold": 0.05
    },
    "MID": {
        "description": "Rendement équilibré",
        "targets": {"hodl": 0.10, "lending": 0.50, "liquidity_pool": 0.25, "borrowing": 0.15},
        "threshold": 0.05
    },
    "DEGEN": {
        "description": "Rendement agressif et risques élevés",
        "targets": {"hodl": 0.05, "lending": 0.25, "liquidity_pool": 0.50, "borrowing": 0.20},
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
# WALLET BACKTEST
# =======================

section_title("Analyse du wallet")

left, right = st.columns([1,2])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Valeurs du wallet")
    portfolio = {}
    for asset in ASSETS:
        portfolio[asset] = st.number_input(asset.upper(), 0.0, step=100.0)
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

# =======================
# BUSINESS PLAN & SCORING
# =======================

section_title("Business plan et scoring du wallet")

st.markdown('<div class="card">', unsafe_allow_html=True)

btc = st.number_input("BTC Treasury", 0.0, step=500.0)
eth = st.number_input("ETH Treasury", 0.0, step=500.0)
stable = st.number_input("Stablecoins", 0.0, step=500.0)
other = st.number_input("Autres actifs", 0.0, step=500.0)

total = btc + eth + stable + other
st.metric("Valeur totale", f"${total:,.0f}")

ltv = st.slider("LTV global", 0, 80, 30)
apr = st.slider("APR moyen estime", 0.0, 30.0, 8.0)

monthly = total * apr / 100 / 12
st.metric("Cashflow mensuel estime", f"${monthly:,.0f}")

score = 0
score += 25 if total >= 100000 else 18 if total >= 50000 else 12 if total >= 20000 else 6
score += 20 if stable/total if total > 0 else 0 >= 0.15 else 10
score += 20 if ltv < 35 else 10 if ltv < 50 else 0

st.metric("Score du wallet", f"{score}/100")

st.markdown('</div>', unsafe_allow_html=True)
