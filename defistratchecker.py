import streamlit as st

# =======================
# CONFIG UI (WIDESCREEN)
# =======================

st.set_page_config(
    page_title="DeFi Strategy Checker",
    layout="wide"
)

# =======================
# STRATEGIE PAR DEFAUT
# =======================

DEFAULT_STRATEGY = {
    "cash": 0.20,
    "lending": 0.50,
    "liquidity_pool": 0.30,
    "rebalance_threshold": 0.05
}

# =======================
# MOCK LECTURE EVM
# =======================

def get_portfolio_from_evm(address: str):
    """
    Mock simple par adresse.
    Remplaçable par DeBank / Zapper.
    """
    if not address or not address.startswith("0x"):
        return None

    # simulation différente selon l'adresse
    seed = int(address[-4:], 16) % 100

    cash = 1000 + seed * 10
    lending = 4000 + seed * 20
    lp = 3000 + seed * 15

    total = cash + lending + lp

    return {
        "cash": cash,
        "lending": lending,
        "liquidity_pool": lp,
        "total_usd": total
    }

# =======================
# LOGIQUE METIER
# =======================

def normalize_portfolio(portfolio):
    total = portfolio["total_usd"]
    return {
        "cash": portfolio["cash"] / total,
        "lending": portfolio["lending"] / total,
        "liquidity_pool": portfolio["liquidity_pool"] / total
    }

def detect_actions(strategy, current):
    actions = []
    threshold = strategy["rebalance_threshold"]

    for asset in ["cash", "lending", "liquidity_pool"]:
        target = strategy[asset]
        actual = current.get(asset, 0)
        delta = actual - target

        if delta > threshold:
            actions.append(f"REDUIRE {asset.upper()} de {delta:.1%}")
        elif delta < -threshold:
            actions.append(f"AUGMENTER {asset.upper()} de {-delta:.1%}")

    return actions

def aggregate_portfolios(portfolios):
    aggregated = {
        "cash": 0,
        "lending": 0,
        "liquidity_pool": 0,
        "total_usd": 0
    }

    for p in portfolios:
        for k in aggregated:
            aggregated[k] += p[k]

    return aggregated

# =======================
# UI
# =======================

st.title("DeFi Strategy Checker")
st.caption("Lecture seule • Analyse stratégie vs portefeuilles EVM")

# -----------------------
# LAYOUT PRINCIPAL
# -----------------------

left, right = st.columns([1, 2])

# =======================
# COLONNE GAUCHE — INPUTS
# =======================

with left:
    st.subheader("1. Adresses EVM (Bundle)")

    addresses_raw = st.text_area(
        "Une adresse par ligne",
        height=160,
        placeholder="0x...\n0x...\n0x..."
    )

    addresses = [
        a.strip() for a in addresses_raw.splitlines()
        if a.strip()
    ]

    st.subheader("2. Stratégie cible")

    cash_pct = st.slider("Cash / Stablecoins", 0.0, 1.0, DEFAULT_STRATEGY["cash"], 0.05)
    lending_pct = st.slider("Lending", 0.0, 1.0, DEFAULT_STRATEGY["lending"], 0.05)
    lp_pct = st.slider("Liquidity Pool", 0.0, 1.0, DEFAULT_STRATEGY["liquidity_pool"], 0.05)

    threshold = st.slider(
        "Seuil de rééquilibrage",
        0.01,
        0.20,
        DEFAULT_STRATEGY["rebalance_threshold"],
        0.01
    )

    total_alloc = cash_pct + lending_pct + lp_pct

    if abs(total_alloc - 1.0) > 0.001:
        st.error("La somme des allocations doit être égale à 100 %")
        st.stop()

    strategy = {
        "cash": cash_pct,
        "lending": lending_pct,
        "liquidity_pool": lp_pct,
        "rebalance_threshold": threshold
    }

    analyze = st.button("Analyser le bundle")

# =======================
# COLONNE DROITE — RESULTATS
# =======================

with right:
    if analyze:
        if not addresses:
            st.error("Aucune adresse fournie")
            st.stop()

        # ---- Lecture par adresse ----
        portfolios = []
        per_address_results = []

        for addr in addresses:
            p = get_portfolio_from_evm(addr)
            if p is None:
                continue

            portfolios.append(p)

            pct = normalize_portfolio(p)
            actions = detect_actions(strategy, pct)

            per_address_results.append({
                "address": addr,
                "portfolio": p,
                "pct": pct,
                "actions": actions
            })

        if not portfolios:
            st.error("Aucune adresse valide")
            st.stop()

        # ---- Agrégation bundle ----
        bundle = aggregate_portfolios(portfolios)
        bundle_pct = normalize_portfolio(bundle)
        bundle_actions = detect_actions(strategy, bundle_pct)

        # =======================
        # RESULTATS BUNDLE
        # =======================

        st.subheader("Résultat global (Bundle)")

        st.write(f"Nombre d’adresses : {len(per_address_results)}")
        st.write(f"Valeur totale : ${bundle['total_usd']:,.0f}")

        st.table({
            "Actif": ["Cash", "Lending", "Liquidity Pool"],
            "Actuel": [
                f"{bundle_pct['cash']:.1%}",
                f"{bundle_pct['lending']:.1%}",
                f"{bundle_pct['liquidity_pool']:.1%}",
            ],
            "Cible": [
                f"{strategy['cash']:.1%}",
                f"{strategy['lending']:.1%}",
                f"{strategy['liquidity_pool']:.1%}",
            ],
        })

        st.markdown("### Actions recommandées (Bundle)")

        if not bundle_actions:
            st.success("Le bundle est aligné avec la stratégie")
        else:
            for a in bundle_actions:
                st.warning(a)

        st.divider()

        # =======================
        # RESULTATS PAR ADRESSE
        # =======================

        st.subheader("Actions par adresse")

        for r in per_address_results:
            with st.expander(r["address"]):
                st.write(f"Valeur totale : ${r['portfolio']['total_usd']:,.0f}")

                st.table({
                    "Actif": ["Cash", "Lending", "Liquidity Pool"],
                    "Actuel": [
                        f"{r['pct']['cash']:.1%}",
                        f"{r['pct']['lending']:.1%}",
                        f"{r['pct']['liquidity_pool']:.1%}",
                    ],
                    "Cible": [
                        f"{strategy['cash']:.1%}",
                        f"{strategy['lending']:.1%}",
                        f"{strategy['liquidity_pool']:.1%}",
                    ],
                })

                if not r["actions"]:
                    st.success("Adresse alignée avec la stratégie")
                else:
                    for act in r["actions"]:
                        st.warning(act)

        st.caption("Aucune transaction n’est exécutée • Lecture seule")
