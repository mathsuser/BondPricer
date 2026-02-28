import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
sns.set(style="whitegrid")

def plot_cash_flows(cash_flows):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Format x-axis: show only year or year-month
    if pd.api.types.is_datetime64_any_dtype(cash_flows.index):
        ax.bar(cash_flows.index, cash_flows.values, width=20)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45, ha='right')
        ax.set_xlabel("Date")
    else:
        # For numeric indices, use range for positions
        ax.bar(range(len(cash_flows)), cash_flows.values)
        ax.set_xticks(range(len(cash_flows)))
        ax.set_xticklabels(cash_flows.index)
        ax.set_xlabel("Payment Period")

    ax.set_title("Future Cash Flows")
    ax.grid(True)
    ax.set_ylabel("Amount")
    plt.tight_layout()
    plt.show();



