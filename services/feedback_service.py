from repositories.feedback_repo import FeedbackRepository

class FeedbackService:
    def __init__(self):
        self.repo = FeedbackRepository()

    def list_all(self):
        return self.repo.list_with_names()

    def create(self, client_id, tour_id, rating, comment, source="Клиент"):
        return self.repo.insert({
            "client_id": client_id,
            "tour_id": tour_id,
            "rating": rating,
            "comment": comment,
            "source": source
        })

    def update(self, pk: int, data: dict):
        self.repo.update(pk, data)

    def delete(self, pk: int):
        self.repo.delete(pk)