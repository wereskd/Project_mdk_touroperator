"""Сервис управления пользователями (для администратора)."""
from repositories.user_repo import UserRepository
from db.database import Database


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def list_all(self) -> list[dict]:
        conn = Database.connect()
        cur = conn.execute("""
            SELECT u.id, u.username, u.full_name,
                   u.is_active, r.name AS role, r.id AS role_id
            FROM users u JOIN roles r ON r.id = u.role_id
            ORDER BY u.id
        """)
        return [dict(r) for r in cur.fetchall()]

    def list_roles(self) -> list[dict]:
        conn = Database.connect()
        cur = conn.execute("SELECT id, name FROM roles ORDER BY id")
        return [dict(r) for r in cur.fetchall()]

    def create(self, username, password, full_name, role_id) -> int:
        conn = Database.connect()
        cur = conn.execute("""
            INSERT INTO users (username, password_hash,
                               full_name, role_id, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, (username, password, full_name, role_id))
        conn.commit()
        return cur.lastrowid

    def update(self, pk, full_name, role_id, is_active) -> None:
        conn = Database.connect()
        conn.execute("""
            UPDATE users
            SET full_name = ?, role_id = ?, is_active = ?
            WHERE id = ?
        """, (full_name, role_id, 1 if is_active else 0, pk))
        conn.commit()

    def reset_password(self, pk, new_password) -> None:
        conn = Database.connect()
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_password, pk),
        )
        conn.commit()

    def delete(self, pk: int) -> None:
        conn = Database.connect()
        conn.execute("DELETE FROM users WHERE id = ?", (pk,))
        conn.commit()