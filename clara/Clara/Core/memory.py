import sqlite3
import os

def get_db_path():
    """Constructs the absolute path to the database file."""
    # Assumes this script is in Core/, and Memory/ is a sibling directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    memory_dir = os.path.join(base_dir, 'Memory')
    os.makedirs(memory_dir, exist_ok=True)
    return os.path.join(memory_dir, 'clara.db')

def get_connection():
    """Creates and returns a database connection."""
    return sqlite3.connect(get_db_path())

def create_tables(conn):
    """Creates the necessary database tables if they don't exist."""
    cursor = conn.cursor()
    
    # Table for study materials
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL UNIQUE,
        title TEXT,
        subject TEXT,
        tags TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Table for study sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        topic TEXT NOT NULL,
        duration_min INTEGER,
        notes TEXT
    );
    """)

    # Table for performance tracking (e.g., mock exam scores)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        subject TEXT NOT NULL,
        score REAL,
        notes TEXT
    );
    """)
    
    conn.commit()
    print("Database tables created or verified successfully.")

def main():
    """Main function for direct CLI execution."""
    print("Running database setup...")
    try:
        conn = get_connection()
        create_tables(conn)
        conn.close()
        print(f"Database is ready at: {get_db_path()}")
    except sqlite3.Error as e:
        print(f"An error occurred with the database: {e}")

if __name__ == "__main__":
    # This allows running `python Core/memory.py` to set up the DB
    main()
