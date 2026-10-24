from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

class ClientForm(QDialog):
    def __init__(self, client=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Клиент")
        self.setMinimumWidth(350)
        self.client = client

        form = QFormLayout(self)

        self.full_name = QLineEdit(client["full_name"] if client else "")
        form.addRow("ФИО:", self.full_name)

        self.phone = QLineEdit(client["phone"] if client else "")
        self.phone.setPlaceholderText("+7 (999) 000-00-00")
        # Разрешаем вводить только цифры, плюс, скобки, дефис и пробел
        regex = QRegularExpression(r"^[\d\+\-\(\)\s]*$")
        self.phone.setValidator(QRegularExpressionValidator(regex, self))
        form.addRow("Телефон:", self.phone)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _validate_and_accept(self):
        if not self.full_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Поле «ФИО» обязательно!")
            return
        if not self.phone.text().strip():
            QMessageBox.warning(self, "Ошибка", "Поле «Телефон» обязательно!")
            return
        self.accept()

    def get_data(self):
        return {
            "full_name": self.full_name.text().strip(),
            "phone":     self.phone.text().strip(),
            "email":     "",
            "passport":  "", # Паспорт удален
        }