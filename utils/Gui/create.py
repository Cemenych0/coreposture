from PySide6.QtGui import (QFont,QIcon)
from PySide6.QtWidgets import (QPushButton,QLineEdit,QMessageBox)
    

from utils.Functionality.db_connection import *
from utils.Gui.constants import BUTTON_STYLE_ACCENT, BUTTON_STYLE_LIGHT, INPUT_FIELD
from utils.Functionality.functions import resource_path

def create_button(text, flag, w= 200, h= 60,font_size= 14):
       
        button = QPushButton(text)
        button.setFont(QFont("Arial", font_size, QFont.Weight.Bold))
        button.setFixedSize(w, h)

        if flag=="light":
            button.setStyleSheet(BUTTON_STYLE_LIGHT)
        else:
            button.setStyleSheet(BUTTON_STYLE_ACCENT)

        return button

def create_input_field(placeholder, is_password=False):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFont(QFont("Arial", 12))
        input_field.setFixedSize(350, 40)
        input_field.setStyleSheet(INPUT_FIELD)
        if is_password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
        return input_field

def show_custom_message(title, message, msg_type):
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(resource_path("Image/app.png")))
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if msg_type == 'warning':
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif msg_type == 'information':
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif msg_type == 'critical':
            msg_box.setIcon(QMessageBox.Icon.Critical)
        
        msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #111530;
            color: white;
            font-family: Arial;
            font-size: 18px;
            min-width: 400px;
            min-height: 200px;
        }
        QMessageBox QLabel {
            color: white;
            font-size: 16px;
            padding: 10px;
        }
        QMessageBox QPushButton {
            background-color: #16213E;
            color: white;
            border-radius: 10px;
            padding: 15px 30px;
            font-size: 16px;
            min-width: 120px;
        }
        QMessageBox QPushButton:hover {
            background-color: #0F3460;
        }
        QMessageBox QPushButton:pressed {
            background-color: #E94560;
        }
        """)
        msg_box.exec()
