# Retail Sales Dashboard

An end-to-end data analytics project built on a 120,000-transaction retail dataset. Covering exploratory data analysis, data cleaning, feature engineering, and an interactive dashboard deployed to the web.

**[Live dashboard →](https://retailsalesdashboard-mus2mks9jtflo9pmbwzycc.streamlit.app/)**

---

## What this project covers

This project simulates a real client data engagement:

1. **Exploratory data analysis** — profiling the raw dataset, identifying data quality issues, validating business logic, and documenting findings
2. **Data cleaning & feature engineering** — fixing data types, deriving new columns from existing data, and producing a clean dataset ready for analysis
3. **Interactive dashboard** — a deployed web app with live filters, KPI cards, and charts across five analytical sections

---

## Dashboard sections

| Section | Business questions answered |
|---|---|
| Revenue over time | How much are we making? Is it growing month over month? |
| Product performance | What categories drive revenue? What sells at the highest value per unit? |
| Customer insights | Do VIP customers actually spend more? Which age groups buy most? |
| Channel & payment | Where do sales happen — in-store, online, or mobile? |
| Discount analysis | Are discounts driving bigger purchases or just reducing margin? |

---

## Key findings from the data

- **Revenue is stable** — monthly revenue stays consistently around $1.9M with no strong seasonal pattern across 2024–2025
- **Beauty leads in volume, not price** — it's the top category by total revenue, but average revenue per unit is similar across all categories, meaning Beauty wins through transaction count
- **Medium transactions dominate** — the $100–$500 tier accounts for the most transactions and the most total revenue
- **Discounts reduce average order value** — discounted transactions average ~$350 vs ~$400 for full-price, and discount rate is identical across all customer segments (~40%), suggesting discounts are applied randomly rather than strategically
- **Channels are perfectly balanced** — In-Store, Online, and Mobile App each account for roughly 33% of revenue

---

## Data pipeline

```
data/raw/                     # original Kaggle dataset (unmodified)
    retail_sales_dataset.csv

notebooks/
    01_eda.ipynb              # exploratory data analysis
    02_cleaning.ipynb         # cleaning and feature engineering

data/clean/                   # output of cleaning pipeline
    retail_sales_dataset_clean.csv    # 120,000 rows × 26 columns
```

### Cleaning steps applied

| Issue found | Action taken |
|---|---|
| `transaction_date` stored as string | Converted to datetime |
| No missing values | No action needed |
| No duplicate transactions | No action needed |
| No categorical inconsistencies | No action needed |
| Sales amount outliers | Validated as legitimate premium purchases |
| Formula check: `sales_amount` vs `quantity × unit_price × (1 − discount)` | Confirmed consistent — max difference of $0.01 due to rounding |

### Features engineered

| Column | Description |
|---|---|
| `year`, `month`, `quarter` | Extracted from transaction date for time-series grouping |
| `month_name`, `day_of_week` | Human-readable labels for dashboard display |
| `is_weekend` | Boolean flag for behavioral pattern analysis |
| `sales_tier` | Small / Medium / Large / Premium classification by sales amount |
| `revenue_per_unit` | Normalizes revenue across transactions with different quantities |
| `has_discount` | Boolean flag for discount vs full-price comparison |

---

## Tech stack

- **Python** — pandas, numpy
- **Jupyter Notebooks** — EDA and cleaning documentation
- **Plotly** — interactive charts
- **Streamlit** — dashboard framework and deployment

---

## Running locally

```bash
# Clone the repo
git clone https://github.com/AntoBeri/Retail_Sales_Dashboard
cd Retail_Sales_Dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app/dashboard.py
```

> The clean dataset is included in `data/clean/`. The original raw file is not tracked — download it from [Kaggle](https://www.kaggle.com) and place it in `data/raw/` if you want to run the notebooks from scratch.

---

## Project structure

```
Retail_Sales_Dashboard/
│
├── data/
│   ├── raw/                      # original CSV (not tracked in git)
│   └── clean/
│       └── retail_sales_dataset_clean.csv
│
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_cleaning.ipynb
│
├── app/
|   ├──.streamlit/
|   |  └──config.toml
│   └── dashboard.py
│
├── requirements.txt
└── README.md
```
