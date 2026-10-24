from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

class ContractForm(QDialog):
    def __init__(self, tour_title, tour_price, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Оформление заявки")
        self.setMinimumWidth(350)

        form = QFormLayout(self)

        self.tour_label = QLineEdit(tour_title)
        self.tour_label.setReadOnly(True)
        form.addRow("Выбранный тур:", self.tour_label)

        self.client_name = QLineEdit()
        self.client_name.setPlaceholderText("Фамилия Имя Отчество")
        form.addRow("ФИО клиента:", self.client_name)

        self.client_phone = QLineEdit()
        self.client_phone.setPlaceholderText("+7 (999) 000-00-00")
        # Разрешаем вводить только цифры и символы телефона
        regex = QRegularExpression(r"^[\d\+\-\(\)\s]*$")
        self.client_phone.setValidator(QRegularExpressionValidator(regex, self))
        form.addRow("Телефон:", self.client_phone)

        self.total = QDoubleSpinBox()
        self.total.setMaximum(10_000_000)
        self.total.setValue(tour_price)
        form.addRow("Сумма заявки:", self.total)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self):
        return {
            "full_name": self.client_name.text().strip(),
            "phone": self.client_phone.text().strip(),
            "total": self.total.value()
        }