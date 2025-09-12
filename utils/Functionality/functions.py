from datetime import datetime
import sys
import os
from PySide6.QtGui import (QColor)


from utils.Functionality.db_connection import *
PURPLE_PALETTE = {
    'dark': '#111530',
    'medium': '#16213E',
    'light': '#0F3460',
    'accent': '#E94560',
    'text': '#FFFFFF',
    'secondary_text': '#E2E2E2'
}

def darken_color(color, factor=0.8):
        c = QColor(color)
        return QColor(int(c.red() * factor), int(c.green() * factor), int(c.blue() * factor)).name()


def center_window_top(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        # Sposta la finestra verso l'alto e poi aggiungi 30 pixel
        qr.moveTop(qr.top() - qr.height() // 4 + 120)
        self.move(qr.topLeft())

def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)


def calculate_statistics(self, results):
        """Calcola le statistiche dai risultati"""
        total_sessions = len(results)
        total_correct = sum(r[1] for r in results)
        total_incorrect = sum(r[2] for r in results)
        avg_correct = total_correct / total_sessions if total_sessions > 0 else 0
        avg_incorrect = total_incorrect / total_sessions if total_sessions > 0 else 0

        return {
                'total_sessions': total_sessions,
                'total_correct': total_correct,
                'total_incorrect': total_incorrect,
                'avg_correct': avg_correct,
                'avg_incorrect': avg_incorrect
        }

def generate_pdf_content(self, doc, username, results, stats):
        """Genera il contenuto HTML per il PDF"""
        css = f"""
        <style>
                body {{ font-family: 'Arial'; margin: 0; padding: 0; color: #333; }}
                .header {{ 
                background-color: {PURPLE_PALETTE['dark']}; 
                color: white; 
                padding: 20px; 
                text-align: center;
                margin-bottom: 20px;
                }}
                h1 {{ color: {PURPLE_PALETTE['accent']}; margin: 0; }}
                h2 {{ color: {PURPLE_PALETTE['medium']}; border-bottom: 2px solid {PURPLE_PALETTE['light']}; 
                padding-bottom: 5px; }}
                .stats-container {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
                }}
                .stat-box {{
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                width: 48%;
                }}
                .stat-row {{
                display: flex;
                justify-content: space-between;
                margin: 8px 0;
                }}
                .stat-label {{ font-weight: bold; color: {PURPLE_PALETTE['medium']}; }}
                table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                }}
                th {{
                background-color: {PURPLE_PALETTE['medium']};
                color: white;
                padding: 10px;
                text-align: left;
                }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 0.8em;
                color: #777;
                }}
        </style>
        """

        # Genera le righe della tabella
        table_rows = ""
        for session in results:
                date, correct, incorrect = session
                total = correct + incorrect
                percentage = (correct / total) * 100 if total > 0 else 0
                
                table_rows += f"""
                <tr>
                <td>{date}</td>
                <td style="text-align: right;">{correct:.2f}</td>
                <td style="text-align: right;">{incorrect:.2f}</td>
                <td style="text-align: right;">{percentage:.1f}%</td>
                </tr>
                """

        html = f"""
        <html>
        <head>{css}</head>
        <body>
                <div class="header">
                <h1>Report Monitoraggio Postura</h1>
                <p>Utente: {username} | Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>
                
                <div class="stats-container">
                <div class="stat-box">
                        <h3>Statistiche Generali</h3>
                        <div class="stat-row">
                        <span class="stat-label">Sessioni totali:</span>
                        <span>{stats['total_sessions']}</span>
                        </div>
                        <div class="stat-row">
                        <span class="stat-label">Tempo totale corretto:</span>
                        <span>{stats['total_correct']:.2f} secondi</span>
                        </div>
                        <div class="stat-row">
                        <span class="stat-label">Tempo totale scorretto:</span>
                        <span>{stats['total_incorrect']:.2f} secondi</span>
                        </div>
                </div>
                
                <div class="stat-box">
                        <h3>Medie per Sessione</h3>
                        <div class="stat-row">
                        <span class="stat-label">Tempo corretto medio:</span>
                        <span>{stats['avg_correct']:.2f} secondi</span>
                        </div>
                        <div class="stat-row">
                        <span class="stat-label">Tempo scorretto medio:</span>
                        <span>{stats['avg_incorrect']:.2f} secondi</span>
                        </div>
                        <div class="stat-row">
                        <span class="stat-label">Percentuale media corretta:</span>
                        <span>{(stats['avg_correct']/(stats['avg_correct']+stats['avg_incorrect'])*100 if (stats['avg_correct']+stats['avg_incorrect']) > 0 else 0):.1f}%</span>
                        </div>
                </div>
                </div>
                
                <h2>Dettaglio Sessioni</h2>
                <table>
                <thead>
                        <tr>
                        <th>Data</th>
                        <th>Tempo Corretto (s)</th>
                        <th>Tempo Scorretto (s)</th>
                        <th>% Corretta</th>
                        </tr>
                </thead>
                <tbody>
                        {table_rows}
                </tbody>
                </table>
                
                <div class="footer">
                <p>Generato automaticamente da Posture Monitor App</p>
                </div>
        </body>
        </html>
        """

        doc.setHtml(html)


def resource_path(relative_path):
    """Restituisce il percorso assoluto, compatibile con PyInstaller"""
    try:
        base_path = sys._MEIPASS  # dove PyInstaller estrae i file
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)