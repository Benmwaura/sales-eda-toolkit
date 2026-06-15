# 📊 Sales & Revenue EDA Toolkit

A clean, reusable **Exploratory Data Analysis** toolkit for sales datasets — built for data analysts who want production-ready insights fast.

---

## Features

- **Automatic data loading** — CSV & Excel, with smart date detection
- **Data quality report** — nulls, uniques, dtypes at a glance
- **Revenue statistics** — mean, median, std, quartiles, total
- **4-panel dashboard** — distribution, time series, category boxplot, correlation heatmap
- **Top-N performers chart** — by any grouping column (product, region, channel…)
- **Synthetic data generator** — run end-to-end with no data needed
- **CLI interface** — one command, all outputs
- **Unit tested** — pytest suite included

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/your-username/sales-eda-toolkit.git
cd sales-eda-toolkit

# 2. Install dependencies
pip install -r requirements.txt

# 3a. Run on your own data
python src/eda.py --data data/your_file.csv --revenue-col revenue --group-col product

# 3b. Run with synthetic sample data (no file needed)
python src/eda.py
```

Charts are saved to `outputs/`.

---

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--data` | *(none)* | Path to CSV or Excel file |
| `--revenue-col` | `revenue` | Name of the revenue column |
| `--date-col` | `date` | Name of the date column |
| `--group-col` | `product` | Column used in top-performers chart |
| `--top-n` | `10` | How many top performers to show |
| `--output` | `outputs` | Directory to save charts |

---

## Expected Data Format

Your CSV/Excel should have at minimum a **revenue column**. Everything else is optional but enriches the analysis:

| Column | Type | Notes |
|--------|------|-------|
| `date` | datetime | Enables time-series chart |
| `revenue` | float | Required |
| `product` | string | Groups top-performer chart |
| `region` | string | Any categorical column works |
| `units_sold` | int | Used in correlation matrix |
| `discount_pct` | float | Used in correlation matrix |

---

## Output Examples

Running the toolkit produces:

```
outputs/
├── revenue_overview.png     ← 4-panel EDA dashboard
├── top_products.png         ← horizontal bar chart
└── sample_sales_data.csv    ← generated data (if no input file)
```

---

## Project Structure

```
sales-eda-toolkit/
├── src/
│   └── eda.py          # Main toolkit (load → clean → stats → plots)
├── tests/
│   └── test_eda.py     # Pytest unit tests
├── data/               # Put your input files here
├── outputs/            # Charts are saved here
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## License

MIT — free to use, adapt, and share.
