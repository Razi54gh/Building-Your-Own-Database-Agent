"""Jalur SQL sederhana untuk Ollama — lebih cepat & tidak hang."""

from __future__ import annotations

import re

from langchain_community.utilities import SQLDatabase


def _extract_sql(text: str) -> str:
    """Ambil query SQL dari respons LLM."""
    match = re.search(r"```sql\s*(.*?)```", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"(SELECT[\s\S]+?;)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    for line in lines:
        if line.upper().startswith("SELECT"):
            return line.rstrip(";") + ";"
    raise ValueError(f"Tidak menemukan SQL valid dalam respons:\n{text}")


def ask_sql_simple(llm, db: SQLDatabase, question: str, max_retries: int = 2) -> dict:
    """
    Tanya database dengan 2 langkah: generate SQL -> eksekusi -> jawab.
    Cocok untuk Ollama yang sering hang di SQL agent penuh.
    """
    table_info = db.get_table_info()
    schema_prompt = f"""You are a SQLite expert.
Only use this schema:

{table_info}

Rules:
- Table name is all_states_history
- Use hospitalizedIncrease column when asked about hospitalizations
- Return ONLY one SQL query inside ```sql ... ``` fences
- No INSERT/UPDATE/DELETE/DROP
- Use date LIKE '2020-10%' for October 2020

Question: {question}
"""

    sql = None
    last_error = None
    for attempt in range(max_retries + 1):
        if attempt == 0:
            response = llm.invoke(schema_prompt)
        else:
            fix_prompt = f"""Previous SQL failed: {last_error}
Rewrite ONE correct SQLite query for:
{question}

Schema:
{table_info}

Return ONLY ```sql ... ```"""
            response = llm.invoke(fix_prompt)

        raw = response.content if hasattr(response, "content") else str(response)
        sql = _extract_sql(raw)
        try:
            result = db.run(sql)
            break
        except Exception as exc:
            last_error = exc
            if attempt == max_retries:
                raise RuntimeError(f"SQL gagal setelah {max_retries + 1} percobaan: {exc}\nSQL: {sql}") from exc

    answer_prompt = f"""Question: {question}

SQL executed:
{sql}

Result:
{result}

Write a clear final answer in Markdown.
Include section "Explanation:" with the SQL used.
Use ONLY the query result, do not invent numbers."""

    final = llm.invoke(answer_prompt)
    answer = final.content if hasattr(final, "content") else str(final)

    return {
        "question": question,
        "sql": sql,
        "result": result,
        "output": answer,
    }
