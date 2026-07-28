# PulseBoard – Retail Data Engineering & Analytics Platform

## Overview

PulseBoard is a Python-based Data Engineering and Analytics application developed for the fictional retail company **NovaMart**.

The application generates intentionally dirty retail datasets, builds a complete data engineering pipeline to clean and transform the data, performs analytical reporting, detects anomalies, and produces management dashboards through a Command Line Interface (CLI).

This project demonstrates practical skills in:

* Data Generation
* Data Engineering
* Data Cleaning
* Data Profiling
* Data Analysis
* Time Series Analysis
* Data Visualization
* Dashboard Development
* Command Line Applications

---

# Features

## Part A – Dirty Dataset Generator

Generates realistic retail datasets for 2025–2026.

Generated files:

* sales_2025.csv
* sales_2026.csv
* stores.json
* products.xlsx
* customer_footfall.csv
* returns.csv

The generator intentionally injects multiple real-world data quality issues including:

* Missing values
* Duplicate transactions
* Mixed date formats
* Inconsistent category names
* Invalid values
* Orphan Store IDs
* Multiple currencies
* Mixed timezone timestamps
* Missing time-series records

---

## Part B – Data Engineering Pipeline

The `DataPipeline` class automatically performs:

* Load CSV, JSON and Excel files
* Data profiling
* Data quality report generation
* Date parsing
* Category normalization
* Missing value handling
* Duplicate removal
* Invalid value correction
* Currency normalization
* Dataset merging
* Reshaping using Pandas
* Export cleaned Parquet dataset

Generated outputs:

* clean_sales.parquet
* quality_report.html

---

## Part C – Analytics

The Jupyter notebook (`analysis.ipynb`) contains solutions for all required analytical tasks.

Implemented analyses include:

1. Monthly Revenue Trend
2. Revenue Rolling Average
3. Weekly & Yearly Seasonality
4. Store Footfall Heatmap
5. Revenue Anomaly Detection
6. Pareto Analysis
7. Cross Correlation
8. Return Rate Analysis
9. Additional Business Insight

The notebook includes:

* 8+ charts
* Seaborn visualizations
* NumPy-based anomaly detection
* Written business interpretations

---

## Part D – Dashboard

PulseBoard generates a management dashboard containing:

### KPIs

* Total Revenue
* Total Profit
* Transactions
* Return Rate
* Average Discount

### Charts

* Revenue Trend
* Revenue by Category
* Top Products
* Payment Type Distribution
* Revenue Distribution
* Daily Footfall
* Return Rate Heatmap
* Revenue Anomaly Detection

Dashboard exports:

* dashboard.html
* dashboard.pdf
* dashboard.png

---

## Part E – Command Line Interface

PulseBoard can be executed entirely through the CLI.

Available commands:

```bash
python pulseboard.py generate
```

Generate dirty datasets.

```bash
python pulseboard.py clean
```

Run the complete data engineering pipeline.

```bash
python pulseboard.py report --month 2025-06 --region North
```

Generate a management dashboard.

```bash
python pulseboard.py anomalies --store S013
```

Display revenue anomalies for a store.

```bash
python pulseboard.py export --format html
```

Export cleaned datasets.

Supported export formats:

* HTML
* CSV
* Excel

---

# Project Structure

```
PulseBoard/
│
├── data/
│   ├── raw/
│   │   ├── sales_2025.csv
│   │   ├── sales_2026.csv
│   │   ├── stores.json
│   │   ├── products.xlsx
│   │   ├── customer_footfall.csv
│   │   └── returns.csv
│   │
│   └── clean/
│       ├── clean_sales.parquet
│       ├── quality_report.html
│       ├── dashboard.html
│       ├── dashboard.pdf
│       └── dashboard.png
│
├── src/
│   ├── __init__.py
│   ├── generate_data.py
│   ├── dirty_data.py
│   ├── pipeline.py
│   ├── dashboard.py
│   └── analysis.ipynb
│
├── pulseboard.py
├── requirements.txt
└── README.md
```

---

# Installation

Clone the repository.

```bash
git clone <repository-url>
```

Navigate to the project.

```bash
cd PulseBoard
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate the environment.

Windows

```bash
venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# Required Libraries

* pandas
* numpy
* matplotlib
* seaborn
* openpyxl
* pyarrow
* xlsxwriter
* jupyter
* streamlit

---

# Running the Project

## 1. Generate Dirty Dataset

```bash
python pulseboard.py generate
```

Outputs:

```
sales_2025.csv
sales_2026.csv
stores.json
products.xlsx
returns.csv
customer_footfall.csv
```

---

## 2. Run the Data Pipeline

```bash
python pulseboard.py clean
```

Outputs:

```
clean_sales.parquet
quality_report.html
```

---

## 3. Generate Dashboard

```bash
python pulseboard.py report --month 2025-06 --region North
```

Outputs:

```
dashboard.html
dashboard.pdf
dashboard.png
```

---

## 4. Detect Anomalies

```bash
python pulseboard.py anomalies --store S013
```

---

## 5. Export Clean Dataset

HTML

```bash
python pulseboard.py export --format html
```

CSV

```bash
python pulseboard.py export --format csv
```

Excel

```bash
python pulseboard.py export --format excel
```

---

# Data Quality Report

The pipeline automatically creates a Data Quality Report.

The report includes:

* Missing Values (%)
* Duplicate Rows
* Invalid Values
* Data Types
* Orphan Records
* Outlier Detection

Exported as:

```
quality_report.html
```

---

# Technologies Used

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* OpenPyXL
* PyArrow
* Jupyter Notebook
* Streamlit (Optional)

---

# Error Handling

The application provides user-friendly error messages.

Examples:

Invalid Store ID

```
Store S999 not found.
```

Missing Raw Data

```
Raw data not found.

Run:

python pulseboard.py generate
```

Invalid Month

```
Invalid month format.

Example:

2025-06
```

---

# Performance

The pipeline is designed to:

* Process approximately 300,000+ records
* Use vectorized Pandas operations
* Avoid row-wise `.apply()` on the main sales dataset
* Export optimized Parquet files

---

# Future Improvements

Possible future enhancements include:

* Interactive Streamlit Dashboard
* Forecasting using Machine Learning
* Database Backend Integration
* Scheduled ETL Pipeline
* REST API
* Docker Deployment
* Cloud Storage Integration

---

# Author

Developed as part of the **PulseBoard – Retail Data Engineering & Analytics** project for the NovaMart analytics case study.
