from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QInputDialog, QDialog, QFormLayout, QComboBox, QTextEdit, QDialogButtonBox
)
from services.recommendation_service import RecommendationService
from services.feedback_service import FeedbackService
from services.tour_service import TourService
from services.incident_service import IncidentService


class RecommendationDialog(QDialog):
    def __init__(self, tours, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новая рекомендация")
        self.setMinimumWidth(400)

        form = QFormLayout(self)

        self.tour_combo = QComboBox()
        self.tour_combo.addItem("— Без привязки к туру —", None)
        for t in tours:
            self.tour_combo.addItem(f"{t.title}", t.id)
        form.addRow("Тур:", self.tour_combo)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Низкий", "Средний", "Высокий"])
        self.priority_combo.setCurrentText("Средний")
        form.addRow("Приоритет:", self.priority_combo)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Например: Высокий спрос, нужно увеличить квоту...")
        self.text_edit.setFixedHeight(100)
        form.addRow("Текст рекомендации:", self.text_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self):
        return {
            "tour_id": self.tour_combo.currentData(),
            "priority": self.priority_combo.currentText(),
            "text": self.text_edit.toPlainText().strip()
        }


class AnalystWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.rec_service = RecommendationService()
        self.fb_service = FeedbackService()
        self.tour_service = TourService()
        self.inc_service = IncidentService()

        self.setWindowTitle(f"Аналитик — {user.full_name}")
        self.resize(1000, 600)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Меню
        menu_bar = QHBoxLayout()
        for name in ("Рекомендации", "Обратная связь", "Инциденты от гидов"):
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
        self.btn_add = QPushButton("Добавить")
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
        self.table = QTableWidget(0, 4)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        self.section_label = QLabel("Раздел: Рекомендации")
        root.addWidget(self.section_label)

        self.current_section = "Рекомендации"
        self._switch_section("Рекомендации")

    def _switch_section(self, name):
        self.current_section = name
        self.section_label.setText(f"Раздел: {name}")
        
        # Скрываем кнопки редактирования, если это инциденты
        is_incidents = (name == "Инциденты от гидов")
        self.btn_add.setVisible(not is_incidents)
        self.btn_edit.setVisible(not is_incidents)
        self.btn_del.setVisible(not is_incidents)
        
        if name == "Рекомендации":
            self._load_recs()
        elif name == "Обратная связь":
            self._load_fb()
        else:
            self._load_incidents()

    def _load_recs(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Тур", "Приоритет", "Текст рекомендации"])
        self.table.setRowCount(0)
        try:
            for r in self.rec_service.list_all():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(r.get("tour_title", "—"))))
                self.table.setItem(row, 2, QTableWidgetItem(str(r.get("priority", "—"))))
                self.table.setItem(row, 3, QTableWidgetItem(str(r["text"])))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def _load_fb(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Оценка", "Комментарий"])
        self.table.setRowCount(0)
        try:
            for f in self.fb_service.list_all():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(f["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(f["rating"])))
                self.table.setItem(row, 2, QTableWidgetItem(str(f["comment"])))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить отзывы: {e}")

    def _load_incidents(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Тур", "Заголовок проблемы", "Решение гида"])
        self.table.setRowCount(0)
        try:
            for i in self.inc_service.list_all():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(i["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(i["tour_title"])))
                self.table.setItem(row, 2, QTableWidgetItem(str(i["title"])))
                self.table.setItem(row, 3, QTableWidgetItem(str(i.get("solution") or "—")))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить инциденты: {e}")

    def _get_selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return None
        try: return int(self.table.item(rows[0].row(), 0).text())
        except: return None

    def _on_add(self):
        if self.current_section == "Рекомендации":
            tours = self.tour_service.list_tours()
            dlg = RecommendationDialog(tours, parent=self)
            if dlg.exec():
                d = dlg.get_data()
                if not d["text"]:
                    QMessageBox.warning(self, "Ошибка", "Введите текст рекомендации")
                    return
                self.rec_service.create(d["tour_id"], self.user.id, d["text"], d["priority"])
                self._refresh()
                    
        elif self.current_section == "Обратная связь":
            rating, ok = QInputDialog.getInt(self, "Отзыв", "Оценка (1-5):", 5, 1, 5)
            if not ok: return
            comment, ok2 = QInputDialog.getMultiLineText(self, "Отзыв", "Комментарий:")
            if ok2 and comment.strip():
                self.fb_service.create(None, None, rating, comment, "Клиент")
                self._refresh()

    def _on_edit(self):
        pk = self._get_selected_id()
        if pk is None: return

        if self.current_section == "Рекомендации":
            text, ok = QInputDialog.getMultiLineText(self, "Изменить", "Новый текст рекомендации:")
            if ok and text.strip():
                self.rec_service.repo.update(pk, {"text": text.strip()})
                self._refresh()

        elif self.current_section == "Обратная связь":
            rating, ok = QInputDialog.getInt(self, "Изменить", "Новая оценка (1-5):", 5, 1, 5)
            if not ok: return
            comment, ok2 = QInputDialog.getMultiLineText(self, "Изменить", "Новый комментарий:")
            if ok2 and comment.strip():
                self.fb_service.repo.update(pk, {"rating": rating, "comment": comment.strip()})
                self._refresh()

    def _on_delete(self):
        pk = self._get_selected_id()
        if pk is None: return
        if QMessageBox.question(self, "Удалить", "Удалить эту запись?") == QMessageBox.StandardButton.Yes:
            if self.current_section == "Рекомендации":
                self.rec_service.delete(pk)
            else:
                self.fb_service.delete(pk)
            self._refresh()

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