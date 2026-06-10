import sqlite3
import csv
import os

DB_PATH = "data/harvestbridge.db"
NGA_CSV = "data/raw/NGA_RTFP.csv"
ETH_CSV = "data/raw/ETH_RTFP.csv"


def safe_float(val):
    """Convert to float or None if empty/invalid."""
    try:
        v = float(val)
        return v if v > 0 else None
    except (ValueError, TypeError):
        return None


def create_schema(cursor):
    """Drop and recreate market_prices with full column set."""
    cursor.execute("DROP TABLE IF EXISTS market_prices")
    cursor.execute("""
        CREATE TABLE market_prices (
            -- Identity
            country         TEXT,
            adm1_name       TEXT,
            adm2_name       TEXT,
            mkt_name        TEXT,
            lat             REAL,
            lon             REAL,
            geo_id          TEXT,

            -- Time
            price_date      TIMESTAMP,
            year            INTEGER,
            month           INTEGER,
            currency        TEXT,

            -- Data quality metadata
            index_confidence_score  REAL,
            spatially_interpolated  INTEGER,

            -- === NIGERIA CROPS (NGN) ===
            -- Beans
            c_beans         REAL,
            h_beans         REAL,
            l_beans         REAL,
            trust_beans     REAL,

            -- Fish
            c_fish          REAL,
            h_fish          REAL,
            l_fish          REAL,
            trust_fish      REAL,

            -- Gari / Cassava
            c_gari_fao      REAL,
            h_gari_fao      REAL,
            l_gari_fao      REAL,
            trust_gari_fao  REAL,

            -- Maize
            c_maize_fao     REAL,
            h_maize_fao     REAL,
            l_maize_fao     REAL,
            trust_maize_fao REAL,

            -- Maize flour
            c_maize_flour   REAL,
            h_maize_flour   REAL,
            l_maize_flour   REAL,
            trust_maize_flour REAL,

            -- Millet
            c_millet_fao    REAL,
            h_millet_fao    REAL,
            l_millet_fao    REAL,
            trust_millet_fao REAL,

            -- Onions
            c_onions        REAL,
            h_onions        REAL,
            l_onions        REAL,
            trust_onions    REAL,

            -- Rice
            c_rice_fao      REAL,
            h_rice_fao      REAL,
            l_rice_fao      REAL,
            trust_rice_fao  REAL,

            -- Sorghum
            c_sorghum_fao   REAL,
            h_sorghum_fao   REAL,
            l_sorghum_fao   REAL,
            trust_sorghum_fao REAL,

            -- Yam
            c_yam           REAL,
            h_yam           REAL,
            l_yam           REAL,
            trust_yam       REAL,

            -- === ETHIOPIA CROPS (ETB) ===
            -- Maize (ETH)
            c_maize         REAL,
            h_maize         REAL,
            l_maize         REAL,
            trust_maize     REAL,

            -- Teff
            c_teff_fao      REAL,
            h_teff_fao      REAL,
            l_teff_fao      REAL,
            trust_teff_fao  REAL,

            -- Sorghum (ETH)
            c_sorghum       REAL,
            h_sorghum       REAL,
            l_sorghum       REAL,
            trust_sorghum   REAL,

            -- Wheat
            c_wheat         REAL,
            h_wheat         REAL,
            l_wheat         REAL,
            trust_wheat     REAL
        )
    """)

    # Create indexes for fast querying
    cursor.execute("CREATE INDEX idx_region_date ON market_prices(adm1_name, price_date)")
    cursor.execute("CREATE INDEX idx_country ON market_prices(country)")
    cursor.execute("CREATE INDEX idx_date ON market_prices(price_date)")

    print("✓ Schema created with full column set")

def create_farmers_registry(cursor):
    """Creates the farmers registry table for WhatsApp notifications."""
    cursor.execute("DROP TABLE IF EXISTS farmers_registry")
    cursor.execute("""
        CREATE TABLE farmers_registry (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            name                TEXT NOT NULL,
            phone_number        TEXT NOT NULL UNIQUE,
            crop                TEXT NOT NULL,
            region              TEXT NOT NULL,
            country             TEXT NOT NULL DEFAULT 'Nigeria',
            currency            TEXT NOT NULL DEFAULT 'NGN',
            quantity_kg         REAL DEFAULT 1000.0,
            price_threshold_pct REAL DEFAULT 10.0,
            registered_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_notified_at    TIMESTAMP NULL
        )
    """)
    print("✓ farmers_registry table created")


def load_nga(cursor, csv_path):
    """Load Nigeria RTFP data."""
    # Skip aggregate rows
    skip_regions = {'Geopolitical Zone', 'Market Average', 'National Average', 'Kano State (1)'}

    count = 0
    skipped = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['adm1_name'] in skip_regions:
                skipped += 1
                continue

            cursor.execute("""
                INSERT INTO market_prices (
                    country, adm1_name, adm2_name, mkt_name, lat, lon, geo_id,
                    price_date, year, month, currency,
                    index_confidence_score, spatially_interpolated,
                    c_beans, h_beans, l_beans, trust_beans,
                    c_fish, h_fish, l_fish, trust_fish,
                    c_gari_fao, h_gari_fao, l_gari_fao, trust_gari_fao,
                    c_maize_fao, h_maize_fao, l_maize_fao, trust_maize_fao,
                    c_maize_flour, h_maize_flour, l_maize_flour, trust_maize_flour,
                    c_millet_fao, h_millet_fao, l_millet_fao, trust_millet_fao,
                    c_onions, h_onions, l_onions, trust_onions,
                    c_rice_fao, h_rice_fao, l_rice_fao, trust_rice_fao,
                    c_sorghum_fao, h_sorghum_fao, l_sorghum_fao, trust_sorghum_fao,
                    c_yam, h_yam, l_yam, trust_yam
                ) VALUES (
                    ?,?,?,?,?,?,?,
                    ?,?,?,?,
                    ?,?,
                    ?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?
                )
            """, (
                row['country'], row['adm1_name'], row.get('adm2_name', ''),
                row['mkt_name'],
                safe_float(row.get('lat')), safe_float(row.get('lon')),
                row.get('geo_id', ''),
                row['price_date'], int(row['year']), int(row['month']),
                row['currency'],
                safe_float(row.get('index_confidence_score')),
                int(row.get('spatially_interpolated', 0) or 0),
                # beans
                safe_float(row.get('c_beans')), safe_float(row.get('h_beans')),
                safe_float(row.get('l_beans')), safe_float(row.get('trust_beans')),
                # fish
                safe_float(row.get('c_fish')), safe_float(row.get('h_fish')),
                safe_float(row.get('l_fish')), safe_float(row.get('trust_fish')),
                # gari
                safe_float(row.get('c_gari_fao')), safe_float(row.get('h_gari_fao')),
                safe_float(row.get('l_gari_fao')), safe_float(row.get('trust_gari_fao')),
                # maize
                safe_float(row.get('c_maize_fao')), safe_float(row.get('h_maize_fao')),
                safe_float(row.get('l_maize_fao')), safe_float(row.get('trust_maize_fao')),
                # maize flour
                safe_float(row.get('c_maize_flour')), safe_float(row.get('h_maize_flour')),
                safe_float(row.get('l_maize_flour')), safe_float(row.get('trust_maize_flour')),
                # millet
                safe_float(row.get('c_millet_fao')), safe_float(row.get('h_millet_fao')),
                safe_float(row.get('l_millet_fao')), safe_float(row.get('trust_millet_fao')),
                # onions
                safe_float(row.get('c_onions')), safe_float(row.get('h_onions')),
                safe_float(row.get('l_onions')), safe_float(row.get('trust_onions')),
                # rice
                safe_float(row.get('c_rice_fao')), safe_float(row.get('h_rice_fao')),
                safe_float(row.get('l_rice_fao')), safe_float(row.get('trust_rice_fao')),
                # sorghum
                safe_float(row.get('c_sorghum_fao')), safe_float(row.get('h_sorghum_fao')),
                safe_float(row.get('l_sorghum_fao')), safe_float(row.get('trust_sorghum_fao')),
                # yam
                safe_float(row.get('c_yam')), safe_float(row.get('h_yam')),
                safe_float(row.get('l_yam')), safe_float(row.get('trust_yam')),
            ))
            count += 1

    print(f"✓ Nigeria: {count} rows loaded, {skipped} aggregate rows skipped")
    return count


def load_eth(cursor, csv_path):
    """Load Ethiopia RTFP data."""
    skip_regions = {'Market Average'}

    count = 0
    skipped = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['adm1_name'] in skip_regions:
                skipped += 1
                continue

            cursor.execute("""
                INSERT INTO market_prices (
                    country, adm1_name, adm2_name, mkt_name, lat, lon, geo_id,
                    price_date, year, month, currency,
                    index_confidence_score, spatially_interpolated,
                    c_maize, h_maize, l_maize, trust_maize,
                    c_teff_fao, h_teff_fao, l_teff_fao, trust_teff_fao,
                    c_sorghum, h_sorghum, l_sorghum, trust_sorghum,
                    c_wheat, h_wheat, l_wheat, trust_wheat
                ) VALUES (
                    ?,?,?,?,?,?,?,
                    ?,?,?,?,
                    ?,?,
                    ?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?
                )
            """, (
                row['country'], row['adm1_name'], row.get('adm2_name', ''),
                row['mkt_name'],
                safe_float(row.get('lat')), safe_float(row.get('lon')),
                row.get('geo_id', ''),
                row['price_date'], int(row['year']), int(row['month']),
                row['currency'],
                safe_float(row.get('index_confidence_score')),
                int(row.get('spatially_interpolated', 0) or 0),
                # maize
                safe_float(row.get('c_maize')), safe_float(row.get('h_maize')),
                safe_float(row.get('l_maize')), safe_float(row.get('trust_maize')),
                # teff
                safe_float(row.get('c_teff_fao')), safe_float(row.get('h_teff_fao')),
                safe_float(row.get('l_teff_fao')), safe_float(row.get('trust_teff_fao')),
                # sorghum
                safe_float(row.get('c_sorghum')), safe_float(row.get('h_sorghum')),
                safe_float(row.get('l_sorghum')), safe_float(row.get('trust_sorghum')),
                # wheat
                safe_float(row.get('c_wheat')), safe_float(row.get('h_wheat')),
                safe_float(row.get('l_wheat')), safe_float(row.get('trust_wheat')),
            ))
            count += 1

    print(f"✓ Ethiopia: {count} rows loaded, {skipped} aggregate rows skipped")
    return count


def rebuild():
    print(f"Rebuilding {DB_PATH}...")

    if not os.path.exists("data/raw"):
        os.makedirs("data/raw")
        print("Created data/raw/ directory")

    # Check CSVs exist
    for path in [NGA_CSV, ETH_CSV]:
        if not os.path.exists(path):
            print(f"✗ File not found: {path}")
            print(f"  Copy your CSV files to data/raw/")
            return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_schema(cursor)
    create_farmers_registry(cursor)

    nga_count = load_nga(cursor, NGA_CSV)
    eth_count = load_eth(cursor, ETH_CSV)

    conn.commit()

    # Verify
    cursor.execute("SELECT COUNT(*) FROM market_prices")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT country, COUNT(*) FROM market_prices GROUP BY country")
    by_country = cursor.fetchall()

    cursor.execute("SELECT COUNT(DISTINCT adm1_name) FROM market_prices")
    regions = cursor.fetchone()[0]

    conn.close()

    print(f"\n{'='*50}")
    print(f"✓ Rebuild complete")
    print(f"  Total rows: {total}")
    print(f"  By country: {dict(by_country)}")
    print(f"  Unique regions: {regions}")
    print(f"  Expected: {nga_count + eth_count}")
    print(f"{'='*50}")


if __name__ == "__main__":
    rebuild()