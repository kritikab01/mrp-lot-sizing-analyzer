#  MRP Lot Sizing Analyzer
### SmartHome Appliances — SAP-X1 Smart Air Purifier

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75?style=flat-square&logo=plotly)
![License](https://img.shields.io/badge/License-Academic-green?style=flat-square)

> **Course:** Operations & Supply Chain Management (OSCM)  
> **Institute:** FORE School of Management  
> **Student:** Kritika Bhachawat | Roll No. 065087  
> **Group:** 76–90 | Focus: EOQ outperforms LUC & LTC

---

##  Overview

An interactive **Material Requirements Planning (MRP) dashboard** built with Streamlit that computes and compares all six major lot sizing techniques for the SAP-X1 Smart Air Purifier case study. The app covers both **Level 1** (MA, FU, CB) and **Level 2** (RU, HS, FM, PF) MRP explosions, a full cost analysis, and a live EOQ outperformance lab.

**Live Demo:** [Deploy on Streamlit Cloud](#-deployment)

---

##  Product Structure (BOM)

```
SAP-X1  (Level 0 — Final Product)
    ├── Motor Assembly (MA)  ×1  [LT=1wk, BI=20, SS=10, SR=30 in W12]
    │       ├── Rotor Unit (RU)  ×2  [LT=1wk, BI=0, SS=0]
    │       └── Housing (HS)     ×1  [LT=1wk, BI=0, SS=0]
    ├── Filter Unit (FU)     ×2  [LT=2wk, BI=40, SS=20]
    │       ├── Filter Media (FM)   ×1  [LT=1wk, BI=0, SS=0]
    │       └── Plastic Frame (PF)  ×1  [LT=1wk, BI=0, SS=0]
    └── Control Board (CB)   ×1  [LT=1wk, BI=25, SS=0, MOQ=100]
```

---

##  Features

### 📋 Tab 1 — MRP Tables (All 6 Techniques)
- Select any of the **6 lot sizing techniques** via radio button
- Full **8-column MRP tables** (W8–W15) for all 3 Level-1 components
- Rows: Gross Requirements → Scheduled Receipts → Proj. On-Hand → Net Requirements → Planned Order Receipts → **Planned Order Releases**
- Auto-calculated **EOQ / FOQ / POQ** parameters displayed as formula boxes
- Per-component cost metrics (# orders, Σ On-Hand, Ordering Cost, Holding Cost)

###  Tab 2 — Cost Analysis & Comparison
- Stacked bar chart: Ordering + Holding cost by technique (grand total)
- Per-component cost bar charts (MA, FU, CB separately)
- Order frequency grouped chart
- Average inventory comparison
- Full **pivot table** with colour gradient (green = cheapest → red = most expensive)
- **Q3 analytical answers** (a–e) in expandable sections

###  Tab 3 — EOQ Outperformance Lab *(Roll No. 65087 Special Analysis)*
- **Live sliders** — adjust Demand CV, Ordering Cost, Holding %, Unit Cost, Planning Horizon
- **Real-time cost chart** — EOQ vs LUC vs LTC updates instantly
- **Right / Wrong live verdict** — does EOQ outperform right now?
- **Sensitivity sweep** — line chart of total cost from CV=0 to CV=0.40
- **Auto breakeven table** — exact CV threshold where EOQ starts winning
- **5 industry scenarios** where EOQ outperforms (FMCG, Pharma, Automotive, Chemical, E-Commerce)
- Summary conditions table (when each method wins)

###  Tab 4 — Level 2 Sub-Components *(New in v2)*
- BOM tree expander
- Technique selector drives Level-1 POREL → Level-2 GR cascade
- **4 MRP tables** (RU, HS, FM, PF) — all colour-coded, W8–W15
- Per sub-component metrics
- **Cross-technique order frequency comparison** bar chart
- Insight box on Level-2 ripple effects

###  Sidebar
- Toggle to **override all default parameters** (demand, BI, SS, costs)
- Fully reactive — every chart and table recomputes live

---

##  Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| `streamlit` | ≥ 1.32 | Web framework & UI |
| `pandas` | ≥ 2.0 | Data tables & pivots |
| `numpy` | ≥ 1.24 | Numerical computations |
| `plotly` | ≥ 5.18 | Interactive charts |
| `math` | stdlib | EOQ, ceil calculations |

---

##  Installation & Local Run

### Step 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/mrp-lot-sizing-analyzer.git
cd mrp-lot-sizing-analyzer
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run the app
```bash
streamlit run app.py
```

Opens automatically at **http://localhost:8501**

---

##  Deployment (Streamlit Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set `app.py` as the main file
4. Click **Deploy** — live in ~60 seconds

No additional configuration needed. `requirements.txt` handles all dependencies.

---

##  Lot Sizing Techniques Covered

| Technique | Abbreviation | Logic |
|-----------|-------------|-------|
| Lot-for-Lot | **L4L** | Order exactly = Net Requirement. Zero excess inventory. |
| Economic Order Quantity | **EOQ** | `EOQ = √(2DS/H)`. Order fixed economic batch when NR > 0. |
| Fixed Order Quantity | **FOQ** | EOQ rounded to nearest 10. Fixed batch each trigger. |
| Periodic Order Quantity | **POQ** | `P = round(EOQ ÷ avg demand)` weeks. Cover P periods per order. |
| Least Unit Cost | **LUC** | Extend cycle until `(S + ΣHC) / ΣQty` starts rising. |
| Least Total Cost | **LTC** | Extend cycle until cumulative HC ≈ ordering cost S. |

---

##  Default Input Parameters

### SAP-X1 Weekly Demand (W11–W16)
| W11 | W12 | W13 | W14 | W15 | W16 |
|-----|-----|-----|-----|-----|-----|
| 50 | 60 | 40 | 70 | 60 | 80 |

### Component Parameters
| Component | Lead Time | Beg. Inv | Safety Stock | Order Cost | Unit Cost | Holding % | Special |
|-----------|-----------|----------|--------------|------------|-----------|-----------|---------|
| Motor Assembly (MA) | 1 week | 20 | 10 | Rs. 250 | Rs. 120 | 20% | SR=30 in W12 |
| Filter Unit (FU) | 2 weeks | 40 | 20 | Rs. 180 | Rs. 40 | 25% | — |
| Control Board (CB) | 1 week | 25 | 0 | Rs. 300 | Rs. 200 | 18% | MOQ = 100 units |

---

##  Key Results Summary

| Technique | Grand Total Cost (Rs.) | Rank |
|-----------|----------------------|------|
| **POQ** | **2,248.46** | 🥇 Lowest |
| LTC | 2,322.31 | 🥈 |
| LUC | 2,530.00 | 🥉 |
| FOQ | 2,905.38 | 4th |
| EOQ | 2,927.69 | 5th |
| L4L | 4,024.62 | 6th — Highest |

> POQ wins in this 6-week horizon because the 4-week cycle aligns with the demand pattern.
> L4L has highest cost due to 6 separate ordering events.

---

##  Roll No. 65087 — Special Analysis

**Focus:** Conditions where EOQ outperforms LUC and LTC

In the SAP-X1 case, EOQ does **not** outperform LUC/LTC because demand is lumpy (CV ≈ 0.24). The **EOQ Outperformance Lab** (Tab 3) lets you explore what changes make EOQ win:

- **Breakeven CV ≤ ~0.06** — when demand variability drops below this, EOQ wins
- **Key industries where EOQ wins:** FMCG staples, pharmaceuticals, automotive stamping, chemical plants, e-commerce fulfillment (all with CV < 0.05)

---

##  File Structure

```
mrp-lot-sizing-analyzer/
│
├── app.py               # Main Streamlit application (all logic + UI)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

##  MRP Formulas Reference

```
Gross Requirements (GR)     = Given demand / Parent POREL × usage qty
Scheduled Receipts (SR)     = Pre-placed open orders (given)
Proj. On-Hand (POH)         = POH(t-1) + SR(t) + POR(t) − GR(t)
Net Requirements (NR)       = max(0, GR(t) − POH(t-1) − SR(t) + SS)
Planned Order Receipts(POR) = Per lot sizing rule applied to NR
Planned Order Releases(POREL)= POR shifted back by Lead Time periods

EOQ  = √(2 × D_annual × S / H_annual)
FOQ  = round(EOQ to nearest 10)    [CB: further rounded UP to nearest 100]
POQ  = round(EOQ ÷ avg weekly demand) weeks per cycle
LUC  = Stop adding periods when (S + ΣHC) / ΣQty rises
LTC  = Stop adding periods when |ΣHC − S| is minimised
```

---

##  Acknowledgements

- **FORE School of Management** — OSCM course material
- **SmartHome Appliances case** — Assignment problem set
- Built with [Streamlit](https://streamlit.io) · [Plotly](https://plotly.com) · [Pandas](https://pandas.pydata.org)
