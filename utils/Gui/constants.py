from utils.Functionality.functions import darken_color

PURPLE_PALETTE = {
    'dark': '#111530',
    'medium': '#16213E',
    'light': '#0F3460',
    'accent': '#E94560',
    'text': '#FFFFFF',
    'secondary_text': '#E2E2E2'
}

BUTTON_STYLE_ACCENT = f"""
    QPushButton {{
        background-color: {PURPLE_PALETTE['accent']};
        color: white;
        border-radius: 10px;
        padding: 5px;
    }}
    QPushButton:hover {{
        background-color: {darken_color(color=PURPLE_PALETTE['accent'], factor=0.8)};
    }}
    QPushButton:pressed {{
        background-color: {darken_color(color=PURPLE_PALETTE['accent'], factor=0.7)};
    }}
"""

BUTTON_STYLE_LIGHT = f"""
    QPushButton {{
        background-color: {PURPLE_PALETTE['light']};
        color: white;
        border-radius: 10px;
        padding: 5px;
    }}
    QPushButton:hover {{
        background-color: {darken_color(color=PURPLE_PALETTE['light'], factor=0.8)};
    }}
    QPushButton:pressed {{
        background-color: {darken_color(color=PURPLE_PALETTE['light'], factor=0.7)};
    }}
"""


INPUT_FIELD = f"""
            QLineEdit {{
                background-color: {PURPLE_PALETTE['medium']};
                color: {PURPLE_PALETTE['text']};
                border-radius: 10px;
                padding: 5px;
                border: 1px solid {PURPLE_PALETTE['light']};
            }}
            QLineEdit:focus {{
                border: 2px solid {PURPLE_PALETTE['accent']};
            }}
        """

EDIT_DIALOG = f"""
            QDialog {{
                background-color: {PURPLE_PALETTE['medium']};
            }}
            QLabel {{
                color: {PURPLE_PALETTE['secondary_text']};
                font-size: 14px;
            }}
            QLineEdit {{
                background-color: {PURPLE_PALETTE['medium']};
                color: {PURPLE_PALETTE['text']};
                border-radius: 10px;
                padding: 5px;
                border: 1px solid {PURPLE_PALETTE['light']};
            }}
            QLineEdit:focus {{
                border: 2px solid {PURPLE_PALETTE['accent']};
            }}
        """

USERS_LIST = f"""
            QListWidget {{
                background-color: {PURPLE_PALETTE['dark']};
                color: {PURPLE_PALETTE['text']};
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                border: 1px solid {PURPLE_PALETTE['light']};
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {PURPLE_PALETTE['light']};
            }}
            QListWidget::item:selected {{
                background-color: {PURPLE_PALETTE['accent']};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {PURPLE_PALETTE['light']};
            }}
        """

DASHBOARD_TABS = f"""
            QTabWidget::pane {{
                border: 1px solid {PURPLE_PALETTE['light']};
                background: {PURPLE_PALETTE['dark']};
            }}
            QTabBar::tab {{
                background: {PURPLE_PALETTE['medium']};
                color: {PURPLE_PALETTE['text']};
                padding: 10px;
                border: 1px solid {PURPLE_PALETTE['light']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: {PURPLE_PALETTE['accent']};
                color: white;
            }}
            QTabBar::tab:hover {{
                background: {PURPLE_PALETTE['light']};
            }}
        """
INFO_CONTAINERS = f"""
            background-color: {PURPLE_PALETTE['dark']};
            border-radius: 10px;
            padding: 20px;
        """

LABEL_STYLE = f"""
                font-size: 14px;
                color: {PURPLE_PALETTE['secondary_text']};
                min-width: 120px;
            """
VALUE_STYLE = f"""
                font-size: 15px;
                color: {PURPLE_PALETTE['text']};
                padding: 8px 0;
                border-bottom: 1px solid {PURPLE_PALETTE['light']};
            """

ADD_USER = f"""
            QDialog {{
                background-color: {PURPLE_PALETTE['medium']};
            }}
            QLabel {{
                color: {PURPLE_PALETTE['text']};
            }}
            QLineEdit {{
                background-color: {PURPLE_PALETTE['dark']};
                color: {PURPLE_PALETTE['text']};
                border: 1px solid {PURPLE_PALETTE['light']};
                border-radius: 5px;
                padding: 5px;
            }}
        """

DELETE_USER = f"""
            QMessageBox {{
                background-color: {PURPLE_PALETTE['dark']};
                color: {PURPLE_PALETTE['text']};
            }}
            QMessageBox QLabel {{
                color: {PURPLE_PALETTE['text']};
            }}
            QMessageBox QPushButton {{
                background-color: {PURPLE_PALETTE['medium']};
                color: {PURPLE_PALETTE['text']};
                border: 1px solid {PURPLE_PALETTE['light']};
                padding: 5px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {PURPLE_PALETTE['light']};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {PURPLE_PALETTE['accent']};
            }}
        """

MONITOR_TAB = f"""
            QTabWidget::pane {{
                border: 1px solid {PURPLE_PALETTE['light']};
                background: {PURPLE_PALETTE['dark']};
            }}
            QTabBar::tab {{
                background: {PURPLE_PALETTE['medium']};
                color: {PURPLE_PALETTE['text']};
                padding: 10px;
                border: 1px solid {PURPLE_PALETTE['light']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: {PURPLE_PALETTE['accent']};
                color: white;
            }}
            QTabBar::tab:hover {{
                background: {PURPLE_PALETTE['light']};
            }}
        """

HISTORY_LIST = f"""
            QListWidget {{
                background-color: {PURPLE_PALETTE['dark']};
                color: {PURPLE_PALETTE['text']};
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                border: 1px solid {PURPLE_PALETTE['light']};
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {PURPLE_PALETTE['light']};
            }}
            QListWidget::item:selected {{
                background-color: {PURPLE_PALETTE['accent']};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {PURPLE_PALETTE['light']};
            }}
        """