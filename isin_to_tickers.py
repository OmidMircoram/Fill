#%%
import yfinance as yf
# import time
def get_isin(all_funds):
    for isin in all_funds:
        try:
            stock = yf.Ticker(isin)
            info = stock.info
            ticker = info.get("symbol", None)
            
            # Ensure "overview_dict" exists

            all_funds[isin]["overview_dict"]["ticker"] = ticker
            # print(f"{isin} → {ticker}")
            
            # time.sleep(0.5)  # slight delay to avoid rate limits
        except Exception as e:
            print(f"Failed for {isin}: {e}")
            all_funds[isin]["overview_dict"]["ticker"] = None
    return all_funds
