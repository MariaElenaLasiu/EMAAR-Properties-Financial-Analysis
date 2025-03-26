#####################################################################
##########  EMAAR Properties : Data cleaning & preparation ##########
#####################################################################

## By Maria Elena Lasiu 

import pandas as pd
import matplotlib.pyplot as plt

# Load the datasets
df_balance = pd.read_csv("official_emaar_balance_sheet.csv")
df_income = pd.read_csv("official_emaar_income_statement.csv")
df_cashflow = pd.read_csv("official_emaar_cash_flow.csv")


# Rename columns
df_balance.rename(columns={"Unnamed: 0":"Metric", "31/12/2024":"2024", "31/12/2023":"2023", "31/12/2022":"2022", "31/12/2021":"2021"}, inplace=True)

df_income.rename(columns={"Unnamed: 0":"Metric", "31/12/2024":"2024", "31/12/2023":"2023", "31/12/2022":"2022", "31/12/2021":"2021"}, inplace=True)

df_cashflow.rename(columns={"Unnamed: 0":"Metric", "31/12/2024":"2024", "31/12/2023":"2023", "31/12/2022":"2022", "31/12/2021":"2021"}, inplace=True)

# Convert wide format to long format
df_balance_long = df_balance.melt(id_vars=["Metric"], var_name="Year", value_name="Value")
df_income_long = df_income.melt(id_vars=["Metric"], var_name="Year", value_name="Value")
df_cashflow_long = df_cashflow.melt(id_vars=["Metric"], var_name="Year", value_name="Value")


# Remove blank lines
df_balance_long.dropna(subset=["Metric"], inplace=True)
df_balance_long = df_balance_long[df_balance_long["Metric"].str.strip().astype(bool)]
df_balance_long = df_balance_long[df_balance_long["Value"].astype(str).str.strip() != "–"]

df_income_long.dropna(subset=["Metric"], inplace=True)
df_income_long = df_income_long[df_income_long["Metric"].str.strip().astype(bool)]
df_income_long = df_income_long[df_income_long["Value"].astype(str).str.strip() != "–"]

df_cashflow_long.dropna(subset=["Metric"], inplace=True)
df_cashflow_long = df_cashflow_long[df_cashflow_long["Metric"].str.strip().astype(bool)]
df_cashflow_long = df_cashflow_long[df_cashflow_long["Value"].astype(str).str.strip() != "–"]

# Remove extra rows on income statement
metrics_to_remove = [
    "ATTRIBUTABLE TO:",
    "Earnings per share attributable to the owners of the Company:"
]

# Remove rows where Metric matches those values (case-insensitive + stripped)
df_income_long = df_income_long[~df_income_long["Metric"].str.strip().str.lower().isin([m.lower() for m in metrics_to_remove])]


# Manage missing values
# df_balance_long.fillna(0, inplace=True)
# df_income_long.fillna(0, inplace=True)
# df_cashflow_long.fillna(0, inplace=True)

# Standardise and Capitalise Metric column
df_balance_long["Metric"] = df_balance_long["Metric"].str.lower().str.strip().str.title()
df_income_long["Metric"] = df_income_long["Metric"].str.lower().str.strip().str.title()
df_cashflow_long["Metric"] = df_cashflow_long["Metric"].str.lower().str.strip().str.title()

# Check for duplicates in each dataset
duplicate_balance = df_balance_long[df_balance_long.duplicated()]
duplicate_income = df_income_long[df_income_long.duplicated()]
duplicate_cashflow = df_cashflow_long[df_cashflow_long.duplicated()]

print(f"\n🔍 Duplicate rows in Balance Sheet: {duplicate_balance.shape[0]}")
print(f"🔍 Duplicate rows in Income Statement: {duplicate_income.shape[0]}")
print(f"🔍 Duplicate rows in Cash Flow Statement: {duplicate_cashflow.shape[0]}")

# Categorise items in balance sheet
# Reset index to make sure ordering is clean
df_balance_long.reset_index(drop=True, inplace=True)

# Create a list of unique metrics in order
unique_metrics = df_balance_long["Metric"].drop_duplicates().reset_index(drop=True)

# Build a manual mapping based on position
manual_categories = {}
manual_categories.update({metric: "Assets" for metric in unique_metrics[:13]})
manual_categories.update({metric: "Liabilities" for metric in unique_metrics[13:22]})
manual_categories.update({metric: "Equity" for metric in unique_metrics[22:29]})

df_balance_long["Category"] = df_balance_long["Metric"].map(manual_categories)


#unique_balance_metrics = df_balance_long[df_balance_long["Category"] == "Liabilities"]["Metric"].unique()
#print(unique_balance_metrics)

#unique_balance_counts = df_balance_long.groupby("Category")["Metric"].nunique()
#print(unique_balance_counts)


# Categorise items in income statement
def income_macro_category(metric):
    m = metric.lower()

    if "cost of revenue" in m:
        return "COGS"
    elif "revenue" in m:
        return "Revenue"
    elif "gross profit" in m:
        return "Gross Profit"
    elif any(x in m for x in ["selling", "general", "admin", "marketing", "depreciation", "operating expense"]):
        return "Operating Expenses"
    elif "operating income" in m or "ebit" in m:
        return "Operating Income"
    elif "finance costs" in m:
        return "Finance Costs"
    elif "finance income" in m:
        return "Finance Income"
    elif any(x in m for x in ["non operating", "unusual", "write off", "other income", "share of results of associates and joint ventures", "impairment"]):
        return "Non-Operating Items"
    elif "profit before tax" in m:
        return "Pretax Income"
    elif "tax" in m:
        return "Tax"
    elif any(x in m for x in ["interest", "normalized income", "profit for the year", "owners of the company"]): 
        return "Net Income"
    elif "basic and diluted earnings per share (aed)" in m:
        return "EPS & Shareholders"
    else:
        return "Other"

df_income_long["Category"] = df_income_long["Metric"].apply(income_macro_category)

unique_income_metrics = df_income_long[df_income_long["Category"] == "Non-Operating Items"]["Metric"].unique()
print(unique_income_metrics)

unique_income_counts = df_income_long.groupby("Category")["Metric"].nunique()
print(unique_income_counts)

# Convert variables format
df_balance_long["Metric"] = df_balance_long["Metric"].astype("category")
df_income_long["Metric"] = df_income_long["Metric"].astype("category")
df_cashflow_long["Metric"] = df_cashflow_long["Metric"].astype("category")

df_balance_long["Category"] = df_balance_long["Category"].astype("category")
df_income_long["Category"] = df_income_long["Category"].astype("category")
#df_cashflow_long["Category"] = df_cashflow_long["Category"].astype("category")

df_balance_long["Year"] = df_balance_long["Year"].astype(int)
df_income_long["Year"] = df_income_long["Year"].astype(int)
df_cashflow_long["Year"] = df_cashflow_long["Year"].astype(int)


#Save cleaned data
df_income_long.to_csv("cleaned_income_statement_v2.csv", index=False)
df_balance_long.to_csv("cleaned_balance_sheet_v2.csv", index=False)
df_cashflow_long.to_csv("cleaned_cash_flow_v2.csv", index=False)
