from repositories.payment_repo import PaymentRepository


class PaymentService:
    def __init__(self):
        self.repo = PaymentRepository()

    def list_all(self):
        return self.repo.list_with_contract()

    def create(self, contract_id, amount, method, status):
        return self.repo.insert({
            "contract_id": contract_id, 
            "amount": amount,
            "method": method, 
            "status": status,
        })

    def delete(self, pk):
        self.repo.delete(pk)