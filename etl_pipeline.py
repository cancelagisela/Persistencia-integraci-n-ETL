import sqlite3
import pandas as pd


def extract_data(csv_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError as err:
        raise FileNotFoundError(f"No se encontró el archivo de origen '{csv_path}'.") from err
    except Exception as err:
        raise RuntimeError(f"Error al extraer datos desde '{csv_path}': {err}") from err


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.dropna(subset=["user_id", "order_id", "amount"]).copy()
    if "status" in clean_df.columns:
        clean_df = clean_df[clean_df["status"] == "completed"]
    clean_df = clean_df[clean_df["amount"] > 0]

    agg_df = (
        clean_df.groupby("user_id", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            total_amount=("amount", "sum"),
        )
    )
    return agg_df


def load_data(agg_df: pd.DataFrame, schema_path: str = "schema.sql", db_path: str = "analytics.db") -> None:
    conn = None
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            ddl_script = f.read()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript(ddl_script)
        cursor.execute("DELETE FROM user_order_metrics;")

        rows = list(
            agg_df[["user_id", "total_orders", "total_amount"]].itertuples(
                index=False, name=None
            )
        )
        cursor.executemany(
            """
            INSERT INTO user_order_metrics (user_id, total_orders, total_amount)
            VALUES (?, ?, ?);
            """,
            rows,
        )
        conn.commit()
    except sqlite3.Error as err:
        if conn:
            conn.rollback()
        raise RuntimeError(f"Error de conexión o carga en SQLite: {err}") from err
    except Exception as err:
        if conn:
            conn.rollback()
        raise RuntimeError(f"Error inesperado durante la carga ETL: {err}") from err
    finally:
        if conn:
            conn.close()


def run_pipeline(csv_path: str = "sample_orders.csv", schema_path: str = "schema.sql", db_path: str = "analytics.db") -> None:
    raw_df = extract_data(csv_path)
    transformed_df = transform_data(raw_df)
    load_data(transformed_df, schema_path=schema_path, db_path=db_path)


if __name__ == "__main__":
    run_pipeline()
