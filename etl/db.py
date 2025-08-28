from pathlib import Path
import pandas as pd
import mysql.connector
from connection import get_connection

def create_tables():
    """Create all tables in the database"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Drop tables if they exist (in correct order due to foreign keys)
        drop_statements = [
            "DROP TABLE IF EXISTS Fact_Application",
            "DROP TABLE IF EXISTS Dim_ExperienceRange",
            "DROP TABLE IF EXISTS Dim_Technology", 
            "DROP TABLE IF EXISTS Dim_Seniority",
            "DROP TABLE IF EXISTS Dim_Country",
            "DROP TABLE IF EXISTS Dim_Date",
            "DROP TABLE IF EXISTS Dim_Candidate"
        ]
        
        for statement in drop_statements:
            cursor.execute(statement)
        
        # Create tables
        create_statements = [
            """
            CREATE TABLE Dim_Candidate (
                candidate_key INT PRIMARY KEY,
                email VARCHAR(255),
                first_name VARCHAR(100),
                last_name VARCHAR(100)
            )
            """,
            """
            CREATE TABLE Dim_Date (
                date_key INT PRIMARY KEY,
                date DATE,
                day INT,
                month INT,
                year INT
            )
            """,
            """
            CREATE TABLE Dim_Country (
                country_key INT PRIMARY KEY,
                country_name VARCHAR(100)
            )
            """,
            """
            CREATE TABLE Dim_Seniority (
                seniority_key INT PRIMARY KEY,
                seniority_name VARCHAR(50)
            )
            """,
            """
            CREATE TABLE Dim_Technology (
                technology_key INT PRIMARY KEY,
                technology_name VARCHAR(100)
            )
            """,
            """
            CREATE TABLE Dim_ExperienceRange (
                experience_key INT PRIMARY KEY,
                range_label VARCHAR(20),
                min_years INT,
                max_years INT
            )
            """,
            """
            CREATE TABLE Fact_Application (
                id INT AUTO_INCREMENT PRIMARY KEY,
                candidate_key INT,
                date_key INT,
                country_key INT,
                seniority_key INT,
                technology_key INT,
                experience_key INT,
                code_challenge_score DECIMAL(3,1),
                technical_interview_score DECIMAL(3,1),
                hired_flag TINYINT,
                yoe DECIMAL(3,1),
                FOREIGN KEY (candidate_key) REFERENCES Dim_Candidate(candidate_key),
                FOREIGN KEY (date_key) REFERENCES Dim_Date(date_key),
                FOREIGN KEY (country_key) REFERENCES Dim_Country(country_key),
                FOREIGN KEY (seniority_key) REFERENCES Dim_Seniority(seniority_key),
                FOREIGN KEY (technology_key) REFERENCES Dim_Technology(technology_key),
                FOREIGN KEY (experience_key) REFERENCES Dim_ExperienceRange(experience_key)
            )
            """
        ]
        
        for statement in create_statements:
            cursor.execute(statement)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ All tables created successfully")
        
    except mysql.connector.Error as err:
        print(f"❌ Error creating tables: {err}")
        raise

def save_to_sql(dataframes: dict, output_file: str = "workshop.sql"):
    """
    Generate SQL DDL + INSERT statements for the transformed DataFrames.
    """
    sql_statements = []

    # ==============================
    # CREATE TABLES
    # ==============================
    sql_statements.append("""DROP TABLE IF EXISTS Fact_Application;
DROP TABLE IF EXISTS Dim_ExperienceRange;
DROP TABLE IF EXISTS Dim_Technology;
DROP TABLE IF EXISTS Dim_Seniority;
DROP TABLE IF EXISTS Dim_Country;
DROP TABLE IF EXISTS Dim_Date;
DROP TABLE IF EXISTS Dim_Candidate;
""")

    sql_statements.append("""
    CREATE TABLE Dim_Candidate (
        candidate_key INT PRIMARY KEY,
        email VARCHAR(255),
        first_name VARCHAR(100),
        last_name VARCHAR(100)
    );
    """)

    sql_statements.append("""
    CREATE TABLE Dim_Date (
        date_key INT PRIMARY KEY,
        date DATE,
        day INT,
        month INT,
        year INT
    );
    """)

    sql_statements.append("""
    CREATE TABLE Dim_Country (
        country_key INT PRIMARY KEY,
        country_name VARCHAR(100)
    );
    """)

    sql_statements.append("""
    CREATE TABLE Dim_Seniority (
        seniority_key INT PRIMARY KEY,
        seniority_name VARCHAR(50)
    );
    """)

    sql_statements.append("""
    CREATE TABLE Dim_Technology (
        technology_key INT PRIMARY KEY,
        technology_name VARCHAR(100)
    );
    """)

    sql_statements.append("""
    CREATE TABLE Dim_ExperienceRange (
        experience_key INT PRIMARY KEY,
        range_label VARCHAR(20),
        min_years INT,
        max_years INT
    );
    """)

    sql_statements.append("""
    CREATE TABLE Fact_Application (
        id INT AUTO_INCREMENT PRIMARY KEY,
        candidate_key INT,
        date_key INT,
        country_key INT,
        seniority_key INT,
        technology_key INT,
        experience_key INT,
        code_challenge_score DECIMAL(3,1),
        technical_interview_score DECIMAL(3,1),
        hired_flag TINYINT,
        yoe DECIMAL(3,1),
        FOREIGN KEY (candidate_key) REFERENCES Dim_Candidate(candidate_key),
        FOREIGN KEY (date_key) REFERENCES Dim_Date(date_key),
        FOREIGN KEY (country_key) REFERENCES Dim_Country(country_key),
        FOREIGN KEY (seniority_key) REFERENCES Dim_Seniority(seniority_key),
        FOREIGN KEY (technology_key) REFERENCES Dim_Technology(technology_key),
        FOREIGN KEY (experience_key) REFERENCES Dim_ExperienceRange(experience_key)
    );
    """)

    # ==============================
    # INSERT DATA
    # ==============================
    for table, df in dataframes.items():
        if df.empty:
            continue
        for _, row in df.iterrows():
            values = []
            for v in row:
                if pd.isna(v):
                    values.append("NULL")
                elif isinstance(v, str):
                    values.append("'" + v.replace("'", "''") + "'")
                else:
                    values.append(str(v))
            sql_statements.append(
                f"INSERT INTO {table} ({','.join(df.columns)}) VALUES ({','.join(values)});"
            )

    # Save to file
    Path(output_file).write_text("\n".join(sql_statements), encoding="utf-8")
    print(f"✅ SQL script saved to {output_file}")
