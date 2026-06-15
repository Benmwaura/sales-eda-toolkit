"""
Sales & Revenue EDA Toolkit
============================
A reusable exploratory data analysis toolkit for sales datasets.
Covers data loading, cleaning, statistical summaries, and visualizations.

Usage:
    python src/eda.py --data data/sales_data.csv --output outputs/
"""

import argparse
import os
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.gridspec import GridSpec

warnings.filterwarnings("ignore")

# ── Aesthetic config ──────────────────────────────────────────────────────────
PALETTE = {
    "primary": "#1B4F72",
    "accent": "#2ECC71",
    "warn": "#E74C3C",
    "neutral": "#95A5A6",
    "bg": "#F8F9FA",
}
sns.set_theme(style="whitegrid", palette="Blues_d")
plt.rcParams.update({
    "figure.facecolor": PALETTE["bg"],
    "axes.facecolor": PALETTE["bg"],
    "font.family": "DejaVu Sans",
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
})


# ── 1. Data Loading ───────────────────────────────────────────────────────────
def load_data(filepath: str) -> pd.DataFrame:
    """Load CSV/Excel sales data and parse date columns automatically."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    ext = path.suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(filepath)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Auto-detect and parse date columns
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")

    print(f"✅  Loaded {len(df):,} rows × {df.shape[1]} columns from '{path.name}'")
    return df


# ── 2. Data Quality Report ────────────────────────────────────────────────────
def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Print and return a data quality summary."""
    report = pd.DataFrame({
        "dtype": df.dtypes,
        "nulls": df.isnull().sum(),
        "null_%": (df.isnull().mean() * 100).round(2),
        "unique": df.nunique(),
        "sample": df.iloc[0],
    })
    print("\n📋  Data Quality Report")
    print("=" * 60)
    print(report.to_string())
    print(f"\nShape : {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Duplicates: {df.duplicated().sum():,}\n")
    return report


# ── 3. Statistical Summary ────────────────────────────────────────────────────
def revenue_stats(df: pd.DataFrame, revenue_col: str = "revenue") -> dict:
    """Compute key revenue statistics."""
    if revenue_col not in df.columns:
        raise KeyError(f"Column '{revenue_col}' not found. Available: {list(df.columns)}")

    series = df[revenue_col].dropna()
    stats = {
        "total": series.sum(),
        "mean": series.mean(),
        "median": series.median(),
        "std": series.std(),
        "min": series.min(),
        "max": series.max(),
        "q25": series.quantile(0.25),
        "q75": series.quantile(0.75),
    }

    print("\n💰  Revenue Statistics")
    print("=" * 40)
    for k, v in stats.items():
        print(f"  {k:<10}: ${v:>14,.2f}")

    return stats


# ── 4. Visualizations ─────────────────────────────────────────────────────────
def plot_revenue_overview(
    df: pd.DataFrame,
    revenue_col: str = "revenue",
    date_col: str = "date",
    output_dir: str = "outputs",
):
    """4-panel revenue overview dashboard."""
    os.makedirs(output_dir, exist_ok=True)

    fig = plt.figure(figsize=(18, 12), facecolor=PALETTE["bg"])
    fig.suptitle("Sales & Revenue — EDA Dashboard", fontsize=20, fontweight="bold", y=0.98)
    gs = GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    rev = df[revenue_col].dropna()

    # Panel 1 — Revenue Distribution
    ax1.hist(rev, bins=40, color=PALETTE["primary"], edgecolor="white", linewidth=0.5)
    ax1.axvline(rev.mean(), color=PALETTE["warn"], linestyle="--", linewidth=1.8, label=f"Mean ${rev.mean():,.0f}")
    ax1.axvline(rev.median(), color=PALETTE["accent"], linestyle="-.", linewidth=1.8, label=f"Median ${rev.median():,.0f}")
    ax1.set_title("Revenue Distribution")
    ax1.set_xlabel("Revenue ($)")
    ax1.set_ylabel("Frequency")
    ax1.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax1.legend(fontsize=9)

    # Panel 2 — Revenue Over Time (if date column available)
    if date_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[date_col]):
        ts = df.groupby(df[date_col].dt.to_period("M"))[revenue_col].sum()
        ts.index = ts.index.to_timestamp()
        ax2.fill_between(ts.index, ts.values, alpha=0.3, color=PALETTE["primary"])
        ax2.plot(ts.index, ts.values, color=PALETTE["primary"], linewidth=2)
        ax2.set_title("Monthly Revenue Trend")
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Revenue ($)")
        ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1e3:,.0f}K"))
        ax2.tick_params(axis="x", rotation=30)
    else:
        ax2.text(0.5, 0.5, "No date column found\nfor time series", ha="center", va="center",
                 transform=ax2.transAxes, color=PALETTE["neutral"], fontsize=12)
        ax2.set_title("Monthly Revenue Trend")

    # Panel 3 — Box plot (detect categorical column)
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        cat_col = cat_cols[0]
        top_cats = df[cat_col].value_counts().nlargest(8).index
        filtered = df[df[cat_col].isin(top_cats)]
        filtered.boxplot(
            column=revenue_col, by=cat_col, ax=ax3,
            boxprops=dict(color=PALETTE["primary"]),
            medianprops=dict(color=PALETTE["warn"], linewidth=2),
            whiskerprops=dict(color=PALETTE["neutral"]),
            patch_artist=True,
        )
        plt.sca(ax3)
        plt.xticks(rotation=30, ha="right")
        ax3.set_title(f"Revenue by {cat_col.replace('_', ' ').title()}")
        ax3.set_xlabel("")
        ax3.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        fig.suptitle("Sales & Revenue — EDA Dashboard", fontsize=20, fontweight="bold", y=0.98)
    else:
        # Fallback: Q-Q plot
        from scipy import stats as scipy_stats
        (osm, osr), (slope, intercept, r) = scipy_stats.probplot(rev, dist="norm")
        ax3.scatter(osm, osr, s=10, alpha=0.6, color=PALETTE["primary"])
        ax3.plot(osm, slope * np.array(osm) + intercept, color=PALETTE["warn"], linewidth=2)
        ax3.set_title("Q-Q Plot (Revenue)")
        ax3.set_xlabel("Theoretical Quantiles")
        ax3.set_ylabel("Sample Quantiles")

    # Panel 4 — Correlation heatmap (numeric columns)
    num_df = df.select_dtypes(include="number")
    if num_df.shape[1] >= 2:
        corr = num_df.corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(
            corr, mask=mask, ax=ax4, annot=True, fmt=".2f",
            cmap="Blues", linewidths=0.5,
            cbar_kws={"shrink": 0.8},
        )
        ax4.set_title("Numeric Correlation Matrix")
    else:
        ax4.text(0.5, 0.5, "Not enough numeric\ncolumns for correlation",
                 ha="center", va="center", transform=ax4.transAxes,
                 color=PALETTE["neutral"], fontsize=12)
        ax4.set_title("Correlation Matrix")

    out_path = Path(output_dir) / "revenue_overview.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\n📊  Dashboard saved → {out_path}")
    plt.close()


def plot_top_performers(
    df: pd.DataFrame,
    revenue_col: str = "revenue",
    group_col: str = "product",
    top_n: int = 10,
    output_dir: str = "outputs",
):
    """Horizontal bar chart of top N performers by revenue."""
    os.makedirs(output_dir, exist_ok=True)

    if group_col not in df.columns:
        print(f"⚠️  Column '{group_col}' not found — skipping top performers chart.")
        return

    top = (
        df.groupby(group_col)[revenue_col]
        .sum()
        .nlargest(top_n)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=PALETTE["bg"])
    colors = [PALETTE["accent"] if i == len(top) - 1 else PALETTE["primary"]
              for i in range(len(top))]
    bars = ax.barh(top.index, top.values, color=colors, edgecolor="white")

    for bar, val in zip(bars, top.values):
        ax.text(
            bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
            f"${val:,.0f}", va="center", fontsize=9, color=PALETTE["primary"],
        )

    ax.set_title(f"Top {top_n} {group_col.replace('_', ' ').title()}s by Revenue",
                 fontsize=15, fontweight="bold")
    ax.set_xlabel("Total Revenue ($)")
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1e3:,.0f}K"))
    ax.set_facecolor(PALETTE["bg"])
    fig.tight_layout()

    out_path = Path(output_dir) / f"top_{group_col}s.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"📊  Top performers chart saved → {out_path}")
    plt.close()


# ── 5. Sample Data Generator ──────────────────────────────────────────────────
def generate_sample_data(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generate a realistic synthetic sales dataset."""
    rng = np.random.default_rng(seed)

    products = ["Laptop Pro", "Wireless Mouse", "USB Hub", "Monitor 4K",
                "Keyboard Mech", "Webcam HD", "Headset Pro", "SSD 1TB"]
    regions = ["North", "South", "East", "West", "Central"]
    channels = ["Online", "In-Store", "Wholesale", "Partner"]

    df = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=n, freq="h")[:n],
        "product": rng.choice(products, n),
        "region": rng.choice(regions, n),
        "channel": rng.choice(channels, n),
        "units_sold": rng.integers(1, 50, n),
        "unit_price": rng.uniform(10, 2000, n).round(2),
        "discount_pct": rng.choice([0, 5, 10, 15, 20], n),
        "customer_age": rng.integers(18, 70, n),
        "customer_satisfaction": rng.uniform(1, 5, n).round(1),
    })

    df["revenue"] = (
        df["units_sold"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
    ).round(2)

    # Inject ~2% nulls realistically
    for col in ["discount_pct", "customer_satisfaction"]:
        null_idx = rng.choice(df.index, size=int(n * 0.02), replace=False)
        df.loc[null_idx, col] = np.nan

    return df


# ── 6. CLI Entry Point ────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Sales EDA Toolkit")
    parser.add_argument("--data", type=str, default=None,
                        help="Path to sales CSV/Excel file. Omit to use generated sample data.")
    parser.add_argument("--revenue-col", type=str, default="revenue")
    parser.add_argument("--date-col", type=str, default="date")
    parser.add_argument("--group-col", type=str, default="product",
                        help="Column to group by in top-performers chart.")
    parser.add_argument("--output", type=str, default="outputs")
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()

    print("\n🔍  Sales & Revenue EDA Toolkit")
    print("=" * 45)

    if args.data:
        df = load_data(args.data)
    else:
        print("ℹ️  No data file provided — generating synthetic sample data...")
        df = generate_sample_data(n=2000)
        sample_path = Path(args.output) / "sample_sales_data.csv"
        os.makedirs(args.output, exist_ok=True)
        df.to_csv(sample_path, index=False)
        print(f"💾  Sample data saved → {sample_path}")

    data_quality_report(df)
    revenue_stats(df, revenue_col=args.revenue_col)
    plot_revenue_overview(df, revenue_col=args.revenue_col,
                          date_col=args.date_col, output_dir=args.output)
    plot_top_performers(df, revenue_col=args.revenue_col,
                        group_col=args.group_col, top_n=args.top_n,
                        output_dir=args.output)

    print("\n✅  EDA complete! Check the outputs/ folder for charts.\n")


if __name__ == "__main__":
    main()
