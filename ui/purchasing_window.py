from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel
)
from services.tour_service import TourService
from services.recommendation_service import RecommendationService
from ui.forms.tour_form import TourForm


class PurchasingWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.tour_service = TourService()
        self.rec_service = RecommendationService()

        self.setWindowTitle(f"Отдел закупок — {user.full_name}")
        self.resize(950, 600)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Меню
        menu_bar = QHBoxLayout()
        for name in ("Управление турами", "Рекомендации аналитика"):
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
        self.btn_add = QPushButton("Создать тур")
        self.btn_add.clicked.connect(self._on_add)
        toolbar.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("Изменить")
        self.btn_edit.clicked.connect(self._on_edit)
        toolbar.addWidget(self.btn_edit)

        self.btn_del = QPushButton("Удалить")
        self.btn_del.clicked.connect(self._on_delete)
        toolbar.addWidget(self.btn_del)

        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self._refresh)
        toolbar.addWidget(self.btn_refresh)
        root.addLayout(toolbar)

        # Таблица
        self.table = QTableWidget(0, 5)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        self.section_label = QLabel("Раздел: Управление турами")
        root.addWidget(self.section_label)

        self.current_section = "Управление турами"
        self._switch_section("Управление турами")

    def _switch_section(self, name):
        self.current_section = name
        self.section_label.setText(f"Раздел: {name}")
        
        if name == "Управление турами":
            self.btn_add.setVisible(True)
            self.btn_edit.setVisible(True)
            self.btn_del.setVisible(True)
            self._load_tours()
        else:
            # В разделе рекомендаций скрываем кнопки редактирования
            self.btn_add.setVisible(False)
            self.btn_edit.setVisible(False)
            self.btn_del.setVisible(False)
            self._load_recommendations()

    # ---------- Загрузка данных ----------
    def _load_tours(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Начало", "Окончание", "Статус"])
        self.table.setRowCount(0)
        for t in self.tour_service.list_tours():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, v in enumerate([str(t.id), t.title, str(t.date_start), str(t.date_end), t.status]):
                self.table.setItem(row, col, QTableWidgetItem(v))

    def _load_recommendations(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Тур", "Приоритет", "Рекомендация (что закупать)"])
        self.table.setRowCount(0)
        
        try:
            # Получаем список рекомендаций от аналитиков
            recs = self.rec_service.list_all()
            if not recs:
                self.table.insertRow(0)
                self.table.setItem(0, 0, QTableWidgetItem("Пока нет рекомендаций от аналитиков"))
                self.table.setSpan(0, 0, 1, 3)
                return

            for r in recs:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r.get("tour_title", "—"))))
                self.table.setItem(row, 1, QTableWidgetItem(str(r.get("priority", "Средний"))))
                self.table.setItem(row, 2, QTableWidgetItem(str(r.get("text", "—"))))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить рекомендации: {e}")

    # ---------- Утилиты ----------
    def _get_selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return None
        try: return int(self.table.item(rows[0].row(), 0).text())
        except: return None

    # ---------- Действия ----------
    def _on_add(self):
        if self.current_section != "Управление турами": return
        dlg = TourForm(parent=self)
        if dlg.exec():
            self.tour_service.save(dlg.get_tour())
            self._refresh()

    def _on_edit(self):
        if self.current_section != "Управление турами": return
        pk = self._get_selected_id()
        if not pk:
            QMessageBox.warning(self, "Внимание", "Выберите тур")
            return
            
        row = self.tour_service.repo.get(pk)
        tour = self.tour_service._to_model(row)
        dlg = TourForm(tour, parent=self)
        if dlg.exec():
            self.tour_service.save(dlg.get_tour())
            self._refresh()

    def _on_delete(self):
        if self.current_section != "Управление турами": return
        pk = self._get_selected_id()
        if not pk: return
        if QMessageBox.question(self, "Удалить", "Удалить тур?") == QMessageBox.StandardButton.Yes:
            self.tour_service.delete(pk)
            self._refresh()

    def _refresh(self):
        self._switch_section(self.current_section)

    # ---------- Выход ----------
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