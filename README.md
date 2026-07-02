# Building Your Own Database Agent

**Project title:** *Building Your Own Database Agent — Natural Language to SQL & CSV Analytics*  
**Course source:** Coursera (Microsoft × Adrian Gonzalez Sanchez)  
**Local implementation:** Python + LangChain + SQLite + multi-provider LLM

---

## Description

This project builds an **AI agent** that answers business and data questions in **natural language** without writing SQL or pandas code manually. The agent can:

- Analyze **CSV** files (US COVID data)
- Connect to a **SQLite** database
- Call **controlled SQL functions** (function calling)
- Mimic the **Assistants API** for database queries

Dataset: `all-states-history.csv` (20,780 rows, 41 columns) from the COVID Tracking Project.

---

## Folder structure

```
Sql/sql/
├── README.md                 ← this guide
├── setup.bat                 ← automated setup (Windows)
├── verify_setup.py           ← environment readiness check
├── setup_data.py             ← download CSV + create SQLite
├── llm_setup.py              ← LLM config (Ollama/Groq/OpenAI/Azure)
├── sql_helper.py             ← fast SQL path for Ollama (L3)
├── assistant_helper.py       ← Assistants API alternative (L5)
├── Helper.py                 ← SQL functions for L4 & L5
├── prompts.py                ← agent prompt templates
├── config.py                 ← loads .env file
├── .env                      ← provider & credentials
├── requirements.txt
├── L2_Interacting_with_a_CSV_Data.ipynb
├── L3_Connecting_to_a_SQL_Database.ipynb
├── L4_Azure_OpenAI_Function_Calling_Feature.ipynb
├── L5_Leveraging_Assistants_API_for_SQL_Databases.ipynb
├── data/all-states-history.csv
└── db/test.db
```

---

## LLM providers

| Provider | Cost | Best for |
|---|---|---|
| **Ollama** (default) | Free | Local learning, no API key |
| **Groq** | Free tier | Faster than Ollama on CPU |
| **OpenAI** | Paid | Best quality, most stable |
| **Azure OpenAI** | Azure subscription | Original Coursera course |

---

## How to run (Visual Studio Code)

### 1. One-time setup

```cmd
cd /d D:\UGM\UGM\Tesis\Sql\sql
setup.bat
```

### 2. Ollama (free)

1. Install: https://ollama.com  
2. Open the Ollama app  
3. CMD: `ollama pull llama3.1:8b`

`.env` file:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

### 3. Verify

```cmd
venv\Scripts\python.exe verify_setup.py
```
Expected result: **READY!**

### 4. VS Code

1. **File → Open Folder** → `Sql\sql`
2. **Python: Select Interpreter** → `venv\Scripts\python.exe`
3. Open a notebook → **Select Kernel** → `venv`
4. **Restart Kernel** → run cells **top to bottom**

---

## Notebooks & expected output

### L2 — Interacting with a CSV Data

**File:** `L2_Interacting_with_a_CSV_Data.ipynb`  
**Goal:** Query a pandas DataFrame using natural language.

| Cell | Expected output |
|---|---|
| LLM setup | `Provider : ollama` / `LLM ready.` |
| Load CSV | `Rows: 20780, Columns: 41` + `head()` table |
| Simple agent | `There are 20780 rows in the dataframe` |
| Complex question | Markdown answer: total hospitalizations in **Texas, July 2020** + **nationwide**, with an **Explanation:** section |

**Example complex-question output:**
```
Final Answer: In July 2020, Texas had X hospitalized patients ...
Nationwide total: Y ...

Explanation:
I filtered the hospitalizedIncrease column where state='TX' and date in July 2020...
```

**Estimated time (Ollama):** 5–15 minutes

---

### L3 — Connecting to a SQL Database

**File:** `L3_Connecting_to_a_SQL_Database.ipynb`  
**Goal:** Translate a natural language question → SQL → answer.

| Cell | Expected output |
|---|---|
| Setup | `Provider : ollama`, `Agent type: ...` |
| Load SQLite | Data loaded into `db/test.db`, table `all_states_history` |
| Ollama mode | `Ollama: skip full SQL agent...` |
| Invoke | `Ollama mode: simple SQL path...` then SQL + result + Markdown answer |

**Example invoke output:**
```
Ollama mode: simple SQL path (faster)...
SQL: SELECT SUM(hospitalizedIncrease) FROM all_states_history WHERE state='NY' AND date LIKE '2020-10%';
Result: [(12345,)]

Final Answer: There were 12345 hospitalized patients in New York during October 2020...
Explanation: ...
```

**Estimated time (Ollama):** 2–8 minutes  
**Note:** Do not use the full SQL agent on Ollama — it can hang for 30+ minutes.

---

### L4 — Azure OpenAI Function Calling Feature

**File:** `L4_Azure_OpenAI_Function_Calling_Feature.ipynb`  
**Goal:** The model automatically calls Python functions.

#### Part 1 — Weather example

| Cell | Expected output |
|---|---|
| Setup | `Client ready. Model: llama3.1:8b` |
| Function call | List of `tool_calls` to `get_current_weather` |
| Final answer | Weather summary for San Francisco, New York, Las Vegas |

**Example output:**
```
ChatCompletion(... content='In San Francisco it is 50°F, in New York 40°F, in Las Vegas 70°F' ...)
```

#### Part 2 — Function calling to the database

| Cell | Expected output |
|---|---|
| Test function | `{'date': '2021-03-05', 'hospitalizedIncrease': 3}` |
| Function call | Model calls `get_hospitalized_increase_for_state_on_date("AK", "2021-03-05")` |
| Answer | `There were 3 hospitalized people in Alaska on 2021-03-05` |

**Estimated time (Ollama):** 5–15 minutes

---

### L5 — Leveraging Assistants API for SQL Databases

**File:** `L5_Leveraging_Assistants_API_for_SQL_Databases.ipynb`  
**Goal:** Agent with database tools (Assistants API equivalent).

| Cell | Expected output |
|---|---|
| Setup | `Assistants API available: False` (if using Ollama) |
| Universal function calling | Answer: Alaska hospitalizations on 2021-03-05 = **3** |
| Assistants API (optional) | `Assistants API not used for this provider.` |

**Example output (Ollama):**
```
Assistants API available: False
...
There were 3 people hospitalized in Alaska on March 5, 2021.
```

**Estimated time (Ollama):** 5–10 minutes

---

## Output summary by lesson

| Lesson | Input (example) | Main output |
|---|---|---|
| **L2** | "How many rows?" | Row count + CSV analysis |
| **L2** | Texas hospitalizations, July 2020 | Number + Explanation |
| **L3** | NY hospitalizations, October 2020 | SQL query + number + Explanation |
| **L4** | Weather in 3 cities | Temperature per city |
| **L4** | Alaska hospitalizations, 2021-03-05 | `{hospitalizedIncrease: 3}` |
| **L5** | Alaska hospitalizations, 2021-03-05 | Natural language answer |

---

## Total time estimates

| Provider | L2 | L3 | L4 | L5 | Total |
|---|---|---|---|---|---|
| **Ollama (CPU)** | 5–15 m | 2–8 m | 5–15 m | 5–10 m | **~30–60 m** |
| **Groq** | 2–5 m | 1–3 m | 2–5 m | 2–5 m | **~10–20 m** |
| **Azure/OpenAI** | 2–5 m | 3–8 m | 2–5 m | 5–15 m | **~15–30 m** |

---

## Alternative providers

### Groq (free, cloud)

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant
```

Sign up: https://console.groq.com

### OpenAI (paid)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Azure (original course)

```env
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://NAME.openai.azure.com
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4-1106
```

---

## Troubleshooting

| Error | Solution |
|---|---|
| `No module named pandas` | Select kernel `venv\Scripts\python.exe` |
| `ChatOllama` import error | `pip install langchain-ollama` |
| `tabulate` missing | `pip install tabulate` |
| L3 hangs 30+ minutes | Interrupt → Restart Kernel → use the new Ollama cell |
| `OutputParserException` | Fixed via `tool-calling` / `sql_helper` |
| `No connection selected` | Ignore — from VS Code SQL extension, not the notebook |
| PowerShell blocks `.ps1` | Use `setup.bat` |
| Ollama not running | Open the Ollama app |

---

## Useful commands

```cmd
setup.bat                              REM full setup
venv\Scripts\python.exe verify_setup.py   REM readiness check
venv\Scripts\python.exe setup_data.py     REM prepare CSV + SQLite
ollama pull llama3.1:8b                   REM download model
ollama list                               REM list installed models
```

---

## References

- Course: *Building Your Own Database Agent* — Coursera / Microsoft
- Dataset: [COVID Tracking Project](https://covidtracking.com/)
- Ollama: https://ollama.com
- Groq: https://console.groq.com

---

## License & notes

This project is for educational purposes. The COVID Tracking Project dataset is archived.  
The local implementation supports providers other than Azure so the course can be run **for free** in Visual Studio Code.
