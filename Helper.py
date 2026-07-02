"""Helper functions and tool definitions for SQL database agents (Lessons 4 & 5)."""

import numpy as np
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE_PATH = BASE_DIR / "db" / "test.db"

engine = create_engine(f"sqlite:///{DATABASE_FILE_PATH}")


def get_hospitalized_increase_for_state_on_date(state_abbr, specific_date):
    """Retrieve daily hospitalization increase for a state on a given date."""
    try:
        query = text(
            """
            SELECT date, hospitalizedIncrease
            FROM all_states_history
            WHERE state = :state_abbr AND date = :specific_date;
            """
        )
        with engine.connect() as connection:
            result = pd.read_sql_query(
                query,
                connection,
                params={"state_abbr": state_abbr, "specific_date": specific_date},
            )
        if not result.empty:
            return result.to_dict("records")[0]
        return np.nan
    except Exception as exc:
        print(exc)
        return np.nan


def get_positive_cases_for_state_on_date(state_abbr, specific_date):
    """Retrieve daily positive case increase for a state on a given date."""
    try:
        query = text(
            """
            SELECT date, state, positiveIncrease AS positive_cases
            FROM all_states_history
            WHERE state = :state_abbr AND date = :specific_date;
            """
        )
        with engine.connect() as connection:
            result = pd.read_sql_query(
                query,
                connection,
                params={"state_abbr": state_abbr, "specific_date": specific_date},
            )
        if not result.empty:
            return result.to_dict("records")[0]
        return np.nan
    except Exception as exc:
        print(exc)
        return np.nan


tools_sql = [
    {
        "type": "function",
        "function": {
            "name": "get_hospitalized_increase_for_state_on_date",
            "description": (
                "Retrieves the daily increase in hospitalizations for a specific "
                "state on a specific date."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "state_abbr": {
                        "type": "string",
                        "description": "The abbreviation of the state (e.g., 'NY', 'CA').",
                    },
                    "specific_date": {
                        "type": "string",
                        "description": "The specific date for the query in 'YYYY-MM-DD' format.",
                    },
                },
                "required": ["state_abbr", "specific_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_positive_cases_for_state_on_date",
            "description": (
                "Retrieves the daily increase in positive cases for a specific "
                "state on a specific date."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "state_abbr": {
                        "type": "string",
                        "description": "The abbreviation of the state (e.g., 'NY', 'CA').",
                    },
                    "specific_date": {
                        "type": "string",
                        "description": "The specific date for the query in 'YYYY-MM-DD' format.",
                    },
                },
                "required": ["state_abbr", "specific_date"],
            },
        },
    },
]
