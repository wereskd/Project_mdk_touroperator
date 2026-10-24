from repositories.base_repo import BaseRepository
from db.database import Database

class FeedbackRepository(BaseRepository):
    table = "feedback"

    def list_with_names(self) -> list[dict]:
        conn = Database.connect()
        cur = conn.execute("""
            SELECT f.*, 
                   cl.full_name AS client_name,
                   t.title AS tour_title
            FROM feedback f
            LEFT JOIN clients cl ON cl.id = f.client_id
            LEFT JOIN tours t ON t.id = f.tour_id
            ORDER BY f.id DESC
        """)
        return [dict(r) for r in cur.fetchall()]