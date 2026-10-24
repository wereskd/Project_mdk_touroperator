"""Сервис справочника направлений."""
from repositories.base_repo import BaseRepository


class _DirectionRepository(BaseRepository):
    table = "directions"


class DirectionService:
    def __init__(self):
        self.repo = _DirectionRepository()

    def list_all(self) -> list[dict]:
        return self.repo.all()

    def create(self, country: str, city: str) -> int:
        return self.repo.insert({"country": country, "city": city})

    def update(self, pk: int, country: str, city: str) -> None:
        self.repo.update(pk, {"country": country, "city": city})

    def delete(self, pk: int) -> None:
        self.repo.delete(pk)