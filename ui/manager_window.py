from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QInputDialog
)
from services.tour_service import TourService
from services.contract_service import ContractService
from services.client_service import ClientService
from services.payment_service import PaymentService
from ui.forms.client_form import ClientForm
from ui.forms.contract_form import ContractForm


class ManagerWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.tour_service = TourService()
        self.contract_service = ContractService()
        self.client_service = ClientService()
        self.payment_service = PaymentService()

        self.setWindowTitle(f"Менеджер по продажам — {user.full_name}")
        self.resize(1050, 620)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Меню
        menu_bar = QHBoxLayout()
        for name in ("Каталог туров", "Заявки", "Клиенты", "Оплаты", "Отчёт"):
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
        self.btn_action1 = QPushButton("Действие")
        self.btn_action1.clicked.connect(self._on_action1)
        toolbar.addWidget(self.btn_action1)
        
        self.btn_edit = QPushButton("Изменить")
        self.btn_edit.clicked.connect(self._on_edit)
        toolbar.addWidget(self.btn_edit)
        
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self._refresh)
        toolbar.addWidget(self.btn_refresh)
        root.addLayout(toolbar)

        # Таблица
        self.table = QTableWidget(0, 6)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        self.section_label = QLabel("Раздел: Каталог туров")
        root.addWidget(self.section_label)

        self.current_section = "Каталог туров"
        self._switch_section("Каталог туров")

    def _switch_section(self, name):
        self.current_section = name
        self.section_label.setText(f"Раздел: {name}")
        self.btn_action1.setVisible(True)
        self.btn_edit.setVisible(False)
        
        if name == "Каталог туров":
            self.btn_action1.setText("Оформить заявку")
            self._load_tours()
        elif name == "Заявки":
            self.btn_action1.setVisible(False)
            self.btn_edit.setText("Сменить статус")
            self.btn_edit.setVisible(True)
            self._load_contracts()
        elif name == "Клиенты":
            self.btn_action1.setText("Добавить клиента")
            self.btn_edit.setText("Изменить клиента")
            self.btn_edit.setVisible(True)
            self._load_clients()
        elif name == "Оплаты":
            self.btn_action1.setText("Добавить оплату")
            self._load_payments()
        elif name == "Отчёт":
            self.btn_action1.setVisible(False)
            self._load_report()

    def _load_tours(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Тур", "Начало", "Окончание", "Цена", "Статус"])
        self.table.setRowCount(0)
        for t in self.tour_service.list_tours():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([str(t.id), t.title, str(t.date_start), str(t.date_end), f"{t.price:.2f}", t.status]):
                self.table.setItem(row, col, QTableWidgetItem(v))

    def _load_contracts(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Клиент", "Тур", "Сумма", "Статус"])
        self.table.setRowCount(0)
        for c in self.contract_service.list_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([str(c["id"]), c["client_name"], c["tour_title"], f"{float(c['total']):.2f}", c["status"]]):
                self.table.setItem(row, col, QTableWidgetItem(str(v)))

    def _load_clients(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон"])
        self.table.setRowCount(0)
        for c in self.client_service.list_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([str(c["id"]), c["full_name"], c["phone"]]):
                self.table.setItem(row, col, QTableWidgetItem(str(v)))

    def _load_payments(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Договор", "Сумма", "Статус"])
        self.table.setRowCount(0)
        try:
            for p in self.payment_service.list_all():
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, v in enumerate([str(p["id"]), str(p["contract_id"]), f"{float(p['amount']):.2f}", p["status"]]):
                    self.table.setItem(row, col, QTableWidgetItem(str(v)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить оплаты: {e}")

    def _load_report(self):
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        self.table.setRowCount(0)
        try:
            contracts = self.contract_service.list_all()
            total_sum = sum(float(c["total"]) for c in contracts)
            
            for label, val in [("Всего заявок", len(contracts)), ("Общая сумма", f"{total_sum:.2f} ₽")]:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(label))
                self.table.setItem(row, 1, QTableWidgetItem(str(val)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить отчёт: {e}")

    def _get_selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return None
        try: return int(self.table.item(rows[0].row(), 0).text())
        except: return None

    def _on_action1(self):
        if self.current_section == "Каталог туров":
            self._create_contract()
        elif self.current_section == "Клиенты":
            dlg = ClientForm(parent=self)
            if dlg.exec():
                d = dlg.get_data()
                self.client_service.create(d["full_name"], d["phone"], "", d["passport"])
                self._load_clients()
        elif self.current_section == "Оплаты":
            self._create_payment()

    def _on_edit(self):
        pk = self._get_selected_id()
        if pk is None:
            QMessageBox.warning(self, "Внимание", "Выберите строку из списка")
            return

        if self.current_section == "Клиенты":
            clients = self.client_service.list_all()
            c = next((x for x in clients if x["id"] == pk), None)
            if c:
                dlg = ClientForm(c, parent=self)
                if dlg.exec():
                    d = dlg.get_data()
                    self.client_service.update(pk, d["full_name"], d["phone"], "", d["passport"])
                    self._load_clients()

        elif self.current_section == "Заявки":
            statuses = ["Оформлен", "Оплачен", "Отменён"]
            new_status, ok = QInputDialog.getItem(self, "Статус", "Новый статус:", statuses, 0, False)
            if ok and new_status:
                self.contract_service.update_status(pk, new_status)
                self._load_contracts()

    def _create_contract(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Внимание", "Выберите тур из списка")
            return
            
        tour_id = int(self.table.item(rows[0].row(), 0).text())
        tour_title = self.table.item(rows[0].row(), 1).text()
        price = float(self.table.item(rows[0].row(), 4).text())
        
        dlg = ContractForm(tour_title, price, parent=self)
        if dlg.exec():
            d = dlg.get_data()
            
            if not d["full_name"]:
                QMessageBox.warning(self, "Ошибка", "Введите ФИО клиента!")
                return
            if not d["phone"]:
                QMessageBox.warning(self, "Ошибка", "Введите Телефон клиента!")
                return
                
            try:
                cid = self.client_service.create(d["full_name"], d["phone"], "", "")
                self.contract_service.create(cid, tour_id, self.user.id, "Оформлен", d["total"])
                QMessageBox.information(self, "Успех", "Заявка оформлена!")
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def _create_payment(self):
        contracts = self.contract_service.list_all()
        if not contracts:
            QMessageBox.warning(self, "Внимание", "Сначала создайте хотя бы одну заявку (договор)!")
            return
            
        items = [f"{c['id']} - {c['client_name']} ({c['tour_title']})" for c in contracts]
        
        item, ok = QInputDialog.getItem(self, "Выбор договора", "К какой заявке привязать оплату?", items, 0, False)
        if not ok: return
        
        contract_id = int(item.split(" - ")[0])
        
        amount, ok2 = QInputDialog.getDouble(self, "Оплата", "Сумма оплаты (руб):", 1000.0)
        if not ok2: return

        try:
            self.payment_service.create(contract_id, amount, "Карта", "paid")
            QMessageBox.information(self, "Успех", "Оплата добавлена!")
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