import streamlit as st
from dotenv import load_dotenv
import os

from sqlalchemy import create_engine

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()

st.set_page_config(page_title="DataOps SQL Copilot")

st.title("GenAI Data Engineering SQL Copilot")

# SQLite connection
engine = create_engine("sqlite:///dataops_demo.db")

db = SQLDatabase(engine)

# Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# SQL Agent
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True
)

question = st.text_input(
    "Ask about pipelines, failures, latency, or data quality:"
)

if question:
    with st.spinner("Thinking..."):
        response = agent_executor.invoke({
            "input": question
        })

        st.subheader("Answer")
        st.write(response["output"])