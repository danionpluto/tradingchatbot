import pandas as pd
import re

def clean_amount(x):
    if pd.isna(x):
        return 0.0
    x = str(x).replace('$', '').replace(',', '').strip()
    if '(' in x:
        return -float(re.sub(r'[^\d.]', '', x))
    return float(re.sub(r'[^\d.]', '', x))

def summarize_data():

    df = pd.read_csv('Trades_sample.csv')



    df['Amount'] = df['Amount'].apply(clean_amount)
    df['Price'] = df['Price'].apply(clean_amount)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0).astype(int)
    df['Activity Date'] = pd.to_datetime(df['Activity Date'])


    df_trades = df[df['Trans Code'].isin(['BTO', 'STC'])].copy()

    df_trades['Trade Key'] = df_trades['Instrument'].astype(str) + ' | ' + df_trades['Description']

    btos = df_trades[df_trades['Trans Code'] == 'BTO'].copy()
    stcs = df_trades[df_trades['Trans Code'] == 'STC'].copy()

    grouped_bto = btos.groupby('Trade Key')
    grouped_stc = stcs.groupby('Trade Key')

    results = []

    for key in df_trades['Trade Key'].unique():
        bto_amt = grouped_bto['Amount'].sum().get(key, 0)
        stc_amt = grouped_stc['Amount'].sum().get(key, 0)
        profit = stc_amt + bto_amt  # bto will be a negative number
        results.append({
            'Trade Key': key,
            'Total BTO Cost': bto_amt,
            'Total STC Proceeds': stc_amt,
            'Net Profit': profit,
            'Type': 'Trade STC/BTO'
        })
        
    results_df = pd.DataFrame(results)
    # results_df = results_df.sort_values(by='Net Profit', ascending=False)
    # print(results_df.head())

    ach_df = df[df['Description'] == 'ACH Deposit'].copy()

    # Each deposit becomes its own row in the output
    ach_entries = ach_df[['Activity Date', 'Amount']].copy()
    ach_entries['Trade Key'] = 'ACH Deposit on ' + ach_entries['Activity Date'].dt.strftime('%Y-%m-%d')
    ach_entries['Total BTO Cost'] = 0.0
    ach_entries['Total STC Proceeds'] = ach_entries['Amount']
    ach_entries['Net Profit'] = ach_entries['Amount']
    ach_entries['Type'] = 'Deposit'

    # Only keep the columns in same order
    ach_entries = ach_entries[['Trade Key', 'Total BTO Cost', 'Total STC Proceeds', 'Net Profit', 'Type']]

    # Combine and sort
    combined_df = pd.concat([results_df, ach_entries], ignore_index=True)
    combined_df = combined_df.sort_values(by='Net Profit', ascending=False)

    # Save to CSV
    combined_df.to_csv('trade_profits_summary.csv', index=False)

    # Print top results
    print(combined_df.head())
    
def eval_data():
    df = pd.read_csv("trade_profits_summary.csv")

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

    #save to 
    summary_df = pd.DataFrame(list(summary.items()), columns=["Metric", "Value"])
    summary_df.to_csv("trade_summary.csv", index=False)

    print("Saved trade_analysis.csv")
