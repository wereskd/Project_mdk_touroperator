from repositories.base_repo import BaseRepository
from db.database import Database


class UserRepository(BaseRepository):
    table = "users"

    def find_by_username(self, username: str) -> dict | None:
        conn = Database.connect()
        cur = conn.execute(
            """SELECT u.*, r.name AS role
               FROM users u
               JOIN roles r ON r.id = u.role_id
               WHERE u.username = ?""",
            (username,),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def list_active(self) -> list[dict]:
        """Все активные пользователи — для выпадающего списка."""
        conn = Database.connect()
        cur = conn.execute("""
            SELECT u.id, u.username, u.full_name, r.name AS role
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE u.is_active = 1
            ORDER BY u.id
        """)
        return [dict(r) for r in cur.fetchall()]