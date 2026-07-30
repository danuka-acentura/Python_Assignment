import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw"

np.random.seed(42)
        
def inject_missing_values():

    files = [
        "sales_2025.csv",
        "sales_2026.csv"
    ]

    numeric_columns = [
        "units",
        "unit_price",
        "discount_pct"
    ]

    date_columns = [
        "date"
    ]

    for file in files:

        df = pd.read_csv(RAW_DATA / file)

        # Numeric columns -> np.nan only
        for col in numeric_columns:

            idx = df.sample(frac=0.03).index

            df.loc[idx, col] = np.nan

        # Date columns -> mix np.nan and empty string
        for col in date_columns:

            idx = df.sample(frac=0.03).index

            half = len(idx) // 2

            df.loc[idx[:half], col] = np.nan
            df.loc[idx[half:], col] = ""

        df.to_csv(RAW_DATA / file, index=False)
        
        
def inject_duplicates():

    for file in ["sales_2025.csv", "sales_2026.csv"]:

        df = pd.read_csv(RAW_DATA / file)

        duplicates = df.sample(
            frac=0.01,
            random_state=42
        )

        df = pd.concat(
            [df, duplicates],
            ignore_index=True
        )

        df.to_csv(
            RAW_DATA / file,
            index=False
        )
        
def inject_date_formats():

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%b %d, %Y"
    ]

    for file in ["sales_2025.csv", "sales_2026.csv"]:

        df = pd.read_csv(RAW_DATA / file)

        df["date"] = pd.to_datetime(df["date"])

        choices = np.random.choice(
            formats,
            len(df)
        )

        df["date"] = [

            d.strftime(fmt)

            for d, fmt in zip(
                df["date"],
                choices
            )

        ]

        df.to_csv(
            RAW_DATA / file,
            index=False
        )
        
def inject_category_cases():

    df = pd.read_excel(
        RAW_DATA / "products.xlsx"
    )

    def convert(text):

        r = np.random.randint(3)

        if r == 0:
            return text.lower()

        elif r == 1:
            return text.upper()

        return text

    df["category"] = df["category"].apply(convert)

    df.to_excel(
        RAW_DATA / "products.xlsx",
        index=False
    )
    
def inject_invalid_values():

    for file in [
        "sales_2025.csv",
        "sales_2026.csv"
    ]:

        df = pd.read_csv(
            RAW_DATA / file
        )

        idx = df.sample(
            frac=0.01,
            random_state=42
        ).index

        third = len(idx) // 3

        df.loc[
            idx[:third],
            "units"
        ] = -np.random.randint(1, 100)

        df.loc[
            idx[third:2*third],
            "unit_price"
        ] = -np.random.randint(0, 100)

        df.loc[
            idx[2*third:],
            "discount_pct"
        ] = np.random.randint(101, 200)

        df.to_csv(
            RAW_DATA / file,
            index=False
        )
        
def inject_orphan_store_ids():

    invalid = [
        "S999",
        "S888",
        "S777"
    ]

    for file in [
        "sales_2025.csv",
        "sales_2026.csv"
    ]:

        df = pd.read_csv(
            RAW_DATA / file
        )

        idx = df.sample(
            frac=0.01,
            random_state=42
        ).index

        df.loc[
            idx,
            "store_id"
        ] = np.random.choice(
            invalid,
            len(idx)
        )

        df.to_csv(
            RAW_DATA / file,
            index=False
        )
        
def inject_currency_changes():

    df = pd.read_csv(
        RAW_DATA / "sales_2025.csv"
    )

    df["currency"] = "LKR"

    df.to_csv(
        RAW_DATA / "sales_2025.csv",
        index=False
    )

    df = pd.read_csv(
        RAW_DATA / "sales_2026.csv"
    )

    df["currency"] = "USD"

    df["unit_price"] = (
        df["unit_price"] / 300
    ).round(2)

    df.to_csv(
        RAW_DATA / "sales_2026.csv",
        index=False
    )
    
def inject_timezone_mix():

    df = pd.read_csv(RAW_DATA / "customer_footfall.csv")

    # Parse timestamps
    timestamps = pd.to_datetime(df["timestamp"])

    # Convert entire column to object (string-capable)
    df["timestamp"] = timestamps.astype(object)

    idx = df.sample(frac=0.5).index

    # Half remain naive
    df["timestamp"] = df["timestamp"].astype(str)

    # Selected rows become UTC-aware strings
    aware = (
        timestamps.loc[idx]
        .dt.tz_localize("UTC")
        .astype(str)
    )

    df.loc[idx, "timestamp"] = aware

    df.to_csv(
        RAW_DATA / "customer_footfall.csv",
        index=False
    )
    
def inject_footfall_gaps():

    df = pd.read_csv(
        RAW_DATA / "customer_footfall.csv"
    )

    remove = df.sample(
        frac=0.02,
        random_state=42
    ).index

    df = df.drop(remove)

    df.to_csv(
        RAW_DATA / "customer_footfall.csv",
        index=False
    )
    
def inject_dirty_data():

    print("Injecting date formats...")
    inject_date_formats()
        
    print("Injecting missing values...")
    inject_missing_values()

    print("Injecting duplicates...")
    inject_duplicates()

    print("Injecting category inconsistencies...")
    inject_category_cases()

    print("Injecting invalid values...")
    inject_invalid_values()

    print("Injecting orphan store IDs...")
    inject_orphan_store_ids()

    print("Injecting currency changes...")
    inject_currency_changes()

    print("Injecting timezone inconsistencies...")
    inject_timezone_mix()

    print("Injecting footfall gaps...")
    inject_footfall_gaps()

    print("Dirty dataset generated successfully.")

