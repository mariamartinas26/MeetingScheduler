import psycopg2
from psycopg2 import Error, OperationalError
import os


class DatabaseManager:
    """
    Manages database connection and schema setup
    """

    def __init__(self):
        """
        Initialize database manager
        """
        self.connection = None
        self.cursor = None
        self.is_connected = False

    def connect(self, host, database, user, password, port="5432"):
        """
        Connect to database

        Returns:
            tuple (bool, str): success flag and message
        """
        try:
            if self.connection:
                self.close()

            self.connection = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port,
                connect_timeout=10
            )

            self.connection.autocommit = False
            self.cursor = self.connection.cursor()
            self.is_connected = True

            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()[0]

            return True, f"Connection established with {version}"

        except (OperationalError, Error) as e:
            self.is_connected = False
            return False, f"Connection failed: {e}"

        except Exception as e:
            self.is_connected = False
            return False, f"Unexpected error: {e}"

    def create_tables(self):
        """
        Create database tables using schema.sql or fallback SQL

        Returns:
            tuple (bool, str)
        """
        if not self.is_connected:
            return False, "No active database connection"

        try:
            schema_path = os.path.join(
                os.path.dirname(__file__),
                "schema.sql"
            )

            if os.path.exists(schema_path):
                with open(schema_path, "r") as f:
                    self.cursor.execute(f.read())
            else:
                self._create_tables_manual()

            self.connection.commit()
            return True, "Tables created successfully"

        except Error as e:
            self.connection.rollback()
            return False, f"Error creating tables: {e}"

        except Exception as e:
            self.connection.rollback()
            return False, f"Unexpected error: {e}"

    def _create_tables_manual(self):
        """
        Fallback table creation (used if schema.sql is missing)
        """

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS persons (
                person_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(100),
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                meeting_id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                location VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT check_times CHECK (end_time > start_time)
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS meeting_participants (
                meeting_id INTEGER REFERENCES meetings(meeting_id) ON DELETE CASCADE,
                person_id INTEGER REFERENCES persons(person_id) ON DELETE CASCADE,
                PRIMARY KEY (meeting_id, person_id)
            );
        """)

    def test_tables(self):
        """
        Verify existence of required tables

        Returns:
            tuple (bool, dict | str)
        """
        if not self.is_connected:
            return False, "No database connection"

        try:
            tables = ["persons", "meetings", "meeting_participants"]
            result = {}

            for table in tables:
                self.cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name = %s
                    );
                """, (table,))

                exists = self.cursor.fetchone()[0]
                result[table] = exists

            return True, result

        except Error as e:
            return False, f"Error testing tables: {e}"

        except Exception as e:
            return False, f"Unexpected error: {e}"

    def get_connection_status(self):
        """
        Return connection status information
        """
        if not self.connection:
            return {"connected": False, "status": "No connection"}

        try:
            self.cursor.execute("SELECT 1;")
            return {
                "connected": True,
                "status": "Active",
                "database": self.connection.info.dbname,
                "user": self.connection.info.user,
                "host": self.connection.info.host,
                "port": self.connection.info.port
            }
        except Exception:
            return {"connected": False, "status": "Connection lost"}

    def close(self):
        """
        Close database connection
        """
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None

            if self.connection:
                self.connection.close()
                self.connection = None

            self.is_connected = False
            return True, "Connection closed"

        except Error as e:
            return False, f"Error closing connection: {e}"

    def __del__(self):
        """
        Destructor – ensures connection is closed
        """
        try:
            self.close()
        except Exception:
            pass
