from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox,
    QDateEdit, QDialogButtonBox, QComboBox
)
from PyQt6.QtCore import QDate
from models.entities import Tour
from services.direction_service import DirectionService
from services.hotel_service import HotelService


class TourForm(QDialog):
    def __init__(self, tour: Tour | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Тур")
        self.tour = tour
        self.dir_service = DirectionService()
        self.hotel_service = HotelService()

        form = QFormLayout(self)

        self.title_edit = QLineEdit(tour.title if tour else "")
        form.addRow("Название:", self.title_edit)

        self.dir_combo = QComboBox()
        self.dir_combo.addItem("— не выбрано —", None)
        for d in self.dir_service.list_all():
            self.dir_combo.addItem(f"{d['country']}, {d['city']}", d["id"])
        if tour and tour.direction_id:
            idx = self.dir_combo.findData(tour.direction_id)
            if idx >= 0: self.dir_combo.setCurrentIndex(idx)
        form.addRow("Направление:", self.dir_combo)

        self.hotel_combo = QComboBox()
        self.hotel_combo.addItem("— не выбрано —", None)
        for h in self.hotel_service.list_all():
            self.hotel_combo.addItem(h["name"], h["id"])
        if tour and tour.hotel_id:
            idx = self.hotel_combo.findData(tour.hotel_id)
            if idx >= 0: self.hotel_combo.setCurrentIndex(idx)
        form.addRow("Отель:", self.hotel_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Черновик", "Активен", "Закрыт"])
        if tour: self.status_combo.setCurrentText(tour.status)
        form.addRow("Статус:", self.status_combo)

        self.start_edit = QDateEdit()
        self.start_edit.setCalendarPopup(True)
        if tour and isinstance(tour.date_start, QDate): pass
        if tour:
            self.start_edit.setDate(QDate(tour.date_start.year, tour.date_start.month, tour.date_start.day))
        else:
            self.start_edit.setDate(QDate.currentDate())
        form.addRow("Дата начала:", self.start_edit)

        self.end_edit = QDateEdit()
        self.end_edit.setCalendarPopup(True)
        if tour:
            self.end_edit.setDate(QDate(tour.date_end.year, tour.date_end.month, tour.date_end.day))
        else:
            self.end_edit.setDate(QDate.currentDate().addDays(7))
        form.addRow("Дата окончания:", self.end_edit)

        self.price_edit = QDoubleSpinBox()
        self.price_edit.setMaximum(10_000_000)
        self.price_edit.setValue(tour.price if tour else 0.0)
        form.addRow("Цена:", self.price_edit)

        self.quota_edit = QSpinBox()
        self.quota_edit.setMaximum(10_000)
        self.quota_edit.setValue(tour.quota if tour else 0)
        form.addRow("Квота:", self.quota_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_tour(self) -> Tour:
        return Tour(
            id=self.tour.id if self.tour else None,
            title=self.title_edit.text().strip(),
            direction_id=self.dir_combo.currentData(),
            hotel_id=self.hotel_combo.currentData(),
            date_start=self.start_edit.date().toPyDate(),
            date_end=self.end_edit.date().toPyDate(),
            price=self.price_edit.value(),
            quota=self.quota_edit.value(),
            status=self.status_combo.currentText(),
        )