from repositories.base_repo import BaseRepository
from db.database import Database


class PaymentRepository(BaseRepository):
    table = "payments"

    def list_with_contract(self) -> list[dict]:
        conn = Database.connect()
        cur = conn.execute("""
            SELECT p.*, 
                   c.id AS contract_id
            FROM payments p
            LEFT JOIN contracts c ON c.id = p.contract_id
            ORDER BY p.id DESC
        """)
        return [dict(r) for r in cur.fetchall()]