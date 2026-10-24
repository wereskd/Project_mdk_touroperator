"""Подключение к SQLite."""
import sqlite3

from config import DB_PATH


class Database:
    """Единая точка подключения к SQLite."""
    _conn = None

    @classmethod
    def connect(cls) -> sqlite3.Connection:
        if cls._conn is None:
            cls._conn = sqlite3.connect(DB_PATH)
            cls._conn.row_factory = sqlite3.Row
            cls._conn.execute("PRAGMA foreign_keys = ON")
        return cls._conn

    @classmethod
    def init_schema(cls) -> None:
        """Создаёт таблицы и начальные данные."""
        cls.close()
        from db.init_db import init_database
        init_database()

    @classmethod
    def close(cls) -> None:
        if cls._conn is not None:
            try:
                cls._conn.close()
            except Exception:
                pass
            cls._conn = None