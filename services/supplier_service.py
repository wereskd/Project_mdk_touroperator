from repositories.supplier_repo import SupplierRepository
from db.database import Database

class SupplierService:
    def __init__(self):
        self.repo = SupplierRepository()

    def list_all(self):
        # Возвращаем всё из таблицы suppliers
        return self.repo.all()

    def create(self, name, amount):
        # Пытаемся сохранить в таблицу suppliers (используем поля name и contact)
        conn = Database.connect()
        cur = conn.execute(
            "INSERT INTO suppliers (name, contact) VALUES (?, ?)",
            (name, str(amount))
        )
        conn.commit()
        return cur.lastrowid

    def delete(self, pk: int):
        self.repo.delete(pk)