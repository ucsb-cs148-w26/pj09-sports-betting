import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'sports_betting'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    """Creates database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_query(query, params=None, fetch_one=False):
    """
    select query
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch_one:
                return cur.fetchone()
            return cur.fetchall()


def execute_insert(query, params=None):
    """
    insert query and returns the inserted id.
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return result[list(result.keys())[0]] if result else None


def execute_update(query, params=None):
    """
    update or delete queries.
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount


def test_connection():
    """Test database connection"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print("Postgres database connection successful!")
                return True
    except Exception as e:
        print("Postgres database connection failed!")
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    test_connection()
