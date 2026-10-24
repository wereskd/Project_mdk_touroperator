"""Сервис справочника отелей."""
from repositories.base_repo import BaseRepository


class _HotelRepository(BaseRepository):
    table = "hotels"


class HotelService:
    def __init__(self):
        self.repo = _HotelRepository()

    def list_all(self) -> list[dict]:
        return self.repo.all()

    def create(self, name: str, city: str, stars: int) -> int:
        return self.repo.insert({"name": name, "city": city, "stars": stars})

    def update(self, pk: int, name: str, city: str, stars: int) -> None:
        self.repo.update(pk, {"name": name, "city": city, "stars": stars})

    def delete(self, pk: int) -> None:
        self.repo.delete(pk)