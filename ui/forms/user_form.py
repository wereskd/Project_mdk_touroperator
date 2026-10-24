"""Форма создания / редактирования пользователя."""
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QCheckBox, QDialogButtonBox
)


class UserForm(QDialog):
    def __init__(self, roles: list[dict],
                 user: dict | None = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Пользователь")
        self.setMinimumWidth(360)

        form = QFormLayout(self)

        self.username = QLineEdit(user["username"] if user else "")
        if user:
            self.username.setReadOnly(True)
        form.addRow("Логин:", self.username)

        if not user:
            self.password = QLineEdit()
            self.password.setEchoMode(QLineEdit.EchoMode.Password)
            form.addRow("Пароль:", self.password)
        else:
            self.password = None

        self.full_name = QLineEdit(user["full_name"] if user else "")
        form.addRow("ФИО:", self.full_name)

        self.role_combo = QComboBox()
        for r in roles:
            self.role_combo.addItem(r["name"], r["id"])
        if user:
            for i in range(self.role_combo.count()):
                if self.role_combo.itemText(i) == user["role"]:
                    self.role_combo.setCurrentIndex(i)
                    break
        form.addRow("Роль:", self.role_combo)

        self.active = QCheckBox("Активен")
        self.active.setChecked(bool(user["is_active"]) if user else True)
        form.addRow(self.active)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_data(self) -> dict:
        return {
            "username":  self.username.text().strip(),
            "password":  self.password.text() if self.password else None,
            "full_name": self.full_name.text().strip(),
            "role_id":   self.role_combo.currentData(),
            "is_active": self.active.isChecked(),
        }