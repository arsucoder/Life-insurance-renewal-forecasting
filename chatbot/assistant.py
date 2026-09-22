import re

import streamlit as st
from huggingface_hub import InferenceClient

from .data_engine import (
    execute_readonly,
    schema_text,
)


# ============================================================
# HUGGING FACE SETTINGS
# ============================================================

MODEL_NAME = "Qwen/Qwen3-32B"


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
# GET HUGGING FACE CLIENT
# ============================================================

@st.cache_resource
def get_huggingface_client():
    """
    Create and cache the Hugging Face InferenceClient.
    """

    api_key = st.secrets.get(
        "HF_TOKEN",
        None
    )

    if not api_key:

        raise RuntimeError(
            "HF_TOKEN was not found. "
            "Add HF_TOKEN to .streamlit/secrets.toml "
            "or Streamlit Cloud Secrets."
        )

    return InferenceClient(
        api_key=api_key,
        provider="auto",
    )


# ============================================================
# EXTRACT TEXT FROM HUGGING FACE RESPONSE
# ============================================================

def get_response_text(response):
    """
    Safely extract text from a Hugging Face
    chat completion response.
    """

    try:

        content = response.choices[0].message.content

    except (
        AttributeError,
        IndexError,
        TypeError,
    ):

        return ""

    if content is None:

        return ""

    return str(content).strip()


# ============================================================
# CALL HUGGING FACE MODEL
# ============================================================

def call_llm(
    user_prompt,
    temperature=0.0,
    max_tokens=1000,
):
    """
    Send a prompt to the Hugging Face model.
    """

    client = get_huggingface_client()

    response = client.chat.completions.create(
        model=MODEL_NAME,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTION,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],

        temperature=temperature,

        max_tokens=max_tokens,

        stream=False,
    )

    text = get_response_text(response)

    if not text:

        raise RuntimeError(
            "Hugging Face returned an empty response."
        )

    return text


# ============================================================
# CLEAN GENERATED SQL
# ============================================================

def clean_sql(sql):
    """
    Remove markdown code fences and extract
    SELECT/WITH query.
    """

    if not sql:

        return ""

    sql = sql.strip()

    # Remove ```sql
    sql = re.sub(
        r"^```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    # Remove ```SQL
    sql = re.sub(
        r"^```SQL\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    # Remove generic ```
    sql = re.sub(
        r"^```\s*|\s*```$",
        "",
        sql,
    )

    # Find SELECT or WITH
    match = re.search(
        r"(?is)\b(SELECT|WITH)\b.*",
        sql,
    )

    if match:

        sql = match.group(0)

    # Remove trailing markdown fences if any
    sql = sql.replace(
        "```",
        "",
    )

    return sql.strip()


# ============================================================
# VALIDATE SQL
# ============================================================

def validate_sql(sql):
    """
    Basic safety validation.

    Only SELECT/WITH queries are allowed.
    """

    if not sql:

        raise ValueError(
            "The AI model did not generate a SQL query."
        )

    sql_upper = sql.strip().upper()

    # Must start with SELECT or WITH
    if not (
        sql_upper.startswith("SELECT")
        or sql_upper.startswith("WITH")
    ):

        raise ValueError(
            "Generated SQL is not a SELECT/WITH query."
        )

    forbidden_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "COPY",
        "ATTACH",
        "DETACH",
        "INSTALL",
        "LOAD",
        "PRAGMA",
        "CALL",
    ]

    for keyword in forbidden_keywords:

        pattern = rf"\b{keyword}\b"

        if re.search(
            pattern,
            sql_upper,
        ):

            raise ValueError(
                f"Unsafe SQL detected: {keyword}"
            )

    return True


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(
    question,
    tables,
    conversation_history=None,
):
    """
    Ask the Hugging Face model to convert natural language
    into a read-only DuckDB SQL query.
    """

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
9. Do not use read_csv or read_parquet.
10. Keep the result to a maximum of 200 rows.
11. Do not invent columns.
12. Do not explain the SQL.
13. Return only the SQL query.

Generate the SQL now.
"""

    sql = call_llm(
        user_prompt=prompt,
        temperature=0.0,
        max_tokens=1000,
    )

    sql = clean_sql(sql)

    validate_sql(sql)

    return sql


# ============================================================
# EXPLAIN QUERY RESULT
# ============================================================

def explain_result(
    question,
    sql,
    result,
):
    """
    Ask the Hugging Face model to convert the database
    result into a natural-language answer.
    """

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
10. Do not mention SQL unless the user explicitly asks.
11. Answer in natural human language.
12. If the result does not contain enough information
    to answer the question, clearly say so.

Provide the final answer now.
"""

    answer = call_llm(
        user_prompt=prompt,
        temperature=0.2,
        max_tokens=1200,
    )

    return answer


# ============================================================
# MAIN QUESTION FUNCTION
# ============================================================

def answer_question(
    question,
    connection,
    tables,
    conversation_history=None,
):
    """
    Complete pipeline:

    Natural language
            ↓
    Hugging Face LLM
            ↓
       SQL query
            ↓
         DuckDB
            ↓
       Actual result
            ↓
    Hugging Face LLM
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
            sql,
        )

    except Exception as first_error:

        # ----------------------------------------------------
        # Retry once with SQL error
        # ----------------------------------------------------

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

IMPORTANT:

- Use only tables and columns from the schema.
- Do not invent columns.
- Do not invent tables.
- Do not use files.
- Do not use the internet.

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

The corrected query must be read-only.
"""

        corrected_sql = call_llm(
            user_prompt=retry_prompt,
            temperature=0.0,
            max_tokens=1000,
        )

        sql = clean_sql(
            corrected_sql
        )

        validate_sql(sql)

        result = execute_readonly(
            connection,
            sql,
        )

    # --------------------------------------------------------
    # STEP 3: Explain result
    # --------------------------------------------------------

    answer = explain_result(
        question=question,
        sql=sql,
        result=result,
    )

    # --------------------------------------------------------
    # STEP 4: Return
    # --------------------------------------------------------

    return (
        answer,
        sql,
        result,
    )
    
