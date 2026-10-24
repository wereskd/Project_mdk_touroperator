"""Форма направления."""
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)


class DirectionForm(QDialog):
    def __init__(self, direction: dict | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Направление")
        self.setMinimumWidth(320)

        form = QFormLayout(self)

        self.country = QLineEdit(direction["country"] if direction else "")
        form.addRow("Страна:", self.country)

        self.city = QLineEdit(direction["city"] if direction else "")
        form.addRow("Город:", self.city)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self) -> dict:
        return {
            "country": self.country.text().strip(),
            "city":    self.city.text().strip(),
        }