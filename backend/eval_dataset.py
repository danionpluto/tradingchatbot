import pandas as pd
import re

import pandas as pd
import re


df = pd.read_csv("trade_profits_summary.csv")

# # --- Parse Trade Key ---
# def parse_trade_key(key):
#     if 'Deposit' in key:
#         return pd.Series([None, None, None, key.split(" on ")[-1]])
#     match = re.search(r"([A-Z]+)\s.*?(\d{1,2}/\d{1,2}/\d{4})\s(Call|Put)\s\$(\d[\d,\.]*)", key)
#     if match:
#         symbol, date, option_type, strike = match.groups()
#         return pd.Series([symbol, option_type, float(strike.replace(',', '')), date])
#     return pd.Series([None, None, None, None])

# df[["Symbol", "Option Type", "Strike", "Trade Date"]] = df["Trade Key"].apply(parse_trade_key)
# df["Trade Date"] = pd.to_datetime(df["Trade Date"], errors="coerce")

# --- Save cleaned data ---
df.to_csv("cleaned_trades.csv", index=False)

# --- Summary metrics ---
summary = {
    "Total Net Profit": df.loc[df["Type"] == "Trade STC/BTO", "Net Profit"].sum(),
    "Total BTO Cost": df["Total BTO Cost"].sum(),
    "Total STC Proceeds": df["Total STC Proceeds"].sum(),
    "Total Deposits": df.loc[df["Type"] == "Deposit", "Net Profit"].sum(),
    "Number of Trades": df[df["Type"] == "Trade STC/BTO"].shape[0],
    "Winning Trades": (df["Net Profit"] > 0).sum(),
    "Losing Trades": (df["Net Profit"] < 0).sum(),
    "Win Rate (%)": 100 * (df["Net Profit"] > 0).sum() / df[df["Type"] == "Trade STC/BTO"].shape[0],
    "Average Net Profit": df.loc[df["Type"] == "Trade STC/BTO", "Net Profit"].mean(),
    "Median Net Profit": df.loc[df["Type"] == "Trade STC/BTO", "Net Profit"].median(),
    "Max Profit": df["Net Profit"].max(),
    "Max Loss": df["Net Profit"].min()
}

# --- Save summary ---
summary_df = pd.DataFrame(list(summary.items()), columns=["Metric", "Value"])
summary_df.to_csv("trade_summary.csv", index=False)

print("Saved: cleaned_trades.csv and trade_summary.csv")
