from pathlib import Path
import re

import duckdb
import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# KNOWN PROJECT DATA FILES
# ============================================================

KNOWN_FILES = {
    "monthly_by_insurer": PROJECT_ROOT / "data" / "processed" / "monthly_by_insurer.csv",

    "business_insights": PROJECT_ROOT / "reports" / "business_insights.csv",

    "model_comparison": PROJECT_ROOT / "reports" / "all_insurers_all_models_comparison.csv",

    "final_model_selection": PROJECT_ROOT / "reports" / "final_model_selection.csv",
}


# ============================================================
# DISCOVER CSV FILES
# ============================================================

def discover_csv_files():
    """
    Find CSV files inside the project's data/processed
    and reports directories.
    """

    discovered = {}

    search_directories = [
        PROJECT_ROOT / "data" / "processed",
        PROJECT_ROOT / "reports",
    ]

    for directory in search_directories:

        if not directory.exists():
            continue

        for file_path in directory.glob("*.csv"):

            table_name = re.sub(
                r"[^A-Za-z0-9_]",
                "_",
                file_path.stem
            ).lower()

            discovered[table_name] = file_path

    # Add known files if they exist
    for table_name, file_path in KNOWN_FILES.items():

        if file_path.exists():
            discovered[table_name] = file_path

    return discovered


# ============================================================
# LOAD DATA INTO DUCKDB
# ============================================================

def load_tables():
    """
    Load project CSV files into an in-memory DuckDB database.

    Returns:
        connection
        tables dictionary containing pandas DataFrames
    """

    connection = duckdb.connect(":memory:")

    tables = {}

    csv_files = discover_csv_files()

    for table_name, file_path in csv_files.items():

        try:

            df = pd.read_csv(file_path)

        except Exception:
            continue

        # Clean column names
        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

        # Try to convert date/month columns
        for column in df.columns:

            column_lower = column.lower()

            if (
                "date" in column_lower
                or "month" in column_lower
            ):

                converted = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

                if converted.notna().sum() > 0:

                    df[column] = converted

        tables[table_name] = df

        # Register pandas dataframe as DuckDB table
        connection.register(
            table_name,
            df
        )

    return connection, tables


# ============================================================
# CREATE SCHEMA DESCRIPTION
# ============================================================

def schema_text(tables):
    """
    Create a human-readable schema description
    for Gemini.
    """

    schema_parts = []

    for table_name, df in tables.items():

        columns = []

        for column in df.columns:

            columns.append(
                f"{column} ({df[column].dtype})"
            )

        schema_parts.append(
            f"TABLE: {table_name}\n"
            f"COLUMNS: {', '.join(columns)}\n"
            f"ROWS: {len(df):,}"
        )

    return "\n\n".join(schema_parts)


# ============================================================
# SAFE READ-ONLY SQL EXECUTION
# ============================================================

def execute_readonly(connection, sql):
    """
    Execute only read-only SELECT/WITH queries.

    This prevents Gemini-generated SQL from modifying
    the local database or filesystem.
    """

    query = sql.strip()

    # Remove final semicolon
    query = query.rstrip(";").strip()

    # Only SELECT / WITH queries allowed
    if not re.match(
        r"^(SELECT|WITH)\b",
        query,
        flags=re.IGNORECASE
    ):

        raise ValueError(
            "Only SELECT and WITH queries are allowed."
        )

    # Block dangerous SQL operations
    blocked_patterns = [

        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bDELETE\b",
        r"\bDROP\b",
        r"\bALTER\b",
        r"\bCREATE\b",
        r"\bCOPY\b",
        r"\bATTACH\b",
        r"\bDETACH\b",
        r"\bINSTALL\b",
        r"\bLOAD\b",
        r"\bPRAGMA\b",
        r"\bCALL\b",

        # Prevent reading arbitrary files
        r"\bread_csv\b",
        r"\bread_parquet\b",
        r"\bread_json\b",

        # Prevent network access
        r"\bhttp://",
        r"\bhttps://",
    ]

    for pattern in blocked_patterns:

        if re.search(
            pattern,
            query,
            flags=re.IGNORECASE
        ):

            raise ValueError(
                "The generated query contains a "
                "disallowed operation."
            )

    # Add a maximum result limit if none exists
    if not re.search(
        r"\bLIMIT\s+\d+\b",
        query,
        flags=re.IGNORECASE
    ):

        query = (
            "SELECT * FROM ("
            + query
            + ") AS result "
            "LIMIT 200"
        )

    return connection.execute(query).df()
