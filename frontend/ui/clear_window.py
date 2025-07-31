from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QCheckBox


class CustomMessageBox(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)

        # Создаем вертикальный layout
        layout = QVBoxLayout()

        # Добавляем метку с сообщением
        self.message_label = QLabel(message)
        layout.addWidget(self.message_label)
        self.checkbox1 = QCheckBox("ZaezdMaps")
        self.checkbox2 = QCheckBox("Zaezd")
        self.checkbox3 = QCheckBox("Players")
        self.checkbox1.setChecked(True)

        layout.addWidget(self.checkbox1)
        layout.addWidget(self.checkbox2)
        layout.addWidget(self.checkbox3)
        # Создаем кнопки
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)

        # Добавляем кнопки в layout
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        # Устанавливаем layout
        self.setLayout(layout)
