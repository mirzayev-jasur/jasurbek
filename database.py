import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.cursor = self.conn.cursor()
            logging.info(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")

    def create_tables(self):
        try:
            # Users table
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS users
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY,
                                    telegram_id
                                    INTEGER
                                    UNIQUE,
                                    username
                                    TEXT,
                                    first_name
                                    TEXT,
                                    last_name
                                    TEXT,
                                    is_bot
                                    INTEGER,
                                    language_code
                                    TEXT,
                                    added_at
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP
                                )
                                """)

            # Messages table
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS messages
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    user_id
                                    INTEGER,
                                    message_text
                                    TEXT,
                                    message_type
                                    TEXT,
                                    file_id
                                    TEXT,
                                    timestamp
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP,
                                    FOREIGN
                                    KEY
                                (
                                    user_id
                                ) REFERENCES users
                                (
                                    telegram_id
                                )
                                    )
                                """)

            # Feedback table
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS feedback
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    user_id
                                    INTEGER,
                                    feedback_text
                                    TEXT,
                                    timestamp
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP,
                                    FOREIGN
                                    KEY
                                (
                                    user_id
                                ) REFERENCES users
                                (
                                    telegram_id
                                )
                                    )
                                """)

            # Suggestions table
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS suggestions
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    user_id
                                    INTEGER,
                                    suggestion_text
                                    TEXT,
                                    timestamp
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP,
                                    FOREIGN
                                    KEY
                                (
                                    user_id
                                ) REFERENCES users
                                (
                                    telegram_id
                                )
                                    )
                                """)

            # Complaints table
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS complaints
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    user_id
                                    INTEGER,
                                    complaint_text
                                    TEXT,
                                    timestamp
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP,
                                    FOREIGN
                                    KEY
                                (
                                    user_id
                                ) REFERENCES users
                                (
                                    telegram_id
                                )
                                    )
                                """)

            # Questions table
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS questions
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    user_id
                                    INTEGER,
                                    question_text
                                    TEXT,
                                    timestamp
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP,
                                    FOREIGN
                                    KEY
                                (
                                    user_id
                                ) REFERENCES users
                                (
                                    telegram_id
                                )
                                    )
                                """)

            # Promocodes table
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS promocodes
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    code
                                    TEXT
                                    UNIQUE,
                                    description
                                    TEXT,
                                    is_active
                                    INTEGER
                                    DEFAULT
                                    1,
                                    created_at
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP
                                )
                                """)

            # Admin sessions table
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS admin_sessions
                                (
                                    user_id
                                    INTEGER
                                    PRIMARY
                                    KEY,
                                    is_logged_in
                                    INTEGER
                                    DEFAULT
                                    0,
                                    login_time
                                    TIMESTAMP
                                )
                                """)

            self.conn.commit()
            logging.info("Tables created or already exist.")
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")

    def add_user(self, telegram_id, username, first_name, last_name, is_bot, language_code):
        try:
            self.cursor.execute("""
                                INSERT
                                OR IGNORE INTO users (telegram_id, username, first_name, last_name, is_bot, language_code)
                VALUES (?, ?, ?, ?, ?, ?)
                                """, (telegram_id, username, first_name, last_name, is_bot, language_code))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                logging.info(f"User {telegram_id} added to database.")
                return True
            else:
                logging.info(f"User {telegram_id} already exists.")
                return False
        except sqlite3.Error as e:
            logging.error(f"Error adding user {telegram_id}: {e}")
            return False

    def user_exists(self, telegram_id):
        self.cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
        return self.cursor.fetchone() is not None

    def get_user(self, telegram_id):
        self.cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return self.cursor.fetchone()

    def get_all_users(self):
        self.cursor.execute("SELECT telegram_id, username, first_name, last_name FROM users")
        return self.cursor.fetchall()

    def add_message(self, user_id, message_text, message_type, file_id=None):
        try:
            self.cursor.execute("""
                                INSERT INTO messages (user_id, message_text, message_type, file_id)
                                VALUES (?, ?, ?, ?)
                                """, (user_id, message_text, message_type, file_id))
            self.conn.commit()
            logging.info(f"Message from user {user_id} ({message_type}) logged.")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding message for user {user_id}: {e}")
            return False

    def get_user_message_count(self, user_id):
        self.cursor.execute("SELECT COUNT(*) FROM messages WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()[0]

    def add_feedback(self, user_id, feedback_text):
        try:
            self.cursor.execute("""
                                INSERT INTO feedback (user_id, feedback_text)
                                VALUES (?, ?)
                                """, (user_id, feedback_text))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding feedback: {e}")
            return False

    def add_suggestion(self, user_id, suggestion_text):
        try:
            self.cursor.execute("""
                                INSERT INTO suggestions (user_id, suggestion_text)
                                VALUES (?, ?)
                                """, (user_id, suggestion_text))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding suggestion: {e}")
            return False

    def add_complaint(self, user_id, complaint_text):
        try:
            self.cursor.execute("""
                                INSERT INTO complaints (user_id, complaint_text)
                                VALUES (?, ?)
                                """, (user_id, complaint_text))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding complaint: {e}")
            return False

    def add_question(self, user_id, question_text):
        try:
            self.cursor.execute("""
                                INSERT INTO questions (user_id, question_text)
                                VALUES (?, ?)
                                """, (user_id, question_text))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding question: {e}")
            return False

    def add_promocode(self, code, description):
        try:
            self.cursor.execute("""
                                INSERT INTO promocodes (code, description)
                                VALUES (?, ?)
                                """, (code, description))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding promocode: {e}")
            return False

    def check_promocode(self, code):
        self.cursor.execute("SELECT * FROM promocodes WHERE code = ? AND is_active = 1", (code,))
        return self.cursor.fetchone()

    def get_all_feedback(self):
        self.cursor.execute("""
                            SELECT f.feedback_text, u.first_name, u.username, f.timestamp
                            FROM feedback f
                                     JOIN users u ON f.user_id = u.telegram_id
                            ORDER BY f.timestamp DESC
                            """)
        return self.cursor.fetchall()

    def get_all_suggestions(self):
        self.cursor.execute("""
                            SELECT s.suggestion_text, u.first_name, u.username, s.timestamp
                            FROM suggestions s
                                     JOIN users u ON s.user_id = u.telegram_id
                            ORDER BY s.timestamp DESC
                            """)
        return self.cursor.fetchall()

    def get_all_complaints(self):
        self.cursor.execute("""
                            SELECT c.complaint_text, u.first_name, u.username, c.timestamp
                            FROM complaints c
                                     JOIN users u ON c.user_id = u.telegram_id
                            ORDER BY c.timestamp DESC
                            """)
        return self.cursor.fetchall()

    def get_all_questions(self):
        self.cursor.execute("""
                            SELECT q.question_text, u.first_name, u.username, q.timestamp
                            FROM questions q
                                     JOIN users u ON q.user_id = u.telegram_id
                            ORDER BY q.timestamp DESC
                            """)
        return self.cursor.fetchall()

    def set_admin_session(self, user_id, is_logged_in):
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO admin_sessions (user_id, is_logged_in, login_time)
                VALUES (?, ?, ?)
            """, (user_id, is_logged_in, datetime.now() if is_logged_in else None))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error setting admin session: {e}")
            return False

    def is_admin_logged_in(self, user_id):
        self.cursor.execute("SELECT is_logged_in FROM admin_sessions WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result and result[0] == 1

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")
