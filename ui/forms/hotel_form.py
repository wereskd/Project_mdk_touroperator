"""Форма отеля."""
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QDialogButtonBox
)


class HotelForm(QDialog):
    def __init__(self, hotel: dict | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Отель")
        self.setMinimumWidth(340)

        form = QFormLayout(self)

        self.name = QLineEdit(hotel["name"] if hotel else "")
        form.addRow("Название:", self.name)

        self.city = QLineEdit(hotel["city"] if hotel else "")
        form.addRow("Город:", self.city)

        self.stars = QSpinBox()
        self.stars.setMinimum(1)
        self.stars.setMaximum(5)
        self.stars.setValue(hotel["stars"] if hotel else 3)
        form.addRow("Звёзд:", self.stars)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self) -> dict:
        return {
            "name":  self.name.text().strip(),
            "city":  self.city.text().strip(),
            "stars": self.stars.value(),
        }