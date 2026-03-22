import streamlit as st
import time
import random

# =======================
# CONFIG
# =======================

st.set_page_config(
    page_title="DEFI WALLET BACKTEST",
    layout="wide"
)

# =======================
# STYLE TERMINAL
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
    box-shadow: 0 0 10px rgba(0,255,150,0.2);
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

# =======================
# TERMINAL ENGINE
# =======================

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
    type_line("> Chargement modules...")
    type_line("> SAFE / MID / DEGEN engine ready")
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

def detect_actions(current):
    actions = []
    for k,v in current.items():
        if v > 0.4:
            actions.append(f"REDUIRE {k}")
        elif v < 0.05:
            actions.append(f"AUGMENTER {k}")
    return actions

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
        type_line(f"> SAFE : {safe:.1%}")
        type_line(f"> MID : {mid:.1%}")
        type_line(f"> DEGEN : {degen:.1%}")

        # =======================
        # JAUGE ANIMÉE
        # =======================

        gauge_placeholder = st.empty()

        for i in range(0, 101, 5):
            gauge_placeholder.markdown(f"""
            <div class="gauge">
                <div class="safe" style="width:{safe*100 * i/100}%"></div>
                <div class="mid" style="width:{mid*100 * i/100}%"></div>
                <div class="degen" style="width:{degen*100 * i/100}%"></div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.02)

        # =======================
        # SCORE RISQUE
        # =======================

        score = risk_score(degen, mid)

        if score < 30:
            level = "SAFE"
        elif score < 70:
            level = "MODÉRÉ"
        else:
            level = "DEGEN"

        type_line(f"> SCORE RISQUE : {score:.1f}/100")
        type_line(f"> PROFIL : {level}")

        # =======================
        # RECOMMANDATIONS
        # =======================

        actions = detect_actions(current)

        type_line("> Recommandations :")

        if actions:
            for a in actions:
                type_line(f"> {a}")
        else:
            type_line("> Portefeuille équilibré")

# =======================
# DISCLAIMER TERMINAL
# =======================

st.markdown("### ")

disclaimer_placeholder = st.empty()

if "disclaimer_done" not in st.session_state:
    st.session_state.disclaimer_done = False
    st.session_state.disclaimer_content = []

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
        "⚠️ DISCLAIMER",
        "Analyse indicative uniquement",
        "Pas un conseil financier",
        "DYOR"
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
