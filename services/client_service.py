"""Сервис клиентов."""
from repositories.client_repo import ClientRepository


class ClientService:
    def __init__(self):
        self.repo = ClientRepository()

    def list_all(self):
        return self.repo.all()

    def search(self, value):
        return self.repo.search("full_name", value)

    def create(self, full_name, phone, email, passport):
        return self.repo.insert({
            "full_name": full_name, "phone": phone,
            "email": email, "passport": passport,
        })

    def update(self, pk, full_name, phone, email, passport):
        self.repo.update(pk, {
            "full_name": full_name, "phone": phone,
            "email": email, "passport": passport,
        })

    def delete(self, pk):
        self.repo.delete(pk)