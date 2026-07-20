import sqlite3
import hashlib

class DatabaseSetup:
    def __init__(self,db_path="study_app.db"):
        """Creates the database connection and sets up the database file."""
        self.db_path = db_path
        self.settings_win = None # Checks if the settings window is open
        self.connection = sqlite3.connect(db_path)#Connect to the database file (creates it if it doesn't exist)
                
    def create_tables(self): 
        """Creates the tables in the database if they don't already exist."""
        cursor = self.connection.cursor() #cursor object to execute SQL commands

        #Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL UNIQUE,
                password    TEXT    NOT NULL
            )
        """)

        #Notes table

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                title      TEXT    NOT NULL,
                body       TEXT    NOT NULL DEFAULT '',
                summary    TEXT    DEFAULT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, title)
            )
        """)

        #Deck table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                name       TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, name)
            )
        """)
        
        #Flashcards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id       INTEGER NOT NULL,
                user_id       INTEGER NOT NULL,
                front         TEXT    NOT NULL,
                back          TEXT    NOT NULL,
                FOREIGN KEY (deck_id)  REFERENCES decks(id)  ON DELETE CASCADE,
                FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE
                
            )
        """)
        
        #Quiz + questions tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                title      TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        self.connection.commit()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct TEXT NOT NULL,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE)
                """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id    INTEGER NOT NULL,
                user_id    INTEGER NOT NULL,
                score      INTEGER NOT NULL,
                total      INTEGER NOT NULL,
                taken_at   TEXT    NOT NULL,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT    NOT NULL,
            event_date  TEXT    NOT NULL,
            event_type  TEXT    NOT NULL DEFAULT 'other',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)
            """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                rem_title      TEXT    NOT NULL,
                remind_at  TEXT    NOT NULL,
                fired      INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

    def get_cursor(self):
        """Returns a cursor so other parts of the app can query the database"""
        return self.connection.cursor()
 
    def commit(self):
        """Saves any changes made to the database"""
        self.connection.commit()
        

def hash_password(password):
    """Hashes the password using SHA-256 and returns the hexadecimal digest."""
    return hashlib.sha256(password.encode()).hexdigest()
