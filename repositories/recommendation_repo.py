from repositories.base_repo import BaseRepository
from db.database import Database

class RecommendationRepository(BaseRepository):
    table = "recommendations"

    def list_with_author(self) -> list[dict]:
        conn = Database.connect()
        cur = conn.execute("""
            SELECT r.*, 
                   t.title AS tour_title,
                   u.full_name AS author_name
            FROM recommendations r
            LEFT JOIN tours t ON t.id = r.tour_id
            LEFT JOIN users u ON u.id = r.author_id
            ORDER BY r.id DESC
        """)
        return [dict(r) for r in cur.fetchall()]