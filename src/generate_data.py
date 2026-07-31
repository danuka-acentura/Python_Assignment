import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.dirty_data import inject_dirty_data

np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw"
RAW_DATA.mkdir(parents=True, exist_ok=True)

def generate_stores():
    """
    Generate the stores master dataset.
    """

    regions = [
        "North",
        "South",
        "East",
        "West",
        "Central",    
    ]

    cities = [
       "Colombo",
        "Kandy",
        "Galle",
        "Jaffna",
        "Kurunegala",
        "Negombo",
        "Matara",
        "Badulla"
    ]

    stores = []

    for i in range(1, 41):

        stores.append({

            "store_id": f"S{i:03}",

            "region": np.random.choice(regions),

            "city": np.random.choice(cities),

            "opened_date": str(
                pd.Timestamp("2015-01-01")
                + pd.to_timedelta(
                    np.random.randint(0, 3500),
                    unit="D"
                )
            ),

            "sqft": np.random.randint(
                2500,
                12000
            )
        })

    with open(RAW_DATA / "stores.json", "w") as f:
        json.dump(stores, f, indent=4)

    return pd.DataFrame(stores)

def generate_products():

    categories = [
        "Electronics",
        "Groceries",
        "Furniture",
        "Fashion",
        "Sports"
    ]

    subcats = [
        "A",
        "B",
        "C",
        "D"
    ]

    products = []

    for i in range(1, 501):

        products.append({

            "product_id": f"P{i:04}",

            "category": np.random.choice(categories),

            "sub_category": np.random.choice(subcats),

            "cost_price": round(
                np.random.uniform(10, 2000),
                2
            ),

            "launch_date": str(
                pd.Timestamp("2024-01-01")
                + pd.to_timedelta(
                    np.random.randint(0, 730),
                    unit="D"
                )
            )

        })

    df = pd.DataFrame(products)

    df.to_excel(
        RAW_DATA / "products.xlsx",
        index=False
    )

    return df

def generate_sales_2025():

    return generate_sales(2025)

def generate_sales_2026():

    return generate_sales(2026)

def generate_sales(year):

    n = 150000

    dates = pd.date_range(
        f"{year}-01-01",
        f"{year}-12-31",
        freq="D"
    )

    df = pd.DataFrame({

        "transaction_id":
            [f"T{year}{i:07}" for i in range(n)],

        "date":
            np.random.choice(dates, n),

        "store_id":
            np.random.choice(
                [f"S{i:03}" for i in range(1, 41)],
                n
            ),

        "product_id":
            np.random.choice(
                [f"P{i:04}" for i in range(1, 501)],
                n
            ),

        "units":
            np.random.randint(
                1,
                8,
                n
            ),

        "unit_price":
            np.round(
                np.random.uniform(20, 4000, n),
                2
            ),

        "discount_pct":
            np.round(
                np.random.uniform(0, 40, n),
                2
            ),

        "payment_type":
            np.random.choice(
                [
                    "Cash",
                    "Card",
                    "Online"
                ],
                n
            )
    })

    df.to_csv(
        RAW_DATA / f"sales_{year}.csv",
        index=False
    )

    return df

def generate_returns():

    sales = pd.concat([

        pd.read_csv(
            RAW_DATA / "sales_2025.csv"
        ),

        pd.read_csv(
            RAW_DATA / "sales_2026.csv"
        )

    ])

    returns = sales.sample(
        frac=0.05,
        random_state=42
    )

    returns = returns[[
        "transaction_id",
        "product_id"
    ]].copy()

    returns["return_date"] = (
        pd.to_datetime("2025-01-01")
        + pd.to_timedelta(
            np.random.randint(
                0,
                730,
                len(returns)
            ),
            unit="D"
        )
    )

    returns["reason"] = np.random.choice(

        [
            "Damaged",
            "Wrong Item",
            "Customer Changed Mind"
        ],

        len(returns)
    )

    returns.to_csv(
        RAW_DATA / "returns.csv",
        index=False
    )

    return returns

def generate_footfall():

    timestamps = pd.date_range(
        "2025-01-01",
        "2026-12-31 23:00",
        freq="h"
    )

    rows = []

    for store in range(1, 41):

        temp = pd.DataFrame({

            "timestamp": timestamps,

            "store_id": f"S{store:03}",

            "footfall":

                np.random.poisson(
                    60,
                    len(timestamps)
                )
        })

        rows.append(temp)

    df = pd.concat(rows)

    df.to_csv(
        RAW_DATA / "customer_footfall.csv",
        index=False
    )

    return df


def generate_all():

    print("Generating stores...")
    generate_stores()

    print("Generating products...")
    generate_products()

    print("Generating sales 2025...")
    generate_sales_2025()

    print("Generating sales 2026...")
    generate_sales_2026()

    print("Generating returns...")
    generate_returns()

    print("Generating footfall...")
    generate_footfall()

    print("Injecting dirty data...")
    
    inject_dirty_data()

    print("Done.")
    
    
if __name__ == "__main__":
    generate_all()