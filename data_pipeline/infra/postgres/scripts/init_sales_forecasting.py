import os
import logging
import psycopg2
from psycopg2 import sql

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


def main():
    try:
        initialize_db()
        initialize_schemas()
        logger.info("Database and essential schemas are ready for dbt.")
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)


if __name__ == "__main__":
    main()
