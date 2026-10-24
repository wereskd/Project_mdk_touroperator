from datetime import date
from repositories.tour_repo import TourRepository
from models.entities import Tour


class TourService:
    def __init__(self):
        self.repo = TourRepository()

    def list_tours(self) -> list[Tour]:
        return [self._to_model(r) for r in self.repo.all()]

    def search(self, value: str) -> list[Tour]:
        return [self._to_model(r) for r in self.repo.search("title", value)]

    def save(self, tour: Tour) -> int:
        data = {
            "title":        tour.title,
            "direction_id": tour.direction_id,
            "hotel_id":     tour.hotel_id,
            "date_start":   tour.date_start.isoformat() if isinstance(tour.date_start, date) else tour.date_start,
            "date_end":     tour.date_end.isoformat() if isinstance(tour.date_end, date) else tour.date_end,
            "price":        tour.price,
            "quota":        tour.quota,
            "status":       tour.status,
        }
        if tour.id is None:
            return self.repo.insert(data)
        self.repo.update(tour.id, data)
        return tour.id

    def delete(self, pk: int) -> None:
        self.repo.delete(pk)

    @staticmethod
    def _to_model(row: dict) -> Tour:
        ds = row["date_start"]
        de = row["date_end"]
        return Tour(
            id=row["id"],
            title=row["title"],
            direction_id=row["direction_id"],
            hotel_id=row["hotel_id"],
            date_start=date.fromisoformat(ds) if isinstance(ds, str) else ds,
            date_end=date.fromisoformat(de) if isinstance(de, str) else de,
            price=float(row["price"]),
            quota=row["quota"],
            status=row["status"],
        )