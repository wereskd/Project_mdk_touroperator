"""Путь к файлу базы данных SQLite."""
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "tour_operator.db"