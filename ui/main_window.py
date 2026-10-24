from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QLabel, QInputDialog
)
from services.tour_service import TourService
from services.user_service import UserService
from services.direction_service import DirectionService
from services.hotel_service import HotelService
from ui.forms.tour_form import TourForm
from ui.forms.user_form import UserForm
from ui.forms.direction_form import DirectionForm
from ui.forms.hotel_form import HotelForm

ROLE_NAMES = {
    "admin": "Администратор", "manager": "Менеджер по продажам",
    "analyst": "Аналитик", "purchasing": "Менеджер закупок",
    "guide": "Гид-сопровождающий", "accountant": "Главный бухгалтер",
}

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.tour_service = TourService()
        self.user_service = UserService()
        self.direction_service = DirectionService()
        self.hotel_service = HotelService()

        role_ru = ROLE_NAMES.get(user.role, user.role)
        self.setWindowTitle(f"АС «ТурОператор» — {user.full_name} ({role_ru})")
        self.resize(950, 600)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Меню
        menu_bar = QHBoxLayout()
        for name in ("Туры", "Пользователи", "Направления", "Отели"):
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
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по названию тура...")
        toolbar.addWidget(self.search_edit)
        search_btn = QPushButton("Поиск")
        search_btn.clicked.connect(self._on_search)
        toolbar.addWidget(search_btn)
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self._on_add)
        toolbar.addWidget(add_btn)
        edit_btn = QPushButton("Изменить")
        edit_btn.clicked.connect(self._on_edit)
        toolbar.addWidget(edit_btn)
        del_btn = QPushButton("Удалить")
        del_btn.clicked.connect(self._on_delete)
        toolbar.addWidget(del_btn)
        self.reset_pwd_btn = QPushButton("Сбросить пароль")
        self.reset_pwd_btn.clicked.connect(self._on_reset_password)
        self.reset_pwd_btn.setVisible(False)
        toolbar.addWidget(self.reset_pwd_btn)
        root.addLayout(toolbar)

        # Таблица
        self.table = QTableWidget(0, 6)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)
        self.section_label = QLabel("Раздел: Туры")
        root.addWidget(self.section_label)
        self.current_section = "Туры"
        self._switch_section("Туры")

    def _switch_section(self, name):
        self.current_section = name
        self.section_label.setText(f"Раздел: {name}")
        self.reset_pwd_btn.setVisible(name == "Пользователи")
        
        if name == "Туры": self._load_tours()
        elif name == "Пользователи": self._load_users()
        elif name == "Направления": self._load_directions()
        elif name == "Отели": self._load_hotels()

    def _load_tours(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Начало", "Окончание", "Цена", "Статус"])
        self.table.setRowCount(0)
        for t in self.tour_service.list_tours():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([str(t.id), t.title, str(t.date_start), str(t.date_end), f"{t.price:.2f}", t.status]):
                self.table.setItem(row, col, QTableWidgetItem(v))

    def _load_users(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Логин", "ФИО", "Роль", "Активен", "_a"])
        self.table.setRowCount(0)
        for u in self.user_service.list_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([str(u["id"]), u["username"], u["full_name"], u["role"], "Да" if u["is_active"] else "Нет", str(u["is_active"])]):
                self.table.setItem(row, col, QTableWidgetItem(v))
        self.table.setColumnHidden(5, True)

    def _load_directions(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Страна", "Город"])
        self.table.setRowCount(0)
        for d in self.direction_service.list_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([str(d["id"]), d["country"], d["city"]]):
                self.table.setItem(row, col, QTableWidgetItem(v))

    def _load_hotels(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Город", "Звёзд"])
        self.table.setRowCount(0)
        for h in self.hotel_service.list_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([str(h["id"]), h["name"], h["city"], str(h["stars"])]):
                self.table.setItem(row, col, QTableWidgetItem(v))

    def _selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return None
        try: return int(self.table.item(rows[0].row(), 0).text())
        except: return None

    def _on_search(self):
        value = self.search_edit.text().strip()
        if self.current_section == "Туры":
            if not value: 
                self._load_tours()
                return
            self.table.setRowCount(0)
            for t in self.tour_service.search(value):
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, v in enumerate([str(t.id), t.title, str(t.date_start), str(t.date_end), f"{t.price:.2f}", t.status]):
                    self.table.setItem(row, col, QTableWidgetItem(v))
        else:
            QMessageBox.information(self, "Поиск", "Поиск только в разделе «Туры»")

    def _on_add(self):
        if self.current_section == "Туры":
            dlg = TourForm(parent=self)
            if dlg.exec():
                self.tour_service.save(dlg.get_tour())
                self._load_tours()
        elif self.current_section == "Пользователи":
            dlg = UserForm(self.user_service.list_roles(), parent=self)
            if dlg.exec():
                data = dlg.get_data()
                if not data["username"] or not data["password"]:
                    QMessageBox.warning(self, "Ошибка", "Логин и пароль обязательны")
                    return
                self.user_service.create(data["username"], data["password"], data["full_name"], data["role_id"])
                self._load_users()
        elif self.current_section == "Направления":
            dlg = DirectionForm(parent=self)
            if dlg.exec():
                d = dlg.get_data()
                self.direction_service.create(d["country"], d["city"])
                self._load_directions()
        elif self.current_section == "Отели":
            dlg = HotelForm(parent=self)
            if dlg.exec():
                d = dlg.get_data()
                self.hotel_service.create(d["name"], d["city"], d["stars"])
                self._load_hotels()

    def _on_edit(self):
        pk = self._selected_id()
        if pk is None: 
            QMessageBox.information(self, "Изменить", "Выберите строку")
            return
            
        if self.current_section == "Туры":
            row = self.tour_service.repo.get(pk)
            tour = self.tour_service._to_model(row)
            dlg = TourForm(tour, parent=self)
            if dlg.exec(): 
                self.tour_service.save(dlg.get_tour())
                self._load_tours()
        elif self.current_section == "Пользователи":
            users = self.user_service.list_all()
            u = next((x for x in users if x["id"] == pk), None)
            if u:
                dlg = UserForm(self.user_service.list_roles(), u, parent=self)
                if dlg.exec():
                    data = dlg.get_data()
                    self.user_service.update(pk, data["full_name"], data["role_id"], data["is_active"])
                    self._load_users()
        elif self.current_section == "Направления":
            items = self.direction_service.list_all()
            d = next((x for x in items if x["id"] == pk), None)
            if d:
                dlg = DirectionForm(d, parent=self)
                if dlg.exec():
                    data = dlg.get_data()
                    self.direction_service.update(pk, data["country"], data["city"])
                    self._load_directions()
        elif self.current_section == "Отели":
            items = self.hotel_service.list_all()
            h = next((x for x in items if x["id"] == pk), None)
            if h:
                dlg = HotelForm(h, parent=self)
                if dlg.exec():
                    data = dlg.get_data()
                    self.hotel_service.update(pk, data["name"], data["city"], data["stars"])
                    self._load_hotels()

    def _on_delete(self):
        pk = self._selected_id()
        if pk is None: 
            QMessageBox.information(self, "Удалить", "Выберите строку")
            return
            
        if QMessageBox.question(self, "Удалить", f"Удалить запись id={pk}?") != QMessageBox.StandardButton.Yes: 
            return
            
        try:
            if self.current_section == "Туры": 
                self.tour_service.delete(pk)
                self._load_tours()
            elif self.current_section == "Пользователи":
                if pk == self.user.id: 
                    QMessageBox.warning(self, "Удалить", "Нельзя удалить себя")
                    return
                self.user_service.delete(pk)
                self._load_users()
            elif self.current_section == "Направления": 
                self.direction_service.delete(pk)
                self._load_directions()
            elif self.current_section == "Отели": 
                self.hotel_service.delete(pk)
                self._load_hotels()
        except Exception as e:
            err_msg = str(e)
            if "FOREIGN KEY" in err_msg:
                QMessageBox.warning(self, "Невозможно удалить", "На эту запись уже ссылаются другие данные. Сначала удалите их.")
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {e}")

    def _on_reset_password(self):
        if self.current_section != "Пользователи": return
        pk = self._selected_id()
        if pk is None: 
            QMessageBox.information(self, "Пароль", "Выберите пользователя")
            return
        new_pwd, ok = QInputDialog.getText(self, "Сброс пароля", "Новый пароль:", QLineEdit.EchoMode.Password)
        if ok and new_pwd: 
            self.user_service.reset_password(pk, new_pwd)
            QMessageBox.information(self, "Готово", "Пароль обновлён")

    def _logout(self):
        if QMessageBox.question(self, "Выход", "Вы действительно хотите выйти?") == QMessageBox.StandardButton.Yes:
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow(self._on_login_success)
            self.login_window.show()
            self.close()

    def _on_login_success(self, user):
        from main import ROLE_WINDOWS
        WindowClass = ROLE_WINDOWS.get(user.role)
        if WindowClass: 
            self.new_window = WindowClass(user)
            self.new_window.show()