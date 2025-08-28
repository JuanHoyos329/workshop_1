from pathlib import Path
import mysql.connector
import pandas as pd
from etl import extract, transform
from db import save_to_sql, create_tables
from connection import get_connection, DB_CONFIG
from visualization import run_visualization_dashboard

INPUT_CSV = r"C:\Users\juana\OneDrive\Escritorio\workshop_1\csv\candidates.csv"
OUTPUT_SQL = Path("workshop.sql")


def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    try:
        temp_config = DB_CONFIG.copy()
        database_name = temp_config.pop("database")
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"✅ Database '{database_name}' created or already exists")
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"❌ Error creating database: {err}")
        raise


def load_data_to_database(dataframes: dict):
    """Load transformed data directly into MySQL database"""
    try:
        connection = get_connection()
        cursor = connection.cursor()

        table_order = [
            "Dim_Candidate",
            "Dim_Date",
            "Dim_Country",
            "Dim_Seniority",
            "Dim_Technology",
            "Dim_ExperienceRange",
            "Fact_Application"
        ]

        for table in table_order:
            df = dataframes.get(table)
            if df is None or df.empty:
                print(f"⚠️ Skipping {table} - no data")
                continue

            columns = list(df.columns)
            placeholders = ", ".join(["%s"] * len(columns))
            insert_query = f"INSERT IGNORE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

            data = []
            for _, row in df.iterrows():
                row_data = [None if pd.isna(v) else v for v in row]
                data.append(tuple(row_data))

            if data:
                cursor.executemany(insert_query, data)
                rows_affected = cursor.rowcount
                print(f"✅ Processed {len(data)} records for {table} (inserted: {rows_affected})")
                connection.commit()

        cursor.close()
        connection.close()
        print("✅ All data loaded successfully into database")
    except mysql.connector.Error as err:
        print(f"❌ Error loading data: {err}")
        raise


def main():
    try:
        print("🚀 STARTING ETL PIPELINE...")
        print("=" * 50)

        print("🔹 STEP 0: Setup Database...")
        create_database_if_not_exists()
        create_tables()

        print("🔹 STEP 1: Extract...")
        raw_df = extract(INPUT_CSV)

        print("🔹 STEP 2: Transform...")
        transformed = transform(raw_df)
        for name, df in transformed.items():
            print(f"{name}: {df.shape}")

        print("🔹 STEP 3: Load to Database...")
        load_data_to_database(transformed)

        print("🔹 STEP 4: Generate SQL backup...")
        save_to_sql(transformed, OUTPUT_SQL)

        print("\n✅ ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)

        # Lanzar dashboard
        choice = input("\n👉 Launch visualization dashboard? (y/n): ").strip().lower()
        if choice in ['y', 'yes', 'si', 's']:
            print("\n🚀 Launching Visualization Dashboard...")
            run_visualization_dashboard()
        else:
            print("\n👍 ETL completed. You can run visualizations later with: python visualization.py")

    except Exception as e:
        print(f"❌ ETL pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()