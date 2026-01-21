from database import get_db
import hashlib

db = get_db()
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    enrollment_id TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS face_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    embedding BLOB,
    image_path TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    time TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# default admin
password = hashlib.sha256("admin123".encode()).hexdigest()
cur.execute("INSERT OR IGNORE INTO admin VALUES (1,'admin',?)", (password,))

db.commit()
print("✅ Database initialized")
