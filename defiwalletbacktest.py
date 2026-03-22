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
.deFi-banner {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 70px;  /* plus compact */
    z-index: 9999;
    background: linear-gradient(135deg, #0b0f14 0%, #141a2a 40%, #1c2338 100%);
    padding: 15px 20px;  /* réduit */
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(0,255,136,0.3);
    box-shadow: 0px 4px 18px rgba(0,0,0,0.45);
}

/* Titre */
.deFi-title-text {
    font-size: 24px;  /* plus petit */
    font-weight: 700;
    color: #00ff88 !important;  /* style terminal vert */
    font-family: "Courier New", monospace;
}

/* Boutons compact terminal style */
.deFi-buttons a {
    color: #00ff88;
    font-size: 12px;  /* plus petit */
    font-weight: 600;
    text-decoration: none;
    padding: 4px 10px;  /* moins de padding */
    border-radius: 6px;
    margin-left: 6px;
    background-color: #11161d;  /* fond sombre style terminal */
    border: 1px solid #00ff88;
    font-family: "Courier New", monospace;
    transition: 0.2s all;
}

.deFi-buttons a:hover {
    background-color: #0b0f14;
    box-shadow: 0 0 8px #00ff88;
}

/* Décaler le reste du contenu */
[data-testid="stAppViewContainer"] {
    margin-top: 70px;  /* correspond à la hauteur du header */
}
</style>

<div class="deFi-banner">
    <div class="deFi-title-text">LP STRATÉGIES BACKTEST ENGINE</div>
    <div class="deFi-buttons">
        <a href="https://defi.krystal.app/referral?r=3JwR8YRQCRJT" target="_blank">Krystal</a>
        <a href="https://plusvalueimposable.streamlit.app/" target="_blank">Plus-value</a>
        <a href="https://backtestenginelp.streamlit.app/" target="_blank">BACKTEST ENGINE LP</a>
        <a href="https://t.me/Pigeonchanceux" target="_blank">
            <img src="https://t.me/i/userpic/320/Pigeonchanceux.jpg" style="width:20px;height:20px;border-radius:50%; vertical-align: middle; margin-right:4px;">Telegram
        </a>
        <a href="https://shorturl.at/X3sYt" target="_blank">Formation</a>
    </div>
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
    type_line("> WALLET Engine chargé")
    type_line("> SAFE / MID / DEGEN prêt")
    type_line("> En attente des entrées utilisateur...")
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
        # RADAR
        # =======================

        st.markdown("### Radar Allocation")

        labels = list(current.keys())
        values = list(current.values())

        angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
        values += values[:1]
        angles = np.concatenate((angles, [angles[0]]))

        fig = plt.figure(figsize=(2.2, 2.2))
        ax = fig.add_subplot(111, polar=True)

        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.1)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=7)

        ax.set_yticklabels([])

        # Centrer le radar
        col_left, col_mid, col_right = st.columns([1,2,1])
        with col_mid:
            st.pyplot(fig, use_container_width=False)

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
