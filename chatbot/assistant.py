import re

import streamlit as st
from google import genai

from .data_engine import (
    execute_readonly,
    schema_text,
)


# ============================================================
# GEMINI SETTINGS
# ============================================================

#MODEL_NAME = "gemini-2.5-flash"
MODEL_NAME = "gemini-3.6-flash"

# ============================================================
# SYSTEM INSTRUCTIONS
# ============================================================

SYSTEM_INSTRUCTION = """
You are the AI assistant for a Life Insurance Analytics
and Forecasting application.

Your job is to answer questions using the project's actual
data and forecasting/model outputs.

IMPORTANT RULES:

1. Never invent numbers.
2. Never invent insurers, models, dates or metrics.
3. Use the supplied database schema and query results.
4. Historical data and forecast values must be clearly
   distinguished.
5. Forecasts are estimates and should not be presented
   as guaranteed future results.
6. Explain technical results in understandable language.
7. For model comparison, clearly mention the metric used.
8. Do not claim causation unless the supplied data supports it.
9. Do not provide personalized financial or insurance advice.
10. If the available data cannot answer the question,
    clearly say that the required information is not available.
"""


# ============================================================
# GET GEMINI CLIENT
# ============================================================

@st.cache_resource
def get_gemini_client():
    """
    Create and cache the Gemini client.
    """

    api_key = st.secrets.get(
        "GEMINI_API_KEY",
        None
    )

    if not api_key:

        raise RuntimeError(
            "GEMINI_API_KEY was not found. "
            "Add it to .streamlit/secrets.toml."
        )

    return genai.Client(
        api_key=api_key
    )


# ============================================================
# EXTRACT TEXT FROM GEMINI RESPONSE
# ============================================================

def get_response_text(response):
    """
    Safely extract text from Gemini response.
    """

    text = getattr(
        response,
        "text",
        None
    )

    if text is None:
        return ""

    return text.strip()


# ============================================================
# CLEAN GENERATED SQL
# ============================================================

def clean_sql(sql):
    """
    Remove markdown code fences and extract
    SELECT/WITH query.
    """

    sql = sql.strip()

    # Remove ```sql
    sql = re.sub(
        r"^```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE
    )

    # Remove ```
    sql = re.sub(
        r"^```\s*|\s*```$",
        "",
        sql
    )

    # Find SELECT or WITH
    match = re.search(
        r"(?is)\b(SELECT|WITH)\b.*",
        sql
    )

    if match:
        sql = match.group(0)

    return sql.strip()


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(
    question,
    tables,
    conversation_history=None
):
    """
    Ask Gemini to convert natural language
    into a read-only SQL query.
    """

    client = get_gemini_client()

    schema = schema_text(tables)

    history_text = ""

    if conversation_history:

        recent_history = conversation_history[-6:]

        history_text = (
            "\n\nRECENT CONVERSATION:\n"
        )

        for message in recent_history:

            history_text += (
                f"{message['role'].upper()}: "
                f"{message['content']}\n"
            )

    prompt = f"""
Convert the following natural-language question
into ONE DuckDB SQL query.

DATABASE SCHEMA
================

{schema}

USER QUESTION
=============

{question}

{history_text}

SQL RULES
=========

1. Return SQL only.
2. The query must begin with SELECT or WITH.
3. Query ONLY the tables listed in the schema.
4. Use the exact table and column names.
5. Do not create, modify or delete anything.
6. Do not access files.
7. Do not access the internet.
8. Do not use INSERT, UPDATE, DELETE, DROP, ALTER,
   CREATE, COPY, ATTACH, DETACH, INSTALL, LOAD,
   PRAGMA or CALL.
9. Keep the result to a maximum of 200 rows.
10. Do not invent columns.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0,
            "max_output_tokens": 1000,
        },
    )

    return clean_sql(
        get_response_text(response)
    )


# ============================================================
# EXPLAIN QUERY RESULT
# ============================================================

def explain_result(
    question,
    sql,
    result
):
    """
    Ask Gemini to convert the database result
    into a natural-language answer.
    """

    client = get_gemini_client()

    if result.empty:

        result_text = "(No rows returned.)"

    else:

        result_text = result.head(200).to_csv(
            index=False
        )

    prompt = f"""
Answer the user's question using ONLY the database
result provided below.

USER QUESTION
=============

{question}


SQL USED
========

{sql}


DATABASE RESULT
===============

{result_text}


ANSWERING RULES
===============

1. Use only information contained in the result.
2. Never invent values.
3. Include relevant numbers and units.
4. Be concise but explanatory.
5. If there are no rows, explain that the available
   data did not return a matching result.
6. Clearly distinguish historical data from forecasts.
7. If a forecast is involved, call it an estimate.
8. Do not claim causation unless the data establishes it.
9. Do not provide personalized financial advice.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.2,
            "max_output_tokens": 1200,
        },
    )

    return get_response_text(response)


# ============================================================
# MAIN QUESTION FUNCTION
# ============================================================

def answer_question(
    question,
    connection,
    tables,
    conversation_history=None
):
    """
    Complete pipeline:

    Natural language
            ↓
        Gemini
            ↓
       SQL query
            ↓
         DuckDB
            ↓
       Actual result
            ↓
        Gemini
            ↓
     Human answer
    """

    # --------------------------------------------------------
    # STEP 1: Generate SQL
    # --------------------------------------------------------

    sql = generate_sql(
        question=question,
        tables=tables,
        conversation_history=conversation_history,
    )

    # --------------------------------------------------------
    # STEP 2: Execute SQL
    # --------------------------------------------------------

    try:

        result = execute_readonly(
            connection,
            sql
        )

    except Exception as first_error:

        # ----------------------------------------------------
        # Retry once with the SQL error
        # ----------------------------------------------------

        client = get_gemini_client()

        schema = schema_text(tables)

        retry_prompt = f"""
Correct the SQL query below.

QUESTION:
{question}

DATABASE SCHEMA:
{schema}

PREVIOUS SQL:
{sql}

DATABASE ERROR:
{first_error}

Return ONLY one corrected SELECT or WITH DuckDB query.

Do not use:
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
COPY
ATTACH
DETACH
INSTALL
LOAD
PRAGMA
CALL
read_csv
read_parquet
network URLs
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=retry_prompt,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "temperature": 0,
                "max_output_tokens": 1000,
            },
        )

        sql = clean_sql(
            get_response_text(response)
        )

        result = execute_readonly(
            connection,
            sql
        )

    # --------------------------------------------------------
    # STEP 3: Explain result
    # --------------------------------------------------------

    answer = explain_result(
        question=question,
        sql=sql,
        result=result,
    )

    return answer, sql, result
