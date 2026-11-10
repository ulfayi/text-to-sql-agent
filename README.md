# Text-to-SQL Retail Analytics Agent 🛍️📊

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Google%20GenAI-SDK-orange.svg" alt="Google GenAI">
  <img src="https://img.shields.io/badge/Streamlit-UI-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

An AI-powered retail analytics agent built with **Python**, **SQLite**, and **Google Gemini API**. It translates natural language business questions into secure, optimized SQL queries, executes them with a built-in **self-correction loop**, and delivers clear business insights through an interactive web UI.

---

## 🚀 Features

- **Dynamic Schema Inspection:** Automatically extracts database tables, DDL structures, and sample rows to feed into the LLM context.
- **Secure Read-Only Execution:** Enforces code-level checks and SQLite URI `mode=ro` flags to prevent any destructive SQL operations (`DROP`, `DELETE`, `UPDATE`).
- **Self-Correction Loop:** Catches SQL execution errors (`sqlite3.Error`), feeds them back to the Gemini model, and automatically rewrites the query.
- **Advanced Business Logic Handling:** Expertly manages complex joins, aggregation traps (Fan-out prevention for discounts), and net profit/COGS calculations.
- **Interactive UI:** A smooth, chat-based web interface built with **Streamlit**.

---

## 🛠️ Tech Stack
Core Logic: **Python**

LLM & Tool Calling: **Google GenAI SDK (gemini-3.5-flash-lite)**

Database: **SQLite (Relational Database)**

Frontend UI: **Streamlit**

## ⚙️ How to Run

1. Clone the repository:
   ```bash
   git clone [https://github.com/user_name/text-to-sql-agent.git](https://github.com/user_name/text-to-sql-agent.git)

   cd text-to-sql-agent

2. Install dependencies:
   ```bash
   pip install google-genai streamlit
4. Set your Gemini API key:
   ```bash

   Windows (CMD): set GEMINI_API_KEY="your-api-key"

   Windows (PowerShell): $env:GEMINI_API_KEY="your-api-key"

   Mac/Linux: export GEMINI_API_KEY="your-api-key"

6. Initialize the database (Mock Retail Data):
   ```bash
   python setup_db.py

7. Run the Web App:
   ```bash
   streamlit run app.py

---

## 📂 Project Structure

```text
text_to_sql_agent/
│
├── setup_db.py           # Initializes the sample SQLite retail database & mock data
├── schema_inspector.py   # Extracts DB schema and sample rows for LLM context
├── sql_agent.py          # Core CLI agent logic with Tool Calling & Self-Correction
├── app.py                # Streamlit web interface application
├── sayad_parfum.db       # SQLite database (auto-generated)
└── README.md             # Project documentation
