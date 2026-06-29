import time
from datetime import datetime
import csv
import os
import urllib.request
import json

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Live Market Data Logger (Pure API Version)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~

# -------- SETTINGS --------
FILE_PATH = r"D:\prdp\Data Analytics\Live-Market\Live-Market.csv"
FETCH_INTERVAL = 300  # seconds
RETRY_LIMIT = 5


# -------- HELPERS --------
def safe_fetch(ticker):
    """Fetches the latest live close price directly from Yahoo Finance API"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=5m&range=1d"

    # User-Agent header mimics a web browser to prevent Yahoo from blocking the script
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            json_data = json.loads(response.read().decode())

            # Navigate through the Yahoo Finance JSON structure
            chart_data = json_data.get("chart", {}).get("result", [])[0]
            indicators = chart_data.get("indicators", {}).get("quote", [])[0]
            close_prices = indicators.get("close", [])

            # Filter out None values and get the latest valid close price
            valid_prices = [p for p in close_prices if p is not None]

            if valid_prices:
                return float(valid_prices[-1])

            raise ValueError(f"No price data available for {ticker}")

    except Exception as e:
        raise ValueError(f"{ticker} fetch failed: {e}")


# -------- DATA FETCH --------
def get_data():
    silver = safe_fetch("SI=F")
    gold = safe_fetch("GC=F")
    usd_inr = safe_fetch("USDINR=X")
    nse = safe_fetch("^NSEI")  # NIFTY 50
    bse = safe_fetch("^BSESN")  # SENSEX
    return silver, gold, usd_inr, nse, bse


# -------- CALCULATION & SAVE --------
def calculate_and_save(silver, gold, usd_inr, nse, bse):
    grams_per_toz = 31.1035

    silver_g = (silver / grams_per_toz) * usd_inr * 1.15
    silver_kg = silver_g * 1000

    gold_g = (gold / grams_per_toz) * usd_inr * 1.15
    gold_kg = gold_g * 1000

    now = datetime.now()

    # -------- DATE/TIME FIELDS --------
    DMD_DateTime = now.strftime("%d-%m-%Y %H:%M:%S")
    DMD_Date = now.strftime("%d-%m-%Y")
    DMD_Day = now.strftime("%d")
    DMD_Month = now.strftime("%m")
    DMD_Year = now.strftime("%Y")

    DMH_Time = now.strftime("%H:%M:%S")
    DMH_Hours_24 = f"{now.hour:02d}"
    DMH_Minutes = f"{now.minute:02d}"

    DMT_Month_Name = now.strftime("%b")
    DMT_Day_Name = now.strftime("%a")

    # -------- QUARTER --------
    m = now.month
    if m in [4, 5, 6]:
        DMT_QTR = "Q1"
    elif m in [7, 8, 9]:
        DMT_QTR = "Q2"
    elif m in [10, 11, 12]:
        DMT_QTR = "Q3"
    else:
        DMT_QTR = "Q4"

    # -------- FINANCIAL YEAR --------
    if m >= 4:
        DMT_FY = f"FY {now.year}-{str(now.year + 1)[-2:]}"
    else:
        DMT_FY = f"FY {now.year - 1}-{str(now.year)[-2:]}"

    # -------- FILE HANDLING --------
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    file_exists = os.path.isfile(FILE_PATH)

    # -------- HEADER --------
    ordered_cols = [
        "DMD-DateTime", "DMD-Date", "DMD-Day", "DMD-Month", "DMD-Year",
        "DMH-Time", "DMH-Hours-24", "DMH-Minutes",
        "DMT-Month_Name", "DMT-Day_Name", "DMT-QTR", "DMT-FY",
        "Silver_USD_t.oz", "Gold_USD_t.oz", "USD_INR",
        "Silver_INR_g", "Silver_INR_kg", "Gold_INR_g", "Gold_INR_kg",
        "Eq-NSE", "Eq-BSE"
    ]

    if not file_exists:
        with open(FILE_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(ordered_cols)

    # -------- ROW --------
    data_row = [
        DMD_DateTime, DMD_Date, DMD_Day, DMD_Month, DMD_Year,
        DMH_Time, DMH_Hours_24, DMH_Minutes,
        DMT_Month_Name, DMT_Day_Name, DMT_QTR, DMT_FY,
        f"{silver:.6f}", f"{gold:.6f}", f"{usd_inr:.6f}",
        f"{silver_g:.6f}", f"{silver_kg:.6f}",
        f"{gold_g:.6f}", f"{gold_kg:.6f}",
        f"{nse:.6f}", f"{bse:.6f}"
    ]

    with open(FILE_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data_row)

    print(f"Saved data at {DMD_DateTime}")


# -------- MAIN LOOP --------
def main():
    fail_count = 0

    try:
        while True:
            try:
                silver, gold, usd_inr, nse, bse = get_data()
                calculate_and_save(silver, gold, usd_inr, nse, bse)
                fail_count = 0

            except Exception as e:
                fail_count += 1
                print(f"Error ({fail_count}):", e)

                if fail_count >= RETRY_LIMIT:
                    print("Too many failures. Stopping script.")
                    break

            time.sleep(FETCH_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopped by user")


# -------- RUN --------
if __name__ == "__main__":
    main()