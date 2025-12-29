import streamlit as st

# =======================
# CONFIG UI
# =======================

st.set_page_config(
    page_title="DeFi wallet backtest",
    layout="wide"
)

# =======================
# CUSTOM CSS (UI ONLY)
# =======================

st.markdown("""
<style>

/* ----- Global ----- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0b1026, #2b1464);
    color: #ffffff;
}

/* ----- Titles ----- */
h1, h2, h3 {
    color: #ffffff;
    font-weight: 700;
}

h1 {
    letter-spacing: 1px;
}

/* ----- Cards ----- */
.card {
    background: linear-gradient(135deg, #10183d, #3a1c71);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.35);
    margin-bottom: 20px;
}

/* ----- Inputs ----- */
.stTextInput input {
    background-color: #0f1533;
    color: white;
    border-radius: 10px;
    border: 1px solid #3c2c77;
}

/* ----- Radio buttons ----- */
div[role="radiogroup"] {
    background: #0f1533;
    padding: 12px;
    border-radius: 14px;
    border: 1px solid #3c2c77;
}

/* ----- Buttons ----- */
.stButton button {
    background: linear-gradient(135deg, #facc15, #f59e0b);
    color: #000000;
    font-weight: 700;
    border-radius: 14px;
    padding: 0.6em 1.6em;
    border: none;
    box-shadow: 0px 6px 20px rgba(250,204,21,0.35);
    transition: all 0.2s ease;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 10px 30px rgba(250,204,21,0.5);
}

/* ----- Info / Success / Warning ----- */
.stAlert {
    border-radius: 14px;
}

.stAlert[data-baseweb="notification"] {
    background-color: #10183d;
}

/* ----- Table ----- */
table {
    background-color: #0f1533 !important;
    border-radius: 14px;
    overflow: hidden;
}

thead tr th {
    background-color: #1e2a6d !important;
    color: #ffffff !important;
}

tbody tr td {
    color: #ffffff !important;
}

/* ----- Footer ----- */
.footer {
    text-align: center;
    opacity: 0.6;
    margin-top: 30px;
    font-size: 0.85rem;
}

</style>
""", unsafe_allow_html=True)

# =======================
# STRATEGIES
# =======================

STRATEGIES = {
    "SAFE": {
        "description": "Préservation du capital, pas de levier",
        "targets": {
            "hodl": 0.45,
            "lending": 0.45,
            "liquidity_pool": 0.10,
            "borrowing": 0.00
        },
        "threshold": 0.05
    },
    "MID": {
        "description": "Rendement équilibré, levier modéré",
        "targets": {
            "hodl": 0.20,
            "lending": 0.45,
            "liquidity_pool": 0.25,
            "borrowing": 0.10
        },
        "threshold": 0.05
    },
    "DEGEN": {
        "description": "Rendement agressif, levier élevé",
        "targets": {
            "hodl": 0.05,
            "lending": 0.35,
            "liquidity_pool": 0.40,
            "borrowing": 0.20
        },
        "threshold": 0.10
    }
}

ASSETS = ["hodl", "lending", "liquidity_pool", "borrowing"]

# =======================
# MOCK EVM
# =======================

def get_portfolio_from_evm(address):
    if not address or not address.startswith("0x"):
        return None

    seed = int(address[-4:], 16) % 100

    hodl = 2500 + seed * 10
    lending = 3500 + seed * 15
    lp = 2500 + seed * 10
    borrowing = 1000 + seed * 5

    exposure = hodl + lending + lp

    return {
        "hodl": hodl,
        "lending": lending,
        "liquidity_pool": lp,
        "borrowing": borrowing,
        "total_exposure": exposure
    }

# =======================
# LOGIQUE
# =======================

def normalize(portfolio):
    total = portfolio["total_exposure"]
    return {
        "hodl": portfolio["hodl"] / total,
        "lending": portfolio["lending"] / total,
        "liquidity_pool": portfolio["liquidity_pool"] / total,
        "borrowing": portfolio["borrowing"] / total
    }

def detect_actions(strategy, current):
    actions = []
    for asset in ASSETS:
        target = strategy["targets"][asset]
        actual = current.get(asset, 0)
        delta = actual - target

        if delta > strategy["threshold"]:
            actions.append(f"REDUIRE {asset.upper()} de {delta:.1%}")
        elif delta < -strategy["threshold"]:
            actions.append(f"AUGMENTER {asset.upper()} de {-delta:.1%}")

    return actions

# =======================
# UI
# =======================

st.title("LP STRATEGIES • DeFi Strategy Analyzer")
st.caption("Lecture seule • SAFE / MID / DEGEN")

left, right = st.columns([1, 2])

# -----------------------
# INPUTS
# -----------------------

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("Adresse EVM")
    address = st.text_input("Adresse", placeholder="0x...")

    st.subheader("Stratégie")
    strategy_choice = st.radio(
        "Profil de risque",
        ["SAFE", "MID", "DEGEN"],
        horizontal=True
    )

    strategy = STRATEGIES[strategy_choice]
    st.info(strategy["description"])

    analyze = st.button("Analyser")

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# RESULTATS
# -----------------------

with right:
    if analyze:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        portfolio = get_portfolio_from_evm(address)

        if portfolio is None:
            st.error("Adresse EVM invalide")
            st.stop()

        current = normalize(portfolio)
        actions = detect_actions(strategy, current)

        st.subheader("Répartition du portefeuille")

        st.write(f"**Exposition totale :** ${portfolio['total_exposure']:,.0f}")
        st.write(f"**Dette (Borrowing) :** ${portfolio['borrowing']:,.0f}")

        st.table({
            "Catégorie": ["HODL", "LENDING", "LIQUIDITY POOL", "BORROWING"],
            "Actuel": [
                f"{current['hodl']:.1%}",
                f"{current['lending']:.1%}",
                f"{current['liquidity_pool']:.1%}",
                f"{current['borrowing']:.1%}",
            ],
            "Cible": [
                f"{strategy['targets']['hodl']:.1%}",
                f"{strategy['targets']['lending']:.1%}",
                f"{strategy['targets']['liquidity_pool']:.1%}",
                f"{strategy['targets']['borrowing']:.1%}",
            ],
        })

        st.subheader("Actions recommandées")

        if not actions:
            st.success("Portefeuille aligné avec la stratégie")
        else:
            for a in actions:
                st.warning(a)

        st.caption("Aucune transaction exécutée • Lecture seule")

        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">© DeFi Analyzer • Backtest UI</div>', unsafe_allow_html=True)
