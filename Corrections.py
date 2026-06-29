# import pandas as pd
# from datetime import datetime
# import os

#
# # -------- FILE PATH --------
# FILE_PATH = r"D:\prdp\Data Analytics\Data Analytics\Live-Market\Correction.csv"
#
# # -------- LOAD DATA --------
# df = pd.read_csv(FILE_PATH)
#
# # Clean column names (remove spaces if any)
# df.columns = df.columns.str.strip()
#
#
# # -------- FIX FUNCTION --------
# def fix_datetime(row):
#     raw_dt = str(row["DateTime"]).strip()
#
#     # Case 1: Only date (yyyy-mm-dd)
#     if len(raw_dt) == 10:
#         dt = datetime.strptime(raw_dt, "%Y-%m-%d")
#
#     # Case 2: Full datetime but wrong time
#     else:
#         try:
#             dt = datetime.strptime(raw_dt[:10], "%Y-%m-%d")
#         except:
#             return row  # skip bad rows safely
#
#     # Force time to 00:00:00
#     dt_fixed = dt.replace(hour=0, minute=0, second=0)
#
#     # Update fields
#     row["DateTime"] = dt_fixed.strftime("%Y-%m-%d %H:%M:%S")
#     row["Time"] = "00:00:00"
#     row["Day"] = dt_fixed.strftime("%a")  # Mon, Tue, etc.
#
#     return row
#
#
# # -------- APPLY FIX --------
# df = df.apply(fix_datetime, axis=1)
#
# # -------- SAVE BACK --------
# df.to_csv(FILE_PATH, index=False)
#
# print("✅ Data correction completed successfully.")




# import pandas as pd
#
# # -------- FILE PATHS --------
# BASE_FILE = r"D:\prdp\Data Analytics\Live-Market\Correction.csv"
#
# # -------- LOAD --------
# base = pd.read_csv(BASE_FILE)
# usd  = pd.read_csv(USD_FILE)
#
# base.columns = base.columns.str.strip()
# usd.columns = usd.columns.str.strip()
#
# # -------- DATE KEY --------
# base["DateKey"] = base["DateTime"].astype(str).str.strip().str[:10]
# usd["DateKey"]  = usd["DateTime"].astype(str).str.strip().str[:10]
#
# # -------- CLEAN USD --------
# usd["USD_INR"] = pd.to_numeric(usd["USD_INR"], errors="coerce")
# usd_map = usd[["DateKey", "USD_INR"]].drop_duplicates()
#
# # -------- MERGE --------
# merged = base.merge(usd_map, on="DateKey", how="left", suffixes=("", "_new"))
#
# # -------- FILL ONLY NULLS --------
# merged["USD_INR"] = pd.to_numeric(merged["USD_INR"], errors="coerce")
# merged["USD_INR"] = merged["USD_INR"].fillna(merged["USD_INR_new"])
#
# # remove helper columns
# merged.drop(columns=["USD_INR_new", "DateKey"], inplace=True)
#
# # -------- SAFE FORMATTING (NO DATA LOSS) --------
# # Only format display, DO NOT re-calc values
#
# def safe_format(x):
#     try:
#         if pd.isna(x):
#             return ""
#         return f"{float(x):.6f}"
#     except:
#         return x
#
# merged["USD_INR"] = merged["USD_INR"].apply(safe_format)
#
# # -------- SAVE --------
# merged.to_csv(BASE_FILE, index=False)
#
# print("✅ Safe update completed (no existing precision modified)")



# ------------------------------


# import pandas as pd
#
# # -------- FILE PATH --------
# BASE_FILE = r"D:\prdp\Data Analytics\Live-Market\Correction.csv"
#
# # -------- LOAD (DO NOT TOUCH DATETIME) --------
# base = pd.read_csv(BASE_FILE)
# base.columns = base.columns.str.strip()
#
# # -------- USE COPY ONLY FOR DERIVATION --------
# dt = pd.to_datetime(base["DateTime"], errors="coerce")
#
# # -------- DERIVED COLUMNS ONLY --------
# base["Date"] = dt.dt.strftime("%Y-%m-%d")
#
# # IMPORTANT: Do NOT reconstruct Time from datetime object
# # KEEP EXACT ORIGINAL STRING (prevents any change like 00 loss)
# base["Time"] = base["DateTime"].astype(str).str.split().str[1]
#
# base["Day"] = dt.dt.strftime("%a")
#
# # -------- INDIAN QTR --------
# def get_qtr(m):
#     if m in [4, 5, 6]:
#         return "Q1"
#     elif m in [7, 8, 9]:
#         return "Q2"
#     elif m in [10, 11, 12]:
#         return "Q3"
#     else:
#         return "Q4"
#
# base["QTR"] = dt.dt.month.apply(get_qtr)
#
# # -------- INDIAN FY --------
# def get_fy(d):
#     if d.month >= 4:
#         return f"FY {d.year}-{str(d.year+1)[-2:]}"
#     else:
#         return f"FY {d.year-1}-{str(d.year)[-2:]}"
#
# base["FY"] = dt.apply(get_fy)
#
# # -------- SAFE NUMBER FORMATTING (NO CHANGE TO DATETIME) --------
# def fmt(x):
#     try:
#         if pd.isna(x):
#             return ""
#         return f"{float(x):.6f}"
#     except:
#         return x
#
# num_cols = [
#     "Silver_USD_oz", "Gold_USD_oz", "USD_INR",
#     "Silver_INR_g", "Silver_INR_kg",
#     "Gold_INR_g", "Gold_INR_kg",
#     "NSE", "BSE"
# ]
#
# for c in num_cols:
#     if c in base.columns:
#         base[c] = base[c].apply(fmt)
#
# # -------- COLUMN ORDER --------
# ordered_cols = [
#     "DMD-DateTime",
#     "DMD-Date",
#     "DMD-Day",
#     "DMD-Month",
#     "DMD-Year",
#     "DMS-Time",
#     "DMS-Hours-24",
#     "DMS-Minutes",
#     "DMT-Month_Name",
#     "DMT-Day_Name",
#     "DMT-QTR",
#     "DMT-FY",
#     "Silver_USD_oz",
#     "Gold_USD_oz",
#     "USD_INR",
#     "Silver_INR_g",
#     "Silver_INR_kg",
#     "Gold_INR_g",
#     "Gold_INR_kg",
#     "Eq-NSE",
#     "Eq-BSE"
# ]
#
# base = base[ordered_cols]
#
# # -------- SAVE --------
# base.to_csv(BASE_FILE, index=False)
#
# print("✅ Fixed: DateTime fully preserved (no formatting change, no zero loss)")

########### correction started on 23-04

#
# import pandas as pd
#
# # -------- FILE PATH --------
# BASE_FILE = r"D:\prdp\Data Analytics\Live-Market\Correction.csv"
#
# # -------- LOAD CSV --------
# base = pd.read_csv(BASE_FILE)
# base.columns = base.columns.str.strip()  # Remove extra spaces
#
# # -------- DETERMINE BASE DATETIME COLUMN --------
# datetime_cols = [c for c in base.columns if 'datetime' in c.lower()]
# if not datetime_cols:
#     raise KeyError("No column found containing 'DateTime'")
# datetime_col = datetime_cols[0]
#
# # -------- CONVERT TO DATETIME --------
# dt = pd.to_datetime(base[datetime_col], errors='coerce', dayfirst=False)
#
# # -------- DERIVED COLUMNS --------
# base["DMD-DateTime"] = dt.dt.strftime("%d-%m-%Y %H:%M:%S")
# base["DMD-Date"] = dt.dt.strftime("%d-%m-%Y")
# base["DMD-Day"] = dt.dt.day.astype('Int64').astype(str).str.zfill(2)
# base["DMD-Month"] = dt.dt.month.astype('Int64').astype(str).str.zfill(2)
# base["DMD-Year"] = dt.dt.year.astype('Int64').astype(str)
# base["DMH-Time"] = dt.dt.strftime("%H:%M:%S")
# base["DMH-Hours-24"] = dt.dt.hour
# base["DMH-Minutes"] = dt.dt.minute
# base["DMT-Month_Name"] = dt.dt.strftime("%b")
# base["DMT-Day_Name"] = dt.dt.strftime("%a")
#
# # -------- INDIAN QTR --------
# def get_qtr(m):
#     if m in [4, 5, 6]:
#         return "Q1"
#     elif m in [7, 8, 9]:
#         return "Q2"
#     elif m in [10, 11, 12]:
#         return "Q3"
#     else:
#         return "Q4"
#
# base["DMT-QTR"] = dt.dt.month.apply(lambda x: get_qtr(x) if pd.notna(x) else "")
#
# # -------- INDIAN FY --------
# def get_fy(d):
#     if pd.isna(d):
#         return ""
#     if d.month >= 4:
#         return f"FY {d.year}-{str(d.year+1)[-2:]}"
#     else:
#         return f"FY {d.year-1}-{str(d.year)[-2:]}"
#
# base["DMT-FY"] = dt.apply(get_fy)
#
# # -------- SAFE NUMBER FORMATTING --------
# num_cols = [
#     "Silver_USD_oz", "Gold_USD_oz", "USD_INR",
#     "Silver_INR_g", "Silver_INR_kg",
#     "Gold_INR_g", "Gold_INR_kg"
# ]
#
# def fmt(x):
#     try:
#         if pd.isna(x):
#             return ""
#         return f"{float(x):.6f}"
#     except:
#         return x
#
# for c in num_cols:
#     if c in base.columns:
#         base[c] = base[c].apply(fmt)
#     else:
#         base[c] = ""
#
# # -------- RENAME NSE/BSE TO Eq-NSE/Eq-BSE --------
# if 'NSE' in base.columns:
#     base['Eq-NSE'] = base['NSE'].apply(fmt)
# else:
#     base['Eq-NSE'] = ""
#
# if 'BSE' in base.columns:
#     base['Eq-BSE'] = base['BSE'].apply(fmt)
# else:
#     base['Eq-BSE'] = ""
#
# # -------- FINAL COLUMN ORDER --------
# ordered_cols = [
#     "DMD-DateTime",
#     "DMD-Date",
#     "DMD-Day",
#     "DMD-Month",
#     "DMD-Year",
#     "DMH-Time",
#     "DMH-Hours-24",
#     "DMH-Minutes",
#     "DMT-Month_Name",
#     "DMT-Day_Name",
#     "DMT-QTR",
#     "DMT-FY",
#     "Silver_USD_oz",
#     "Gold_USD_oz",
#     "USD_INR",
#     "Silver_INR_g",
#     "Silver_INR_kg",
#     "Gold_INR_g",
#     "Gold_INR_kg",
#     "Eq-NSE",
#     "Eq-BSE"
# ]
#
# base = base[ordered_cols]
#
# # -------- SAVE CSV --------
# base.to_csv(BASE_FILE, index=False)
#
# print("✅ Transformation complete. All columns preserved, Eq-NSE/Eq-BSE populated correctly.")


####### for minute padding

import pandas as pd

# -------- FILE PATH --------
BASE_FILE = r"D:\prdp\Data Analytics\Live-Market\Correction.csv"

# -------- LOAD CSV --------
df = pd.read_csv(BASE_FILE, dtype=str)  # read all as string to preserve formatting

# -------- PAD HOURS AND MINUTES --------
df["DMH-Hours-24"] = df["DMH-Hours-24"].apply(lambda x: x.zfill(2) if pd.notnull(x) else x)
df["DMH-Minutes"] = df["DMH-Minutes"].apply(lambda x: x.zfill(2) if pd.notnull(x) else x)

# -------- SAVE BACK WITHOUT TOUCHING OTHER COLUMNS --------
df.to_csv(BASE_FILE, index=False)
print("✅ DMH-Hours-24 and DMH-Minutes padded, other columns untouched.")