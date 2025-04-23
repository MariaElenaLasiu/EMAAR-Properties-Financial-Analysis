###############################################################
##########  EMAAR Properties : Analysis and insights ##########
###############################################################

## By Maria Elena Lasiu 

import pandas as pd
import matplotlib.pyplot as plt

# Load the datasets
df_income_long = pd.read_csv("cleaned_income_statement_v2.csv")
df_balance_long = pd.read_csv("cleaned_balance_sheet_v2.csv")
df_cashflow_long = pd.read_csv("cleaned_cash_flow_v2.csv")

# Convert value with floats
df_income_long["Value"] = df_income_long["Value"].astype(str).str.replace(",", "").astype(float)
df_balance_long["Value"] = df_balance_long["Value"].astype(str).str.replace(",", "").astype(float)
df_cashflow_long["Value"] = df_cashflow_long["Value"].astype(str).str.replace(",", "").astype(float)
df_cashflow_long["Metric"] = df_cashflow_long["Metric"].str.lower().str.strip()


# Is Emaar growing?

# Calculate key metrics
revenue = df_income_long[df_income_long["Category"] == "Revenue"]
net_income = df_income_long[df_income_long["Metric"].str.contains("Profit For The Year", case=False, na=False)]
op_expenses = df_income_long[df_income_long["Category"] == "Operating Expenses"]
cost_of_revenue = df_income_long[df_income_long["Metric"].str.contains("Cost of Revenue", case=False, na=False)]
finance_costs = df_income_long[df_income_long["Metric"].str.contains("Finance Costs", case=False, na=False)]

# Aggregate by year
rev = revenue.groupby("Year")["Value"].sum()
ni = net_income.groupby("Year")["Value"].sum()
opexp = op_expenses.groupby("Year")["Value"].sum()
costs = cost_of_revenue.groupby("Year")["Value"].sum()
fin_costs = finance_costs.groupby("Year")["Value"].sum()

# Create summary table with key metrics
df_summary = pd.DataFrame({
    "Revenue": rev,
    "Net Income": ni,
    "Operating Expenses": opexp,
    "Cost of Revenue": costs,
    "Finance Costs": fin_costs
}).fillna(0)

# Sort by year
df_summary = df_summary.sort_index()

# Calculate YoY % change
df_changes = df_summary.pct_change().dropna() * 100
df_changes = df_changes.round(2)

# Print the result
print("Year-over-Year % Change in Financial Metrics:")
print(df_changes)

## In 2022 and 2023, net income increased despite flat or declining revenue due to significant cost reductions. In 2024, revenue grew strongly, but higher production and operating costs reduced profit growth, leading to margin compression. 

#  Calculate CAGR
def calculate_cagr(start_value, end_value, periods):
    return ((end_value / start_value) ** (1 / periods)) - 1

# Define start and end years
start_year = df_summary.index.min()
end_year = df_summary.index.max()
num_years = end_year - start_year

# Calculate Revenue CAGR and Net Income CAGR
rev_start = df_summary.loc[start_year, "Revenue"]
rev_end = df_summary.loc[end_year, "Revenue"]

ni_start = df_summary.loc[start_year, "Net Income"]
ni_end = df_summary.loc[end_year, "Net Income"]

# Calculate CAGR
cagr_revenue = calculate_cagr(rev_start, rev_end, num_years)
cagr_net_income = calculate_cagr(ni_start, ni_end, num_years)

# Print results
print(f"\n📈 Revenue CAGR ({start_year}–{end_year}): {cagr_revenue * 100:.2f}%")
print(f"📈 Net Income CAGR ({start_year}–{end_year}): {cagr_net_income * 100:.2f}%")



# Is Emaar profitable?

# Calculate Gross Margin %
df_summary["Gross Profit"] = df_summary["Revenue"] + df_summary["Cost of Revenue"]
df_summary["Gross Margin (%)"] = (df_summary["Gross Profit"] / df_summary["Revenue"]) * 100

# Calculate Operating Margin %
sga = df_income_long[df_income_long["Metric"].str.contains("Selling, General And Administrative Expenses", case=False, na=False)]
other_op_exp = df_income_long[df_income_long["Metric"].str.contains("Other Operating Expenses", case=False, na=False)]
dep_ppe = df_income_long[df_income_long["Metric"].str.contains("Depreciation Of Property, Plant And Equipment", case=False, na=False)]
dep_inv = df_income_long[df_income_long["Metric"].str.contains("Depreciation Of Investment Properties", case=False, na=False)]

# Group each by year
sga_year = sga.groupby("Year")["Value"].sum()
other_op_year = other_op_exp.groupby("Year")["Value"].sum()
dep_ppe_year = dep_ppe.groupby("Year")["Value"].sum()
dep_inv_year = dep_inv.groupby("Year")["Value"].sum()

# Total Operating Expenses (should be negative)
opexp = sga_year + other_op_year + dep_ppe_year + dep_inv_year

# Calculate the metric
df_summary["Operating Expenses"] = opexp
df_summary["Operating Profit"] = df_summary["Gross Profit"] + df_summary["Operating Expenses"]
df_summary["Operating Margin (%)"] = (df_summary["Operating Profit"] / df_summary["Revenue"]) * 100

# Calculate Net Margin %
df_summary["Net Margin (%)"] = (df_summary["Net Income"] / df_summary["Revenue"]) * 100


# Round for readability
df_summary_rounded = df_summary[[
    "Revenue", "Net Income", "Gross Margin (%)", "Operating Margin (%)", "Net Margin (%)"
]].round(2)

# Display
print("\n📊 Profitability Summary Table:")
print(df_summary_rounded)


## Strong cost control and margin improvement across 2021–2024 show increasing operational efficiency and healthy profitability. Even with a slight dip in margin in 2024, the income-to-revenue ratio remains excellent.

# Calculate EBITDA

# Key metrics
gross_profit = df_income_long[df_income_long["Metric"].str.contains("Gross Profit", case=False, na=False)]
other_op_income = df_income_long[df_income_long["Metric"].str.contains("Other Operating Income", case=False, na=False)]
other_op_expenses = df_income_long[df_income_long["Metric"].str.contains("Other Operating Expenses", case=False, na=False)]
sga_expenses = df_income_long[df_income_long["Metric"].str.contains("Selling, General and Administrative Expenses", case=False, na=False)]
dep_pp_e = df_income_long[df_income_long["Metric"].str.contains("Depreciation of property, plant and equipment", case=False, na=False)]
dep_investment_props = df_income_long[df_income_long["Metric"].str.contains("Depreciation of investment properties", case=False, na=False)]

# Aggregate each item by year
gp = gross_profit.groupby("Year")["Value"].sum()
op_inc = other_op_income.groupby("Year")["Value"].sum()
op_exp = other_op_expenses.groupby("Year")["Value"].sum()
sga = sga_expenses.groupby("Year")["Value"].sum()
dep_ppe = dep_pp_e.groupby("Year")["Value"].sum()
dep_inv = dep_investment_props.groupby("Year")["Value"].sum()

# Compute EBITDA considering negative values of op_exp, sga, dep_ppe, dep_inv
ebitda = gp + op_inc + op_exp + sga + dep_ppe + dep_inv

# Store in summary table
df_summary["EBITDA"] = ebitda
df_summary["EBITDA Margin (%)"] = (df_summary["EBITDA"] / df_summary["Revenue"]) * 100

# Print results
print("\n📊 EBITDA Summary:")
print(df_summary[["EBITDA", "EBITDA Margin (%)"]].round(2))



# Is Emaar growing?

# Calculate key metrics
total_assets = df_balance_long[df_balance_long["Metric"].str.contains("Total Assets", case=False, na=False)]
shareholders_equity = df_balance_long[df_balance_long["Metric"].str.contains("Total Equity", case=False, na=False)]
op_profit = df_summary["Operating Profit"]
debt = df_balance_long[
    df_balance_long["Metric"].str.contains("Interest-bearing loans and borrowings|Sukuk", case=False, na=False)]

# Aggregate by Year
assets = total_assets.groupby("Year")["Value"].sum()
interest = finance_costs.groupby("Year")["Value"].sum().abs()  
equity = shareholders_equity.groupby("Year")["Value"].sum()
debt_by_year = debt.groupby("Year")["Value"].sum()

# Combine into a single DataFrame
df_ratios = pd.DataFrame({
    "Net Income": ni,
    "Total Assets": assets,
    "Shareholders' Equity": equity,
    "Debt": debt_by_year
}).dropna()

# Calculate ROA, ROE and Debt to Equity
df_ratios["ROA (%)"] = (df_ratios["Net Income"] / df_ratios["Total Assets"]) * 100
df_ratios["ROE (%)"] = (df_ratios["Net Income"] / df_ratios["Shareholders' Equity"]) * 100
df_ratios["Debt to Equity"] = (df_ratios["Debt"] / df_ratios["Shareholders' Equity"])

# Calculate Current Ratio
# Key metrics
current_asset_items = [
    "Bank Balances And Cash",
    "Trade And Unbilled Receivables",
    "Other Assets, Receivables, Deposits And Prepayments",
    "Assets Classified As Held For Sale"]

current_liability_items = [
    "Trade And Other Payables",
    "Advances From Customers",
    "Retentions Payable",
    "Liabilities Directly Associated With Assets Classified As Held For Sale"]

# Filter using exact match
current_assets = df_balance_long[
    df_balance_long["Metric"].str.strip().isin(current_asset_items)]

current_liabilities = df_balance_long[
    df_balance_long["Metric"].str.strip().isin(current_liability_items)]


# Group by Year
current_assets_by_year = current_assets.groupby("Year")["Value"].sum().round(2)
current_liabilities_by_year = current_liabilities.groupby("Year")["Value"].sum().round(2)

# Current Ratio
current_ratio = current_assets_by_year / current_liabilities_by_year

# Add to df_ratios
df_ratios["Current Ratio"] = current_ratio

# Round for readability
df_ratios = df_ratios.round(2)

# Display the results
print("\n📊 ROA, ROE, Debt to Equity by Year and Current Ratio:")
print(df_ratios[["ROA (%)", "ROE (%)", "Debt to Equity", "Current Ratio"]])


# Create dataframe for analysis
df_efficiency = pd.DataFrame({
    "Revenue": rev,
    "Operating Profit (EBIT)": op_profit,
    "Total Assets": assets,
    "Interest Expense": interest
}).dropna()

# Asset Turnover and Interest Coverage
df_efficiency["Asset Turnover"] = df_efficiency["Revenue"] / df_efficiency["Total Assets"]
df_efficiency["Interest Coverage"] = df_efficiency["Operating Profit (EBIT)"] / df_efficiency["Interest Expense"]

# Round for readability
df_efficiency = df_efficiency.round(2)

# Display results
print("\n📊 Efficiency & Risk Ratios:")
print(df_efficiency[["Asset Turnover", "Interest Coverage"]])


# Does Emaar generate enough cash?

# Extract cash from operations and capital expenditures (CapEx)
cash_ops = df_cashflow_long[df_cashflow_long["Metric"].str.contains("net cash flows from operating activities", na=False)]
capex = df_cashflow_long[df_cashflow_long["Metric"].str.contains("amounts incurred on property, plant and equipment|amounts incurred on investment properties", na=False)]

cash_ops = cash_ops.groupby("Year")["Value"].sum()
capex = capex.groupby("Year")["Value"].sum()

# Align years
years = sorted(list(set(cash_ops.index) & set(capex.index)))
cash_ops = cash_ops.reindex(years)
capex = capex.reindex(years)

# Calculate FCF
df_fcf = pd.DataFrame({
    "Operating Cash Flow": cash_ops,
    "CapEx": capex
})
df_fcf["Free Cash Flow"] = df_fcf["Operating Cash Flow"] + df_fcf["CapEx"]
df_fcf = df_fcf.round(2)

print("\n📊 Free Cash Flow Analysis:")
print(df_fcf)




# Charts
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import font_manager
import os

font_path = "Merriweather-VariableFont_opsz,wdth,wght.ttf"
if not os.path.exists(font_path):
    print("Font not found. Using default font.")
    merriweather = None
else:
    merriweather = font_manager.FontProperties(fname=font_path, size=16)

# Graph 1
# Group and prepare data
rev = revenue.groupby("Year")["Value"].sum()
ni = net_income.groupby("Year")["Value"].sum()
opexp = op_expenses.groupby("Year")["Value"].sum().abs()
fin_costs = finance_costs.groupby("Year")["Value"].sum().abs()

df_plot = pd.DataFrame({
    "Revenue": rev,
    "Net Income": ni,
    "Finance Costs": fin_costs,
    "Operating Expenses": opexp
}).dropna()

years = df_plot.index.astype(str).tolist()
x = range(len(years))
revenue = df_plot["Revenue"]
net_income = df_plot["Net Income"]
finance_costs = df_plot["Finance Costs"]
op_expenses = df_plot["Operating Expenses"]
total_costs = finance_costs + op_expenses

# Plot
fig, ax = plt.subplots(figsize=(14, 6))
bar_width = 0.4

# Bars
ax.bar(x, finance_costs.values, width=bar_width, label='Finance Costs', color='black')
ax.bar(x, op_expenses.values, bottom=finance_costs.values, width=bar_width, label='Operational Costs', color='#f5f7f8')

# Bar labels
for i, val in enumerate(total_costs):
    ax.text(i, val, f'{val/1e6:.0f}M', ha='center', va='bottom', fontsize=14, color='gray', fontproperties=merriweather)

# Lines
ax.plot(x, revenue.values, label='Revenue', color='#0c243f', marker='o', linewidth=2)
ax.plot(x, net_income.values, label='Net Income', color='#cba366', marker='s', linewidth=2)

# Line labels
for i, val in enumerate(revenue.values):
    ax.text(i, val - 2e6, f'{val/1e6:.0f}M', ha='center', va='top', fontsize=14, color='#0c243f', fontproperties=merriweather)
for i, val in enumerate(net_income.values):
    ax.text(i, val + 2.1e6, f'{val/1e6:.0f}M', ha='center', va='bottom', fontsize=14, color='#cba366', fontproperties=merriweather)

# Axis settings
ax.set_xticks(x)
ax.set_xticklabels(years, fontproperties=merriweather, fontsize=16)
ax.set_xlabel('Year', fontproperties=merriweather, fontsize=16)

# Remove Y tick labels but keep axis name
ax.set_yticklabels([])
ax.tick_params(axis='y', which='both', length=0)
ax.set_ylabel('Value (AED)', fontproperties=merriweather, fontsize=16)

# Title & Legend
ax.set_title('Emaar Financial Overview (2021–2024)', fontproperties=merriweather, fontsize=30)
ax.legend(
    loc='upper center',
    bbox_to_anchor=(0.5, -0.15),
    ncol=4,
    prop=merriweather,
    frameon=False
)

# Styling
ax.set_facecolor('white')
fig.patch.set_facecolor('white')
ax.grid(False)

# Save + Show
plt.tight_layout()
plt.savefig("emaar_financial_overview.png", dpi=300)
plt.show()


# Graph 2
# Group and prepare data
roa = (df_ratios["Net Income"] / df_ratios["Total Assets"]) * 100
roe = (df_ratios["Net Income"] / df_ratios["Shareholders' Equity"]) * 100
roa = roa.sort_index()
roe = roe.sort_index()


df_plot = pd.DataFrame({
    "Return on Asset": roa,
    "Return on Equity": roe
}).dropna()

years = df_plot.index.astype(str).tolist()
x = range(len(years))
returnonasset = df_plot["Return on Asset"]
returnonequity = df_plot["Return on Equity"]

# Plot
fig, ax = plt.subplots(figsize=(14, 6))
bar_width = 0.4

# Lines
ax.plot(x, roe.values, label='ROE', color='#0c243f', marker='o', linewidth=2)
ax.plot(x, roa.values, label='ROA', color='#cba366', marker='s', linewidth=2)

# Line labels
for i, val in enumerate(roe.values):
    ax.text(i, val - 0.7, f'{val:.1f}%', ha='center', va='top', fontsize=14, color='#0c243f', fontproperties=merriweather)

for i, val in enumerate(roa.values):
    ax.text(i, val + 0.7, f'{val:.1f}%', ha='center', va='bottom', fontsize=14, color='#cba366', fontproperties=merriweather)


# Axis settings
ax.set_xticks(x)
ax.set_xticklabels(years, fontproperties=merriweather, fontsize=16)
ax.set_xlabel('Year', fontproperties=merriweather, fontsize=16)

# Remove Y tick labels but keep axis name
ax.set_yticklabels([])
ax.tick_params(axis='y', which='both', length=0)
ax.set_ylabel('Value', fontproperties=merriweather, fontsize=16)

# Title & Legend
ax.set_title('Emaar Profitability (2021–2024)', fontproperties=merriweather, fontsize=30)
ax.legend(
    loc='upper center',
    bbox_to_anchor=(0.5, -0.15),
    ncol=4,
    prop=merriweather,
    frameon=False
)

# Styling
ax.set_facecolor('white')
fig.patch.set_facecolor('white')
ax.grid(False)

# Save + Show
plt.tight_layout()
plt.savefig("emaar_profitability_overview.png", dpi=300)
plt.show()
