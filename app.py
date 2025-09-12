import sys
import cv2
import sqlite3
import numpy as np
import mediapipe as mp
import bcrypt
import re
from datetime import datetime
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCore import Qt, QTimer, QMarginsF
from PySide6.QtGui import (QPainter, QPen, QImage, QPixmap, QIcon,
                          QFont, QColor, QPalette, QTextDocument)
from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QLabel, 
                              QVBoxLayout, QPushButton, QLineEdit, QMessageBox, 
                              QHBoxLayout, QListWidget, QListWidgetItem, 
                              QSizePolicy, QFileDialog, QTabWidget,QFormLayout,QDialog,)

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


import utils.Functionality.gmail as gmail
from utils.Functionality.db_connection import *
from utils.Gui.constants import PURPLE_PALETTE,EDIT_DIALOG, USERS_LIST, DASHBOARD_TABS,INFO_CONTAINERS, LABEL_STYLE, VALUE_STYLE, ADD_USER, DELETE_USER, MONITOR_TAB, HISTORY_LIST
from utils.Gui.create import create_button, create_input_field, show_custom_message
from utils.Functionality.functions import center_window_top, darken_color, hex_to_bgr, generate_pdf_content, calculate_statistics, resource_path

# Inizializzazione di MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("Image/app.png")))
        self.setWindowTitle("Posture Monitor")
        
        # Imposta la dimensione della finestra
        self.resize(900, 700)
        
        # Posiziona la finestra in alto al centro
        center_window_top(self)
        
        self.setup_ui()


    def setup_ui(self):
        # Configurazione palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(PURPLE_PALETTE['dark']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(PURPLE_PALETTE['text']))
        self.setPalette(palette)

        # Layout principale
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Titolo
        title_label = QLabel("Benvenuto in")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont('Arial', 26, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {PURPLE_PALETTE['text']};")
        layout.addWidget(title_label)

        # Logo
        logo_label = QLabel(self)
        logo_pixmap = QPixmap(resource_path("Image/logo postura.png"))
        logo_pixmap = logo_pixmap.scaled(480, 480, Qt.AspectRatioMode.KeepAspectRatio)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Descrizione
        desc_label = QLabel("Monitora la tua postura in tempo reale\ne migliora le tue abitudini lavorative")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(QFont('Arial', 16))
        desc_label.setStyleSheet(f"color: {PURPLE_PALETTE['secondary_text']};")
        layout.addWidget(desc_label)

        # Pulsanti
        btn_layout = QHBoxLayout()
        
        login_btn = create_button("Accedi", "accent")
        login_btn.clicked.connect(self.show_login)
        btn_layout.addWidget(login_btn)
        
        register_btn = create_button("Registrati", "light")
        register_btn.clicked.connect(self.show_register)
        btn_layout.addWidget(register_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def show_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def show_register(self):
        self.register_window = RegistrationWindow()
        self.register_window.show()
        self.close()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowIcon(QIcon(resource_path("Image/app.png")))
        self.setWindowTitle("Login")
        self.resize(900, 700)
        center_window_top(self)

        # Configurazione palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(PURPLE_PALETTE['dark']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(PURPLE_PALETTE['text']))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        self.title_label = QLabel("Login")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont('Arial', 26, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {PURPLE_PALETTE['text']};")
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap(resource_path("Image/logo postura.png"))
        self.logo_pixmap = self.logo_pixmap.scaled(480, 480, Qt.AspectRatioMode.KeepAspectRatio)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.username_input = create_input_field("Username:")
        layout.addWidget(self.username_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.password_input = create_input_field("Password:", is_password=True)
        layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        
        self.login_button = create_button("Login", "light")
        self.login_button.clicked.connect(self.login_user)
        button_layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        
        self.register_button = create_button("Registrati", "accent")
        self.register_button.clicked.connect(self.open_registration_window)
        button_layout.addWidget(self.register_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.user_id = None

    
    def login_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        cursor.execute("SELECT id, password, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user:
            user_id, stored_hash, role = user
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                self.user_id = user_id
                self.accept_login(username, role)
            else:
                show_custom_message("Login fallito", "Username o password errati!", 'warning')
        else:
            show_custom_message("Login fallito", "Username o password errati!", 'warning')

    def accept_login(self, username, role):
        show_custom_message("Login riuscito", f"Benvenuto {username}!", 'information')
        self.close()
        self.show_monitoring(self.user_id, role)

    def show_monitoring(self, user_id, role):
        if role == "supervisor":
            self.app = SupervisorDashboard(user_id)
        else:
            self.app = PostureApp(user_id)
        self.app.show()

    def open_registration_window(self):
        self.registration_window = RegistrationWindow()
        self.registration_window.show()
        self.close()

class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowIcon(QIcon(resource_path("Image/app.png")))
        self.setWindowTitle("Registrazione")
        self.setGeometry(100, 100, 900, 700)

        # Configurazione palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(PURPLE_PALETTE['dark']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(PURPLE_PALETTE['text']))
        self.setPalette(palette)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(50)

        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("Registrazione")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {PURPLE_PALETTE['text']};")
        logo_layout.addWidget(self.title_label)

        

        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap(resource_path("Image/logo postura.png"))
        self.logo_pixmap = self.logo_pixmap.scaled(450, 450, Qt.AspectRatioMode.KeepAspectRatio)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(self.logo_label)

        main_layout.addLayout(logo_layout)

        # Colonna destra: FORM
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)

        # Layout per input divisi in due colonne
        input_columns_layout = QHBoxLayout()
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()

        # Campi sinistra
        self.full_name_input = create_input_field("Nome Completo:")
        left_column.addWidget(self.full_name_input)

        self.username_input = create_input_field("Username:")
        left_column.addWidget(self.username_input)

        self.email_input = create_input_field("Email:")
        left_column.addWidget(self.email_input)

        # Campi destra
        self.password_input = create_input_field("Password:", is_password=True)
        right_column.addWidget(self.password_input)

        self.confirm_password_input = create_input_field("Conferma Password:", is_password=True)
        right_column.addWidget(self.confirm_password_input)

        self.supervisor_code_input = create_input_field("Codice Supervisore (opzionale):")
        right_column.addWidget(self.supervisor_code_input)


        # Aggiungi colonne al layout
        input_columns_layout.addLayout(left_column)
        input_columns_layout.addSpacing(20)
        input_columns_layout.addLayout(right_column)
        form_layout.addLayout(input_columns_layout)

        # Pulsanti
        # Layout orizzontale per i due pulsanti
        button_row = QHBoxLayout()

        self.register_button = create_button("Registrati", "accent")
        self.register_button.clicked.connect(self.register_user)
        button_row.addWidget(self.register_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.back_to_login_button = create_button("Torna al Login", "light")
        self.back_to_login_button.clicked.connect(self.go_to_login)
        button_row.addWidget(self.back_to_login_button, alignment=Qt.AlignmentFlag.AlignRight)

        form_layout.addLayout(button_row)

        main_layout.addLayout(form_layout)

        self.setLayout(main_layout)
    
    def go_to_login(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def is_valid_password(self, password):
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        return re.match(pattern, password) is not None

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed
    
    def register_user(self):
        full_name = self.full_name_input.text()
        email = self.email_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        supervisor_code = self.supervisor_code_input.text()

        # Validazione dei campi
        if not all([full_name, email, username, password, confirm_password]):
            show_custom_message("Errore", "Tutti i campi sono obbligatori!", 'warning')
            return

        if password != confirm_password:
            show_custom_message("Errore", "Le password non coincidono!", 'warning')
            return

        if not self.is_valid_password(password):
            show_custom_message("Errore", "La password deve contenere almeno 8 caratteri, una lettera maiuscola, una minuscola, un numero e un carattere speciale.", 'warning')
            return

        if not self.is_valid_email(email):
            show_custom_message("Errore", "Inserisci un indirizzo email valido!", 'warning')
            return

        # Verifica se l'username esiste già
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            show_custom_message("Errore", "Nome utente già esistente!", 'warning')
            return

        # Verifica codice supervisore se fornito
        supervisor_id = None
        if supervisor_code:
            cursor.execute("SELECT id FROM users WHERE id = ? AND role = 'supervisor'", (supervisor_code,))
            supervisor = cursor.fetchone()
            if not supervisor:
                show_custom_message("Errore", "Codice supervisore non valido!", 'warning')
                return
            supervisor_id = supervisor[0]

        # Hash della password
        hashed_password = self.hash_password(password)

        try:
            cursor.execute("""
                INSERT INTO users (username, password, role, supervisor_id, full_name, email) 
                VALUES (?, ?, 'user', ?, ?, ?)
            """, (username, hashed_password, supervisor_id, full_name, email))
            conn.commit()
            show_custom_message("Registrazione riuscita", "Registrazione completata con successo!", 'information')
            self.close()
            self.go_to_login()
            gmail.send_registration_email(user_email=email, user_name=username)

        except sqlite3.Error as e:
            show_custom_message("Errore database", f"Errore durante la registrazione: {str(e)}", 'critical')

    def is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

class SupervisorDashboard(QMainWindow):
    def __init__(self, supervisor_id):
        super().__init__()
        self.supervisor_id = supervisor_id
        self.setWindowIcon(QIcon(resource_path("Image/app.png")))
        self.setWindowTitle("Dashboard Supervisore")
        self.setGeometry(200, 30, 1200, 800)
        self.setup_ui()

    def setup_ui(self):
        # Configurazione palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(PURPLE_PALETTE['medium']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(PURPLE_PALETTE['text']))
        self.setPalette(palette)

        # Creazione dei tab
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(DASHBOARD_TABS)

        # Tab Utenti
        self.users_tab = QWidget()
        self.setup_users_tab()
        self.tabs.addTab(self.users_tab, "Gestione Utenti")

        # Tab Statistiche
        self.stats_tab = QWidget()
        self.setup_stats_tab()
        self.tabs.addTab(self.stats_tab, "Statistiche")

        # Tab Profilo
        self.profile_tab = QWidget()
        self.setup_profile_tab()


        # Layout principale
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        # Pulsante logout
        self.logout_button = create_button("Logout", PURPLE_PALETTE['accent'])
        self.logout_button.clicked.connect(self.logout)
        main_layout.addWidget(self.logout_button, alignment=Qt.AlignmentFlag.AlignRight)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def setup_users_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Titolo
        title_label = QLabel("Gestione Utenti")
        title_label.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {PURPLE_PALETTE['text']};")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Lista utenti con connessione per il cambio selezione
        self.users_list = QListWidget()
        self.users_list.setStyleSheet(USERS_LIST)
        self.users_list.itemSelectionChanged.connect(self.update_buttons_state)
        layout.addWidget(self.users_list)

        # Pulsanti azioni
        button_layout = QHBoxLayout()
        
        # Pulsanti (inizialmente disabilitati)
        self.view_user_button = create_button("Visualizza Dettagli", "light")
        self.view_user_button.setEnabled(False)
        self.view_user_button.clicked.connect(self.view_user_details)
        button_layout.addWidget(self.view_user_button)

        self.add_user_button = create_button("Aggiungi Utente", "light")
        self.add_user_button.clicked.connect(self.add_user)
        button_layout.addWidget(self.add_user_button)

        self.delete_user_button = create_button("Elimina Utente", "accent")
        self.delete_user_button.setEnabled(False)
        self.delete_user_button.clicked.connect(self.delete_user)
        button_layout.addWidget(self.delete_user_button)

        layout.addLayout(button_layout)
        self.users_tab.setLayout(layout)
        self.load_users()
    def setup_stats_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Titolo
        title_label = QLabel("Statistiche Utenti")
        title_label.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {PURPLE_PALETTE['text']};")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Grafico statistiche
        self.stats_chart = QChartView()
        self.stats_chart.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.stats_chart)

        # Aggiorna statistiche
        self.update_stats_button = create_button("Aggiorna Statistiche", "accent")
        self.update_stats_button.clicked.connect(self.load_stats)
        layout.addWidget(self.update_stats_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stats_tab.setLayout(layout)
        self.load_stats()

    

    def setup_profile_tab(self):
        """Crea il tab per la visualizzazione del profilo del supervisore"""
        profile_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Titolo
        title = QLabel("Profilo Supervisore")
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PURPLE_PALETTE['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Container informazioni
        info_container = QWidget()
        info_container.setStyleSheet(INFO_CONTAINERS)
        
        info_layout = QFormLayout()
        info_layout.setVerticalSpacing(15)
        info_layout.setHorizontalSpacing(20)

        # Recupera dati supervisore
        cursor.execute("SELECT username, full_name, email, registration_date FROM users WHERE id = ?", (self.supervisor_id,))
        user_data = cursor.fetchone()

        if user_data: 
            username, full_name, email, reg_date = user_data
            
            # Stili coerenti
            label_style = LABEL_STYLE
            value_style = VALUE_STYLE
            fields = [
                ("Username:", username),
                ("Nome Completo:", full_name),
                ("Email:", email),
                ("Data Registrazione:", reg_date),
                ("Codice Supervisore:", str(self.supervisor_id))
            ]
            
            for label_text, value_text in fields:
                label = QLabel(label_text)
                label.setStyleSheet(label_style)
                
                value = QLabel(value_text)
                value.setStyleSheet(value_style)
                
                info_layout.addRow(label, value)

        info_container.setLayout(info_layout)
        layout.addWidget(info_container)
        layout.addStretch()

        # Pulsante modifica profilo
        edit_button = create_button("Modifica Profilo", "accent")
        edit_button.setFixedWidth(200)
        edit_button.clicked.connect(lambda: self.edit_supervisor_profile(username, full_name, email))
        layout.addWidget(edit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        profile_tab.setLayout(layout)
        self.profile_tab = profile_tab  # per referenza futura, se ti serve
        self.tabs.addTab(profile_tab, "Profilo Supervisore")

    def edit_supervisor_profile(self, username, full_name, email):
        # Finestra di dialogo per modificare le informazioni del supervisore
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Modifica Profilo")
        edit_dialog.setFixedSize(400, 400)

        edit_dialog.setStyleSheet(EDIT_DIALOG)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 20, 30, 20)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)

        self.username_edit = QLineEdit(username)
        self.full_name_edit = QLineEdit(full_name)
        self.email_edit = QLineEdit(email)
        
        form_layout.addRow("Username:", self.username_edit)
        form_layout.addRow("Nome Completo:", self.full_name_edit)
        form_layout.addRow("Email:", self.email_edit)

        layout.addLayout(form_layout)

        # Pulsanti
        save_button = create_button("Salva", "accent")
        cancel_button = create_button("Annulla", "light")
        
        # Corrected connection - no arguments, we'll access the fields directly
        save_button.clicked.connect(lambda: self.save_changes(edit_dialog))
        cancel_button.clicked.connect(edit_dialog.reject)

        save_button.setFixedWidth(150)
        cancel_button.setFixedWidth(150)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        edit_dialog.setLayout(layout)
        edit_dialog.adjustSize()  # <--- questa ricalcola le dimensioni in base al contenuto
        edit_dialog.exec()

    # Modified save_changes method to access the fields directly
    def save_changes(self, edit_dialog):
        new_username = self.username_edit.text()
        new_full_name = self.full_name_edit.text()
        new_email = self.email_edit.text()

        # Add validation
        if not all([new_username, new_full_name, new_email]):
            QMessageBox.warning(self, "Errore", "Tutti i campi sono obbligatori!")
            return

        try:
            cursor.execute("""
                UPDATE users SET username = ?, full_name = ?, email = ? WHERE id = ?
            """, (new_username, new_full_name, new_email, self.supervisor_id))
            conn.commit()

            # Show success message
            show_custom_message("Successo", "Modifiche salvate con successo!", "information")
            
            # Close the dialog
            edit_dialog.accept()
            
            # Refresh the profile tab to show changes
            self.tabs.removeTab(2)  # Remove profile tab
            self.setup_profile_tab()  # Recreate it with updated data
            
        except Exception as e:
            conn.rollback()
            show_custom_message("Errore", f"Errore durante il salvataggio:\n{str(e)}", "critical")
    
    
    
    def update_buttons_state(self):
        """Aggiorna lo stato dei pulsanti in base alla selezione"""
        selected_items = self.users_list.selectedItems()
        enabled = bool(selected_items) and selected_items[0].data(Qt.ItemDataRole.UserRole) is not None
        
        self.view_user_button.setEnabled(enabled)
        self.delete_user_button.setEnabled(enabled)

    def load_users(self):
        """Carica gli utenti con gestione avanzata degli stati"""
        self.users_list.clear()
        
        try:
            cursor.execute("""
                SELECT id, username, full_name, email, registration_date 
                FROM users 
                WHERE supervisor_id = ?
                ORDER BY username
            """, (self.supervisor_id,))
            users = cursor.fetchall()

            if not users:
                self.add_empty_list_item()
            else:
                for user in users:
                    self.add_user_item(*user)
                    
        except sqlite3.Error as e:
            show_custom_message("Errore", f"Errore nel caricamento utenti: {str(e)}", 'critical')
            self.add_empty_list_item()

        # Forza l'aggiornamento dello stato dei pulsanti
        self.update_buttons_state()

    def load_stats(self):
        # Statistiche generali
        cursor.execute("""
            SELECT COUNT(DISTINCT u.id), 
                SUM(r.correct_time), 
                SUM(r.incorrect_time),
                COUNT(r.id)
            FROM users u
            LEFT JOIN results r ON u.id = r.user_id
            WHERE u.supervisor_id = ?
        """, (self.supervisor_id,))
        stats = cursor.fetchone()

        total_users = stats[0] if stats else 0
        total_correct = stats[1] if stats and stats[1] else 0
        total_incorrect = stats[2] if stats and stats[2] else 0

        # Crea grafico a torta
        series = QPieSeries()
        
        correct_slice = series.append("Corretta", total_correct)
        correct_slice.setColor(QColor(PURPLE_PALETTE['light']))
        
        incorrect_slice = series.append("Scorretta", total_incorrect)
        incorrect_slice.setColor(QColor(PURPLE_PALETTE['accent']))
        
        # Configura grafico
        
        chart = QChart()
        chart.addSeries(series)

        if(total_users >1):
            chart.setTitle(f"Statistiche Postura - {total_users} Utenti")
        else:
            chart.setTitle(f"Statistiche Postura - {total_users} Utente")

        chart.setTitleFont(QFont("Arial", 14, QFont.Weight.Bold))
        chart.setTitleBrush(QColor(PURPLE_PALETTE['text']))
        chart.legend().setVisible(True)
        chart.legend().setLabelColor(QColor(PURPLE_PALETTE['text']))
        chart.setBackgroundBrush(QColor(PURPLE_PALETTE['dark']))
        
        self.stats_chart.setChart(chart)

    def view_user_details(self):
        if not (selected_item := self.get_valid_selected_item()):
            return 
        selected_item = self.get_valid_selected_item()
        if selected_item:
            user_id = selected_item.data(Qt.ItemDataRole.UserRole)
            self.show_user_details(user_id)

    def get_valid_selected_item(self):
            """Restituisce l'item selezionato solo se valido"""
            selected = self.users_list.selectedItems()
            if selected and selected[0].data(Qt.ItemDataRole.UserRole):
                return selected[0]
            return None
    
    def add_user_item(self, user_id, username, full_name, email, redDate):
        """Aggiunge un elemento utente alla lista"""
        item = QListWidgetItem(f"{username} - {full_name} - {email}")
        item.setData(Qt.ItemDataRole.UserRole, user_id)
        self.users_list.addItem(item)

    def add_empty_list_item(self):
        """Aggiunge un elemento vuoto non selezionabile"""
        item = QListWidgetItem("Nessun utente registrato")
        item.setFlags(Qt.NoItemFlags)
        item.setForeground(QColor("#999999"))
        self.users_list.addItem(item)
        self.users_list.setCurrentItem(None)

    def show_user_details(self, user_id):
        cursor.execute("""
            SELECT u.username, u.full_name, u.email, u.registration_date,
                   COUNT(r.id), SUM(r.correct_time), SUM(r.incorrect_time)
            FROM users u
            LEFT JOIN results r ON u.id = r.user_id
            WHERE u.id = ?
        """, (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            username, full_name, email, reg_date, sessions, correct_time, incorrect_time = user_data
            
            # Creazione finestra dettagli con stile uniforme
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle(f"Dettagli Utente: {username}")
            details_dialog.resize(500, 400)
            details_dialog.setStyleSheet(f"""
                QDialog {{
                    background-color: {PURPLE_PALETTE['medium']};
                }}
                QLabel {{
                    color: {PURPLE_PALETTE['text']};
                }}
            """)
            
            layout = QVBoxLayout()
            layout.setContentsMargins(30, 30, 30, 30)
            layout.setSpacing(20)
            
            # Informazioni base
            info_group = QWidget()
            info_layout = QFormLayout()
            
            info_layout.addRow("Username:", QLabel(username))
            info_layout.addRow("Nome Completo:", QLabel(full_name))
            info_layout.addRow("Email:", QLabel(email))
            info_layout.addRow("Data Registrazione:", QLabel(reg_date))
            info_layout.addRow("Sessioni Completate:", QLabel(str(sessions)))
            
            info_group.setLayout(info_layout)
            layout.addWidget(info_group)
            

            # Statistiche postura
            if sessions > 0:
                stats_group = QWidget()
                stats_layout = QFormLayout()
                
                total_time = correct_time + incorrect_time
                percentage = (correct_time / total_time) * 100 if total_time > 0 else 0
                
                stats_layout.addRow("Tempo Totale Corretto:", QLabel(f"{correct_time:.2f} secondi"))
                stats_layout.addRow("Tempo Totale Scorretto:", QLabel(f"{incorrect_time:.2f} secondi"))
                stats_layout.addRow("Percentuale Corretta:", QLabel(f"{percentage:.1f}%"))
                
                stats_group.setLayout(stats_layout)
                layout.addWidget(stats_group)
                
                # Pulsante per vedere cronologia completa
                history_button = create_button("Visualizza Cronologia Completa", "accent",w=350, h=40, font_size=12)
                history_button.clicked.connect(lambda: self.show_user_history(user_id))
                layout.addWidget(history_button)
            
            details_dialog.setLayout(layout)
            details_dialog.exec()

    def show_user_history(self, user_id):
        # Salva l'istanza come attributo della classe
        self.history_app_window = HistoryApp(user_id)
        self.history_app_window.exec()

    def add_user(self):
        # Finestra di dialogo per aggiungere un nuovo utente con stile uniforme
        dialog = QDialog(self)
        dialog.setWindowTitle("Aggiungi Nuovo Utente")
        dialog.resize(400, 500)
        dialog.setStyleSheet(ADD_USER)
        
        layout = QVBoxLayout()
        
        # Campi del form
        form_layout = QFormLayout()
        
        full_name_input = QLineEdit()
        email_input = QLineEdit()
        username_input = QLineEdit()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_password_input = QLineEdit()
        confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Nome Completo:", full_name_input)
        form_layout.addRow("Email:", email_input)
        form_layout.addRow("Username:", username_input)
        form_layout.addRow("Password:", password_input)
        form_layout.addRow("Conferma Password:", confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Pulsanti
        button_layout = QHBoxLayout()
        
        save_button = create_button("Salva", "accent")
        save_button.clicked.connect(lambda: self.save_new_user(
            full_name_input.text(),
            email_input.text(),
            username_input.text(),
            password_input.text(),
            confirm_password_input.text(),
            dialog
        ))
        
        cancel_button = create_button("Annulla", "light")
        cancel_button.clicked.connect(dialog.close)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()

    def save_new_user(self, full_name, email, username, password, confirm_password, dialog):
        # Validazione
        if not all([full_name, email, username, password, confirm_password]):
            show_custom_message("Errore", "Tutti i campi sono obbligatori!", 'warning')
            return

        if password != confirm_password:
            show_custom_message("Errore", "Le password non coincidono!", 'warning')
            return

        if not RegistrationWindow().is_valid_password(password):
            show_custom_message("Errore", "La password deve contenere almeno 8 caratteri, una lettera maiuscola, una minuscola, un numero e un carattere speciale.", 'warning')
            return

        if not RegistrationWindow().is_valid_email(email):
            show_custom_message("Errore", "Inserisci un indirizzo email valido!", 'warning')
            return

        # Verifica username univoco
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            show_custom_message("Errore", "Username già in uso!", 'warning')
            return

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor.execute("""
                INSERT INTO users (username, password, role, supervisor_id, full_name, email)
                VALUES (?, ?, 'user', ?, ?, ?)
            """, (username, hashed_password, self.supervisor_id, full_name, email))
            conn.commit()
            
            show_custom_message("Successo", "Utente aggiunto con successo!", 'information')
            self.load_users()
            dialog.close()
        except sqlite3.Error as e:
            show_custom_message("Errore", f"Errore durante il salvataggio: {str(e)}", 'critical')

    def delete_user(self):
        
        if not (selected_item := self.get_valid_selected_item()):
            return 
        else:
            selected_item = self.get_valid_selected_item() 
            user_id = selected_item.data(Qt.ItemDataRole.UserRole)
            
            # Conferma eliminazione con stile uniforme
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Conferma Eliminazione")
            msg_box.setText("Sei sicuro di voler eliminare questo utente? Tutti i suoi dati verranno cancellati.")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            msg_box.setStyleSheet(DELETE_USER)
            
            reply = msg_box.exec()
            
            if reply == QMessageBox.Yes:
                try:
                    # Elimina prima i risultati associati
                    cursor.execute("DELETE FROM results WHERE user_id = ?", (user_id,))
                    # Poi elimina l'utente
                    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                    conn.commit()
                    
                    show_custom_message("Successo", "Utente eliminato con successo!", 'information')
                    self.load_users()
                except sqlite3.Error as e:
                    show_custom_message("Errore", f"Errore durante l'eliminazione: {str(e)}", 'critical')

    def logout(self):
        self.close()
        self.welcome_window = WelcomeScreen()
        self.welcome_window.show()


# Finestra di Monitoraggio
class PostureApp(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()

    def setup_ui(self):
        self.setWindowIcon(QIcon(resource_path("Image/app.png")))
        self.setWindowTitle("Analisi della Postura")
        self.setGeometry(180, 30, 1200, 800)

        # Configurazione palette viola
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(PURPLE_PALETTE['medium']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(PURPLE_PALETTE['text']))
        self.setPalette(palette)

        # Crea il widget centrale con tab
        self.tab_widget = QTabWidget()
        # Creazione dei tab
        
        self.tab_widget.setStyleSheet(MONITOR_TAB)
        self.setCentralWidget(self.tab_widget)

        # Tab 1: Applicazione principale
        self.setup_main_tab()
        
        # Tab 2: Profilo utente
        self.setup_profile_tab()

    def setup_main_tab(self):
        """Crea il tab principale con le funzionalità di monitoraggio"""
        main_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Etichetta stato registrazione
        self.recording_status = QLabel("Stato: Pronto")
        self.recording_status.setStyleSheet(f"""
            color: {PURPLE_PALETTE['text']}; 
            font-size: 14px;
            font-weight: bold;
        """)
        layout.addWidget(self.recording_status, alignment=Qt.AlignmentFlag.AlignCenter)

        # Etichetta tempo
        self.time_label = QLabel("Tempo: 00:00")
        self.time_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.time_label.setStyleSheet(f"color: {PURPLE_PALETTE['text']};")
        self.time_label.hide()
        layout.addWidget(self.time_label)

        # Video label
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.video_label.setFixedHeight(500)  # Altezza ridotta per lo spazio dei tab
        self.video_label.hide()
        layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Pulsanti controllo camera
        btn_layout = QHBoxLayout()
        self.start_button = create_button("▶ Avvia", "accent")
        self.start_button = create_button("▶ Avvia", "accent",w=280, h=60, font_size=14)
        self.start_button.clicked.connect(self.start_camera)
        
        self.stop_button = create_button("⏹ Interrompi", "light")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_camera)
        
        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        layout.addLayout(btn_layout)

        # Pulsanti azioni secondarie
        action_layout = QHBoxLayout()
        self.view_history_button = create_button("Visualizza Cronologia", "light",w=280, h=60, font_size=14)
        self.view_history_button.clicked.connect(self.history)

        self.logout_button = create_button("Logout", "accent")
        self.logout_button.clicked.connect(self.logout)

        action_layout.addWidget(self.view_history_button)
        action_layout.addWidget(self.logout_button)
        layout.addLayout(action_layout)

        main_tab.setLayout(layout)
        self.tab_widget.addTab(main_tab, "Monitoraggio Postura")

        # Timer e variabili di stato
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.cap = None
        self.monitoring = False
        self.tempo_scorretta_consecutivo = 0
        self.fps = 30
        self.soglia_avviso = 10
        self.contatore_true = 0
        self.contatore_false = 0
        self.elapsed_time = 0

    def setup_profile_tab(self):
        """Crea il tab per la visualizzazione del profilo utente"""
        profile_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Titolo
        title = QLabel("IL TUO PROFILO")
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PURPLE_PALETTE['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Container informazioni
        info_container = QWidget()
        info_container.setStyleSheet(INFO_CONTAINERS)
        
        info_layout = QFormLayout()
        info_layout.setVerticalSpacing(15)
        info_layout.setHorizontalSpacing(20)

        # Recupera dati utente
        cursor.execute("SELECT username, full_name, email, registration_date FROM users WHERE id = ?", (self.user_id,))
        user_data = cursor.fetchone()

        if user_data:
            username, full_name, email, reg_date = user_data
            
            # Stili per le label
            label_style = LABEL_STYLE
            value_style = VALUE_STYLE
            
            # Campi informativi
            fields = [
                ("Username:", username),
                ("Nome Completo:", full_name),
                ("Email:", email),
                ("Data Registrazione:", reg_date)
            ]
            
            for label_text, value_text in fields:
                label = QLabel(label_text)
                label.setStyleSheet(label_style)
                
                value = QLabel(value_text)
                value.setStyleSheet(value_style)
                
                info_layout.addRow(label, value)

        info_container.setLayout(info_layout)
        layout.addWidget(info_container)
        layout.addStretch()

        # Pulsante modifica profilo
        edit_button = create_button("Modifica Profilo", "accent")
        edit_button.setFixedWidth(200)
        edit_button.clicked.connect(self.edit_profile)
        layout.addWidget(edit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        profile_tab.setLayout(layout)
        # Rimuove il tab del profilo esistente, se presente
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Profilo Utente":
                self.tab_widget.removeTab(i)
                break

        # Aggiunge il nuovo tab aggiornato
        self.tab_widget.addTab(profile_tab, "Profilo Utente")

    def edit_profile(self):
        """Finestra di modifica del profilo"""
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Modifica Profilo")
        edit_dialog.resize(400, 300)
        edit_dialog.setStyleSheet(EDIT_DIALOG)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Recupera i dati attuali
        cursor.execute("SELECT full_name, email FROM users WHERE id = ?", (self.user_id,))
        current_data = cursor.fetchone()
        current_name = current_data[0] if current_data else ""
        current_email = current_data[1] if current_data else ""

        # Campi modificabili
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        
        self.name_edit = QLineEdit(current_name)
        self.email_edit = QLineEdit(current_email)
        
        form_layout.addRow("Nome Completo:", self.name_edit)
        form_layout.addRow("Email:", self.email_edit)
        
        # Validatore per email
        email_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'))
        self.email_edit.setValidator(email_validator)

        layout.addLayout(form_layout)

        # Pulsanti
        button_layout = QHBoxLayout()
        
        save_button = create_button("Salva Modifiche", "accent")
        save_button.clicked.connect(lambda: self.save_profile_changes(edit_dialog))
        
        cancel_button = create_button("Annulla","light")
        cancel_button.clicked.connect(edit_dialog.close)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        edit_dialog.setLayout(layout)
        edit_dialog.exec()

    def save_profile_changes(self, dialog):
        """Salva le modifiche al profilo"""
        new_name = self.name_edit.text().strip()
        new_email = self.email_edit.text().strip()

        if not new_name or not new_email:
            show_custom_message("Errore", "Tutti i campi sono obbligatori!", 'warning')
            return

        if not QRegularExpression(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').match(new_email).hasMatch():
            show_custom_message("Errore", "Inserisci un indirizzo email valido!", 'warning')
            return

        try:
            cursor.execute("""
                UPDATE users 
                SET full_name = ?, email = ?
                WHERE id = ?
            """, (new_name, new_email, self.user_id))
            conn.commit()
            
            show_custom_message("Successo", "Profilo aggiornato con successo!", 'information')
            dialog.close()
            # Ricarica il tab del profilo per mostrare i nuovi dati
            self.setup_profile_tab()
        except sqlite3.Error as e:
            show_custom_message("Errore", f"Errore durante l'aggiornamento: {str(e)}", 'critical')


    def closeEvent(self, event):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if self.timer.isActive():
            self.timer.stop()
        event.accept()

    def logout(self):
        self.close()
        self.open_login_window()

    def open_login_window(self):
        self.welcome_window = WelcomeScreen()
        self.welcome_window.show()

    def start_camera(self):
        if self.user_id is None:
            QMessageBox.warning(self, "Accesso negato", "Per favore, effettua il login prima di avviare la webcam.")
            return

        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise RuntimeError("Impossibile accedere alla webcam")
                
            self.monitoring = True
            self.timer.start(30)

            # Pulsante STOP attivo con stile
            self.stop_button.setEnabled(True)
            self.stop_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PURPLE_PALETTE['light']};
                    color: white;
                    border-radius: 12px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {darken_color(PURPLE_PALETTE['light'], 0.85)};
                }}
            """)

            # Pulsante START disabilitato con stile "spento"
            self.start_button.setEnabled(False)
            self.start_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {darken_color(PURPLE_PALETTE['accent'], 0.8)};
                    color: {PURPLE_PALETTE['secondary_text']};
                    border: 1px solid {PURPLE_PALETTE['medium']};
                    border-radius: 12px;
                    padding: 6px 12px;
                    font-size: 14px;
                }}
            """)

            # Stato attivo
            self.recording_status.setText("🎥 Registrazione in corso...")
            self.recording_status.setStyleSheet(f"""
                color: {PURPLE_PALETTE['accent']};
                font-size: 16px;
                font-weight: 600;
            """)

            self.time_label.show()
            self.video_label.show()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'avvio della webcam: {str(e)}")
            if self.cap:
                self.cap.release()

    def stop_camera(self):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        self.video_label.clear()
        self.monitoring = False

        # Pulsante STOP disattivato
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PURPLE_PALETTE['light']};
                color: {PURPLE_PALETTE['secondary_text']};
                border: 1px solid {PURPLE_PALETTE['medium']};
                border-radius: 12px;
                padding: 6px 12px;
                font-size: 14px;
            }}
        """)

        # Pulsante START riattivato
        self.start_button.setEnabled(True)
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PURPLE_PALETTE['accent']};
                color: {PURPLE_PALETTE['secondary_text']};
                border: 1px solid {PURPLE_PALETTE['medium']};
                border-radius: 12px;
                padding: 6px 12px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {darken_color(PURPLE_PALETTE['accent'], 0.85)};
            }}
        """)

        # Stato aggiornato
        self.recording_status.setText("Stato: Webcam disattivata")
        self.recording_status.setStyleSheet(f"""
            color: {PURPLE_PALETTE['secondary_text']};
            font-size: 14px;
            font-weight: normal;
        """)

        
        # Ripristina stato registrazione
        self.recording_status.setText("Stato: Pronto")
        self.recording_status.setStyleSheet(f"""
            color: {PURPLE_PALETTE['text']}; 
            font-size: 14px;
            font-weight: bold;
        """)
        
        self.time_label.hide()
        self.video_label.hide()
        
        # Salva risultati se c'è stata registrazione
        if self.elapsed_time > 0:
            self.save_results()
        
        # Resetta contatori
        self.contatore_true = 0
        self.contatore_false = 0
        self.elapsed_time = 0
        self.time_label.setText("Tempo: 00:00")

    def save_results(self):
        total_frames = self.contatore_true + self.contatore_false
        if total_frames == 0:
            QMessageBox.information(self, "Nessun dato", "Nessun frame processato durante questa sessione.")
            return
        
        try:
            percentage_true = self.contatore_true / total_frames
            percentage_false = self.contatore_false / total_frames
            total_time_seconds = self.elapsed_time
            correct_time = round(percentage_true * total_time_seconds, 2)
            incorrect_time = round(percentage_false * total_time_seconds, 2)

            # Calcola valutazione (da 1 a 5 stelle)
            score = min(5, max(1, round((percentage_true * 5))))


            cursor.execute("""
            INSERT INTO results (user_id, correct_time, incorrect_time)
            VALUES (?, ?, ?)
            """, (self.user_id, correct_time, incorrect_time))
            conn.commit()

            # Mostra valutazione all'utente
            stars = "⭐" * score
            show_custom_message(
            "Risultati Salvati", 
            f"""Monitoraggio completato!\n\nTempo corretto: {correct_time:.2f}s\nTempo scorretto: {incorrect_time:.2f}s\n\nValutazione: {stars} ({score}/5)""",
            'information'
        )
        except sqlite3.Error as e:
            show_custom_message("Errore database", f"Impossibile salvare i risultati: {str(e)}", 'critical')
    
    
    def update_frame(self):
        if not self.monitoring:
            return

        try:
            ret, frame = self.cap.read()
            if not ret:
                self.stop_camera()
                show_custom_message("Errore", "Impossibile acquisire il frame dalla webcam", 'warning')
                return

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)
            
            self.elapsed_time += 1 / self.fps

            if results.pose_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                landmarks = results.pose_landmarks.landmark
                spalla_destra = (int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * frame.shape[1]),
                                 int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame.shape[0]))
                spalla_sinistra = (int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * frame.shape[1]),
                                   int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame.shape[0]))

                differenza_spalle = abs(spalla_destra[1] - spalla_sinistra[1])

                
                postura_corretta = differenza_spalle <= 10
                posture_status = "POSTURA CORRETTA" if postura_corretta else "POSTURA SCORRETTA"

                # Colori in formato BGR
                posture_color = (
                    hex_to_bgr(PURPLE_PALETTE['light'])  # Viola per postura corretta
                    if postura_corretta 
                    else (0, 0, 255)  # Rosso acceso per postura scorretta
                )
                bg_box_color = (50, 50, 50)  # sfondo scuro opaco (senza alpha per OpenCV)

                # Dimensioni del testo
                (text_w, text_h), baseline = cv2.getTextSize(posture_status, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)

                # Disegna riquadro opaco dietro al testo per renderlo più leggibile
                overlay = frame.copy()
                cv2.rectangle(overlay, (10, 20), (30 + text_w, 50 + text_h), bg_box_color, -1)
                alpha = 0.6
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

                # Disegna il testo sopra al riquadro
                cv2.putText(frame, posture_status, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, posture_color, 2)


                if differenza_spalle > 10:
                    self.tempo_scorretta_consecutivo += 1
                    self.contatore_false += 1
                    
                    # Avviso dopo 5 secondi di postura scorretta
                    if self.tempo_scorretta_consecutivo >= 5 * self.fps:
                        warning_text = "⚠ RADDRIZZA LA SCHIENA!"
                        (text_w, text_h), baseline = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 3)
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (10, 70), (20 + text_w, 100 + text_h), (20, 0, 50), -1)
                        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                        cv2.putText(frame, warning_text, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 70, 70), 3)

                else:
                    self.tempo_scorretta_consecutivo = 0
                    self.contatore_true += 1

                elapsed_minutes = int(self.elapsed_time) // 60
                elapsed_seconds = int(self.elapsed_time) % 60
                self.time_label.setText(f"Tempo: {elapsed_minutes:02}:{elapsed_seconds:02}")

            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
            self.video_label.setPixmap(QPixmap.fromImage(qt_image))

        except Exception as e:
            self.stop_camera()
            show_custom_message("Errore", f"Errore durante l'elaborazione del frame: {str(e)}", 'critical')

    def history(self):
        self.history_app = HistoryApp(self.user_id)
        self.history_app.exec()

class PostureChart(QDialog):
    def __init__(self, correct_time, incorrect_time):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("Image/app.png")))
        self.setWindowTitle("Grafico Postura")
        self.resize(600, 500)
        
        # Configurazione palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(PURPLE_PALETTE['medium']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(PURPLE_PALETTE['text']))
        self.setPalette(palette)

        # Layout principale
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Creazione serie e fette del grafico
        series = QPieSeries()
        
        # Fetta postura corretta (viola chiaro)
        correct_slice = series.append("Postura Corretta", correct_time)
        correct_slice.setLabelVisible(True)
        correct_slice.setPen(QPen(QColor(PURPLE_PALETTE['light']), 2))
        correct_slice.setBrush(QColor(PURPLE_PALETTE['light']))
        
        # Fetta postura scorretta (accento rosato)
        incorrect_slice = series.append("Postura Scorretta", incorrect_time)
        incorrect_slice.setLabelVisible(True)
        incorrect_slice.setPen(QPen(QColor(PURPLE_PALETTE['accent']), 2))
        incorrect_slice.setBrush(QColor(PURPLE_PALETTE['accent']))
        incorrect_slice.setExploded(True)
        incorrect_slice.setExplodeDistanceFactor(0.1)

        # Etichette con percentuali
        total_time = correct_time + incorrect_time
        if total_time > 0:
            correct_slice.setLabel(f"✔ Corretta ({(correct_time / total_time) * 100:.1f}%)")
            incorrect_slice.setLabel(f"❌ Scorretta ({(incorrect_time / total_time) * 100:.1f}%)")

        # Configurazione del grafico
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Monitoraggio della Postura")
        chart.setTitleFont(QFont("Arial", 16, QFont.Weight.Bold))
        chart.setTitleBrush(QColor(PURPLE_PALETTE['text']))
        chart.legend().setVisible(True)
        chart.legend().setLabelColor(QColor(PURPLE_PALETTE['text']))
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        chart.setBackgroundBrush(QColor(PURPLE_PALETTE['dark']))
        chart.setPlotAreaBackgroundBrush(QColor(PURPLE_PALETTE['medium']))

        # Vista del grafico
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(chart_view)

        # Pulsante Chiudi
        close_button = QPushButton("Chiudi")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PURPLE_PALETTE['accent']};
                color: white;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {darken_color(PURPLE_PALETTE['accent'])};
            }}
        """)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

class HistoryApp(QDialog):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowIcon(QIcon(resource_path("Image/app.png")))
        self.setWindowTitle("Cronologia Monitoraggi")
        self.resize(900, 700)
        center_window_top(self)
        self.setup_ui()

    def setup_ui(self):
        # Configurazione palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(PURPLE_PALETTE['medium']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(PURPLE_PALETTE['text']))
        self.setPalette(palette)

        # Layout principale
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # Titolo
        self.title_label = QLabel("Cronologia dei Monitoraggi")
        self.title_label.setFont(QFont('Arial', 22, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"color: {PURPLE_PALETTE['text']};")
        self.layout.addWidget(self.title_label)

        # Lista cronologia
        self.history_list = QListWidget()
        self.history_list.setStyleSheet(HISTORY_LIST)
        self.layout.addWidget(self.history_list)

        # Pulsanti azioni
        self.button_layout = QHBoxLayout()
        
        self.view_button = create_button("👁️ Visualizza", "light")
        self.view_button.clicked.connect(self.view_selected)
        self.button_layout.addWidget(self.view_button)

        self.delete_button = create_button("🗑️ Elimina", "accent")
        self.delete_button.clicked.connect(self.delete_selected)
        self.button_layout.addWidget(self.delete_button)
        
        self.layout.addLayout(self.button_layout)

        self.export_button = create_button("Esporta PDF", "light")
        self.export_button.clicked.connect(self.export_to_pdf)
        self.button_layout.addWidget(self.export_button)

        # Pulsante chiusura
        self.close_button = create_button("Chiudi", "accent")
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)
        self.load_history()


    def load_history(self):
        self.history_list.clear()
        cursor.execute("""
            SELECT id, session_date, correct_time, incorrect_time 
            FROM results 
            WHERE user_id = ? 
            ORDER BY id DESC;
        """, (self.user_id,))
        results = cursor.fetchall()

        if not results:
            self.history_list.addItem("Nessun monitoraggio registrato.")
            return

        for row in results:
            session_id, date, correct, incorrect = row
            item_text = f"{date} | Corretto: {correct:.2f}s | Scorretto: {incorrect:.2f}s"
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.ItemDataRole.UserRole, (session_id, correct, incorrect))
            self.history_list.addItem(list_item)

    def view_selected(self):
        selected_item = self.history_list.currentItem()
        if selected_item:
            session_data = selected_item.data(Qt.ItemDataRole.UserRole)
            if session_data:
                _, correct_time, incorrect_time = session_data
                self.show_chart(correct_time, incorrect_time)

    def delete_selected(self):
        selected_item = self.history_list.currentItem()
        if selected_item:
            session_data = selected_item.data(Qt.ItemDataRole.UserRole)
            if session_data:
                session_id, _, _ = session_data
                self.delete_entry(session_id, selected_item)

    def show_chart(self, correct_time, incorrect_time):
        self.chart_window = PostureChart(correct_time, incorrect_time)
        self.chart_window.exec()

    def delete_entry(self, session_id, list_item):
        # Crea un QMessageBox personalizzato con lo stile della palette
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Conferma Eliminazione")
        msg_box.setText("Sei sicuro di voler eliminare questa voce?")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Applica lo stile dalla palette
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #16213E;
                color: #E2E2E2;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0F3460;
                color: #FFFFFF;
                border: 1px solid #1A1A2E;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1A1A2E;
            }
            QPushButton:pressed {
                background-color: #E94560;
                color: #FFFFFF;
            }
        """)

        reply = msg_box.exec()

        if reply == QMessageBox.Yes:
            try:
                cursor.execute("DELETE FROM results WHERE id = ?", (session_id,))
                conn.commit()
                self.history_list.takeItem(self.history_list.row(list_item))

                if self.history_list.count() == 0:
                    self.history_list.addItem("Nessun monitoraggio registrato.")
            except sqlite3.Error as e:
                # Errore con stile
                error_box = QMessageBox(self)
                error_box.setWindowTitle("Errore")
                error_box.setText(f"Impossibile eliminare la voce: {str(e)}")
                error_box.setIcon(QMessageBox.Critical)
                error_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #16213E;
                        color: #E2E2E2;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #0F3460;
                        color: #FFFFFF;
                        border: 1px solid #1A1A2E;
                        padding: 6px 12px;
                        border-radius: 6px;
                    }
                    QPushButton:hover {
                        background-color: #1A1A2E;
                    }
                    QPushButton:pressed {
                        background-color: #E94560;
                        color: #FFFFFF;
                    }
                """)
                error_box.exec()

    def export_to_pdf(self):
            """Esporta i dati della cronologia in un PDF ben formattato"""
            try:
                # Ottieni i dati dell'utente
                cursor.execute("SELECT username FROM users WHERE id = ?", (self.user_id,))
                user_data = cursor.fetchone()
                if not user_data:
                    raise ValueError("Utente non trovato")
                username = user_data[0]

                # Ottieni tutti i risultati ordinati per data
                cursor.execute("""
                    SELECT session_date, correct_time, incorrect_time 
                    FROM results 
                    WHERE user_id = ?
                    ORDER BY session_date DESC
                """, (self.user_id,))
                results = cursor.fetchall()
                
                if not results:
                    show_custom_message("Nessun dato", f"Non ci sono dati da esportare", 'warning')
                    return

                # Calcola statistiche
                stats = calculate_statistics(self,results)

                # Crea il documento HTML
                doc = QTextDocument()
                generate_pdf_content(self,doc, username, results, stats)

                # Mostra dialogo di salvataggio
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Salva Report PDF",
                    f"Posture_Report_{username}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    "PDF Files (*.pdf)"
                )

                if file_path:
                    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                    printer.setOutputFileName(file_path)
                    printer.setPageMargins(QMarginsF(15, 15, 15, 15))

                    doc.print_(printer)
                    show_custom_message("Successo", "PDF esportato con successo!", "information")

            except Exception as e:
                show_custom_message("Errore", f"Errore durante l'esportazione PDF:\n{str(e)}", 'critical')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    
    welcome_screen = WelcomeScreen()
    welcome_screen.show()
    sys.exit(app.exec())