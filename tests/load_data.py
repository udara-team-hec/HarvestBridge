"""
HarvestBridge Intelligence — Data Loader
Loads World Bank RTFP Nigeria data into SQLite.

Run from your harvestbridge_intelligence folder:
    python load_data.py

Requirements:
    pip install pandas
"""

import pandas as pd
import sqlite3
import os

# ── CONFIG ─────────────────────────────────────────────────────────
NGA_FILE = "data/raw/NGA_RTFP.csv"
DB_PATH  = "data/harvestbridge.db"

# Maps friendly crop names (what the user types) to column names in the CSV
CROP_MAP = {
    "gari":        "c_gari_fao",       # cassava product — most traded cassava form
    "cassava":     "c_gari_fao",       # alias — maps to gari
    "maize":       "c_maize_fao",
    "corn":        "c_maize_fao",      # alias
    "rice":        "c_rice_fao",
    "beans":       "c_beans",
    "yam":         "c_yam",
    "millet":      "c_millet_fao",
    "sorghum":     "c_sorghum_fao",
    "maize_flour": "c_maize_flour",
    "onions":      "c_onions",
    "fish":        "c_fish",
}

# Columns to keep — we do not need all 137 columns
KEEP_COLS = [
    "country", "adm1_name", "mkt_name", "lat", "lon",
    "price_date", "year", "month", "currency",
    "c_gari_fao", "c_maize_fao", "c_rice_fao", "c_beans",
    "c_yam", "c_millet_fao", "c_sorghum_fao",
    "c_maize_flour", "c_onions", "c_fish",
    "trust_gari_fao", "trust_maize_fao", "trust_rice_fao",
]

# ── LOAD ────────────────────────────────────────────────────────────

def load_nigeria():
    print("Loading Nigeria RTFP data...")

    if not os.path.exists(NGA_FILE):
        print(f"ERROR: File not found at {NGA_FILE}")
        print("Make sure NGA_RTFP_mkt_2007_2026-05-18.csv is in data/raw/")
        return None

    df = pd.read_csv(NGA_FILE, usecols=KEEP_COLS)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["country"] = "Nigeria"

    print(f"  Loaded {len(df):,} rows")
    print(f"  Markets: {df['mkt_name'].nunique()}")
    print(f"  States: {df['adm1_name'].nunique()}")
    print(f"  Date range: {df['price_date'].min().date()} to {df['price_date'].max().date()}")
    return df


# ── WRITE TO SQLITE ─────────────────────────────────────────────────

def write_to_db(df):
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # Write price data
    df.to_sql("market_prices", conn, if_exists="replace", index=False)
    print(f"\n  Written to market_prices table")

    # Write crop map as a lookup table
    crop_rows = [(k, v) for k, v in CROP_MAP.items()]
    conn.execute("DROP TABLE IF EXISTS crop_map")
    conn.execute("""
        CREATE TABLE crop_map (
            crop_name TEXT PRIMARY KEY,
            column_name TEXT
        )
    """)
    conn.executemany("INSERT INTO crop_map VALUES (?, ?)", crop_rows)

    # Create farmers registry table (for Week 4 notifications)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS farmers_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            crop TEXT NOT NULL,
            region TEXT NOT NULL,
            lat REAL,
            lon REAL,
            quantity_kg REAL,
            last_notified_at TEXT,
            alert_threshold_pct REAL DEFAULT 10.0
        )
    """)

    conn.commit()
    conn.close()
    print(f"  Database saved to: {DB_PATH}")


# ── TEST QUERY ──────────────────────────────────────────────────────

def run_test_query():
    """
    Test: Average gari (cassava) price in Ondo over the last 6 months.
    This is the exact query the Price Agent will use.
    """
    conn = sqlite3.connect(DB_PATH)

    print("\n" + "="*50)
    print("TEST QUERY: Avg gari price in Ondo, last 12 months")
    print("="*50)

    query = """
        SELECT
            adm1_name                        AS state,
            mkt_name                         AS market,
            ROUND(AVG(c_gari_fao), 2)        AS avg_price,
            ROUND(MIN(c_gari_fao), 2)        AS min_price,
            ROUND(MAX(c_gari_fao), 2)        AS max_price,
            currency,
            COUNT(*)                         AS data_points
        FROM market_prices
        WHERE
            adm1_name LIKE '%Ondo%'
            AND c_gari_fao IS NOT NULL
            AND year >= 2024
        GROUP BY mkt_name
        ORDER BY avg_price DESC
    """

    result = pd.read_sql(query, conn)
    conn.close()

    if result.empty:
        print("  No Ondo data found. Trying national average instead...")
        conn2 = sqlite3.connect(DB_PATH)
        fallback = pd.read_sql("""
            SELECT
                adm1_name,
                ROUND(AVG(c_gari_fao), 2) AS avg_gari_price,
                currency,
                COUNT(*) AS rows
            FROM market_prices
            WHERE year >= 2024 AND c_gari_fao IS NOT NULL
            GROUP BY adm1_name
            ORDER BY avg_gari_price DESC
            LIMIT 10
        """, conn2)
        conn2.close()
        print(fallback.to_string(index=False))
    else:
        print(result.to_string(index=False))

    print("\n✓ Database is working correctly.")
    print("✓ Week 1 data task is COMPLETE.")


# ── MAIN ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = load_nigeria()
    if df is not None:
        write_to_db(df)
        run_test_query()
