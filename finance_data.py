#%%
import yfinance as yf
from dateutil.relativedelta import relativedelta

def fetch_exact_returns_variance_safe(alla_fonder):
    periods = [6, 12, 24]  # months

    for isin, data in alla_fonder.items():
        ticker = data.get("översikt", {}).get("ticker")
        if not ticker:
            continue
        
        try:
            # Fetch fresh history for each ticker
            hist = yf.Ticker(ticker).history(period="3y", auto_adjust=True)["Close"].dropna()
            end_date = hist.index[-1]
            
            # Compute returns locally first
            computed_returns = {}
            for months in periods:
                start_date = end_date - relativedelta(months=months)
                hist_period = hist[hist.index >= start_date]
                if hist_period.empty:
                    computed_returns[f"{months}m"] = None
                    continue
                start_price = hist_period.iloc[0]
                end_price = hist_period.iloc[-1]
                computed_returns[f"{months}m"] = (end_price / start_price - 1) * 100

            # Compute variance
            variance = hist.pct_change().dropna().var() * 252  # annualized

            # Only now assign to the dict
            data["översikt"]["returns"] = computed_returns
            data["översikt"]["variance"] = variance

        except Exception as e:
            print(f"Failed for {isin} ({ticker}): {e}")
            data["översikt"]["returns"] = {f"{m}m": None for m in periods}
            data["översikt"]["variance"] = None

    return alla_fonder


# Usage
alla_fonder = fetch_exact_returns_variance_safe(alla_fonder)
