# MRP Lot Sizing Analyzer — SmartHome Appliances SAP-X1
### FORE School of Management · OSCM Assignment · Roll No. 87

## How to Run Locally

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Run the app
```bash
streamlit run app.py
```

### Step 3 — Open in browser
Streamlit will automatically open: http://localhost:8501

---

## App Structure

### Tab 1 — 📋 MRP Tables
- Select any of the 6 lot sizing techniques (L4L, EOQ, FOQ, POQ, LUC, LTC)
- See full MRP tables for all 3 components (MA, FU, CB) with all 6 rows
- Cost breakdown per component

### Tab 2 — 💰 Cost Analysis
- Grand total stacked bar chart
- Per-component cost comparison
- Order frequency chart
- Full summary pivot table
- Q3 answers (a–e) in expandable sections

### Tab 3 — 🔬 EOQ Outperformance Lab (Roll #87)
- Live sliders to adjust demand variability, ordering cost, holding cost
- Real-time cost comparison: EOQ vs LUC vs LTC
- Breakeven CV analysis (sensitivity sweep)
- 5 practical industry scenarios where EOQ wins
- Summary conditions table

---

## Parameters (Default = SAP-X1 Assignment Data)
| Component | LT | BI | SS | S (Rs.) | UC (Rs.) | h% |
|-----------|----|----|----|---------|-----------|----|
| Motor Assembly (MA) | 1 wk | 20 | 10 | 250 | 120 | 20% |
| Filter Unit (FU)    | 2 wk | 40 | 20 | 180 |  40 | 25% |
| Control Board (CB)  | 1 wk | 25 |  0 | 300 | 200 | 18% |

Use the **✏️ Override default parameters** toggle in the sidebar to change any value.
