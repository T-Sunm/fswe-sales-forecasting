import io
import os
import csv
import logging
import pathlib
import psycopg2
from psycopg2 import sql
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Config from environment
PG_HOST = os.environ.get("PG_HOST", "localhost")
PG_PORT = os.environ.get("PG_PORT", "5432")
PG_USER = os.environ.get("PG_USER", "postgres")
PG_PASS = os.environ.get("PG_PASS", "changeme")
TARGET_DB = os.environ.get("PG_DB", "sales_forecasting")


def initialize_db():
    """Ensure the target database exists."""
    logger.info("Connecting to administrative database 'postgres' to check for %s", TARGET_DB)
    
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname="postgres",
        user=PG_USER, password=PG_PASS
    )
    conn.autocommit = True
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TARGET_DB,))
            if cur.fetchone() is None:
                logger.info("Creating database: %s", TARGET_DB)
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(TARGET_DB)))
            else:
                logger.info("Database %s already exists.", TARGET_DB)
    finally:
        conn.close()


def initialize_schemas():
    """Ensure essential schemas exist in the target database."""
    logger.info("Connecting to %s to create schemas.", TARGET_DB)
    
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=TARGET_DB,
        user=PG_USER, password=PG_PASS
    )
    conn.autocommit = True
    
    try:
        with conn.cursor() as cur:
            # 'raw' schema is necessary as a source for dbt
            cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
            logger.info("Schema 'raw' is ready.")
    finally:
        conn.close()


def load_seeds(seeds_dir: str):
    """Bulk-load CSV seed files into raw schema using COPY FROM STDIN."""
    seeds_path = pathlib.Path(seeds_dir)
    csv_files = sorted(seeds_path.glob("*.csv"))
    if not csv_files:
        logger.info("No CSV files found in %s, skipping seed load.", seeds_dir)
        return

    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=TARGET_DB,
        user=PG_USER, password=PG_PASS
    )
    try:
        for csv_path in csv_files:
            table = csv_path.stem
            logger.info("Loading %s → raw.%s ...", csv_path.name, table)

            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)

            col_defs = ", ".join(f'"{h}" TEXT' for h in headers)
            col_names = ", ".join(f'"{h}"' for h in headers)

            with conn.cursor() as cur:
                cur.execute(
                    f'CREATE TABLE IF NOT EXISTS raw."{table}" ({col_defs});'
                )
                cur.execute(f'TRUNCATE raw."{table}";')

            conn.commit()

            with conn.cursor() as cur, open(csv_path, encoding="utf-8") as f:
                cur.copy_expert(
                    f'COPY raw."{table}" ({col_names}) FROM STDIN WITH CSV HEADER',
                    f,
                )
            conn.commit()
            logger.info("✓ raw.%s loaded.", table)
    finally:
        conn.close()


def load_special_dates(start_year: int = 2012, end_year: int = 2014):
    """Generate stg_holidays and stg_blackfriday tables in raw schema."""
    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start=f"{start_year}-01-01", end=f"{end_year}-12-31")
    df_holidays = pd.DataFrame({"date": holidays.strftime("%Y-%m-%d"), "holiday": "US Federal Holiday"})

    blackfriday_dates = [
        "2012-11-23", "2012-11-24", "2012-11-25", "2012-11-26",
        "2013-11-29", "2013-11-30", "2013-12-01", "2013-12-02",
        "2014-11-28", "2014-11-29", "2014-11-30", "2014-12-01",
    ]
    df_blackfriday = pd.DataFrame({"date": blackfriday_dates, "event_name": "Black Friday Weekend"})

    tables = {
        "stg_holidays": df_holidays,
        "stg_blackfriday": df_blackfriday,
    }

    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=TARGET_DB,
        user=PG_USER, password=PG_PASS
    )
    try:
        for table, df in tables.items():
            cols = list(df.columns)
            col_defs = ", ".join(
                f'"{c}" DATE' if c == "date" else f'"{c}" TEXT'
                for c in cols
            )
            col_names = ", ".join(f'"{c}"' for c in cols)
            with conn.cursor() as cur:
                cur.execute(f'DROP TABLE IF EXISTS raw."{table}";')
                cur.execute(f'CREATE TABLE raw."{table}" ({col_defs});')
            conn.commit()
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            buf.seek(0)
            with conn.cursor() as cur:
                cur.copy_expert(f'COPY raw."{table}" ({col_names}) FROM STDIN WITH CSV HEADER', buf)
            conn.commit()
            logger.info("✓ raw.%s loaded (%d rows).", table, len(df))
    finally:
        conn.close()


def main():
    seeds_dir = os.environ.get(
        "SEEDS_DIR",
        str(pathlib.Path(__file__).parents[3] / "dbt" / "sales_forecasting" / "seeds"),
    )
    try:
        initialize_db()
        initialize_schemas()
        load_seeds(seeds_dir)
        load_special_dates()
        logger.info("Initialization complete.")
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)


if __name__ == "__main__":
    main()
