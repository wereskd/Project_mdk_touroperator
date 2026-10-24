from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QInputDialog
)
from services.contract_service import ContractService
from services.supplier_service import SupplierService
from services.incident_service import IncidentService
from db.database import Database

class AccountantWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.contract_service = ContractService()
        self.supplier_service = SupplierService()
        self.inc_service = IncidentService()

        self.setWindowTitle(f"Бухгалтерия — {user.full_name}")
        self.resize(950, 600)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Меню
        menu_bar = QHBoxLayout()
        for name in ("Отчёт по продажам", "Сверка с поставщиками", "Инциденты по турам"):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self._switch_section(n))
            menu_bar.addWidget(btn)
        menu_bar.addStretch()
        
        logout_btn = QPushButton("Выход")
        logout_btn.clicked.connect(self._logout)
        menu_bar.addWidget(logout_btn)
        root.addLayout(menu_bar)

        # Инструменты
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("Добавить сверку")
        self.btn_add.clicked.connect(self._on_add)
        toolbar.addWidget(self.btn_add)
        
        self.btn_del = QPushButton("Удалить")
        self.btn_del.clicked.connect(self._on_delete)
        toolbar.addWidget(self.btn_del)

        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self._refresh)
        toolbar.addWidget(self.btn_refresh)
        root.addLayout(toolbar)

        # Таблица
        self.table = QTableWidget(0, 3)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        self.section_label = QLabel("Раздел: Отчёт по продажам")
        root.addWidget(self.section_label)

        self.current_section = "Отчёт по продажам"
        self._switch_section("Отчёт по продажам")

    def _switch_section(self, name):
        self.current_section = name
        self.section_label.setText(f"Раздел: {name}")
        
        # Кнопки добавления/удаления только для сверки с поставщиками
        is_suppliers = (name == "Сверка с поставщиками")
        self.btn_add.setVisible(is_suppliers)
        self.btn_del.setVisible(is_suppliers)
        
        if name == "Отчёт по продажам":
            self._load_sales()
        elif name == "Сверка с поставщиками":
            self._load_suppliers()
        else:
            self._load_incidents()

    def _load_sales(self):
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Показатель", "Сумма"])
        self.table.setRowCount(0)
        try:
            conn = Database.connect()
            cur = conn.execute("SELECT SUM(total) as rev FROM contracts WHERE status IN ('Оформлен', 'Оплачен')")
            row = cur.fetchone()
            rev = float(row["rev"] or 0)
            tax = rev * 0.06
            for label, val in [("Выручка", rev), ("Налог (6%)", tax), ("Чистая прибыль", rev - tax)]:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(label))
                self.table.setItem(r, 1, QTableWidgetItem(f"{val:.2f} ₽"))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить отчёт: {e}")

    def _load_suppliers(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Поставщик", "Сумма"])
        self.table.setRowCount(0)
        try:
            for s in self.supplier_service.list_all():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(s.get("id", ""))))
                self.table.setItem(row, 1, QTableWidgetItem(str(s.get("name", "—"))))
                self.table.setItem(row, 2, QTableWidgetItem(str(s.get("contact", "—"))))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить сверки: {e}")

    def _load_incidents(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Тур", "Проблема", "Статус решения"])
        self.table.setRowCount(0)
        try:
            for i in self.inc_service.list_all():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(i["tour_title"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(i["title"])))
                self.table.setItem(row, 2, QTableWidgetItem(str(i.get("status", ""))))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить инциденты: {e}")

    def _on_add(self):
        name, ok = QInputDialog.getText(self, "Сверка", "Название поставщика:")
        if not ok or not name.strip(): return
        amount, ok2 = QInputDialog.getDouble(self, "Сверка", "Сумма (руб):", 1000.0)
        if not ok2: return
        try:
            self.supplier_service.create(name.strip(), amount)
            self._refresh()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить: {e}")

    def _on_delete(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return
        pk = int(self.table.item(rows[0].row(), 0).text())
        if QMessageBox.question(self, "Удалить", "Удалить запись?") == QMessageBox.StandardButton.Yes:
            try:
                self.supplier_service.delete(pk)
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def _refresh(self):
        self._switch_section(self.current_section)

    def _logout(self):
        if QMessageBox.question(self, "Выход", "Вы действительно хотите выйти?") == QMessageBox.StandardButton.Yes:
            from ui.login_window import LoginWindow
            from main import ROLE_WINDOWS
            self.login_window = LoginWindow(self._on_login_success)
            self.login_window.show()
            self.close()

    def _on_login_success(self, user):
        from main import ROLE_WINDOWS
        WindowClass = ROLE_WINDOWS.get(user.role)
        if WindowClass:
            self.new_window = WindowClass(user)
            self.new_window.show()