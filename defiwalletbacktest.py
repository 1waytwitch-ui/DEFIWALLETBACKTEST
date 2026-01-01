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

/* Titles overlay */
.section-title {
    background: linear-gradient(135deg, #0a0f1f 0%, #1e2761 40%, #4b1c7d 100%);
    padding: 12px 18px;
    border-radius: 12px;
    color: white;
    font-weight: 700;
    margin-bottom: 15px;
    font-size: 20px;
}

/* Gauge */
.gauge-container {
    width: 100%;
    height: 25px;
    background: #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
    display: flex;
}

.gauge-segment {
    height: 100%;
}

.safe { background-color: #16a34a; }
.mid { background-color: #f97316; }
.degen { background-color: #dc2626; }

</style>
""", unsafe_allow_html=True)

# =======================
# HEADER BANNER
# =======================

st.markdown("""
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

if "show_disclaimer" not in st.session_state:
    st.session_state.show_disclaimer = True

if st.session_state.show_disclaimer:
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
    Analyse purement indicative – pas un conseil financier.
    </div>
    """, unsafe_allow_html=True)

# =======================
# STRATEGIES
# =======================

STRATEGIES = {
    "SAFE": {
        "targets": {"BTC NATIF": 0.50, "lending": 0.70, "borrowing": 0.05, "hodl": 0.15, "liquidity_pool": 0.10},
        "threshold": 0.05
    },
    "MID": {
        "targets": {"BTC NATIF": 0.30, "lending": 0.50, "borrowing": 0.15, "hodl": 0.10, "liquidity_pool": 0.25},
        "threshold": 0.05
    },
    "DEGEN": {
        "targets": {"BTC NATIF": 0.10, "lending": 0.25, "borrowing": 0.20, "hodl": 0.05, "liquidity_pool": 0.50},
        "threshold": 0.10
    }
}

ASSETS = ["BTC NATIF", "lending", "borrowing", "hodl", "liquidity_pool"]

def normalize(portfolio):
    total = sum(portfolio.values())
    return {a: portfolio[a]/total if total > 0 else 0 for a in ASSETS}

def detect_actions(targets, current, threshold):
    actions = []
    for asset in ASSETS:
        delta = current[asset] - targets[asset]
        if delta > threshold:
            actions.append(f"REDUIRE {asset.upper()} de {delta:.1%}")
        elif delta < -threshold:
            actions.append(f"AUGMENTER {asset.upper()} de {-delta:.1%}")
    return actions

# =======================
# UI
# =======================

left, right = st.columns([1,2])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Valeurs du wallet</div>', unsafe_allow_html=True)

    portfolio = {}
    for asset in ASSETS:
        portfolio[asset] = st.number_input(asset.upper(), min_value=0.0, value=0.0, step=100.0)

    st.markdown('<div class="section-title">Répartition SAFE / MID / DEGEN (cible)</div>', unsafe_allow_html=True)
    safe_pct = st.slider("SAFE", 0, 100, 40)
    mid_pct = st.slider("MID", 0, 100, 60)
    degen_pct = st.slider("DEGEN", 0, 100, 0)

    total_pct = safe_pct + mid_pct + degen_pct
    if total_pct > 0:
        safe_pct /= total_pct
        mid_pct /= total_pct
        degen_pct /= total_pct

    analyze = st.button("Analyser")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    if analyze:
        current = normalize(portfolio)

        # CIBLE EXACTE
        composite_targets = {
            asset:
                STRATEGIES["SAFE"]["targets"][asset]*safe_pct +
                STRATEGIES["MID"]["targets"][asset]*mid_pct +
                STRATEGIES["DEGEN"]["targets"][asset]*degen_pct
            for asset in ASSETS
        }

        threshold = (
            STRATEGIES["SAFE"]["threshold"]*safe_pct +
            STRATEGIES["MID"]["threshold"]*mid_pct +
            STRATEGIES["DEGEN"]["threshold"]*degen_pct
        )

        actions = detect_actions(composite_targets, current, threshold)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Répartition du portefeuille</div>', unsafe_allow_html=True)

        total_exposure = sum(portfolio.values())
        st.write(f"Exposition totale : ${total_exposure:,.2f}")
        
        st.table({
            "Catégorie": [a.upper() for a in ASSETS],
            "Actuel": [f"{current[a]:.1%}" for a in ASSETS],
            "Cible (selon répartition choisie)": [f"{composite_targets[a]:.1%}" for a in ASSETS]
        })

        st.markdown('<div class="section-title">Actions recommandées</div>', unsafe_allow_html=True)
        if actions:
            for a in actions:
                st.warning(a)
        else:
            st.success("Portefeuille aligné avec la stratégie cible")

        st.markdown('</div>', unsafe_allow_html=True)
