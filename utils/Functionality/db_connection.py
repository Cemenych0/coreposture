import sqlite3
# Inserimento utenti di default se non esistono
import bcrypt

# Connessione al database SQLite
conn = sqlite3.connect("corePosture.db")
cursor = conn.cursor()

# Creazione della tabella utenti
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    supervisor_id INTEGER,
    full_name TEXT,
    email TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supervisor_id) REFERENCES users (id)
)
""")

# Creazione della tabella risultati
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    correct_time REAL NOT NULL,
    incorrect_time REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")



# Inserimento utenti di default se non esistono
cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
if cursor.fetchone()[0] == 0:
    hashed_pw = bcrypt.hashpw("admin".encode("utf-8"), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", hashed_pw, "supervisor"))

cursor.execute("SELECT COUNT(*) FROM users WHERE username='test'")
if cursor.fetchone()[0] == 0:
    hashed_pw = bcrypt.hashpw("test".encode("utf-8"), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("test", hashed_pw, "user"))

# Salvataggio e chiusura
conn.commit()
