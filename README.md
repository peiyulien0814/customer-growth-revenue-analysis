# Customer Growth & Revenue Analysis

**[View Live Interactive Dashboard](https://customer-growth-revenue-analysis-euprnnc5liwmbrwhrauiey.streamlit.app)**

**[View Business Case Study (PDF)](Business_Case_Study_3_Pages.pdf)**

**A reproducible business analytics case study on actual UCI Online Retail transactions (2010–2011).**

> Portfolio exercise. Historical public dataset; not a commissioned business engagement. Python, SQL, and dashboard code were initially prepared with AI assistance and should be reviewed and explained by the presenter.

## Deliverables
- **Live dashboard:** [Open Interactive Dashboard](https://customer-growth-revenue-analysis-euprnnc5liwmbrwhrauiey.streamlit.app)
- **Three-page case study:** [`Business_Case_Study_3_Pages.pdf`](Business_Case_Study_3_Pages.pdf)
- **Excel analytics report:** [`Retail_Analysis_UCI_REAL.xlsx`](Retail_Analysis_UCI_REAL.xlsx)
- **Data pipeline:** `src/pipeline.py` (Python -> SQLite -> aggregated CSVs)
- **SQL:** `sql/business_queries.sql`
- **Interview talk track:** `INTERVIEW_TALK_TRACK.md`

## Verified results
| Metric | Value |
|---|---:|
| Source rows | 541,909 |
| Included positive-sale lines | 530,104 |
| Positive sales, excluding returns | £10,666,684.54 |
| Unique sale invoices | 19,960 |
| Average positive-sales amount / invoice | £534.40 |
| Identified customers | 4,338 |
| Customers with 2+ sale invoices | 2,845 / 4,338 (65.6%) |
| UK positive sales | £9,025,222.08 (84.6%) |

**Definitions / cautions:** excludes cancelled and nonpositive lines, does not offset refunds. This is not net revenue, profit, marketing ROI or website conversion. 132,220 included positive-sale lines lack customer ID; customer analyses exclude them. December 2011 ends on Dec 9; no full-month comparison. Some product descriptions represent postage and fees.

## Run the dashboard
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Uses precomputed, real-data output CSVs under `outputs/`, included in this repo. No raw dataset is required just to run the dashboard.

## Reproduce the analysis
Download original `Online Retail.xlsx` from [UCI](https://archive.ics.uci.edu/dataset/352/online+retail) and place it under `data/Online Retail.xlsx`. Then:
```bash
python src/pipeline.py --input 'data/Online Retail.xlsx' --output outputs
```
This also generates `outputs/retail_analysis.sqlite`, excluded from Git. The original data are deliberately not redistributed in this repository. Dataset author: Daqing Chen, UCI ML Repository, DOI 10.24432/C5BW33, CC BY 4.0.

## Practical recommendations (not achieved outcomes)
1. Test first-to-second purchase reminders using randomized treatment/control and 30/60-day reorder rates.
2. Pilot bundle/shipping threshold incentives, measuring contribution margin, not only invoice size.
3. Clean fee/charge codes and improve customer ID completeness to make dashboards reliable.

## Project layout
`app.py` dashboard · `outputs/` real-data aggregates · `src/` data transformation · `sql/` queries · Excel report · PDF case study · presentation notes.

## Status
Dashboard application is prepared for deployment. No live public URL exists until the repository is pushed and the app is deployed through your own account.
