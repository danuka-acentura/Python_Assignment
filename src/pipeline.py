from pathlib import Path
import pandas as pd
import numpy as np
BASE_DIR = Path(__file__).resolve().parent.parent

class DataPipeline:

    def __init__(self):

        self.raw_path = BASE_DIR / "data" / "raw"
        self.clean_path = BASE_DIR / "data" / "clean"

        self.clean_path.mkdir(parents=True, exist_ok=True)

        self.clean_path.mkdir(parents=True, exist_ok=True)

        self.sales2025 = None
        self.sales2026 = None
        self.sales = None
        self.stores = None
        self.products = None
        self.returns = None
        self.footfall = None

        self.rejects = pd.DataFrame()
        self.analytics = None
        
    def load_files(self):

        self.sales2025 = pd.read_csv(
            self.raw_path / "sales_2025.csv"
        )

        self.sales2026 = pd.read_csv(
            self.raw_path / "sales_2026.csv"
        )

        self.sales = pd.concat(
            [
                self.sales2025,
                self.sales2026
            ],
            ignore_index=True
        )

        self.stores = pd.read_json(
            self.raw_path / "stores.json"
        )

        self.products = pd.read_excel(
            self.raw_path / "products.xlsx"
        )

        self.returns = pd.read_csv(
            self.raw_path / "returns.csv"
        )

        self.footfall = pd.read_csv(
            self.raw_path / "customer_footfall.csv"
        )
        
        
    def profile_data(self):

        report = []

        datasets = {
            "sales": self.sales,
            "stores": self.stores,
            "products": self.products,
            "returns": self.returns,
            "footfall": self.footfall
        }

        # -------------------------------
        # Orphan store ids
        # -------------------------------

        orphan_store_ids = (
            ~self.sales["store_id"].isin(
                self.stores["store_id"]
            )
        ).sum()

        # -------------------------------
        # Orphan product ids
        # -------------------------------

        orphan_product_ids = (
            ~self.sales["product_id"].isin(
                self.products["product_id"]
            )
        ).sum()

        # -------------------------------
        # Orphan transaction ids
        # -------------------------------

        orphan_transactions = (
            ~self.returns["transaction_id"].isin(
                self.sales["transaction_id"]
            )
        ).sum()

        # -------------------------------
        # Loop every dataset
        # -------------------------------

        for name, df in datasets.items():

            duplicate_rows = df.duplicated().sum()

            for col in df.columns:

                dtype = str(df[col].dtype)

                missing = round(
                    df[col].isna().mean() * 100,
                    2
                )

                # ------------------------
                # dtype issue
                # ------------------------

                dtype_issue = "No"

                if df[col].dtype == object:

                    sample = df[col].dropna().head(50)

                    try:

                        pd.to_numeric(sample)

                        dtype_issue = "Possible numeric stored as text"

                    except:

                        try:

                            pd.to_datetime(sample)

                            dtype_issue = "Possible date stored as text"

                        except:

                            pass

                # ------------------------
                # out of range values
                # ------------------------

                out_of_range = 0

                if col == "units":

                    out_of_range = (
                        df[col] < 0
                    ).sum()

                elif col == "unit_price":

                    out_of_range = (
                        df[col] <= 0
                    ).sum()

                elif col == "discount_pct":

                    out_of_range = (
                        df[col] > 100
                    ).sum()

                elif col == "footfall":

                    out_of_range = (
                        df[col] < 0
                    ).sum()

                # ------------------------
                # orphan keys
                # ------------------------

                orphan = 0

                if name == "sales" and col == "store_id":

                    orphan = orphan_store_ids

                elif name == "sales" and col == "product_id":

                    orphan = orphan_product_ids

                elif name == "returns" and col == "transaction_id":

                    orphan = orphan_transactions

                report.append({

                    "dataset": name,

                    "column": col,

                    "dtype": dtype,

                    "missing_percent": missing,

                    "duplicates": duplicate_rows,

                    # "dtype_issue": dtype_issue,

                    "orphan_keys": orphan,

                    "out_of_range": out_of_range

                })

        self.quality_report = pd.DataFrame(report)

        return self.quality_report

    def clean_dates(self):

        datasets = [

            (self.sales, "date"),

            (self.stores, "opened_date"),

            (self.products, "launch_date"),

            (self.returns, "return_date"),

            (self.footfall, "timestamp")

        ]

        for df, date_col in datasets:

            if date_col not in df.columns:
                continue

            # Convert everything to string first
            df[date_col] = df[date_col].astype(str).str.strip()

            # Parse mixed date formats
            df[date_col] = pd.to_datetime(
                df[date_col],
                errors="coerce",
                format="mixed",      
                utc=True
            )

            # Remove invalid dates
            df.dropna(subset=[date_col], inplace=True)

            # Sort chronologically
            df.sort_values(date_col, inplace=True)

            # Make tz-aware datetime index
            df.set_index(date_col, inplace=True)

            # Keep the column as well if needed later
            df[date_col] = df.index
            print('df[date_col] : ',df[date_col].head())

                
    def clean_categories(self):

        self.products["category"] = (

            self.products["category"]

            .astype(str)

            .str.strip()

            .str.lower()

            .str.title()

        )

        self.sales["payment_type"] = (

            self.sales["payment_type"]

            .astype(str)

            .str.strip()

            .str.title()

        )
    
    def clean_missing_values(self):

        numeric = [

            "units",

            "unit_price",

            "discount_pct"

        ]

        for col in numeric:

            self.sales[col] = self.sales[col].fillna(

                self.sales[col].median()

            )

        self.sales["payment_type"] = (

            self.sales["payment_type"]

            .fillna(

                self.sales["payment_type"].mode()[0]

            )

        )

        self.footfall["footfall"] = (

            self.footfall["footfall"]

            .interpolate()

        )
        
    def clean_duplicates(self):

        self.sales = self.sales.drop_duplicates()

        self.products = self.products.drop_duplicates()

        self.returns = self.returns.drop_duplicates()

        self.footfall = self.footfall.drop_duplicates()
        
    def clean_invalid_values(self):

        self.sales.loc[

            self.sales["units"] < 0,

            "units"

        ] = np.nan

        self.sales.loc[

            self.sales["unit_price"] <= 0,

            "unit_price"

        ] = np.nan

        self.sales.loc[

            self.sales["discount_pct"] > 100,

            "discount_pct"

        ] = 100

        self.sales["units"] = (

            self.sales["units"]

            .fillna(

                self.sales["units"].median()

            )

        )

        self.sales["unit_price"] = (

            self.sales["unit_price"]

            .fillna(

                self.sales["unit_price"].median()

            )

        )
        
    def normalize_currency(self):

        rate = 300

        usd = self.sales["currency"] == "USD"

        self.sales.loc[

            usd,

            "unit_price"

        ] *= rate

        self.sales["currency"] = "LKR"
        

    def merge_tables(self):

        valid = self.sales["store_id"].isin(
            self.stores["store_id"]
        )

        self.rejects = self.sales.loc[~valid].copy()

        self.sales = self.sales.loc[valid].copy()

        # -----------------------
        # Prepare footfall
        # -----------------------

        self.footfall["timestamp"] = pd.to_datetime(
            self.footfall["timestamp"],
            errors="coerce",
            utc=True
        )

        self.footfall["date"] = (
            self.footfall["timestamp"]
            .dt.floor("D")
        )

        daily_footfall = (

            self.footfall

            .groupby(

                ["store_id", "date"]

            )["footfall"]

            .sum()

            .reset_index()

        )

        # -----------------------
        # Prepare sales date
        # -----------------------

        self.sales["date"] = pd.to_datetime(
            self.sales["date"],
            errors="coerce",
            utc=True
        )

        self.sales["date"] = (
            self.sales["date"]
            .dt.floor("D")
        )

        # -----------------------
        # Merge sales + stores
        # -----------------------

        merged = self.sales.merge(

            self.stores,

            on="store_id",

            how="left"

        )

        # -----------------------
        # Merge products
        # -----------------------

        merged = merged.merge(

            self.products,

            on="product_id",

            how="inner"

        )

        # -----------------------
        # Merge returns
        # -----------------------

        merged = merged.merge(

            self.returns,

            on=["transaction_id", "product_id"],

            how="left"

        )

        # -----------------------
        # Merge footfall
        # -----------------------

        merged = merged.merge(

            daily_footfall,

            on=["store_id", "date"],

            how="left"

        )

        self.analytics = merged
        
        return merged
    

    def reshape_tables(self):

        pivot = self.analytics.pivot_table(

            index="region",

            columns="category",

            values="units",

            aggfunc="sum"

        )

        melted = pivot.reset_index().melt(

            id_vars="region"

        )

        stacked = pivot.stack()

        unstacked = stacked.unstack()

        grouped = self.analytics.groupby(

            "region"

        ).agg(

            total_sales=("units", np.sum),

            avg_price=("unit_price", np.mean),

            total_discount=("discount_pct", np.mean)

        )

        return {

            "pivot": pivot,

            "melt": melted,

            "stack": stacked,

            "unstack": unstacked,

            "groupby": grouped

        }
        
    def save_clean_data(self):

        self.analytics.to_parquet(

            self.clean_path /

            "clean_sales.parquet",

            index=False

        )
        saved_file = self.clean_path / "clean_sales.parquet"
        print("Saved to:", saved_file.resolve())
        print("Exists after save:", saved_file.exists())
        
    def save_quality_report(self):

        styled = (

            self.quality_report

            .style

            .background_gradient(

                subset=["missing_percent"],

                cmap="Reds"

            )
            .background_gradient(
                subset=["out_of_range"],
                cmap="Oranges"
            )
            .background_gradient(
                subset=["orphan_keys"],
                cmap="Purples"
            )

        )

        styled.to_html(

            self.clean_path /

            "quality_report.html"

        )
        
    def run(self):

        self.load_files()

        self.profile_data()

        self.clean_dates()

        self.clean_categories()

        self.clean_missing_values()

        self.clean_duplicates()

        self.clean_invalid_values()

        self.normalize_currency()

        self.merge_tables()

        self.reshape_tables()

        self.save_clean_data()

        self.save_quality_report()

        print("Pipeline completed successfully.")
        
if __name__ == "__main__":

    pipeline = DataPipeline()

    pipeline.run()