import streamlit as st
import time
import random
import matplotlib.pyplot as plt
import numpy as np

# =======================
# CONFIG
# =======================

st.set_page_config(
    page_title="DEFI WALLET BACKTEST",
    layout="wide"
)

# =======================
# STYLE
# =======================

st.markdown("""
<style>

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0b0f0c !important;
    color: #00ff88 !important;
    font-family: monospace;
}

.deFi-banner {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 70px;
    z-index: 9999;
    background: linear-gradient(135deg, #0b0f14 0%, #141a2a 40%, #1c2338 100%);
    padding: 15px 20px;
    display: flex;
    align-items: center;
}

.deFi-title-text {
    font-size: 22px;
    font-weight: 700;
    color: #00ff88;
}

[data-testid="stAppViewContainer"] {
    margin-top: 80px;
}

.terminal {
    background-color: #000000;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #00ff88;
    margin-bottom: 15px;
}

.stNumberInput input {
    background-color: #000000 !important;
    color: #00ff88 !important;
    border: 1px solid #00ff88 !important;
}

.stButton button {
    background-color: #000000;
    color: #00ff88;
    border: 1px solid #00ff88;
}

.gauge {
    display: flex;
    height: 25px;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 10px;
}

.safe { background: #00ff88; }
.mid { background: #ffaa00; }
.degen { background: #ff0055; }

</style>

<div class="deFi-banner">
    <div class="deFi-title-text">DEFI WALLET BACKTEST</div>
</div>
""", unsafe_allow_html=True)

# =======================
# STATE
# =======================

if "terminal" not in st.session_state:
    st.session_state.terminal = []

if "initialized" not in st.session_state:
    st.session_state.initialized = False

terminal_placeholder = st.empty()

def render():
    terminal_placeholder.markdown(
        "<div class='terminal'>" +
        "<br>".join(st.session_state.terminal) +
        "</div>",
        unsafe_allow_html=True
    )

def type_line(line):
    current = ""
    st.session_state.terminal.append("")
    for char in line:
        current += char
        st.session_state.terminal[-1] = current
        render()
        time.sleep(random.uniform(0.002, 0.008))

# =======================
# INIT
# =======================

if not st.session_state.initialized:
    type_line("$ wallet-backtest --boot")
    type_line("> IA LP Engine chargé")
    type_line("> SAFE / MID / DEGEN prêt")
    type_line("> En attente input utilisateur...")
    st.session_state.initialized = True

# =======================
# INPUTS
# =======================

st.markdown("### Saisie du portefeuille")

col1, col2 = st.columns(2)

ASSETS = ["BTC", "Lending", "Borrowing", "HODL", "LP"]

portfolio = {}

with col1:
    for asset in ASSETS:
        portfolio[asset] = st.number_input(asset, min_value=0.0, step=100.0)

with col2:
    safe_pct = st.number_input("SAFE (%)", value=40.0)
    mid_pct = st.number_input("MID (%)", value=40.0)
    degen_pct = st.number_input("DEGEN (%)", value=20.0)

run = st.button("▶ Lancer analyse")

# =======================
# LOGIQUE
# =======================

def normalize(p):
    total = sum(p.values())
    return {k: v/total if total > 0 else 0 for k,v in p.items()}

def risk_score(degen, mid):
    return (degen * 2 + mid) * 100

def lp_score(current):
    score = (
        current["LP"] * 40 +
        current["Lending"] * 20 +
        (1 - current["Borrowing"]) * 20 +
        current["BTC"] * 20
    ) * 100
    return score

def detect_actions(current):
    actions = []
    for k,v in current.items():
        if v > 0.4:
            actions.append(f"REDUIRE {k}")
        elif v < 0.05:
            actions.append(f"AUGMENTER {k}")
    return actions

# =======================
# ANALYSE
# =======================

if run:

    total = sum(portfolio.values())

    if total == 0:
        type_line("> ERREUR : portefeuille vide")
    else:
        current = normalize(portfolio)

        total_pct = safe_pct + mid_pct + degen_pct
        safe = safe_pct / total_pct if total_pct else 0
        mid = mid_pct / total_pct if total_pct else 0
        degen = degen_pct / total_pct if total_pct else 0

        type_line("")
        type_line("> Analyse en cours...")

        # JAUGE
        gauge_placeholder = st.empty()
        for i in range(0, 101, 5):
            gauge_placeholder.markdown(f"""
            <div class="gauge">
                <div class="safe" style="width:{safe*100 * i/100}%"></div>
                <div class="mid" style="width:{mid*100 * i/100}%"></div>
                <div class="degen" style="width:{degen*100 * i/100}%"></div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.01)

        # SCORE
        score = risk_score(degen, mid)
        type_line(f"> SCORE RISQUE : {score:.1f}/100")

        # LP IA
        lp = lp_score(current)
        type_line(f"> SCORE IA LP : {lp:.1f}/100")

        # =======================
        # RADAR PETIT FORMAT
        # =======================

        st.markdown("### Radar Allocation")

        labels = list(current.keys())
        values = list(current.values())

        angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
        values += values[:1]
        angles = np.concatenate((angles, [angles[0]]))

        fig = plt.figure(figsize=(3,3))  # 👈 PLUS PETIT
        ax = fig.add_subplot(111, polar=True)

        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.1)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=8)  # 👈 plus lisible petit

        ax.set_yticklabels([])  # 👈 enlève bruit visuel

        st.pyplot(fig)

        # RECO
        actions = detect_actions(current)
        type_line("> Recommandations :")

        if actions:
            for a in actions:
                type_line(f"> {a}")
        else:
            type_line("> Portefeuille équilibré")

# =======================
# DISCLAIMER
# =======================

st.markdown("### ")

if "disclaimer_done" not in st.session_state:
    st.session_state.disclaimer_done = False
    st.session_state.disclaimer_content = []

disclaimer_placeholder = st.empty()

def type_disclaimer(line):
    current = ""
    st.session_state.disclaimer_content.append("")
    for char in line:
        current += char
        st.session_state.disclaimer_content[-1] = current
        disclaimer_placeholder.markdown(
            "<div class='terminal'>" +
            "<br>".join(st.session_state.disclaimer_content) +
            "</div>",
            unsafe_allow_html=True
        )
        time.sleep(random.uniform(0.01, 0.03))

if not st.session_state.disclaimer_done:

    disclaimer_lines = [
        "⚠️ SYSTEM DISCLAIMER LOADED",
        "----------------------------------------",
        "",
        "> Cet outil analyse uniquement la répartition",
        "> de votre portefeuille entre différentes catégories d'actifs.",
        "",
        "> Les résultats sont basés sur des modèles théoriques",
        "> de stratégie (SAFE / MID / DEGEN) et de pondération.",
        "",
        "> Cette analyse ne prend pas en compte :",
        "> - votre situation personnelle",
        "> - les conditions de marché en temps réel",
        "> - les variations de prix ou de liquidité",
        "",
        "> Les allocations proposées sont indicatives",
        "> et peuvent ne pas être adaptées à votre profil.",
        "",
        "> Aucune donnée n'est stockée ou transmise",
        "> toutes les informations restent locales.",
        "",
        "> Cet outil ne constitue PAS :",
        "> - un conseil en investissement",
        "> - une recommandation personnalisée",
        "",
        "> Vous êtes seul responsable de vos décisions.",
        "> Faites vos propres recherches (DYOR).",
        "",
        "----------------------------------------"
    ]

    for line in disclaimer_lines:
        type_disclaimer(line)

    st.session_state.disclaimer_done = True

else:
    disclaimer_placeholder.markdown(
        "<div class='terminal'>" +
        "<br>".join(st.session_state.disclaimer_content) +
        "</div>",
        unsafe_allow_html=True
    )
