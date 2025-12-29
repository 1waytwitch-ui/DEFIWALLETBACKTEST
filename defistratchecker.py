import streamlit as st

# =======================
# CONFIG UI
# =======================

st.set_page_config(
    page_title="DeFi Strategy Analyzer",
    layout="wide"
)

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

st.title("DeFi Strategy Analyzer")
st.caption("Lecture seule • Stratégies SAFE / MID / DEGEN")

left, right = st.columns([1, 2])

# -----------------------
# INPUTS
# -----------------------

with left:
    st.subheader("Adresse EVM")
    address = st.text_input("Adresse", placeholder="0x...")

    st.subheader("Choix de stratégie")

    strategy_choice = st.radio(
        "Profil de risque",
        ["SAFE", "MID", "DEGEN"],
        horizontal=True
    )

    strategy = STRATEGIES[strategy_choice]
    st.info(strategy["description"])

    analyze = st.button("Analyser")

# -----------------------
# RESULTATS
# -----------------------

with right:
    if analyze:
        portfolio = get_portfolio_from_evm(address)

        if portfolio is None:
            st.error("Adresse EVM invalide")
            st.stop()

        current = normalize(portfolio)
        actions = detect_actions(strategy, current)

        st.subheader("Répartition du portefeuille")

        st.write(f"Exposition totale : ${portfolio['total_exposure']:,.0f}")
        st.write(f"Dette (Borrowing) : ${portfolio['borrowing']:,.0f}")

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
