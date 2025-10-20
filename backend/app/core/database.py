"""
Database connection and session management
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator
from app.core.config import settings


class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.connection_string = settings.DATABASE_URL
    
    @contextmanager
    def get_connection(self) -> Generator:
        """Get a database connection with automatic cleanup"""
        conn = None
        try:
            conn = psycopg2.connect(
                self.connection_string,
                cursor_factory=RealDictCursor
            )
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self) -> Generator:
        """Get a database cursor with automatic cleanup"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()


# Global database instance
db = Database()


def get_db():
    """Dependency for FastAPI route handlers"""
    with db.get_cursor() as cursor:
        yield cursor

