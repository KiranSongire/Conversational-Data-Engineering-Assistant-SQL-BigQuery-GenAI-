import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

import os
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

st.title("DataOps SQL Copilot - Fast Mode")

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

schema = """
Tables:

pipeline_runs(
run_id, pipeline_name, source_system, target_table, status,
start_time, end_time, rows_read, rows_written, error_message
)

pipeline_errors(
error_id, run_id, error_type, error_message, error_time, severity
)

data_quality_checks(
check_id, run_id, table_name, check_name, expected_count,
actual_count, check_status, created_at
)
"""

question = st.text_input("Ask your question:")

if question:
    prompt = f"""
You are a SQLite SQL assistant.

Generate ONLY SQLite SQL query.
No explanation.
No markdown.

IMPORTANT:
- status values are uppercase: 'SUCCESS', 'FAILED', 'RUNNING'
- check_status values are uppercase: 'PASS', 'FAIL'
- severity values are uppercase: 'HIGH', 'MEDIUM', 'LOW'

{schema}

Question:
{question}
"""

    with st.spinner("Generating SQL..."):
        sql = llm.invoke(prompt).content.strip()

    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    try:
        conn = sqlite3.connect("dataops_demo.db")
        cursor = conn.cursor()
        sql = sql.replace("'failed'", "'FAILED'")
        sql = sql.replace("'running'", "'RUNNING'")
        sql = sql.replace("'success'", "'SUCCESS'")
        sql = sql.replace("'fail'", "'FAIL'")
        sql = sql.replace("'pass'", "'PASS'")
        sql = sql.replace("'high'", "'HIGH'")
        sql = sql.replace("'medium'", "'MEDIUM'")
        sql = sql.replace("'low'", "'LOW'")
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        st.subheader("Result")
        st.dataframe([dict(zip(columns, row)) for row in rows])

        explain_prompt = f"""
Explain this SQL result in simple data engineering language.

Question: {question}
SQL: {sql}
Rows: {rows}
"""
        explanation = llm.invoke(explain_prompt).content
        st.subheader("Explanation")
        st.write(explanation)

    except Exception as e:
        st.error(f"SQL failed: {e}")