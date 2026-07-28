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

        for name, df in datasets.items():

            for col in df.columns:

                report.append({

                    "dataset": name,

                    "column": col,

                    "dtype": str(df[col].dtype),

                    "missing_percent":

                        round(

                            df[col].isna().mean()*100,

                            2

                        ),

                    "duplicates":

                        df.duplicated().sum()

                })

        self.quality_report = pd.DataFrame(report)

        return self.quality_report   
     

    def clean_dates(self):

        date_columns = [

            (self.sales, ["date"]),

            (self.stores, ["opened_date"]),

            (self.products, ["launch_date"]),

            (self.returns, ["return_date"]),

            (self.footfall, ["timestamp"])

        ]

        for df, columns in date_columns:

            for col in columns:

                if col in df.columns:

                    df[col] = pd.to_datetime(
                        df[col],
                        errors="coerce",
                        utc=True
                    )
                
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