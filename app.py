import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from math import sqrt, ceil
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="MRP Analyzer — SmartHome Appliances",
    layout="wide", page_icon="🏭", initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
  .hero { background: linear-gradient(135deg, #0f2140 0%, #1a3a6b 50%, #1e5c9b 100%);
    border-radius: 12px; padding: 28px 36px; margin-bottom: 24px;
    border: 1px solid rgba(255,255,255,0.1); }
  .hero h1 { color: #fff; font-size: 26px; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.3px; }
  .hero p  { color: rgba(255,255,255,0.65); font-size: 14px; margin: 0; }
  .hero .tag { display: inline-block; background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25); border-radius: 20px;
    padding: 3px 12px; font-size: 12px; color: #7ecfff; margin: 8px 4px 0 0;
    font-family: 'IBM Plex Mono', monospace; }
  .section-header { font-size: 13px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: #64748b; margin: 20px 0 10px 0; }
  .kpi-box { background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 16px 18px; text-align: center; }
  .kpi-label { font-size: 11px; color: #94a3b8; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px; }
  .kpi-value { font-size: 22px; font-weight: 700; color: #1e293b;
    font-family: 'IBM Plex Mono', monospace; }
  .kpi-sub { font-size: 11px; color: #64748b; margin-top: 2px; }
  .insight-box { background: #fffbeb; border-left: 3px solid #f59e0b;
    padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 10px 0;
    font-size: 13px; color: #78350f; }
  .success-box { background: #f0fdf4; border-left: 3px solid #22c55e;
    padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 10px 0;
    font-size: 13px; color: #14532d; }
  .info-box { background: #eff6ff; border-left: 3px solid #3b82f6;
    padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 10px 0;
    font-size: 13px; color: #1e3a8a; }
  .tech-badge { display: inline-block; padding: 6px 18px; border-radius: 6px;
    font-size: 13px; font-weight: 700; font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.5px; }
  .formula-box { background: #1e293b; border-radius: 8px; padding: 14px 18px;
    font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #7ecfff;
    margin: 8px 0; border: 1px solid #334155; }
  div[data-testid="stDataFrame"] table { font-size: 13px; }
  div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th { padding: 6px 12px !important; }
  .stTabs [data-baseweb="tab"] { font-size: 14px; font-weight: 600; }
  .stExpander { border: 1px solid #e2e8f0 !important; border-radius: 10px !important; }
  div[data-testid="stSidebarContent"] { background: #0f172a; }
  div[data-testid="stSidebarContent"] label,
  div[data-testid="stSidebarContent"] p,
  div[data-testid="stSidebarContent"] span { color: #cbd5e1 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════
WEEKS      = ["W10","W11","W12","W13","W14","W15"]
ALL_WEEKS  = ["W8","W9","W10","W11","W12","W13","W14","W15"]
TECHNIQUES = ["L4L","EOQ","FOQ","POQ","LUC","LTC"]

TECH_COLOR = {"L4L":"#1d4ed8","EOQ":"#0891b2","FOQ":"#059669",
              "POQ":"#7c3aed","LUC":"#ea580c","LTC":"#dc2626"}
TECH_NAME  = {"L4L":"Lot-for-Lot","EOQ":"Economic Order Qty",
              "FOQ":"Fixed Order Qty","POQ":"Periodic Order Qty",
              "LUC":"Least Unit Cost","LTC":"Least Total Cost"}
TECH_DESC  = {
  "L4L": "Order exactly = Net Requirement. Zero excess inventory.",
  "EOQ": "EOQ = √(2DS/H). Order fixed economic batch when NR > 0.",
  "FOQ": "Fixed batch = EOQ rounded to nearest 10. Order when NR > 0.",
  "POQ": "Order interval P = round(EOQ ÷ avg demand). Cover P periods per order.",
  "LUC": "Extend order cycle until unit cost (S+HC)/Q starts rising.",
  "LTC": "Extend order cycle until cumulative HC ≈ ordering cost S.",
}
COMP_COLOR = {"MA":"#1e40af","FU":"#166534","CB":"#92400e"}
COMP_BG    = {"MA":"#dbeafe","FU":"#dcfce7","CB":"#fef3c7"}
COMP_FULL  = {"MA":"Motor Assembly","FU":"Filter Unit","CB":"Control Board"}

# Level 2 sub-component config
LVL2_INFO = {
  "RU": dict(full="Rotor Unit (RU)", parent="MA", qty=2, lt=1,
             bg="#e0e7ff", hdr="#3730a3",
             desc="×2 per Motor Assembly | LT=1wk | BI=0 | SS=0 | L4L"),
  "HS": dict(full="Housing (HS)", parent="MA", qty=1, lt=1,
             bg="#f0fdf4", hdr="#14532d",
             desc="×1 per Motor Assembly | LT=1wk | BI=0 | SS=0 | L4L"),
  "FM": dict(full="Filter Media (FM)", parent="FU", qty=1, lt=1,
             bg="#fef9c3", hdr="#854d0e",
             desc="×1 per Filter Unit | LT=1wk | BI=0 | SS=0 | L4L"),
  "PF": dict(full="Plastic Frame (PF)", parent="FU", qty=1, lt=1,
             bg="#fce7f3", hdr="#9d174d",
             desc="×1 per Filter Unit | LT=1wk | BI=0 | SS=0 | L4L"),
}

# ══════════════════════════════════════════════════════════════════
# MRP ENGINE
# ══════════════════════════════════════════════════════════════════
def rup(x, m):
    if m <= 1: return int(round(x))
    return int(ceil(x / m) * m)

def l4l_nr(gr, sr, bi, ss):
    n, nr, ph = len(gr), [], bi
    for t in range(n):
        av  = ph + sr[t]
        net = max(0.0, gr[t] + ss - av)
        nr.append(net)
        ph  = av + net - gr[t]
    return nr

def compute_mrp(gr, sr_dict, bi, ss, lt, tech, S, uc, hpct, mult=1):
    n   = len(gr)
    sr  = [sr_dict.get(i, 0) for i in range(n)]
    hw  = uc * hpct / 52
    Dan = sum(gr) * 52 / n
    Han = uc * hpct
    eoq = sqrt(2 * Dan * S / Han) if Han > 0 else 1
    foq = max(mult, rup(round(eoq / 10) * 10, mult))
    avd = sum(gr) / n
    poq_p  = max(1, round(eoq / avd)) if avd > 0 else 2
    oq_eoq = max(mult, rup(eoq, mult))
    nr_l4l = l4l_nr(gr, sr, bi, ss)
    ph_prev = bi
    poh_o, nr_o, por_o = [], [], []

    if tech == "L4L":
        for t in range(n):
            av = ph_prev + sr[t]; net = max(0.0, gr[t] + ss - av)
            ord_ = rup(net, mult) if net > 0 else 0
            nr_o.append(net); por_o.append(ord_)
            poh_o.append(av + ord_ - gr[t]); ph_prev = poh_o[-1]

    elif tech in ("EOQ", "FOQ"):
        oq = foq if tech == "FOQ" else oq_eoq
        for t in range(n):
            av = ph_prev + sr[t]; net = max(0.0, gr[t] + ss - av)
            ord_ = oq if net > 0 else 0
            nr_o.append(net); por_o.append(ord_)
            poh_o.append(av + ord_ - gr[t]); ph_prev = poh_o[-1]

    elif tech == "POQ":
        t = 0
        while t < n:
            av = ph_prev + sr[t]; net = max(0.0, gr[t] + ss - av); nr_o.append(net)
            if net > 0:
                qty  = sum(nr_l4l[t: t + poq_p]); ord_ = rup(qty, mult)
                por_o.append(ord_); poh_o.append(av + ord_ - gr[t])
                ph_prev = poh_o[-1]; t += 1
                for k in range(t, min(t + poq_p - 1, n)):
                    avk = ph_prev + sr[k]; por_o.append(0); nr_o.append(0)
                    poh_o.append(avk - gr[k]); ph_prev = poh_o[-1]; t += 1
            else:
                por_o.append(0); poh_o.append(av - gr[t]); ph_prev = poh_o[-1]; t += 1

    elif tech in ("LUC", "LTC"):
        t = 0
        while t < n:
            av = ph_prev + sr[t]; net = max(0.0, gr[t] + ss - av); nr_o.append(net)
            if net > 0:
                best_span, best_qty = 1, nr_l4l[t]
                if tech == "LUC":
                    best_c = 1e18
                    for sp in range(1, n - t + 1):
                        qty = sum(nr_l4l[t: t + sp])
                        if qty == 0: continue
                        hc = sum(nr_l4l[t+k] * k * hw for k in range(1, sp))
                        c  = (S + hc) / qty
                        if c < best_c: best_c = c; best_span = sp; best_qty = qty
                        else: break
                else:
                    best_d = 1e18
                    for sp in range(1, n - t + 1):
                        hc = sum(nr_l4l[t+k] * k * hw for k in range(1, sp))
                        d  = abs(hc - S)
                        if d < best_d: best_d = d; best_span = sp; best_qty = sum(nr_l4l[t: t + sp])
                        else: break
                ord_ = rup(best_qty, mult)
                por_o.append(ord_); poh_o.append(av + ord_ - gr[t])
                ph_prev = poh_o[-1]; t += 1
                for k in range(t, min(t + best_span - 1, n)):
                    avk = ph_prev + sr[k]; por_o.append(0); nr_o.append(0)
                    poh_o.append(avk - gr[k]); ph_prev = poh_o[-1]; t += 1
            else:
                por_o.append(0); poh_o.append(av - gr[t]); ph_prev = poh_o[-1]; t += 1

    porel = {}
    for t, q in enumerate(por_o):
        if q > 0:
            porel[t - lt] = q

    n_ord = sum(1 for p in por_o if p > 0)
    spoh  = sum(max(0, p) for p in poh_o)
    oc    = n_ord * S
    hc_t  = spoh * hw
    return dict(
        GR=list(gr), SR=sr, POH=poh_o, NR=nr_o, POR=por_o,
        POREL=porel, n_orders=n_ord, sum_poh=spoh,
        ordering_cost=round(oc, 2), holding_cost=round(hc_t, 2),
        total_cost=round(oc + hc_t, 2),
        eoq=round(eoq, 1), foq=foq, poq_p=poq_p, hw=hw,
    )

def run_all(params):
    return {t: compute_mrp(
        params["gr"], params["sr"], params["bi"], params["ss"],
        params["lt"], t, params["S"], params["uc"], params["hpct"], params["mult"]
    ) for t in TECHNIQUES}

def compute_lvl2(parent_porel_dict, qty_mult, lt=1):
    """
    Compute Level-2 L4L MRP given parent POREL dict (offset→qty).
    parent_porel_dict keys are period offsets: -2,-1,0,1,2,3,4,5
    We map these to ALL_WEEKS positions: offset+2 gives index in ALL_WEEKS
    Returns rows keyed by week label for ALL_WEEKS.
    """
    # Build GR array indexed by ALL_WEEKS
    gr = {}
    for offset, q in parent_porel_dict.items():
        idx = offset + 2   # W8=idx0 → offset=-2, W9=idx1→offset=-1, W10=idx2→offset=0 ...
        if 0 <= idx <= 7:
            wk = ALL_WEEKS[idx]
            gr[wk] = gr.get(wk, 0) + q * qty_mult

    # L4L with BI=0, SS=0, LT=1
    poh_prev = 0
    rows = {k: {"GR":0,"SR":0,"POH":0,"NR":0,"POR":0,"POREL":""} for k in ALL_WEEKS}
    for wk in ALL_WEEKS:
        g = gr.get(wk, 0)
        rows[wk]["GR"] = g if g else 0
        av = poh_prev + 0  # no SR
        net = max(0, g - av)
        rows[wk]["NR"]  = net
        rows[wk]["POR"] = net
        rows[wk]["POH"] = av + net - g  # always 0 for L4L, BI=0
        poh_prev = rows[wk]["POH"]

    # POREL = POR shifted 1 week earlier
    for i, wk in enumerate(ALL_WEEKS):
        pval = rows[wk]["POR"]
        if pval > 0:
            prev_idx = i - lt
            if prev_idx >= 0:
                prev_wk = ALL_WEEKS[prev_idx]
                rows[prev_wk]["POREL"] = pval
            # current week's POREL is empty (it was the receipt week)

    n_orders = sum(1 for wk in ALL_WEEKS if rows[wk]["POR"] > 0)
    return rows, n_orders

# ══════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ══════════════════════════════════════════════════════════════════
def make_table_df(res, comp_k):
    def wk_val(row_data, week_label, row_type):
        idx = ALL_WEEKS.index(week_label)
        period_idx = idx - 2
        if row_type == "POREL":
            return res["POREL"].get(period_idx, "")
        elif 0 <= period_idx <= 5:
            v = row_data[period_idx]
            return v if v != 0 else 0
        else:
            return ""

    labels = {
        "GR":    "① Gross Requirements",
        "SR":    "② Scheduled Receipts",
        "POH":   "③ Proj. On-Hand (EOD)",
        "NR":    "④ Net Requirements",
        "POR":   "⑤ Planned Order Receipts",
        "POREL": "⑥ Planned Order Releases ▶",
    }
    rows = {}
    for key, label in labels.items():
        row = {}
        data = res.get(key, {})
        for wk in ALL_WEEKS:
            row[wk] = wk_val(data, wk, key)
        rows[label] = row
    df = pd.DataFrame(rows).T
    df.columns = ALL_WEEKS
    return df

def make_lvl2_df(lvl2_rows):
    labels = {
        "GR":    "① Gross Requirements",
        "SR":    "② Scheduled Receipts",
        "POH":   "③ Proj. On-Hand (EOD)",
        "NR":    "④ Net Requirements",
        "POR":   "⑤ Planned Order Receipts",
        "POREL": "⑥ Planned Order Releases ▶",
    }
    rows = {}
    for key, label in labels.items():
        row = {}
        for wk in ALL_WEEKS:
            v = lvl2_rows[wk][key]
            row[wk] = v if v != "" else ""
        rows[label] = row
    df = pd.DataFrame(rows).T
    df.columns = ALL_WEEKS
    return df

def style_mrp_table(df, hdr_color, tc):
    def highlight(data):
        styles = pd.DataFrame("", index=data.index, columns=data.columns)
        for idx in data.index:
            for col in data.columns:
                val = data.at[idx, col]
                if "⑥" in idx:
                    if val not in ("", 0):
                        styles.at[idx, col] = (
                            f"background-color:{tc}20; color:{tc}; "
                            "font-weight:700; font-family:'IBM Plex Mono',monospace;")
                    else:
                        styles.at[idx, col] = f"background-color:{tc}08;"
                elif "⑤" in idx:
                    if val not in ("", 0):
                        styles.at[idx, col] = "background-color:#1e293b15; font-weight:600;"
                elif "③" in idx:
                    styles.at[idx, col] = "background-color:#f1f5f9;"
                elif col in ("W8", "W9") and "⑥" not in idx:
                    styles.at[idx, col] = "color:#cbd5e1;"
        return styles

    return (
        df.style
          .apply(highlight, axis=None)
          .format(lambda v: "" if v == "" else (
              f"{int(v):,}" if isinstance(v, (int, float)) and v == int(v) else str(v)))
          .set_table_styles([
              {"selector": "th", "props": [
                  ("background-color", hdr_color), ("color", "white"),
                  ("font-family", "'IBM Plex Sans', sans-serif"),
                  ("font-size", "12px"), ("padding", "8px 12px")]},
              {"selector": "td", "props": [
                  ("font-family", "'IBM Plex Mono', monospace"),
                  ("font-size", "12px"), ("padding", "6px 12px")]},
          ])
    )

def cost_summary_df(all_results):
    rows = []
    for comp in ["MA", "FU", "CB"]:
        for tech in TECHNIQUES:
            r = all_results[comp][tech]
            rows.append({
                "Component": COMP_FULL[comp], "Technique": tech,
                "# Orders": r["n_orders"], "Σ On-Hand": r["sum_poh"],
                "Ordering Cost (Rs.)": r["ordering_cost"],
                "Holding Cost (Rs.)": r["holding_cost"],
                "Total Cost (Rs.)": r["total_cost"],
            })
    return pd.DataFrame(rows)

# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px 0;'>
      <div style='font-size:11px;letter-spacing:2px;font-weight:700;color:#475569;text-transform:uppercase;'>SmartHome Appliances</div>
      <div style='font-size:18px;font-weight:700;color:#f1f5f9;margin:4px 0;'>MRP Analyzer</div>
      <div style='font-size:12px;color:#64748b;'>SAP-X1 Smart Air Purifier</div>
    </div>
    <hr style='border-color:#1e293b;margin:10px 0 16px 0;'/>
    """, unsafe_allow_html=True)

    use_custom = st.toggle("✏️ Override default parameters", value=False)

    if use_custom:
        st.markdown("<div class='section-header'>📦 SAP-X1 Demand (W11–W16)</div>", unsafe_allow_html=True)
        d_cols = st.columns(3)
        raw_demand = [
            d_cols[0].number_input("W11", value=50, min_value=0, step=5, key="d1"),
            d_cols[1].number_input("W12", value=60, min_value=0, step=5, key="d2"),
            d_cols[2].number_input("W13", value=40, min_value=0, step=5, key="d3"),
            d_cols[0].number_input("W14", value=70, min_value=0, step=5, key="d4"),
            d_cols[1].number_input("W15", value=60, min_value=0, step=5, key="d5"),
            d_cols[2].number_input("W16", value=80, min_value=0, step=5, key="d6"),
        ]
        st.markdown("<div class='section-header'>⚙️ Motor Assembly (MA)</div>", unsafe_allow_html=True)
        ma_bi  = st.number_input("Beg. Inventory", value=20, min_value=0, key="ma_bi")
        ma_ss  = st.number_input("Safety Stock",   value=10, min_value=0, key="ma_ss")
        ma_S   = st.number_input("Ordering Cost (Rs.)", value=250, min_value=1, key="ma_s")
        ma_uc  = st.number_input("Unit Cost (Rs.)", value=120, min_value=1, key="ma_uc")
        ma_hpc = st.slider("Annual Holding %", 1, 50, 20, key="ma_hpc") / 100
        st.markdown("<div class='section-header'>🔵 Filter Unit (FU)</div>", unsafe_allow_html=True)
        fu_bi  = st.number_input("Beg. Inventory", value=40, min_value=0, key="fu_bi")
        fu_ss  = st.number_input("Safety Stock",   value=20, min_value=0, key="fu_ss")
        fu_S   = st.number_input("Ordering Cost (Rs.)", value=180, min_value=1, key="fu_s")
        fu_uc  = st.number_input("Unit Cost (Rs.)", value=40, min_value=1, key="fu_uc")
        fu_hpc = st.slider("Annual Holding %", 1, 50, 25, key="fu_hpc") / 100
        st.markdown("<div class='section-header'>🟡 Control Board (CB)</div>", unsafe_allow_html=True)
        cb_bi  = st.number_input("Beg. Inventory", value=25, min_value=0, key="cb_bi")
        cb_ss  = st.number_input("Safety Stock",   value=0,  min_value=0, key="cb_ss")
        cb_S   = st.number_input("Ordering Cost (Rs.)", value=300, min_value=1, key="cb_s")
        cb_uc  = st.number_input("Unit Cost (Rs.)", value=200, min_value=1, key="cb_uc")
        cb_hpc = st.slider("Annual Holding %", 1, 50, 18, key="cb_hpc") / 100
        PARAMS = {
            "MA": dict(gr=[d*1 for d in raw_demand], sr={2:30}, bi=ma_bi, ss=ma_ss,
                       lt=1, S=ma_S, uc=ma_uc, hpct=ma_hpc, mult=1),
            "FU": dict(gr=[d*2 for d in raw_demand], sr={}, bi=fu_bi, ss=fu_ss,
                       lt=2, S=fu_S, uc=fu_uc, hpct=fu_hpc, mult=1),
            "CB": dict(gr=[d*1 for d in raw_demand], sr={}, bi=cb_bi, ss=cb_ss,
                       lt=1, S=cb_S, uc=cb_uc, hpct=cb_hpc, mult=100),
        }
    else:
        PARAMS = {
            "MA": dict(gr=[50,60,40,70,60,80], sr={2:30}, bi=20, ss=10,
                       lt=1, S=250, uc=120, hpct=0.20, mult=1),
            "FU": dict(gr=[100,120,80,140,120,160], sr={}, bi=40, ss=20,
                       lt=2, S=180, uc=40, hpct=0.25, mult=1),
            "CB": dict(gr=[50,60,40,70,60,80], sr={}, bi=25, ss=0,
                       lt=1, S=300, uc=200, hpct=0.18, mult=100),
        }

    st.markdown("<hr style='border-color:#1e293b;margin:16px 0;'/>", unsafe_allow_html=True)
    st.markdown("""
<div style='background:#020617;border:2px solid #38bdf8;border-radius:10px;
            padding:14px 16px;margin-top:10px;line-height:1.6;'>
  <div style='font-size:20px;font-weight:800;color:#ffffff;'>Kritika Bhachawat</div>
  <div style='font-size:16px;color:#facc15;font-weight:600;'>Roll No: 065087</div>
  <div style='font-size:15px;color:#38bdf8;font-weight:600;'>Course: Operation and Supply Chain Management</div>
  <div style='font-size:15px;color:#4ade80;font-weight:600;'>Focus: EOQ outperforms LUC &amp; LTC</div>
  <div style='font-size:15px;color:#c084fc;font-weight:600;'>FORE School of Management</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# COMPUTE ALL RESULTS
# ══════════════════════════════════════════════════════════════════
@st.cache_data
def cached_run(params_json):
    import json
    p = json.loads(params_json)
    for c in p:
        p[c]["sr"] = {int(k): v for k, v in p[c]["sr"].items()}
    return {comp: run_all(p[comp]) for comp in ["MA","FU","CB"]}

import json
params_json = json.dumps({
    c: {**PARAMS[c], "sr": {str(k): v for k, v in PARAMS[c]["sr"].items()}}
    for c in PARAMS
})
ALL_RESULTS = cached_run(params_json)

# ══════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <h1>🏭 MRP Lot Sizing Analyzer</h1>
  <p>SmartHome Appliances · SAP-X1 Smart Air Purifier · 6-Week Planning Horizon · Level 1 + Level 2 MRP</p>
  <span class="tag">L4L</span><span class="tag">EOQ</span><span class="tag">FOQ</span>
  <span class="tag">POQ</span><span class="tag">LUC</span><span class="tag">LTC</span>
  <span class="tag" style="color:#fbbf24;">Level 2: RU · HS · FM · PF</span>
</div>
""", unsafe_allow_html=True)

# KPIs
cdf = cost_summary_df(ALL_RESULTS)
best_tech   = cdf.groupby("Technique")["Total Cost (Rs.)"].sum().idxmin()
worst_tech  = cdf.groupby("Technique")["Total Cost (Rs.)"].sum().idxmax()
best_cost   = cdf.groupby("Technique")["Total Cost (Rs.)"].sum().min()
worst_cost  = cdf.groupby("Technique")["Total Cost (Rs.)"].sum().max()
highest_inv = cdf.groupby("Component")["Σ On-Hand"].sum().idxmax()

k1,k2,k3,k4 = st.columns(4)
for col, label, val, sub in [
    (k1, "BEST TECHNIQUE",    best_tech,  f"Rs. {best_cost:,.0f} total cost"),
    (k2, "WORST TECHNIQUE",   worst_tech, f"Rs. {worst_cost:,.0f} total cost"),
    (k3, "HIGHEST AVG INV.",  highest_inv,"across all techniques"),
    (k4, "COST SAVING",       f"Rs. {worst_cost-best_cost:,.0f}",
         f"{((worst_cost-best_cost)/worst_cost*100):.1f}% reduction"),
]:
    col.markdown(f"""
    <div class='kpi-box'>
      <div class='kpi-label'>{label}</div>
      <div class='kpi-value'>{val}</div>
      <div class='kpi-sub'>{sub}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📋  MRP Tables — All 6 Techniques",
    "💰  Cost Analysis & Comparison",
    "🔬  EOQ Outperformance Lab",
    "🔩  Level 2 Sub-Components",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — MRP TABLES
# ══════════════════════════════════════════════════════════════════
with tab1:
    sel_tech = st.radio(
        "Select Lot Sizing Technique:",
        TECHNIQUES,
        format_func=lambda t: f"{t}  —  {TECH_NAME[t]}",
        horizontal=True, key="tab1_tech"
    )
    tc = TECH_COLOR[sel_tech]
    st.markdown(f"""
    <div style='background:{tc}10; border:1px solid {tc}40; border-radius:10px;
                padding:14px 18px; margin:12px 0 20px 0; display:flex; align-items:center; gap:16px;'>
      <span class='tech-badge' style='background:{tc}; color:white;'>{sel_tech}</span>
      <div>
        <div style='font-weight:700;color:{tc};font-size:15px;'>{TECH_NAME[sel_tech]}</div>
        <div style='font-size:13px;color:#64748b;margin-top:3px;'>{TECH_DESC[sel_tech]}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    ref = ALL_RESULTS["MA"][sel_tech]
    if sel_tech == "EOQ":
        st.markdown(f"""<div class='formula-box'>
          EOQ = √(2DS/H) &nbsp;|&nbsp;
          MA: √(2×{sum(PARAMS['MA']['gr'])*52//6}×{PARAMS['MA']['S']}÷{PARAMS['MA']['uc']*PARAMS['MA']['hpct']:.0f}) = <b>{ref['eoq']}</b> units &nbsp;|&nbsp;
          FU: <b>{ALL_RESULTS['FU']['EOQ']['eoq']}</b> units &nbsp;|&nbsp;
          CB: {ALL_RESULTS['CB']['EOQ']['eoq']} → <b>{ALL_RESULTS['CB']['EOQ']['foq']}</b> (×100)
        </div>""", unsafe_allow_html=True)
    elif sel_tech == "FOQ":
        st.markdown(f"""<div class='formula-box'>
          FOQ = round(EOQ, 10) &nbsp;|&nbsp;
          MA: {ALL_RESULTS['MA']['FOQ']['eoq']} → <b>{ALL_RESULTS['MA']['FOQ']['foq']}</b> &nbsp;|&nbsp;
          FU: {ALL_RESULTS['FU']['FOQ']['eoq']} → <b>{ALL_RESULTS['FU']['FOQ']['foq']}</b> &nbsp;|&nbsp;
          CB: {ALL_RESULTS['CB']['FOQ']['eoq']} → <b>{ALL_RESULTS['CB']['FOQ']['foq']}</b> (×100 supplier rule)
        </div>""", unsafe_allow_html=True)
    elif sel_tech == "POQ":
        st.markdown(f"""<div class='formula-box'>
          P = round(EOQ ÷ avg_demand) &nbsp;|&nbsp;
          MA: {ALL_RESULTS['MA']['POQ']['eoq']} ÷ {sum(PARAMS['MA']['gr'])/6:.0f} = <b>P={ALL_RESULTS['MA']['POQ']['poq_p']} wks</b> &nbsp;|&nbsp;
          FU: <b>P={ALL_RESULTS['FU']['POQ']['poq_p']} wks</b> &nbsp;|&nbsp;
          CB: <b>P={ALL_RESULTS['CB']['POQ']['poq_p']} wks</b>
        </div>""", unsafe_allow_html=True)

    for comp in ["MA","FU","CB"]:
        res = ALL_RESULTS[comp][sel_tech]
        lt  = PARAMS[comp]["lt"]
        cc  = COMP_COLOR[comp]; bg_c = COMP_BG[comp]
        st.markdown(f"""
        <div style='background:{bg_c}; border-left:4px solid {cc};
                    padding:10px 16px; border-radius:0 8px 8px 0; margin:16px 0 6px 0;
                    display:flex; justify-content:space-between; align-items:center;'>
          <div>
            <span style='font-weight:700;font-size:16px;color:{cc};'>{COMP_FULL[comp]} ({comp})</span>
            <span style='font-size:12px;color:#64748b;margin-left:14px;'>
              LT={lt}wk · BI={PARAMS[comp]['bi']} · SS={PARAMS[comp]['ss']} · SR={PARAMS[comp]['sr'] or 'None'}
              {'· Supplier: ×100 only' if comp=='CB' else ''}
            </span>
          </div>
          <div style='text-align:right;'>
            <span style='font-size:11px;color:#94a3b8;'># Orders: </span>
            <span style='font-weight:700;color:{cc};font-family:IBM Plex Mono;'>{res['n_orders']}</span>
            <span style='font-size:11px;color:#94a3b8;margin-left:12px;'>Total Cost: </span>
            <span style='font-weight:700;color:{cc};font-family:IBM Plex Mono;'>Rs. {res['total_cost']:,.2f}</span>
          </div>
        </div>""", unsafe_allow_html=True)

        df = make_table_df(res, comp)
        st.dataframe(style_mrp_table(df, cc, tc), use_container_width=True, height=270)

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Orders Placed",     res["n_orders"])
        mc2.metric("Σ On-Hand (units)", res["sum_poh"])
        mc3.metric("Ordering Cost",     f"Rs. {res['ordering_cost']:,.0f}")
        mc4.metric("Holding Cost",      f"Rs. {res['holding_cost']:,.2f}")

    st.markdown("""
    <div class='info-box' style='margin-top:20px;'>
      <b>Table guide:</b> W8–W9 shown for Filter Unit POREL only (LT=2 weeks).
      Row ⑥ (Planned Order Releases) is highlighted in the technique colour — these are actionable orders.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# TAB 2 — COST ANALYSIS
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 💰 Total Cost Comparison Across All Techniques")
    grand = cdf.groupby("Technique")[["Ordering Cost (Rs.)","Holding Cost (Rs.)"]].sum().reset_index()
    grand["Total"] = grand["Ordering Cost (Rs.)"] + grand["Holding Cost (Rs.)"]
    grand = grand.sort_values("Total")

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=grand["Technique"], y=grand["Ordering Cost (Rs.)"],
        name="Ordering Cost", marker_color="#3b82f6",
        text=grand["Ordering Cost (Rs.)"].apply(lambda x: f"Rs.{x:,.0f}"),
        textposition="inside", textfont_size=11))
    fig_bar.add_trace(go.Bar(x=grand["Technique"], y=grand["Holding Cost (Rs.)"],
        name="Holding Cost", marker_color="#f59e0b",
        text=grand["Holding Cost (Rs.)"].apply(lambda x: f"Rs.{x:,.2f}"),
        textposition="inside", textfont_size=11))
    fig_bar.update_layout(barmode="stack", title="Grand Total Cost (MA+FU+CB) by Technique",
        xaxis_title="Technique", yaxis_title="Total Cost (Rs.)",
        plot_bgcolor="white", paper_bgcolor="white", font_family="IBM Plex Sans",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=380)
    st.plotly_chart(fig_bar, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### Per-Component Cost by Technique")
        for comp in ["MA","FU","CB"]:
            cd = cdf[cdf["Component"] == COMP_FULL[comp]].sort_values("Total Cost (Rs.)")
            fig_c = go.Figure(go.Bar(x=cd["Technique"], y=cd["Total Cost (Rs.)"],
                marker_color=[TECH_COLOR[t] for t in cd["Technique"]],
                text=cd["Total Cost (Rs.)"].apply(lambda x: f"Rs.{x:,.0f}"),
                textposition="outside", textfont_size=10))
            fig_c.update_layout(title=f"{COMP_FULL[comp]} ({comp})", height=240,
                plot_bgcolor="white", paper_bgcolor="white",
                font_family="IBM Plex Sans", showlegend=False,
                margin=dict(t=40,b=20,l=20,r=20), yaxis_title="Rs.", xaxis_title="")
            st.plotly_chart(fig_c, use_container_width=True)

    with col_r:
        st.markdown("#### Order Frequency by Technique")
        freq = cdf.groupby(["Technique","Component"])["# Orders"].sum().reset_index()
        fig_f = px.bar(freq, x="Technique", y="# Orders", color="Component", barmode="group",
            title="Total Orders per Technique per Component",
            color_discrete_map={"Motor Assembly":"#1e40af","Filter Unit":"#166534","Control Board":"#92400e"},
            height=300)
        fig_f.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_family="IBM Plex Sans")
        st.plotly_chart(fig_f, use_container_width=True)

        st.markdown("#### Average Inventory by Technique")
        avg_inv = cdf.groupby("Technique")["Σ On-Hand"].mean().reset_index()
        avg_inv.columns = ["Technique","Avg On-Hand"]
        fig_i = go.Figure(go.Bar(x=avg_inv["Technique"], y=avg_inv["Avg On-Hand"],
            marker_color=[TECH_COLOR[t] for t in avg_inv["Technique"]],
            text=avg_inv["Avg On-Hand"].round(1), textposition="outside"))
        fig_i.update_layout(title="Avg Σ On-Hand per Technique", height=280,
            plot_bgcolor="white", paper_bgcolor="white", font_family="IBM Plex Sans",
            showlegend=False, yaxis_title="Units", xaxis_title="", margin=dict(t=40,b=20,l=20,r=20))
        st.plotly_chart(fig_i, use_container_width=True)

    st.markdown("#### 📊 Full Summary Table")
    pivot = cdf.pivot_table(index="Technique", columns="Component",
                            values="Total Cost (Rs.)", aggfunc="sum")
    pivot["GRAND TOTAL"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("GRAND TOTAL")
    pivot.index.name = "Technique"

    def highlight_table(val):
        try:
            col_min = pivot["GRAND TOTAL"].min(); col_max = pivot["GRAND TOTAL"].max()
            if isinstance(val, float):
                ratio = (val - col_min) / (col_max - col_min + 1e-9)
                g = int(255 - ratio * 80); r = int(200 + ratio * 55)
                return f"background-color: rgb({r},{g},180); color:#1e293b;"
        except: pass
        return ""

    st.dataframe(pivot.style.format("Rs. {:,.0f}").apply(
        lambda x: [highlight_table(v) for v in x], axis=1), use_container_width=True)

    st.markdown("---")
    st.markdown("### 📝 Q3 — Analytical Questions")
    qa_pairs = [
        ("a. Which item results in highest average inventory?",
         f"**Filter Unit (FU)** under EOQ/FOQ → avg ≈ **{ALL_RESULTS['FU']['EOQ']['sum_poh']//6} units/week**. "
         f"FU has 2× demand of MA & CB and the largest EOQ ({ALL_RESULTS['FU']['EOQ']['eoq']} units), "
         "leading to large inventory buildups. Under L4L, avg = 20 (safety stock only)."),
        ("b. Which item incurs highest ordering frequency?",
         "**MA and FU under L4L** — **6 orders each** (one per demand period). "
         "CB under L4L has 4 orders (100-unit rounding absorbs multiple periods). "
         "L4L always produces the highest ordering frequency for any item."),
        ("c. Total relevant cost comparison across techniques?",
         f"**POQ = lowest** (Rs. {cdf.groupby('Technique')['Total Cost (Rs.)'].sum()['POQ']:,.0f}) — "
         f"4-week cycle aligns with demand rhythm. **L4L = highest** "
         f"(Rs. {cdf.groupby('Technique')['Total Cost (Rs.)'].sum()['L4L']:,.0f}) due to 6 separate ordering costs. "
         "LTC & LUC beat EOQ/FOQ because demand is **lumpy** (50→60→40→70→60→80)."),
        ("d. How do lead time and safety stock influence order releases?",
         "**Lead Time:** MA & CB (LT=1wk) → POREL 1 period earlier. FU (LT=2wks) → POREL 2 periods "
         "earlier (W8), shrinking planning window to 4 effective weeks.\n\n"
         "**Safety Stock:** MA (SS=10) and FU (SS=20) inflate every NR by their SS value, "
         "triggering orders earlier/larger than pure demand requires. CB (SS=0) has no buffer."),
        ("e. Which component creates greatest planning complexity?",
         "**Filter Unit (FU)** — (1) Longest LT=2wks → POREL in W8 (outside demand horizon). "
         "(2) Highest demand volume (2× SAP-X1). (3) Two sub-components (FM + PF) needing their own cascade. "
         "(4) Highest SS=20 → largest NR inflation."),
    ]
    for q, a in qa_pairs:
        with st.expander(q):
            st.markdown(a)

# ══════════════════════════════════════════════════════════════════
# TAB 3 — EOQ LAB
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class='hero' style='background:linear-gradient(135deg,#1e3a1e 0%,#14532d 60%,#166534 100%);'>
      <h1>🔬 EOQ Outperformance Lab</h1>
      <p>Kritika Bhachawat · Roll No. 065087 · Group 76–90 — Conditions where EOQ beats LUC and LTC</p>
      <span class='tag' style='color:#86efac;'>Sensitivity Sliders</span>
      <span class='tag' style='color:#86efac;'>Live Cost Comparison</span>
      <span class='tag' style='color:#86efac;'>Breakeven Analysis</span>
    </div>""", unsafe_allow_html=True)

    with st.expander("📌 Baseline: Does EOQ outperform LUC/LTC in the SAP-X1 case?", expanded=True):
        base_rows = []
        for comp in ["MA","FU","CB"]:
            for tech in ["EOQ","LUC","LTC"]:
                r = ALL_RESULTS[comp][tech]
                base_rows.append({"Component":comp,"Technique":tech,
                                   "Total Cost":r["total_cost"],"# Orders":r["n_orders"]})
        bdf = pd.DataFrame(base_rows)
        pivot_b = bdf.pivot_table(index="Component", columns="Technique", values="Total Cost")
        pivot_b["EOQ wins LUC?"] = pivot_b["EOQ"] < pivot_b["LUC"]
        pivot_b["EOQ wins LTC?"] = pivot_b["EOQ"] < pivot_b["LTC"]

        def hl_win(v):
            if v is True:  return "background-color:#dcfce7;color:#166534;font-weight:700;"
            if v is False: return "background-color:#fee2e2;color:#991b1b;font-weight:700;"
            return ""

        st.dataframe(
            pivot_b.style
                   .format(lambda v: f"Rs.{v:,.2f}" if isinstance(v,(int,float)) and not isinstance(v,bool) else str(v))
                   .applymap(hl_win, subset=["EOQ wins LUC?","EOQ wins LTC?"]),
            use_container_width=True)
        st.markdown("""
        <div class='insight-box'>
          <b>❌ EOQ does NOT outperform LUC/LTC in the SAP-X1 case.</b>
          Demand is <b>lumpy</b> (CV ≈ 0.24). Dynamic methods exploit variability to group periods efficiently.
          Use the lab below to find conditions where EOQ wins.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎛️ Parameter Tuning Lab — Make EOQ Outperform LUC & LTC")

    lab_col1, lab_col2 = st.columns([1, 2])
    with lab_col1:
        st.markdown("**Demand Pattern**")
        demand_cv = st.slider("Demand Variability (CV)", 0.0, 0.5, 0.24, 0.01, key="lab_cv",
            help="CV=0 → uniform. CV=0.24 = SAP-X1 baseline.")
        base_mean = 60
        st.caption(f"Base mean = {base_mean} units/week")
        st.markdown("**Component Parameters**")
        lab_S  = st.slider("Ordering Cost S (Rs.)",     50,  600, 250, 10, key="lab_S")
        lab_h  = st.slider("Annual Holding Cost % (h)",  5,   60,  20,  1, key="lab_h")
        lab_uc = st.slider("Unit Cost (Rs.)",            10,  500, 120, 10, key="lab_uc")
        n_weeks = st.slider("Planning Horizon (weeks)",   4,   12,   6,  1, key="lab_n")
        h_weekly_lab = lab_uc * (lab_h / 100) / 52
        D_annual_lab = base_mean * 52
        eoq_lab = sqrt(2 * D_annual_lab * lab_S / (lab_uc * lab_h / 100))
        st.markdown(f"""
        <div class='formula-box' style='margin-top:12px;'>
          EOQ = √(2 × {D_annual_lab} × {lab_S} ÷ {lab_uc*lab_h/100:.1f})<br/>
          &nbsp;&nbsp;&nbsp;&nbsp;= <b style='color:#4ade80;'>{eoq_lab:.1f} units</b><br/>
          Weekly HC = Rs. {h_weekly_lab:.4f}/unit
        </div>""", unsafe_allow_html=True)

    with lab_col2:
        np.random.seed(42)
        if demand_cv < 0.02:
            lab_gr = [base_mean] * n_weeks
        else:
            std = base_mean * demand_cv
            raw = np.random.normal(base_mean, std, n_weeks)
            lab_gr = [max(5, int(round(v / 5) * 5)) for v in raw]
            actual_mean = np.mean(lab_gr)
            lab_gr = [max(5, int(round(v * base_mean / actual_mean / 5) * 5)) for v in lab_gr]
        actual_cv = np.std(lab_gr) / (np.mean(lab_gr) + 1e-9)

        st.markdown(f"""
        <div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
                    padding:10px 14px;margin-bottom:12px;'>
          <b>Generated demand:</b> {' → '.join(str(v) for v in lab_gr)}<br/>
          <span style='font-size:12px;color:#64748b;'>
            Mean={np.mean(lab_gr):.1f} · CV={actual_cv:.3f}
            {'&nbsp;&nbsp;✅ <b style="color:#166534;">EOQ can compete here</b>' if actual_cv < 0.15 else
             '&nbsp;&nbsp;⚠️ <b style="color:#92400e;">Still lumpy — LUC/LTC likely win</b>'}
          </span>
        </div>""", unsafe_allow_html=True)

        lab_params = dict(gr=lab_gr, sr_dict={}, bi=0, ss=0, lt=1, S=lab_S, uc=lab_uc, hpct=lab_h/100, mult=1)
        lab_res = {t: compute_mrp(**lab_params, tech=t) for t in ["EOQ","LUC","LTC"]}

        fig_lab = go.Figure()
        for tech, col in [("EOQ","#0891b2"),("LUC","#ea580c"),("LTC","#dc2626")]:
            r = lab_res[tech]
            fig_lab.add_trace(go.Bar(name=tech,
                x=["Ordering Cost","Holding Cost","Total Cost"],
                y=[r["ordering_cost"], r["holding_cost"], r["total_cost"]],
                marker_color=col,
                text=[f"Rs.{v:,.2f}" for v in [r["ordering_cost"],r["holding_cost"],r["total_cost"]]],
                textposition="outside", textfont_size=10))
        fig_lab.update_layout(title=f"EOQ vs LUC vs LTC  (CV={actual_cv:.3f})",
            barmode="group", height=300, plot_bgcolor="white", paper_bgcolor="white",
            font_family="IBM Plex Sans", legend=dict(orientation="h", y=1.15),
            margin=dict(t=60,b=20,l=20,r=20))
        st.plotly_chart(fig_lab, use_container_width=True)

        eoq_tc = lab_res["EOQ"]["total_cost"]
        luc_tc = lab_res["LUC"]["total_cost"]
        ltc_tc = lab_res["LTC"]["total_cost"]
        eoq_wins_luc = eoq_tc < luc_tc; eoq_wins_ltc = eoq_tc < ltc_tc

        if eoq_wins_luc and eoq_wins_ltc:
            st.markdown(f"""<div class='success-box'>
              ✅ <b>EOQ OUTPERFORMS BOTH LUC and LTC!</b><br/>
              EOQ: Rs.{eoq_tc:.2f} &lt; LUC: Rs.{luc_tc:.2f} (saves Rs.{luc_tc-eoq_tc:.2f}) &amp;
              LTC: Rs.{ltc_tc:.2f} (saves Rs.{ltc_tc-eoq_tc:.2f})<br/>
              Key: Demand CV = {actual_cv:.3f} (low variability → EOQ excels)
            </div>""", unsafe_allow_html=True)
        elif not eoq_wins_luc and not eoq_wins_ltc:
            st.markdown(f"""<div class='insight-box'>
              ❌ EOQ still loses: Rs.{eoq_tc:.2f} vs LUC: Rs.{luc_tc:.2f}, LTC: Rs.{ltc_tc:.2f}<br/>
              Try: reduce CV below 0.10, or increase S/H ratio above 10.
            </div>""", unsafe_allow_html=True)
        else:
            winner = "LUC" if not eoq_wins_luc else "LTC"
            st.markdown(f"""<div class='info-box'>
              ⚠️ EOQ beats {'LTC' if eoq_wins_ltc else 'LUC'} but loses to {winner}. Reduce CV further.
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Auto-Calculated Breakeven Conditions")
    cv_range  = np.arange(0, 0.41, 0.02)
    sweep_rows = []
    for cv_v in cv_range:
        if cv_v < 0.02: gr_v = [base_mean] * 6
        else:
            np.random.seed(42)
            raw_v = np.random.normal(base_mean, base_mean*cv_v, 6)
            gr_v  = [max(5, int(round(v/5)*5)) for v in raw_v]
        sweep_p = dict(gr=gr_v, sr_dict={}, bi=0, ss=0, lt=1, S=250, uc=120, hpct=0.20, mult=1)
        rr = {t: compute_mrp(**sweep_p, tech=t) for t in ["EOQ","LUC","LTC"]}
        sweep_rows.append({"CV":round(cv_v,2),
            "EOQ":rr["EOQ"]["total_cost"],"LUC":rr["LUC"]["total_cost"],"LTC":rr["LTC"]["total_cost"]})
    sdf = pd.DataFrame(sweep_rows)

    fig_sweep = go.Figure()
    for tech, col in [("EOQ","#0891b2"),("LUC","#ea580c"),("LTC","#dc2626")]:
        fig_sweep.add_trace(go.Scatter(x=sdf["CV"], y=sdf[tech], name=tech,
            mode="lines+markers", line=dict(color=col, width=2.5), marker=dict(size=5)))
    fig_sweep.add_vline(x=0.24, line_dash="dash", line_color="#94a3b8",
                        annotation_text="SAP-X1 baseline (CV=0.24)", annotation_position="top right")
    fig_sweep.update_layout(title="Total Cost vs Demand CV — EOQ vs LUC vs LTC",
        xaxis_title="Demand CV", yaxis_title="Total Cost (Rs.)", height=380,
        plot_bgcolor="white", paper_bgcolor="white", font_family="IBM Plex Sans",
        legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_sweep, use_container_width=True)

    st.markdown("#### 📋 Breakeven Summary Table")
    brk_rows = []
    for row in sweep_rows:
        eoq_wins = row["EOQ"] < min(row["LUC"], row["LTC"])
        brk_rows.append({"Demand CV":row["CV"],"EOQ Cost":round(row["EOQ"],2),
            "LUC Cost":round(row["LUC"],2),"LTC Cost":round(row["LTC"],2),
            "EOQ Outperforms?":"✅ YES" if eoq_wins else "❌ NO"})
    brkdf = pd.DataFrame(brk_rows)
    def hl_eoq(val):
        if val == "✅ YES": return "background-color:#dcfce7;color:#166534;font-weight:700;"
        if val == "❌ NO":  return "background-color:#fee2e2;color:#991b1b;"
        return ""
    st.dataframe(brkdf.style.applymap(hl_eoq, subset=["EOQ Outperforms?"])
                 .format({"EOQ Cost":"Rs.{:.2f}","LUC Cost":"Rs.{:.2f}","LTC Cost":"Rs.{:.2f}"}),
                 use_container_width=True, height=420)

    breakeven_cv = sdf[sdf["EOQ"] < sdf[["LUC","LTC"]].min(axis=1)]["CV"]
    if len(breakeven_cv) > 0:
        st.markdown(f"""<div class='success-box'>
          <b>EOQ breakeven point: CV ≤ {breakeven_cv.max():.2f}</b><br/>
          Below this threshold EOQ achieves lower total cost than both LUC and LTC.
          SAP-X1 baseline CV = 0.24 is above this threshold.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏭 Practical Scenarios: When EOQ Outperforms in Real Business")
    scenarios = [
        ("🧼 FMCG / Retail Staples","A soap manufacturer ordering palm oil",
         "Demand: 50,000 litres/week — stable year-round. CV ≈ 0.03.",
         "EOQ is mathematically optimal. LUC/LTC find no advantage (all periods identical). EOQ wins on accuracy AND simplicity.",
         "#dbeafe","#1e40af"),
        ("💊 Pharmaceuticals","API sourcing for a blockbuster drug (e.g., paracetamol)",
         "Fixed production schedule, 12-month visibility. CV ≈ 0.02.",
         "EOQ = textbook optimal. LUC/LTC add computational overhead with no cost benefit. Regulatory constraints favour predictable batches.",
         "#dcfce7","#166534"),
        ("🔩 Automotive Stamping","Standard bolt (M6×20) used in every vehicle model",
         "50 bolts/car × 500 cars/day = 25,000/day (constant). CV ≈ 0.01.",
         "EOQ with accurate costs = lowest-cost solution. Industry uses EOQ-based VMI at Tier-1 suppliers.",
         "#fef3c7","#92400e"),
        ("⚗️ Chemical Plants","Ethylene oxide procurement for polyester production",
         "Plant runs at constant rate; demand is deterministic. CV ≈ 0.",
         "Large order sizes, well-defined storage costs → EOQ provably optimal. LUC/LTC give identical groupings with more effort.",
         "#f3e8ff","#7c3aed"),
        ("📦 E-Commerce Fulfillment","Shipping boxes (30×20×15 cm) for large-scale fulfillment",
         "Millions of units, stable demand, standardized commodity. CV ≈ 0.04.",
         "EOQ beats LUC/LTC: demand so smooth dynamic methods produce identical groupings. EOQ wins on simplicity and supplier leverage.",
         "#fce7f3","#be185d"),
    ]
    sc_cols = st.columns(2)
    for i, (title, product, condition, reason, bg, fc) in enumerate(scenarios):
        with sc_cols[i % 2]:
            st.markdown(f"""
            <div style='background:{bg};border:1px solid {fc}40;border-radius:10px;
                        padding:16px 18px;margin-bottom:14px;'>
              <div style='font-weight:700;color:{fc};font-size:15px;margin-bottom:4px;'>{title}</div>
              <div style='font-weight:600;color:#1e293b;font-size:13px;margin-bottom:6px;'>📦 {product}</div>
              <div style='font-size:12px;color:#64748b;margin-bottom:8px;'>📊 {condition}</div>
              <div style='font-size:13px;color:#374151;'>💡 {reason}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ✅ Summary: Conditions for EOQ Outperformance")
    sum_col1, sum_col2, sum_col3 = st.columns(3)
    summary_conditions = [
        ("EOQ WINS WHEN",
         ["Demand CV &lt; 0.10 (near-uniform)", "Planning horizon &gt; 12 periods",
          "Costs accurately measured", "Continuous demand flow", "Simplicity is valued"],
         "#dbeafe", "#1e40af"),
        ("LUC WINS WHEN",
         ["Demand CV &gt; 0.15 (lumpy)", "High unit holding cost",
          "Short horizons (3-8 periods)", "Clear peaks and troughs", "Minimising cost-per-unit matters"],
         "#fef3c7", "#92400e"),
        ("LTC WINS WHEN",
         ["HC approx S (similar magnitude)", "Medium demand variability",
          "Short-to-medium horizons", "Balance of both cost types", "Dynamic grouping beneficial"],
         "#fee2e2", "#991b1b"),
    ]
    for sum_col, sum_item in zip([sum_col1, sum_col2, sum_col3], summary_conditions):
        sum_title   = sum_item[0]
        sum_bullets = sum_item[1]
        sum_bg      = sum_item[2]
        sum_fc      = sum_item[3]
        sum_items   = "".join(f"<li>{str(pt)}</li>" for pt in sum_bullets)
        sum_col.markdown(f"""
        <div style='background:{sum_bg};border-left:4px solid {sum_fc};border-radius:0 10px 10px 0;padding:16px 18px;'>
          <div style='font-weight:700;color:{sum_fc};font-size:13px;letter-spacing:0.5px;margin-bottom:10px;'>{sum_title}</div>
          <ul style='font-size:13px;color:#374151;margin:0;padding-left:18px;line-height:1.9;'>{sum_items}</ul>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# TAB 4 — LEVEL 2 SUB-COMPONENTS
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class='hero' style='background:linear-gradient(135deg,#1e1b4b 0%,#312e81 60%,#3730a3 100%);'>
      <h1>🔩 Level 2 MRP — Sub-Component Explosion</h1>
      <p>GR for each Level-2 item = Parent (Level-1) Planned Order Releases × Usage Quantity</p>
      <span class='tag' style='color:#c7d2fe;'>Rotor Unit (RU) ×2/MA</span>
      <span class='tag' style='color:#c7d2fe;'>Housing (HS) ×1/MA</span>
      <span class='tag' style='color:#c7d2fe;'>Filter Media (FM) ×1/FU</span>
      <span class='tag' style='color:#c7d2fe;'>Plastic Frame (PF) ×1/FU</span>
    </div>""", unsafe_allow_html=True)

    # BOM Tree
    with st.expander("📋 Product Structure Tree (BOM)", expanded=False):
        st.markdown("""
        ```
        SAP-X1 (Level 0) — Final Product
            ├── Motor Assembly / MA  ×1  (Level 1)   →  LT=1wk, BI=20, SS=10, SR=30 in W12
            │       ├── Rotor Unit / RU  ×2  (Level 2)   →  LT=1wk, BI=0, SS=0, L4L
            │       └── Housing / HS  ×1  (Level 2)   →  LT=1wk, BI=0, SS=0, L4L
            ├── Filter Unit / FU  ×2  (Level 1)   →  LT=2wk, BI=40, SS=20
            │       ├── Filter Media / FM  ×1  (Level 2)   →  LT=1wk, BI=0, SS=0, L4L
            │       └── Plastic Frame / PF  ×1  (Level 2)   →  LT=1wk, BI=0, SS=0, L4L
            └── Control Board / CB  ×1  (Level 1, Purchased)   →  LT=1wk, BI=25, SS=0, MOQ=100
        ```
        *CB has no Level-2 sub-components (purchased item).*
        """)
        st.markdown("""
        <div class='info-box'>
          <b>Assumptions for all Level-2 items</b> (not stated in assignment):<br/>
          Lead Time = 1 week · Beginning Inventory = 0 · Safety Stock = 0 · No Scheduled Receipts · Lot Sizing = L4L<br/>
          <b>Key principle:</b> Level-2 GR timing aligns with Level-1 POREL (when manufacturing starts), not when L1 demand occurs.
        </div>""", unsafe_allow_html=True)

    # Technique selector
    sel_tech4 = st.radio("Select Technique (drives Level-1 POREL → Level-2 GR):",
        TECHNIQUES, format_func=lambda t: f"{t} — {TECH_NAME[t]}",
        horizontal=True, key="tab4_tech")

    tc4 = TECH_COLOR[sel_tech4]
    ma_res = ALL_RESULTS["MA"][sel_tech4]
    fu_res = ALL_RESULTS["FU"][sel_tech4]

    # Show parent POREL reference
    st.markdown(f"""
    <div style='background:{tc4}10; border:1px solid {tc4}40; border-radius:10px;
                padding:12px 18px; margin:10px 0 20px 0;'>
      <span class='tech-badge' style='background:{tc4}; color:white; margin-right:12px;'>{sel_tech4}</span>
      <b style='color:{tc4};'>Parent POREL reference:</b>
      <span style='font-family:IBM Plex Mono; font-size:13px; color:#374151; margin-left:10px;'>
        MA POREL: {' | '.join(f"{ALL_WEEKS[k+2]}={v}" for k,v in sorted(ma_res['POREL'].items()) if 0<=k+2<=7)}
        &nbsp;&nbsp;&nbsp;
        FU POREL: {' | '.join(f"{ALL_WEEKS[k+2]}={v}" for k,v in sorted(fu_res['POREL'].items()) if 0<=k+2<=7)}
      </span>
    </div>""", unsafe_allow_html=True)

    # Show all 4 Level-2 items
    for sub_k in ["RU", "HS", "FM", "PF"]:
        info = LVL2_INFO[sub_k]
        parent_res = ALL_RESULTS[info["parent"]][sel_tech4]
        lvl2_rows, n_ord = compute_lvl2(parent_res["POREL"], info["qty"])

        cc = info["hdr"]; bg_c = info["bg"]

        st.markdown(f"""
        <div style='background:{bg_c}; border-left:4px solid #{cc[1:] if cc.startswith("#") else cc};
                    padding:10px 16px; border-radius:0 8px 8px 0; margin:18px 0 6px 0;
                    display:flex; justify-content:space-between; align-items:center;'>
          <div>
            <span style='font-weight:700;font-size:16px;color:{cc};'>{info["full"]}</span>
            <span style='font-size:12px;color:#64748b;margin-left:14px;'>{info["desc"]}</span>
          </div>
          <div style='text-align:right;'>
            <span style='font-size:11px;color:#94a3b8;'>Parent: </span>
            <span style='font-weight:700;color:{cc};font-family:IBM Plex Mono;'>{COMP_FULL[info["parent"]]} ({info["parent"]})</span>
            <span style='font-size:11px;color:#94a3b8;margin-left:10px;'>Usage: ×{info["qty"]} | Orders: </span>
            <span style='font-weight:700;color:{cc};font-family:IBM Plex Mono;'>{n_ord}</span>
          </div>
        </div>""", unsafe_allow_html=True)

        df4 = make_lvl2_df(lvl2_rows)
        st.dataframe(style_mrp_table(df4, cc, tc4), use_container_width=True, height=255)

        # Quick metrics
        m1, m2, m3, m4 = st.columns(4)
        total_gr = sum(v["GR"] for v in lvl2_rows.values())
        m1.metric("Total GR (all weeks)",  total_gr)
        m2.metric("# Orders",             n_ord)
        m3.metric("Σ On-Hand",            0, help="L4L with BI=0, SS=0 → always 0")
        m4.metric("Holding Cost",         "Rs. 0.00", help="No excess inventory under L4L with 0 starting stock")

    st.markdown("""
    <div class='info-box' style='margin-top:20px;'>
      <b>Reading the Level-2 tables:</b>
      · Row ⑥ (Planned Order Releases) shows when orders must be placed for sub-components.
      · W8/W9 columns appear grey for non-POREL rows — these are pre-planning-horizon periods.
      · CB has no Level-2 sub-components (it is a purchased item with no further BOM explosion).
      · All Level-2 POH = 0 because L4L with BI=0 and SS=0 means ordering exactly what's needed, when needed.
    </div>""", unsafe_allow_html=True)

    # Cross-technique comparison for Level-2
    st.markdown("---")
    st.markdown("### 📊 Level-2 Order Frequency Comparison Across Techniques")
    cmp_rows = []
    for tech in TECHNIQUES:
        for sub_k in ["RU","HS","FM","PF"]:
            info = LVL2_INFO[sub_k]
            pr = ALL_RESULTS[info["parent"]][tech]
            _, n_o = compute_lvl2(pr["POREL"], info["qty"])
            par_gr = [info["qty"] * pr["POREL"].get(i-2, 0) for i in range(8)]
            total_gr = sum(pr["POREL"].get(i,0) * info["qty"] for i in pr["POREL"])
            cmp_rows.append({
                "Technique": tech, "Sub-Component": f"{sub_k} ({info['full'].split('(')[0].strip()})",
                "# Orders": n_o, "Total GR": total_gr, "Parent": info["parent"]
            })
    cmp_df = pd.DataFrame(cmp_rows)

    fig_l2 = px.bar(cmp_df, x="Technique", y="# Orders", color="Sub-Component", barmode="group",
        title="Level-2 Sub-Component Order Frequency by Parent Technique",
        height=350,
        color_discrete_map={
            "RU (Rotor Unit": "#3730a3","HS (Housing": "#0f766e",
            "FM (Filter Media": "#92400e","PF (Plastic Frame": "#9d174d"
        })
    fig_l2.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_family="IBM Plex Sans",
        legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_l2, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
      <b>Key insight:</b> Level-2 order frequency mirrors the parent's lot sizing technique.
      L4L at Level-1 → 6 orders/period at Level-2 (most complex).
      EOQ/FOQ/LUC/LTC at Level-1 → 2 large orders at Level-2, arriving in big batches (W8/W9 and W13/W14).
      POQ creates the most balanced ripple: 2 orders spaced evenly across the horizon.
    </div>""", unsafe_allow_html=True)
