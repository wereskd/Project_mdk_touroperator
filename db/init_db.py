"""Создание таблиц и начальных данных для SQLite."""
from db.database import Database


TABLES = [
    """
    CREATE TABLE IF NOT EXISTS roles (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name     TEXT NOT NULL,
        role_id       INTEGER NOT NULL REFERENCES roles(id),
        is_active     INTEGER NOT NULL DEFAULT 1
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS directions (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT NOT NULL,
        city    TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS hotels (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT NOT NULL,
        city  TEXT NOT NULL,
        stars INTEGER CHECK (stars BETWEEN 1 AND 5)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS clients (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone     TEXT,
        email     TEXT,
        passport  TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tours (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        title        TEXT NOT NULL,
        direction_id INTEGER REFERENCES directions(id) ON DELETE SET NULL,
        hotel_id     INTEGER REFERENCES hotels(id)     ON DELETE SET NULL,
        date_start   TEXT NOT NULL,
        date_end     TEXT NOT NULL,
        price        REAL NOT NULL CHECK (price >= 0),
        quota        INTEGER NOT NULL DEFAULT 0 CHECK (quota >= 0),
        status       TEXT NOT NULL DEFAULT 'Черновик'
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS contracts (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id  INTEGER NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
        tour_id    INTEGER NOT NULL REFERENCES tours(id)   ON DELETE RESTRICT,
        manager_id INTEGER REFERENCES users(id)            ON DELETE SET NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        status     TEXT NOT NULL DEFAULT 'Оформлен',
        total      REAL NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS incidents (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        tour_id       INTEGER NOT NULL REFERENCES tours(id) ON DELETE CASCADE,
        author_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
        assignee_id   INTEGER REFERENCES users(id) ON DELETE SET NULL,
        title         TEXT NOT NULL,
        description   TEXT,
        incident_type TEXT NOT NULL DEFAULT 'other',
        severity      TEXT NOT NULL DEFAULT 'normal',
        status        TEXT NOT NULL DEFAULT 'new',
        solution      TEXT,
        created_at    TEXT NOT NULL DEFAULT (datetime('now')),
        closed_at     TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS feedback (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id   INTEGER REFERENCES clients(id) ON DELETE SET NULL,
        tour_id     INTEGER REFERENCES tours(id) ON DELETE SET NULL,
        rating      INTEGER CHECK (rating BETWEEN 1 AND 5),
        comment     TEXT,
        source      TEXT NOT NULL DEFAULT 'Клиент',
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS payments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
        amount      REAL NOT NULL CHECK (amount > 0),
        method      TEXT NOT NULL DEFAULT 'Карта',
        status      TEXT NOT NULL DEFAULT 'paid',
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS recommendations (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        tour_id    INTEGER REFERENCES tours(id) ON DELETE CASCADE,
        author_id  INTEGER REFERENCES users(id) ON DELETE SET NULL,
        text       TEXT NOT NULL,
        priority   TEXT NOT NULL DEFAULT 'normal',
        status     TEXT NOT NULL DEFAULT 'new',
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS suppliers (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT NOT NULL,
        contact TEXT,
        phone   TEXT,
        email   TEXT,
        city    TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS audit_log (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
        action     TEXT NOT NULL,
        entity     TEXT,
        entity_id  INTEGER,
        details    TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
]


INITIAL_ROLES = """
INSERT OR IGNORE INTO roles (id, name) VALUES
    (1, 'admin'), (2, 'manager'), (3, 'analyst'),
    (4, 'purchasing'), (5, 'guide'), (6, 'accountant')
"""

INITIAL_USERS = """
INSERT OR IGNORE INTO users (id, username, password_hash, full_name, role_id) VALUES
    (1, 'admin',      'admin',      'Администратор',        1),
    (2, 'manager',    'manager',    'Дёмина Александра',    2),
    (3, 'analyst',    'analyst',    'Барановский Дмитрий',  3),
    (4, 'purchasing', 'purchasing', 'Смирнова Ольга',       4),
    (5, 'guide',      'guide',      'Петров Иван',          5),
    (6, 'accountant', 'accountant', 'Кузнецова Мария',      6)
"""


def init_database() -> None:
    """Создаёт таблицы и начальные данные, если их ещё нет."""
    conn = Database.connect()

    for sql in TABLES:
        conn.execute(sql)

    conn.execute(INITIAL_ROLES)
    conn.execute(INITIAL_USERS)
    conn.commit()