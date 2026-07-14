import streamlit as st
import time
import random
import numpy as np
import plotly.graph_objects as go

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="DeFi Wallet Backtest V2",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== GLOBAL THEME =====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-main:     #080c10;
    --bg-panel:    #0d1318;
    --bg-card:     #111820;
    --accent:      #00d4aa;
    --accent-dim:  rgba(0,212,170,0.10);
    --accent-mid:  rgba(0,212,170,0.30);
    --accent-2:    #0ea5e9;
    --accent-3:    #f59e0b;
    --accent-red:  #ef4444;
    --accent-green:#22c55e;
    --border:      rgba(0,212,170,0.18);
    --border-soft: rgba(255,255,255,0.06);
    --text-hi:     #f0f4f8;
    --text-mid:    #8899aa;
    --text-lo:     #445566;
    --font-mono:   'JetBrains Mono','Courier New',monospace;
    --font-ui:     'Inter',sans-serif;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer { visibility: hidden !important; }
[data-testid="stSidebar"]       { display: none !important; }
[data-testid="collapsedControl"]{ display: none !important; }
[data-testid="stToolbar"]       { display: none !important; }
[data-testid="stHeader"]        { display: none !important; }
.block-container { padding-top: 72px !important; padding-bottom: 40px !important; }

/* ── BASE ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-main) !important;
    color: var(--text-hi);
    font-family: var(--font-ui);
}

/* ── NAV BAR ── */
.nav-bar {
    position: fixed; top:0; left:0; width:100%; height:58px;
    z-index:99999;
    background: rgba(6,10,14,0.97);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border);
    display:flex; align-items:center; justify-content:space-between;
    padding: 0 28px; box-sizing:border-box;
}
.nav-brand { display:flex; align-items:center; gap:10px; }
.nav-glyph {
    width:28px; height:28px; border:2px solid var(--accent); border-radius:6px;
    display:flex; align-items:center; justify-content:center;
    font-family:var(--font-mono); font-size:14px; color:var(--accent); font-weight:700;
}
.nav-title  { font-family:var(--font-mono); font-size:13px; font-weight:600; color:var(--text-hi); letter-spacing:2px; text-transform:uppercase; }
.nav-subtitle { font-family:var(--font-mono); font-size:10px; color:var(--text-mid); letter-spacing:1px; }
.status-dot { width:7px; height:7px; border-radius:50%; background:var(--accent); display:inline-block; margin-right:5px; animation:pulse-dot 2s infinite; }
@keyframes pulse-dot { 0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(0,212,170,0.4);} 50%{opacity:.7;box-shadow:0 0 0 4px rgba(0,212,170,0);} }
.nav-links { display:flex; align-items:center; gap:6px; }
.nav-links a {
    font-family:var(--font-mono); font-size:11px; font-weight:500;
    color:var(--text-mid); text-decoration:none;
    padding:5px 12px; border:1px solid transparent; border-radius:5px;
    transition:all 0.2s; letter-spacing:.5px;
}
.nav-links a:hover { color:var(--accent); border-color:var(--border); background:var(--accent-dim); }

/* ── SECTION HEADERS ── */
.sec-head { display:flex; align-items:center; gap:10px; margin:28px 0 14px 0; padding-bottom:8px; border-bottom:1px solid var(--border); }
.sec-head-icon { width:24px; height:24px; background:var(--accent-dim); border:1px solid var(--border); border-radius:5px; display:flex; align-items:center; justify-content:center; font-size:11px; color:var(--accent); }
.sec-head-label { font-family:var(--font-mono); font-size:11px; font-weight:600; color:var(--accent); letter-spacing:2px; text-transform:uppercase; }

/* ── METRIC CARDS ── */
.m-card {
    background:var(--bg-card); border:1px solid var(--border-soft);
    border-radius:10px; padding:16px 18px; margin:8px 0;
    transition:border-color .2s,box-shadow .2s; position:relative; overflow:hidden;
}
.m-card::before { content:''; position:absolute; top:0;left:0;right:0; height:2px; background:linear-gradient(90deg,var(--accent),transparent); opacity:0; transition:opacity .2s; }
.m-card:hover { border-color:var(--border); box-shadow:0 0 18px rgba(0,212,170,.07); }
.m-card:hover::before { opacity:1; }
.m-card-wide { background:var(--bg-card); border:1px solid var(--border-soft); border-radius:10px; padding:18px 20px; margin:8px 0; }
.m-card-highlight { background:var(--accent-dim); border:1px solid var(--border); border-radius:10px; padding:18px 20px; margin:8px 0; }
.m-label { font-family:var(--font-mono); font-size:10px; color:var(--text-mid); letter-spacing:1.5px; text-transform:uppercase; margin-bottom:8px; }
.m-value { font-family:var(--font-mono); font-size:20px; font-weight:600; color:var(--accent); line-height:1.1; }
.m-value-sm { font-family:var(--font-mono); font-size:14px; font-weight:500; color:var(--accent); line-height:1.3; }

/* ── GAUGE BAR ── */
.gauge-wrap { margin:12px 0; }
.gauge-bar { display:flex; height:22px; border-radius:8px; overflow:hidden; width:100%; }
.gauge-safe  { background:linear-gradient(90deg,#22c55e,#16a34a); transition:width .6s ease; }
.gauge-mid   { background:linear-gradient(90deg,#f59e0b,#d97706); transition:width .6s ease; }
.gauge-degen { background:linear-gradient(90deg,#ef4444,#dc2626); transition:width .6s ease; }
.gauge-legend { display:flex; gap:16px; margin-top:6px; font-family:'JetBrains Mono',monospace; font-size:11px; }
.leg-dot { width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:4px; }

/* ── RISK BADGE ── */
.risk-badge {
    display:inline-flex; align-items:center; gap:8px;
    padding:10px 18px; border-radius:8px;
    font-family:'JetBrains Mono',monospace; font-size:14px; font-weight:600;
    letter-spacing:1px;
}

/* ── TERMINAL ── */
.term-block {
    background:#050809; border:1px solid var(--border); border-radius:10px;
    padding:18px; font-family:var(--font-mono); font-size:12px;
    line-height:1.65; color:var(--accent); max-height:380px; overflow-y:auto;
}
.term-block::-webkit-scrollbar{width:4px;}
.term-block::-webkit-scrollbar-thumb{background:var(--accent-mid);border-radius:2px;}
.term-cursor { display:inline-block; width:7px; height:13px; background:var(--accent); margin-left:2px; vertical-align:middle; animation:blink-cur 1s step-end infinite; }
@keyframes blink-cur{0%,100%{opacity:1;}50%{opacity:0;}}

/* ── DISC BAR ── */
.disc-bar { background:rgba(0,212,170,.05); border:1px solid var(--border); border-radius:8px; padding:10px 16px; font-family:var(--font-mono); font-size:11px; color:var(--text-mid); margin:10px 0 18px 0; }
.disc-bar span { color:var(--accent); }

/* ── INPUTS ── */
div[data-baseweb="input"] input, .stNumberInput input, .stTextInput input {
    background:var(--bg-panel) !important; color:var(--text-hi) !important;
    border:1px solid var(--border-soft) !important; border-radius:7px !important;
    font-family:var(--font-mono) !important; font-size:13px !important;
}
div[data-baseweb="input"] input:focus, .stNumberInput input:focus {
    border-color:var(--accent-mid) !important; box-shadow:0 0 0 2px var(--accent-dim) !important;
}
label, .stLabel { font-family:var(--font-ui) !important; font-size:12px !important; color:var(--text-mid) !important; }

/* ── BUTTONS ── */
.stButton > button {
    background:var(--accent) !important; color:#030a07 !important;
    border:none !important; border-radius:8px !important;
    font-family:var(--font-mono) !important; font-size:12px !important;
    font-weight:700 !important; letter-spacing:1px !important;
    padding:10px 20px !important; text-transform:uppercase !important;
    transition:all .2s !important;
}
.stButton > button:hover { transform:translateY(-1px) !important; box-shadow:0 6px 20px rgba(0,212,170,.3) !important; }

/* ── DIVIDER ── */
.v2-divider { height:1px; background:linear-gradient(90deg,var(--border),transparent); margin:28px 0; }
::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}

/* ── RECO CARD ── */
.reco-card {
    background:var(--bg-card); border:1px solid var(--border-soft); border-radius:10px;
    padding:14px 18px; margin:6px 0; display:flex; align-items:center; gap:12px;
    font-family:'JetBrains Mono',monospace; font-size:12px;
}
.reco-icon { font-size:16px; }
.reco-text { color:var(--text-hi); }
.reco-sub  { color:var(--text-mid); font-size:11px; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

# ── NAV BAR ──
st.markdown("""
<div class="nav-bar">
    <div class="nav-brand">
        <div class="nav-glyph">◈</div>
        <div>
            <div class="nav-title">DeFi Wallet Backtest</div>
            <div class="nav-subtitle"><span class="status-dot"></span>ALLOCATION · RISQUE · SCORING · RADAR</div>
        </div>
    </div>
    <div class="nav-links">
        <a href="https://defi.krystal.app/referral?r=3JwR8YRQCRJT" target="_blank">Krystal</a>
        <a href="https://plusvalueimposable.streamlit.app/" target="_blank">Plus-value</a>
        <a href="https://backtestenginelp.streamlit.app/" target="_blank">Backtest Engine LP</a>
        <a href="https://t.me/Pigeonchanceux" target="_blank">Telegram</a>
        <a href="https://shorturl.at/X3sYt" target="_blank">Formation</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── HELPERS ──
# ══════════════════════════════════════════════════════════
def sec(icon, label):
    st.markdown(f"""<div class="sec-head"><div class="sec-head-icon">{icon}</div><div class="sec-head-label">{label}</div></div>""", unsafe_allow_html=True)

def card(label, value, color="var(--accent)", wide=False):
    cls = "m-card-wide" if wide else "m-card"
    st.markdown(f"""<div class="{cls}"><div class="m-label">{label}</div><div class="m-value" style="color:{color};">{value}</div></div>""", unsafe_allow_html=True)

def render_term(placeholder, content, div_id="term-boot"):
    html = "<br>".join(content)
    placeholder.markdown(
        f"<div id='{div_id}' class='term-block'>" +
        "<br>".join(content) +
        "<span class='term-cursor'></span></div>"
        f"<script>var t=document.getElementById('{div_id}');if(t)t.scrollTop=t.scrollHeight;</script>",
        unsafe_allow_html=True
    )

def type_line_to(content_list, placeholder, line, div_id="term-boot"):
    current = ""
    content_list.append("")
    for c in line:
        current += c
        content_list[-1] = current
        render_term(placeholder, content_list, div_id)
        time.sleep(0.003)

def add_term_line(content_list, placeholder, line, div_id="term-boot"):
    type_line_to(content_list, placeholder, line, div_id)

# ── LOGIC ──
def normalize(p):
    total = sum(p.values())
    return {k: v / total if total > 0 else 0 for k, v in p.items()}

def risk_score(degen, mid):
    return (degen * 2 + mid) * 100

def lp_score(current):
    return (
        current.get("LP", 0) * 40 +
        current.get("Lending", 0) * 20 +
        (1 - current.get("Borrowing", 0)) * 20 +
        current.get("BTC Natif", 0) * 20
    ) * 100

def detect_actions(current, total_usd):
    actions = []
    thresholds = {
        "BTC Natif":  {"high": 0.50, "low": 0.05, "reco_high": "Envisager de diversifier une partie en LP ou Lending", "reco_low": "BTC sous-représenté — socle de sécurité recommandé"},
        "Lending":    {"high": 0.45, "low": 0.03, "reco_high": "Exposition Lending élevée — vérifiez les taux et protocoles", "reco_low": "Lending faible — opportunité de rendement passif disponible"},
        "Borrowing":  {"high": 0.30, "low": 0.00, "reco_high": "Exposition dette élevée — risque de liquidation accru", "reco_low": None},
        "HODL":       {"high": 0.55, "low": 0.05, "reco_high": "HODL dominant — capital potentiellement sous-productif", "reco_low": "Position HODL faible — envisager un socle de réserve"},
        "LP":         {"high": 0.60, "low": 0.03, "reco_high": "LP très concentré — surveillance du range recommandée", "reco_low": "Faible exposition LP — potentiel de fees sous-exploité"},
    }
    for k, v in current.items():
        t = thresholds.get(k, {})
        if t.get("high") and v > t["high"]:
            actions.append({"type": "reduce", "asset": k, "pct": v * 100, "msg": t.get("reco_high", f"Réduire {k}")})
        elif t.get("low") is not None and v < t["low"] and total_usd > 0:
            if t.get("reco_low"):
                actions.append({"type": "increase", "asset": k, "pct": v * 100, "msg": t.get("reco_low", f"Augmenter {k}")})
    return actions

# ══════════════════════════════════════════════════════════
# ── SESSION STATE ──
# ══════════════════════════════════════════════════════════
for k, v in [
    ("authenticated", False),
    ("boot_content", []),
    ("boot_done", False),
    ("disc_shown", False),
    ("secret_content", []),
    ("checklist_validee", False),
    ("checklist_content", []),
]:
    if k not in st.session_state:
        st.session_state[k] = v

SECRET_CODE = st.secrets["Secret_Code"]

# ══════════════════════════════════════════════════════════
# ── BOOT TERMINAL ──
# ══════════════════════════════════════════════════════════
boot_ph = st.empty()

if not st.session_state.boot_done:
    lines_boot = [
        "◈ DEFI WALLET BACKTEST V2 — INITIALIZING",
        "─────────────────────────────────────────────",
        "▸ Chargement des modules...",
        "  [✓] Analyse d'allocation de portefeuille (BTC / Lending / Borrowing / HODL / LP)",
        "  [✓] Scoring de risque SAFE / MID / DEGEN",
        "  [✓] Score IA LP — évaluation de l'efficacité de la position",
        "  [✓] Radar d'allocation interactive (Plotly)",
        "  [✓] Recommandations automatiques par seuil",
        "  [✓] Simulateur de scénario de marché (Stress Test)",
        "─────────────────────────────────────────────",
        "▸ Nouveautés V2 :",
        "  [✓] Design unifié avec le Backtest Engine LP",
        "  [✓] Radar interactif Plotly dark mode",
        "  [✓] Jauge SAFE/MID/DEGEN animée",
        "  [✓] Recommandations enrichies avec contexte",
        "─────────────────────────────────────────────",
        "▸ Système prêt. Saisissez votre portefeuille.",
        "  WALLET ENGINE READY ◈"
    ]
    for line in lines_boot:
        add_term_line(
            st.session_state.boot_content,
            boot_ph,
            line
        )

    if not st.session_state.disc_shown:
        disc_lines = [
            "",
            "$ cat disclaimer.txt",
            "──────────────────────────────────────────────",
            "[!] SYSTEM WARNING — DISCLAIMER LOADED",
            "──────────────────────────────────────────────",
            "⚠  DISCLAIMER IMPORTANT",
            "",
            "Cet outil analyse uniquement la répartition de votre portefeuille.",
            "Les résultats sont basés sur des modèles théoriques de stratégie.",
            "",
            "Cette analyse ne prend pas en compte :",
            "  · votre situation personnelle",
            "  · les conditions de marché en temps réel",
            "  · les variations de prix ou de liquidité",
            "",
            "Cet outil ne constitue PAS un conseil en investissement.",
            "Faites vos propres recherches (DYOR).",
            "",
            "Accès réservé aux membres Team Élite (KBOUR Crypto)",
            "──────────────────────────────────────────────"
        ]
        for line in disc_lines:
            add_term_line(
                st.session_state.boot_content,
                boot_ph,
                line
            )
        st.session_state.disc_shown = True

    st.session_state.boot_done = True
else:
    render_term(boot_ph, st.session_state.boot_content)

st.markdown("""
<div class="disc-bar">
  <span>⚠</span> Cet outil ne constitue pas un conseil en investissement. Les résultats sont indicatifs. DYOR.
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── SECRET CODE ──
# ══════════════════════════════════════════════════════════
sec_ph = st.empty()

if not st.session_state.authenticated:
    if not st.session_state.secret_content:
        st.session_state.secret_content.append("◈ ACCESS PROTOCOL — TEAM ÉLITE KBOUR CRYPTO")
        render_term(sec_ph, st.session_state.secret_content, "sec-term")
        time.sleep(0.4)
        st.session_state.secret_content.append("▸ Vérification des droits d'accès en cours...")
        render_term(sec_ph, st.session_state.secret_content, "sec-term")
        time.sleep(0.3)
        st.session_state.secret_content.append("▸ Saisissez le code d'accès ci-dessous.")
        render_term(sec_ph, st.session_state.secret_content, "sec-term")
    else:
        render_term(sec_ph, st.session_state.secret_content, "sec-term")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col_in, col_btn = st.columns([3, 1])
    with col_in:
        code_input = st.text_input("Code d'accès", key="secret_code", type="password",
                                   label_visibility="collapsed", placeholder="Entrez le code d'accès…")
    with col_btn:
        if st.button("◈ VALIDER", use_container_width=True):
            if code_input == SECRET_CODE:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.session_state.secret_content.append("[!] CODE INCORRECT — Accès refusé.")
                render_term(sec_ph, st.session_state.secret_content, "sec-term")
                st.error("Code incorrect")
    st.stop()

st.markdown("""
<div class="disc-bar" style="border-color:var(--accent); color:var(--accent);">
  <span>◈</span> ACCÈS AUTORISÉ — Bienvenue dans le DeFi Wallet Backtest V2 !
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── CHECKLIST ──
# ══════════════════════════════════════════════════════════
checklist_items = [
    "Je comprends que cet outil analyse uniquement la répartition de mon portefeuille",
    "Je sais que les scores SAFE/MID/DEGEN sont des indicateurs relatifs, non absolus",
    "Je comprends que le Score IA LP est basé sur des pondérations théoriques",
    "Je ne fournis de liquidité que sur des paires que je suis prêt à détenir",
    "Je comprends que le Borrowing augmente le risque de liquidation",
    "Je dispose d'une réserve de liquidité hors protocole DeFi",
    "Je surveille régulièrement mes positions de Lending et Borrowing",
    "Je comprends que cet outil ne constitue pas un conseil en investissement",
    "Je ferai mes propres recherches avant toute décision (DYOR)"
]

cl_ph = st.empty()

if not st.session_state.checklist_validee:
    if not st.session_state.checklist_content:
        st.session_state.checklist_content.append("$ init checklist_protocol --wallet_safety")
        render_term(cl_ph, st.session_state.checklist_content, "cl-term")
        time.sleep(0.3)
        st.session_state.checklist_content.append("▸ auto-checking all items...")
        render_term(cl_ph, st.session_state.checklist_content, "cl-term")
        time.sleep(0.2)
        for item in checklist_items:
            add_term_line(
                st.session_state.checklist_content,
                cl_ph,
                f"  [✓] {item}",
                "cl-term"
            )
        bar = "█" * 20
        add_term_line(
            st.session_state.checklist_content,
            cl_ph,
            f"▸ progress: [{bar}] {len(checklist_items)}/{len(checklist_items)} — READY",
            "cl-term"
        )
    else:
        render_term(cl_ph, st.session_state.checklist_content, "cl-term")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("◈ J'AI COMPRIS — ACCÉDER À L'ANALYSE", use_container_width=True):
        st.session_state.checklist_validee = True
        st.rerun()
    st.stop()

st.markdown("""
<div class="disc-bar">
  <span>◈</span> Déverrouillage de l'outil d'analyse...
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='v2-divider'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── SECTION 1 : PORTEFEUILLE ──
# ══════════════════════════════════════════════════════════
sec("⬡", "Saisie du portefeuille ($)")

st.markdown("""
<div class="m-card-wide" style="margin-bottom:18px;">
    <div class="m-label">Instructions</div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:12px; color:#b0bec5; line-height:1.8;">
        Renseignez la <b style="color:#f0f4f8;">valeur en USD</b> de chaque catégorie d'actifs dans votre portefeuille DeFi.<br>
        Laissez à <b style="color:#f0f4f8;">0</b> les catégories non utilisées.
    </div>
</div>
""", unsafe_allow_html=True)

ASSETS = ["BTC Natif", "Lending", "Borrowing", "HODL", "LP"]

ASSET_DESCRIPTIONS = {
    "BTC Natif":  "Bitcoin détenu en self-custody ou sur hardware wallet. Actif de réserve principal.",
    "Lending":    "Capital prêté sur protocoles DeFi (Aave, Compound, etc.) générant des intérêts.",
    "Borrowing":  "Capital emprunté contre collatéral. Crée un risque de liquidation si le collatéral baisse.",
    "HODL":       "Actifs détenus sans stratégie active (ETH, altcoins, etc.) — capital non productif.",
    "LP":         "Capital déployé en position de liquidité concentrée (Uniswap V3, Aerodrome, etc.).",
}

ASSET_ICONS = {
    "BTC Natif": "₿", "Lending": "◉", "Borrowing": "⚠",
    "HODL": "◈", "LP": "⬡"
}

portfolio = {}

col1, col2 = st.columns(2)
assets_left  = ASSETS[:3]
assets_right = ASSETS[3:]

with col1:
    for asset in assets_left:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:3px;">
            <span style="font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--accent);">{ASSET_ICONS[asset]}</span>
            <span style="font-size:12px; color:var(--text-mid); font-family:'Inter',sans-serif;">{asset}</span>
            <span style="font-size:10px; color:var(--text-lo); font-family:'JetBrains Mono',monospace;">— {ASSET_DESCRIPTIONS[asset]}</span>
        </div>""", unsafe_allow_html=True)
        portfolio[asset] = st.number_input(
            f"_{asset}", min_value=0.0, step=100.0,
            label_visibility="collapsed", key=f"port_{asset}"
        )

with col2:
    for asset in assets_right:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:3px;">
            <span style="font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--accent);">{ASSET_ICONS[asset]}</span>
            <span style="font-size:12px; color:var(--text-mid); font-family:'Inter',sans-serif;">{asset}</span>
            <span style="font-size:10px; color:var(--text-lo); font-family:'JetBrains Mono',monospace;">— {ASSET_DESCRIPTIONS[asset]}</span>
        </div>""", unsafe_allow_html=True)
        portfolio[asset] = st.number_input(
            f"_{asset}", min_value=0.0, step=100.0,
            label_visibility="collapsed", key=f"port_{asset}"
        )

st.markdown("<div class='v2-divider'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── SECTION 2 : PROFIL DE RISQUE ──
# ══════════════════════════════════════════════════════════
sec("◉", "Profil de risque — Allocation SAFE / MID / DEGEN")

st.markdown("""
<div class="m-card-wide" style="margin-bottom:14px;">
    <div class="m-label">Définition des niveaux</div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:12px; color:#b0bec5; line-height:1.8;">
        <span style="color:#22c55e;">■ SAFE</span> : BTC natif, stablecoins, Lending sur protocoles établis — capital préservé<br>
        <span style="color:#f59e0b;">■ MID</span>  : ETH, HODL blue chips, LP sur paires majeures — risque modéré<br>
        <span style="color:#ef4444;">■ DEGEN</span>: Altcoins, LP sur paires volatiles, Borrowing agressif — risque élevé
    </div>
</div>
""", unsafe_allow_html=True)

r1, r2, r3 = st.columns(3)
with r1:
    st.markdown('<p style="font-size:12px;color:#22c55e;font-family:JetBrains Mono,monospace;margin-bottom:3px;">▸ SAFE (%)</p>', unsafe_allow_html=True)
    safe_pct = st.number_input("safe_pct", value=40.0, min_value=0.0, max_value=100.0, step=5.0, label_visibility="collapsed")
with r2:
    st.markdown('<p style="font-size:12px;color:#f59e0b;font-family:JetBrains Mono,monospace;margin-bottom:3px;">▸ MID (%)</p>', unsafe_allow_html=True)
    mid_pct = st.number_input("mid_pct", value=40.0, min_value=0.0, max_value=100.0, step=5.0, label_visibility="collapsed")
with r3:
    st.markdown('<p style="font-size:12px;color:#ef4444;font-family:JetBrains Mono,monospace;margin-bottom:3px;">▸ DEGEN (%)</p>', unsafe_allow_html=True)
    degen_pct = st.number_input("degen_pct", value=20.0, min_value=0.0, max_value=100.0, step=5.0, label_visibility="collapsed")

total_risk_pct = safe_pct + mid_pct + degen_pct
if total_risk_pct > 0:
    s_n = safe_pct  / total_risk_pct
    m_n = mid_pct   / total_risk_pct
    d_n = degen_pct / total_risk_pct
    st.markdown(f"""
    <div class="gauge-wrap">
        <div class="gauge-bar">
            <div class="gauge-safe"  style="width:{s_n*100:.1f}%"></div>
            <div class="gauge-mid"   style="width:{m_n*100:.1f}%"></div>
            <div class="gauge-degen" style="width:{d_n*100:.1f}%"></div>
        </div>
        <div class="gauge-legend">
            <span><span class="leg-dot" style="background:#22c55e;"></span>SAFE {s_n*100:.0f}%</span>
            <span><span class="leg-dot" style="background:#f59e0b;"></span>MID {m_n*100:.0f}%</span>
            <span><span class="leg-dot" style="background:#ef4444;"></span>DEGEN {d_n*100:.0f}%</span>
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='v2-divider'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── RUN BUTTON ──
# ══════════════════════════════════════════════════════════
run_col, _ = st.columns([1, 3])
with run_col:
    run = st.button("◈ LANCER L'ANALYSE", use_container_width=True)

if run:
    total = sum(portfolio.values())

    if total == 0:
        st.error("⚠ Portefeuille vide — renseignez au moins une catégorie.")
    else:
        current = normalize(portfolio)
        total_pct_r = safe_pct + mid_pct + degen_pct
        s = safe_pct  / total_pct_r if total_pct_r else 0
        m = mid_pct   / total_pct_r if total_pct_r else 0
        d = degen_pct / total_pct_r if total_pct_r else 0

        score_r = risk_score(d, m)
        score_lp = lp_score(current)
        actions  = detect_actions(current, total)

        # ── RISK BADGE ──
        if score_r < 30:
            badge_label = "🟢 PROFIL SAFE"
            badge_bg = "rgba(34,197,94,.12)"; badge_border = "rgba(34,197,94,.3)"; badge_color = "#22c55e"
        elif score_r < 60:
            badge_label = "🟡 PROFIL ÉQUILIBRÉ"
            badge_bg = "rgba(245,158,11,.12)"; badge_border = "rgba(245,158,11,.3)"; badge_color = "#f59e0b"
        elif score_r < 80:
            badge_label = "🟠 PROFIL MID-DEGEN"
            badge_bg = "rgba(239,68,68,.10)"; badge_border = "rgba(239,68,68,.25)"; badge_color = "#f97316"
        else:
            badge_label = "🔴 PROFIL DEGEN"
            badge_bg = "rgba(239,68,68,.15)"; badge_border = "rgba(239,68,68,.4)"; badge_color = "#ef4444"

        # ══════════════════════════════════════════════════
        # ── SCORES ──
        # ══════════════════════════════════════════════════
        sec("◉", "Résultats de l'analyse")

        st.markdown(f"""
        <div style="margin-bottom:14px;">
            <span class="risk-badge" style="background:{badge_bg}; border:1px solid {badge_border}; color:{badge_color};">
                {badge_label}
            </span>
        </div>""", unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            lp_color = "#22c55e" if score_lp > 60 else "#f59e0b" if score_lp > 35 else "#ef4444"
            st.markdown(f"""<div class="m-card">
                <div class="m-label">Capital total</div>
                <div class="m-value">${total:,.0f}</div></div>""", unsafe_allow_html=True)
        with k2:
            risk_color = "#22c55e" if score_r < 30 else "#f59e0b" if score_r < 60 else "#ef4444"
            st.markdown(f"""<div class="m-card">
                <div class="m-label">Score risque</div>
                <div class="m-value" style="color:{risk_color};">{score_r:.1f}<span style="font-size:12px;color:var(--text-mid);">/100</span></div></div>""", unsafe_allow_html=True)
        with k3:
            st.markdown(f"""<div class="m-card">
                <div class="m-label">Score IA LP</div>
                <div class="m-value" style="color:{lp_color};">{score_lp:.1f}<span style="font-size:12px;color:var(--text-mid);">/100</span></div></div>""", unsafe_allow_html=True)
        with k4:
            borrow_val = portfolio.get("Borrowing", 0)
            borrow_ratio = borrow_val / total * 100 if total > 0 else 0
            borrow_color = "#22c55e" if borrow_ratio < 10 else "#f59e0b" if borrow_ratio < 25 else "#ef4444"
            st.markdown(f"""<div class="m-card">
                <div class="m-label">Exposition Borrowing</div>
                <div class="m-value" style="color:{borrow_color};">{borrow_ratio:.1f}%</div></div>""", unsafe_allow_html=True)

        st.markdown("<div class='v2-divider'></div>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════════
        # ── DÉCOMPOSITION ──
        # ══════════════════════════════════════════════════
        sec("⬡", "Décomposition du portefeuille")

        decamp_cols = st.columns(len(ASSETS))
        colors_map = {"BTC Natif":"#f59e0b","Lending":"#22c55e","Borrowing":"#ef4444","HODL":"#0ea5e9","LP":"#00d4aa"}

        for i, asset in enumerate(ASSETS):
            val = portfolio.get(asset, 0)
            pct = current.get(asset, 0) * 100
            col_c = colors_map.get(asset, "var(--accent)")
            with decamp_cols[i]:
                st.markdown(f"""
                <div class="m-card">
                    <div class="m-label">{ASSET_ICONS.get(asset,'')} {asset}</div>
                    <div class="m-value" style="color:{col_c};">${val:,.0f}</div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:12px; color:var(--text-mid); margin-top:4px;">{pct:.1f}%</div>
                    <div style="height:3px; background:{col_c}; border-radius:2px; margin-top:8px; opacity:0.6; width:{pct:.0f}%; max-width:100%;"></div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div class='v2-divider'></div>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════════
        # ── RADAR ──
        # ══════════════════════════════════════════════════
        sec("△", "Radar d'allocation")

        labels_r = list(current.keys())
        values_r = [current[k] * 100 for k in labels_r]
        if sum(values_r) == 0:
            st.warning("Impossible d'afficher le radar : portefeuille vide.")
            st.stop()
        colors_r = [colors_map.get(k, "#00d4aa") for k in labels_r]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values_r + [values_r[0]],
            theta=labels_r + [labels_r[0]],
            fill="toself",
            fillcolor="rgba(0,212,170,0.08)",
            line=dict(color="#00d4aa", width=2),
            marker=dict(color="#00d4aa", size=6),
            name="Allocation"
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#0d1318",
                radialaxis=dict(
                    visible=True, range=[0, 100],
                    tickfont=dict(color="#8899aa", size=9, family="JetBrains Mono"),
                    gridcolor="rgba(255,255,255,0.06)",
                    linecolor="rgba(255,255,255,0.08)"
                ),
                angularaxis=dict(
                    tickfont=dict(color="#f0f4f8", size=12, family="JetBrains Mono"),
                    gridcolor="rgba(255,255,255,0.06)",
                    linecolor="rgba(255,255,255,0.08)"
                )
            ),
            paper_bgcolor="#0d1318",
            plot_bgcolor="#0d1318",
            showlegend=False,
            margin=dict(l=50, r=50, t=30, b=30),
            height=380
        )
        col_r_l, col_r_c, col_r_r = st.columns([1, 2, 1])
        with col_r_c:
            st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("<div class='v2-divider'></div>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════════
        # ── RECOMMANDATIONS ──
        # ══════════════════════════════════════════════════
        sec("◎", "Recommandations automatiques")

        if not actions:
            st.markdown("""
            <div class="m-card-highlight">
                <div class="m-label">Statut</div>
                <div class="m-value-sm" style="color:var(--accent-green);">✓ Portefeuille bien équilibré — aucune action critique détectée</div>
            </div>""", unsafe_allow_html=True)
        else:
            for a in actions:
                icon = "🔻" if a["type"] == "reduce" else "🔺"
                col_a = "#ef4444" if a["type"] == "reduce" else "#22c55e"
                label_a = "RÉDUIRE" if a["type"] == "reduce" else "AUGMENTER"
                st.markdown(f"""
                <div class="reco-card">
                    <div class="reco-icon">{icon}</div>
                    <div>
                        <div class="reco-text">
                            <span style="color:{col_a}; font-weight:600;">{label_a} {a['asset']}</span>
                            &nbsp;<span style="color:var(--text-lo);">({a['pct']:.1f}% du portefeuille)</span>
                        </div>
                        <div class="reco-sub">{a['msg']}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div class='v2-divider'></div>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════════
        # ── STRESS TEST ──
        # ══════════════════════════════════════════════════
        sec("∿", "Stress Test — Impact scénarios de marché")

        scenarios = {
            "🔻 Bear -30%":  {"BTC Natif": -0.30, "Lending":  0.00, "Borrowing":  0.30, "HODL": -0.35, "LP": -0.28},
            "🔻 Crash -50%": {"BTC Natif": -0.50, "Lending": -0.05, "Borrowing":  0.60, "HODL": -0.60, "LP": -0.52},
            "🔺 Bull +50%":  {"BTC Natif":  0.50, "Lending":  0.02, "Borrowing": -0.20, "HODL":  0.70, "LP":  0.45},
            "↔ Sideways":   {"BTC Natif":  0.02, "Lending":  0.04, "Borrowing":  0.00, "HODL": -0.05, "LP":  0.03},
        }

        st_cols = st.columns(len(scenarios))
        for i, (scen_name, impacts) in enumerate(scenarios.items()):
            new_total = sum(
                portfolio.get(asset, 0) * (1 + impacts.get(asset, 0))
                for asset in ASSETS
            )
            delta = new_total - total
            delta_pct = (delta / total * 100) if total > 0 else 0
            d_color = "#22c55e" if delta >= 0 else "#ef4444"
            with st_cols[i]:
                st.markdown(f"""
                <div class="m-card">
                    <div class="m-label">{scen_name}</div>
                    <div class="m-value" style="color:{d_color};">{delta_pct:+.1f}%</div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--text-mid); margin-top:4px;">
                        ${new_total:,.0f} <span style="color:{d_color};">({delta:+,.0f}$)</span>
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div class='v2-divider'></div>", unsafe_allow_html=True)

        # ── DISCLAIMER FINAL ──
        st.markdown("""
        <div class="m-card-wide">
            <div class="m-label">◈ Disclaimer</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--text-mid); line-height:1.8;">
                Cet outil analyse uniquement la répartition de votre portefeuille entre différentes catégories d'actifs.<br>
                Les résultats sont basés sur des modèles théoriques de stratégie (SAFE / MID / DEGEN) et de pondération.<br>
                Cette analyse ne prend pas en compte votre situation personnelle, les conditions de marché en temps réel,
                les variations de prix ou de liquidité.<br>
                <span style="color:var(--accent);">Vous êtes seul responsable de vos décisions. Faites vos propres recherches (DYOR).</span>
            </div>
        </div>""", unsafe_allow_html=True)

st.markdown("""
<div style="height:40px;"></div>
<div style="text-align:center; font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--text-lo); letter-spacing:1px;">
    ◈ DEFI WALLET BACKTEST V2 · PIGEON CHANCEUX LAB · DYOR · NOT FINANCIAL ADVICE
</div>
<div style="height:20px;"></div>
""", unsafe_allow_html=True)
