from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QInputDialog
)
from services.tour_service import TourService
from services.incident_service import IncidentService
from ui.forms.incident_form import IncidentForm
from ui.forms.resolve_incident_form import ResolveIncidentForm
from db.database import Database

class GuideWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.tour_service = TourService()
        self.incident_service = IncidentService()

        self.setWindowTitle(f"Сопровождение туров — {user.full_name}")
        self.resize(1050, 620)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        menu_bar = QHBoxLayout()
        for name in ("Инциденты", "Отчёты"):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self._switch_section(n))
            menu_bar.addWidget(btn)
        menu_bar.addStretch()
        logout_btn = QPushButton("Выход")
        logout_btn.clicked.connect(self._logout)
        menu_bar.addWidget(logout_btn)
        root.addLayout(menu_bar)

        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("Новый инцидент")
        self.btn_add.clicked.connect(self._on_add)
        toolbar.addWidget(self.btn_add)
        self.btn_resolve = QPushButton("Решить")
        self.btn_resolve.clicked.connect(self._on_resolve)
        toolbar.addWidget(self.btn_resolve)
        self.btn_del = QPushButton("Удалить")
        self.btn_del.clicked.connect(self._on_delete)
        toolbar.addWidget(self.btn_del)
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self._refresh)
        toolbar.addWidget(self.btn_refresh)
        root.addLayout(toolbar)

        self.table = QTableWidget(0, 5)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        self.section_label = QLabel("Раздел: Инциденты")
        root.addWidget(self.section_label)

        self.current_section = "Инциденты"
        self._switch_section("Инциденты")

    def _switch_section(self, name):
        self.current_section = name
        self.section_label.setText(f"Раздел: {name}")
        if name == "Инциденты": self._load_incidents()
        else: self._load_reports()

    def _load_incidents(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Тур", "Заголовок", "Тип", "Статус", "Решение"])
        self.table.setRowCount(0)
        for i in self.incident_service.list_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([str(i["id"]), i["tour_title"], i["title"], i["incident_type"], i["status"], i.get("solution") or "—"]):
                self.table.setItem(row, col, QTableWidgetItem(str(v)))

    def _load_reports(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Тур", "Всего инцидентов", "Решено"])
        self.table.setRowCount(0)
        conn = Database.connect()
        cur = conn.execute("""
            SELECT t.title, COUNT(i.id) AS total, SUM(CASE WHEN i.status IN ('resolved','closed') THEN 1 ELSE 0 END) AS resolved
            FROM tours t LEFT JOIN incidents i ON i.tour_id = t.id GROUP BY t.id, t.title
        """)
        for r in cur.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([r["title"], str(r["total"]), str(r["resolved"] or 0)]):
                self.table.setItem(row, col, QTableWidgetItem(v))

    def _refresh(self): self._switch_section(self.current_section)

    def _get_id(self):
        rows = self.table.selectionModel().selectedRows()
        return int(self.table.item(rows[0].row(), 0).text()) if rows else None

    def _on_add(self):
        if self.current_section != "Инциденты": return
        tours = [{"id": t.id, "title": t.title} for t in self.tour_service.list_tours()]
        if not tours: QMessageBox.warning(self, "Ошибка", "Нет туров"); return
        dlg = IncidentForm(tours, parent=self)
        if dlg.exec():
            d = dlg.get_data()
            self.incident_service.add(d["tour_id"], d["title"], d["description"], d["incident_type"], d["severity"], self.user.id)
            self._refresh()

    def _on_resolve(self):
        if self.current_section != "Инциденты": return
        pk = self._get_id()
        if not pk: return
        dlg = ResolveIncidentForm("Решение", parent=self)
        if dlg.exec():
            self.incident_service.resolve(pk, dlg.get_solution())
            self._refresh()

    def _on_delete(self):
        if self.current_section != "Инциденты": return
        pk = self._get_id()
        if not pk: return
        if QMessageBox.question(self, "Удалить", "Удалить инцидент?") == QMessageBox.StandardButton.Yes:
            self.incident_service.delete(pk)
            self._refresh()

    def _logout(self): self.close()