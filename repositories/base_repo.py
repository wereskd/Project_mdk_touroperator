from typing import Any
from db.database import Database


class BaseRepository:
    table: str = ""

    def all(self) -> list[dict[str, Any]]:
        conn = Database.connect()
        cur = conn.execute(f"SELECT * FROM {self.table} ORDER BY id")
        return [dict(r) for r in cur.fetchall()]

    def get(self, pk: int) -> dict[str, Any] | None:
        conn = Database.connect()
        cur = conn.execute(f"SELECT * FROM {self.table} WHERE id = ?", (pk,))
        row = cur.fetchone()
        return dict(row) if row else None

    def insert(self, data: dict[str, Any]) -> int:
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        conn = Database.connect()
        cur = conn.execute(
            f"INSERT INTO {self.table} ({keys}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        conn.commit()
        return cur.lastrowid

    def update(self, pk: int, data: dict[str, Any]) -> None:
        assignments = ", ".join(f"{k} = ?" for k in data)
        conn = Database.connect()
        conn.execute(
            f"UPDATE {self.table} SET {assignments} WHERE id = ?",
            (*data.values(), pk),
        )
        conn.commit()

    def delete(self, pk: int) -> None:
        conn = Database.connect()
        conn.execute(f"DELETE FROM {self.table} WHERE id = ?", (pk,))
        conn.commit()

    def search(self, field: str, value: str) -> list[dict[str, Any]]:
        conn = Database.connect()
        cur = conn.execute(
            f"SELECT * FROM {self.table} "
            f"WHERE LOWER({field}) LIKE LOWER(?) ORDER BY id",
            (f"%{value}%",),
        )
        return [dict(r) for r in cur.fetchall()]