import argparse
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.generate_data import generate_all
from src.pipeline import DataPipeline


BASE_DIR = Path(__file__).resolve().parent
CLEAN_DATA = BASE_DIR / "data" / "clean"


def generate_command():
    """Generate dirty datasets."""
    print("Generating dirty dataset...")
    generate_all()
    print("Dataset generated successfully.")


def clean_command():
    """Run the data engineering pipeline."""
    print("Running data pipeline...")

    pipeline = DataPipeline()
    pipeline.run()

    print("Pipeline completed successfully.")
    print(f"Clean parquet : {CLEAN_DATA / 'clean_sales.parquet'}")
    print(f"Quality report: {CLEAN_DATA / 'quality_report.html'}")


def report_command(month, region):
    """Generate a dashboard for a given month and region."""

    
    parquet = CLEAN_DATA / "clean_sales.parquet"
    print("Looking for:", parquet)
    print("Exists:", parquet.exists())

    if not parquet.exists():
        print("Error: clean_sales.parquet not found.")
        print("Run: python pulseboard.py clean")
        sys.exit(1)

    try:
        month = pd.to_datetime(month)
    except Exception:
        print("Error: Invalid month format.")
        print("Example: 2025-06")
        sys.exit(1)

    df = pd.read_parquet(parquet)

    df["date"] = pd.to_datetime(df["date"])

    df["revenue"] = (
        df["units"]
        * df["unit_price"]
        * (1 - df["discount_pct"] / 100)
    )

    df = df[
        (df["date"].dt.year == month.year)
        &
        (df["date"].dt.month == month.month)
        &
        (df["region"].str.lower() == region.lower())
    ]

    if df.empty:
        print("No records found.")
        return

    fig, ax = plt.subplots(2, 2, figsize=(14, 10))

    # Revenue trend
    trend = (
        df.groupby("date")["revenue"]
        .sum()
        .reset_index()
    )

    sns.lineplot(
        data=trend,
        x="date",
        y="revenue",
        ax=ax[0, 0]
    )

    ax[0, 0].set_title("Revenue Trend")

    # Top products
    top = (
        df.groupby("product_id")["revenue"]
        .sum()
        .nlargest(10)
    )

    sns.barplot(
        x=top.values,
        y=top.index,
        ax=ax[0, 1]
    )

    ax[0, 1].set_title("Top Products")

    # Payment type
    sns.countplot(
        data=df,
        x="payment_type",
        ax=ax[1, 0]
    )

    ax[1, 0].set_title("Payment Types")

    # Category revenue
    cat = (
        df.groupby("category")["revenue"]
        .sum()
        .reset_index()
    )

    sns.barplot(
        data=cat,
        x="category",
        y="revenue",
        ax=ax[1, 1]
    )

    ax[1, 1].tick_params(axis="x", rotation=45)
    ax[1, 1].set_title("Revenue by Category")

    plt.tight_layout()

    output = CLEAN_DATA / "dashboard.html"

    plt.savefig(CLEAN_DATA / "dashboard.png")

    html = f"""
    <html>
    <body>

    <h1>PulseBoard Dashboard</h1>

    <h3>Month : {month.strftime('%Y-%m')}</h3>

    <h3>Region : {region}</h3>

    <img src="dashboard.png" width="1200">

    </body>
    </html>
    """

    output.write_text(html)

    print(f"Dashboard exported to {output}")


def anomalies_command(store):
    """Display anomalies for one store."""

    parquet = CLEAN_DATA / "clean_sales.parquet"

    if not parquet.exists():
        print("Run clean first.")
        return

    df = pd.read_parquet(parquet)

    if store not in df["store_id"].unique():
        print(f"Invalid store id : {store}")
        return

    df["date"] = pd.to_datetime(df["date"])

    df["revenue"] = (
        df["units"]
        * df["unit_price"]
        * (1 - df["discount_pct"] / 100)
    )

    temp = (
        df[df["store_id"] == store]
        .groupby("date")["revenue"]
        .sum()
        .reset_index()
    )

    temp["rolling"] = (
        temp["revenue"]
        .rolling(30)
        .mean()
    )

    temp["std"] = (
        temp["revenue"]
        .rolling(30)
        .std()
    )

    temp["anomaly"] = (
        abs(
            temp["revenue"]
            - temp["rolling"]
        )
        >
        3 * temp["std"]
    )

    plt.figure(figsize=(14, 5))

    plt.plot(
        temp["date"],
        temp["revenue"]
    )

    plt.scatter(
        temp.loc[temp["anomaly"], "date"],
        temp.loc[temp["anomaly"], "revenue"],
        color="red"
    )

    plt.title(f"Revenue Anomalies ({store})")

    plt.show()


def export_command(fmt):
    """Export clean data."""

    parquet = CLEAN_DATA / "clean_sales.parquet"

    if not parquet.exists():
        print("Run clean first.")
        return

    df = pd.read_parquet(parquet)

    fmt = fmt.lower()

    if fmt == "csv":

        df.to_csv(
            CLEAN_DATA / "clean_sales.csv",
            index=False
        )

        print("CSV exported.")

    elif fmt == "excel":

        df.to_excel(
            CLEAN_DATA / "clean_sales.xlsx",
            index=False
        )

        print("Excel exported.")

    elif fmt == "html":

        df.head(100).to_html(
            CLEAN_DATA / "clean_sales.html",
            index=False
        )

        print("HTML exported.")

    else:

        print("Unsupported format.")
        print("Supported: csv, excel, html")


def main():

    parser = argparse.ArgumentParser(
        description="PulseBoard CLI"
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("generate")

    sub.add_parser("clean")

    report = sub.add_parser("report")

    report.add_argument(
        "--month",
        required=True
    )

    report.add_argument(
        "--region",
        required=True
    )

    anomaly = sub.add_parser("anomalies")

    anomaly.add_argument(
        "--store",
        required=True
    )

    export = sub.add_parser("export")

    export.add_argument(
        "--format",
        required=True
    )

    args = parser.parse_args()

    if args.command == "generate":
        generate_command()

    elif args.command == "clean":
        clean_command()

    elif args.command == "report":
        report_command(
            args.month,
            args.region
        )

    elif args.command == "anomalies":
        anomalies_command(
            args.store
        )

    elif args.command == "export":
        export_command(
            args.format
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()