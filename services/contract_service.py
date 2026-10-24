from repositories.contract_repo import ContractRepository
from db.database import Database


class ContractService:
    def __init__(self):
        self.repo = ContractRepository()

    def list_all(self) -> list[dict]:
        conn = Database.connect()
        cur = conn.execute("""
            SELECT c.id, c.status, c.total,
                   cl.full_name AS client_name,
                   t.title AS tour_title
            FROM contracts c
            JOIN clients cl ON cl.id = c.client_id
            JOIN tours   t  ON t.id = c.tour_id
            ORDER BY c.id DESC
        """)
        return [dict(r) for r in cur.fetchall()]

    def create(self, client_id, tour_id, manager_id, status, total) -> int:
        conn = Database.connect()
        cur = conn.execute("""
            INSERT INTO contracts (client_id, tour_id, manager_id, status, total)
            VALUES (?, ?, ?, ?, ?)
        """, (client_id, tour_id, manager_id, status, total))
        conn.commit()
        return cur.lastrowid

    def update_status(self, pk: int, status: str) -> None:
        conn = Database.connect()
        conn.execute("UPDATE contracts SET status = ? WHERE id = ?", (status, pk))
        conn.commit()

    def delete(self, pk: int) -> None:
        conn = Database.connect()
        conn.execute("DELETE FROM contracts WHERE id = ?", (pk,))
        conn.commit()