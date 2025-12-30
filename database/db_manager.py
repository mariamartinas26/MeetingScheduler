import psycopg2
from psycopg2 import Error, OperationalError
import os
from datetime import datetime


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
            #if connection already exists
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

        Return: tuple (bool, str)
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
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
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

        Returns: tuple (bool, dict | str)
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
        Destructor
        """
        try:
            self.close()
        except Exception:
            pass

    def add_person(self, name, email, phone=None):
        """
        Adds a new person to the database
        return: tuple: (success: bool, message: str)
        """

        if not self.is_connected:
            return False, "No database connection"

        name = name.strip()
        email = email.strip().lower()
        phone = phone.strip() if phone else None

        #Input validation
        if len(name) < 2:
            return False, "Name must be at least 2 characters"

        if "@" not in email or "." not in email:
            return False, "Invalid email address"

        if len(phone) > 10:
            return False, "Invalid phone number"

        try:
            #duplicate emails
            self.cursor.execute(
                "SELECT 1 FROM persons WHERE email = %s;",
                (email,)
            )
            if self.cursor.fetchone():
                return False, "Email already registered"

            # Insert person
            self.cursor.execute(
                """
                INSERT INTO persons (name, email, phone)
                VALUES (%s, %s, %s);
                """,
                (name, email, phone)
            )

            self.connection.commit()
            return True, "Person added successfully"

        except Exception as e:
            self.connection.rollback()
            return False, f"Database error: {str(e)}"

    def get_all_persons(self):
        """
        Return all persons in the database (for selecting them)
        """
        if not self.is_connected:
            return False, "No database connection"

        self.cursor.execute(
            "SELECT person_id,name FROM persons ORDER BY name;"
        )

        return self.cursor.fetchall()

    def check_conflicts(self,participant_ids,start_time,end_time):
        """
        Checks for overlapping meetings between participants
        """
        if not self.is_connected:
            return False, "No database connection"

        if not participant_ids:
            return True,[]

        query="""
            SELECT DISTINCT p.person_id,p.name FROM meetings m 
            JOIN meeting_participants mp ON m.meeting_id = mp.meeting_id
            JOIN persons p ON mp.person_id = p.person_id
            WHERE mp.person_id=ANY(%s::int[])
            AND (%s<m.end_time AND %s>m.start_time);
        """

        self.cursor.execute(query,(participant_ids,start_time,end_time))
        return self.cursor.fetchall()


    def add_meeting(self,title,description, start_time,end_time,location,participant_ids):
        """
        Creates new meeting
        """
        if not self.is_connected:
            return False, "No database connection"

        title = title.strip()
        description = description.strip()
        location = location.strip()

        if not title:
            return False, "Title is required"

        if not participant_ids:
            return False, "At least one participant is required"

        if start_time < datetime.now():
            return False, "Meeting cannot be scheduled in the past"

        if end_time<=start_time:
            return False,"End time must be after start time"

        try:
            #check conflicts
            conflicts=self.check_conflicts(
                participant_ids,
                start_time,
                end_time
            )

            if conflicts:
               unique_names={person_name for person_id,person_name in conflicts}
               names=", ".join(sorted(unique_names))
               return False, f"Schedule conflict for: {names}"

            #Insert meeting
            self.cursor.execute(
                """
                INSERT INTO meetings (title, description, start_time, end_time, location)
                    VALUES (%s,%s,%s,%s,%s) RETURNING meeting_id;
                """, (title, description, start_time, end_time, location)
            )

            meeting_id=self.cursor.fetchone()[0]

            #insert participants
            for person_id in participant_ids:
                self.cursor.execute(
                    """
                    INSERT INTO meeting_participants (meeting_id, person_id)
                        VALUES (%s, %s);
                    """, (meeting_id, person_id)
                )

            self.connection.commit()
            return True, "Meeting scheduled successfully"

        except Exception as e:
            self.connection.rollback()
            return False, f"Database error: {str(e)}"


    def get_meetings_in_interval(self, start_time, end_time):
        """
        Return all meetings in the interval
        """

        if not self.is_connected:
            return False, "No database connection"

        query="""
            SELECT
                m.title,m.description,m.start_time,m.end_time,m.location, STRING_AGG(p.name,', ') AS participants
            FROM meetings m JOIN meeting_participants mp ON m.meeting_id = mp.meeting_id
                JOIN persons p ON mp.person_id = p.person_id
            WHERE start_time >= %s AND end_time <= %s GROUP BY m.meeting_id ORDER BY start_time;
        """

        self.cursor.execute(query,(start_time,end_time))
        results= self.cursor.fetchall()
        return results
