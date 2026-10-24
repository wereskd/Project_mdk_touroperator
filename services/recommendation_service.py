from repositories.recommendation_repo import RecommendationRepository

class RecommendationService:
    def __init__(self):
        self.repo = RecommendationRepository()

    def list_all(self):
        return self.repo.list_with_author()

    def create(self, tour_id, author_id, text, priority="Средний"):
        return self.repo.insert({
            "tour_id": tour_id,
            "author_id": author_id,
            "text": text,
            "priority": priority,
            "status": "new"
        })

    def update(self, pk: int, data: dict):
        self.repo.update(pk, data)

    def delete(self, pk: int):
        self.repo.delete(pk)