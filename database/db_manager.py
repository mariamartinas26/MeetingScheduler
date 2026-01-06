import os
import uuid
from datetime import datetime

import psycopg2
from icalendar import Calendar, Event
from psycopg2 import Error, OperationalError


class DatabaseManager:
    """
    Manages database connection and schema setup
    Handles import/export of meetings
    """

    def __init__(self):
        """
        Initialize database manager

        Returns:
            None
        """
        self.connection = None
        self.cursor = None
        self.is_connected = False

    def connect(self, host, database, user, password, port="5432"):
        """
        Connect to database

        Returns:
            (bool, str): success flag and message
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

        Return: tuple (bool, str):
            - True and success message if tables created
            - False and error message on failure
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
            - True and dict {"persons": True, ...}
            - False and error message on failure
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
        Returns:
            dict
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
        Returns:
            (bool, str):
                - True and message if closed successfully
                - False and error message on failure
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
        Adds a new person to the database with input validation
        and duplicate email prevention

        Returns:
            (bool, str):
                - True and message if added successfully
                - False and error message on failure
        """

        if not self.is_connected:
            return False, "No database connection"

        ok,response=self.validate_name(name)
        if not ok:
            return False, response
        name=response

        ok, response = self.validate_email(email)
        if not ok:
            return False, response
        email=response

        ok, response = self.validate_phone(phone)
        if not ok:
            return False, response
        phone=response

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
        Fetch all persons from GUI selection (person_id, name)
        Returns:
            list[(int,str)]
        """
        if not self.is_connected:
            return False, "No database connection"
        self.cursor.execute(
                "SELECT person_id,name FROM persons ORDER BY name;"
        )
        return self.cursor.fetchall()

    def check_conflicts(self,participant_ids,start_time,end_time):
        """
        Checks for overlapping meetings for a list of participants

        Returns:
            (bool,list,str):
                -(True,conflicts,"") on success
                conflicts - list of tuples [(person_id, name),...]
                -(False,[],error_msg) on failure
        """
        if not self.is_connected:
            return False,[], "No database connection"

        if end_time<=start_time:
            return False,[],"End time must be after start time"

        if not participant_ids:
            return True,[],""

        try:
            query="""
                SELECT DISTINCT p.person_id,
                                p.name FROM meetings m 
                JOIN meeting_participants mp ON m.meeting_id = mp.meeting_id
                JOIN persons p ON mp.person_id = p.person_id
                WHERE mp.person_id=ANY(%s::int[])
                AND (%s<m.end_time AND %s>m.start_time);
            """

            self.cursor.execute(query,(participant_ids,start_time,end_time))
            conflicts= self.cursor.fetchall()
            return True, conflicts, ""
        except Error as e:
            return False,[],f"Database error: {e}"
        except Exception as e:
            return False,[],f"Unexpected error: {e}"


    def add_meeting(self,title,description, start_time,end_time,location,participant_ids):
        """
        Creates new meeting, validate input, check conflicts, and store participants

        Returns:
            (bool, str):
                - True and success msg if meeting created
                - False and error message on failure
        """
        if not self.is_connected:
            return False, "No database connection"

        ok,title,msg=self.clean_str(title,"Title",allow_empty=False,max_len=100)
        if not ok:
            return False, msg

        ok,description,msg=self.clean_str(description,"Description",allow_empty=True,max_len=1000)
        if not ok:
            return False, msg

        ok,location,msg=self.clean_str(location,"Location",allow_empty=True,max_len=100)
        if not ok:
            return False, msg

        if end_time<=start_time:
            return False,"End time must be after start time"

        if start_time< datetime.now():
            return False, "Meeting cannot be scheduled in the past"

        try:
            #check conflicts
            ok,conflicts,msg=self.check_conflicts(participant_ids,start_time,end_time)
            if not ok:
                return False, msg

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

        except Error as e:
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            self.connection.rollback()
            return False, f"Unexpected error: {e}"


    def get_meetings_in_interval(self, start_time, end_time):
        """
        Return all meetings in the interval

        Returns:
            (bool,list|str):
                - True and a list of meetings:
                    [
                        (title,description,start_time,end_time,location,participants),
                        ...
                    ]
                - False and error msg on failure
        """

        if not self.is_connected:
            return False, "No database connection"

        if end_time<=start_time:
            return False, "End time must be after start time"

        try:
            query="""
                SELECT
                    m.title,
                    m.description,
                    m.start_time,
                    m.end_time,
                    m.location, 
                    STRING_AGG(p.name,', ') AS participants
                FROM meetings m JOIN meeting_participants mp ON m.meeting_id = mp.meeting_id
                    JOIN persons p ON mp.person_id = p.person_id
                WHERE start_time >= %s AND end_time <= %s GROUP BY m.meeting_id ORDER BY start_time;
            """

            self.cursor.execute(query,(start_time,end_time))
            results= self.cursor.fetchall()
            return True, results
        except Error as e:
            return False,  f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"


    #EXPORT MEETINGS PART
    def export_meetings_to_file(self,meetings,file_path):
        """
        Export meetings to ics file

        Returns:
            (bool,str):
                - True and success msg on success
                - False and error message on failure
        """

        if not meetings:
            return False, "No meetings"

        try:
            #create calendar
            cal=Calendar()
            cal.add("prodid", "-//Meeting Scheduler//EN")
            cal.add("version", "2.0")

            for title,description,start_time,end_time,location,participants in meetings:
                event = Event()
                event.add("uid", f"{uuid.uuid4()}@meeting-scheduler")
                event.add("summary", title)
                event.add("description", f"{description}\nParticipants: {participants}")
                event.add("location", location)
                event.add("dtstart", start_time)
                event.add("dtend", end_time)
                event.add("dtstamp", datetime.utcnow())

                cal.add_component(event)

            #write calendar to file
            with open(file_path, "wb") as f:
                f.write(cal.to_ical())

            return True, "Exported meetings successfully"

        except Exception as e:
            return False, f"Export failed: {str(e)}"


    #IMPORT MEETINGS PART
    def get_person_id_by_name(self,names):
        """
        Map a list of participant names to person_ids from the db

        Returns:
            dict:
                A dict mapping lowercase_name -> person_id
                Returns {} if not connected or names list is empty
        """

        if not self.is_connected:
            return {}

        new_names=[]
        for name in names:
            stripped=name.strip()
            if stripped:
                new_names.append(stripped)

        if not new_names:
            return {}

        #convert names to lowercase
        lower_names=[]
        for name in new_names:
            lower_names.append(name.lower())

        #query
        self.cursor.execute(
            """
            SELECT person_id,name FROM persons WHERE LOWER(name)=ANY(%s)
            """, (lower_names,)
        )

        rows=self.cursor.fetchall()

        result={}
        for person_id,name in rows:
            result[name.lower()]=person_id

        return result

    def extract_participants(self, description):
        """
        Extract participants from meeting description

        Returns:
            list[str]:
                - List of participants names found after "Participants:"
                - [] if none found
        """
        if not description:
            return []

        text = str(description)

        lines = text.splitlines()

        for line in lines:
            line_stripped = line.strip()
            if line_stripped.lower().startswith("participants:"):
                parts = line_stripped.split(":", 1)
                if len(parts) < 2:
                    return []

                names_part = parts[1]

                participants = []
                for name in names_part.split(","):
                    name = name.strip()
                    if name:
                        participants.append(name)

                return participants

        return []

    def remove_participants_description(self,description):
        """
        Remove "Participants:" line from description when importing

        Returns:
            str:
                Description without "Participants: line
                "" if description is empty
        """
        if not description:
            return ""

        lines=str(description).splitlines()
        kept=[]

        for line in lines:
            stripped=line.strip()
            if stripped.lower().startswith("participants:"):
                continue #skip line
            kept.append(stripped)

        return "\n".join(kept).strip()

    def import_meetings_from_file(self,file_path):
        """
        Import meetings from ics file and insert in db

        Returns:
            (bool,str):
                - True and success msg with imported count
                - False and error msg on failure
        """

        if not self.is_connected:
            return False, "No database connection"


        try:
            with open(file_path, "rb") as f:
                cal = Calendar.from_ical(f.read())

            imported = 0
            for component in cal.walk():
                if component.name != "VEVENT":
                    continue

                title =str(component.get("summary", "")).strip()
                description =str(component.get("description", "")).strip()
                location =str(component.get("location", "")).strip()

                dtstart_obj=component.get("dtstart")
                dtend_obj=component.get("dtend")
                if not dtstart_obj or not dtend_obj:
                    continue

                start_dt=dtstart_obj.dt
                end_dt=dtend_obj.dt

                if start_dt.tzinfo is not None:
                    start_dt=start_dt.replace(tzinfo=None)
                if end_dt.tzinfo is not None:
                    end_dt=end_dt.replace(tzinfo=None)

                if end_dt <= start_dt:
                    return False, f"Invalid time interval for {title}"


                participant_names=self.extract_participants(description)
                #added validation
                if not participant_names:
                    return False,f"Event {title} has not participants. Add participants"

                new_description=self.remove_participants_description(description)
                name_to_id =self.get_person_id_by_name(participant_names)
                participant_ids=[]

                for name in participant_names:
                    person_id=name_to_id.get(name.lower())
                    if person_id:
                        participant_ids.append(person_id)

                #added validation
                if not participant_ids:
                    return False,f"Participants for {title} do not exist in database"


                success, message = self.add_meeting(
                    title=title,
                    description=new_description,
                    start_time=start_dt,
                    end_time=end_dt,
                    location=location,
                    participant_ids=participant_ids
                )

                if not success:
                    return False, f"Import stopped at {title}: {message}"

                imported+= 1

            return True, f"Imported {imported} meetings successfully"

        except Exception as e:
            self.connection.rollback()
            return False, f"Import failed: {str(e)}"


    def clean_str(self,s,field,allow_empty=False,max_len=None):
        """
        String cleaning function and validator:
            - converts None -> ""
            -strips whitespace
            -check empty constraint
            - check max length constraint

        Returns:
            (bool,str,str):
                - success flag
                - cleaned string
                - error msg ("" if success)
        """
        s="" if s is None else str(s).strip()

        if not allow_empty and s=="":
            return False,"",f"{field} is required"

        if max_len is not None and len(s)>max_len:
            return False,"",f"{field} must be less than {max_len} characters long"

        return True,s,""

    def validate_name(self,name):
        """
        Validate a person name

        Returns:
            (bool,str):
                - True and cleand name if valid
                - False and error msg if invalid
        """
        ok,name,msg=self.clean_str(name,"Name",allow_empty=False,max_len=100)
        if not ok:
            return False,msg

        if len(name)<2:
            return False,"Name must be at least 2 characters"

        return True,name

    def validate_email(self,email):
        """
        Validate email address

        Returns:
            (bool,str):
                - True and lowercase email if valid
                - False and error msg if invalid
        """
        ok,email,msg=self.clean_str(email,"Email",allow_empty=False,max_len=100)
        if not ok:
            return False,msg

        email=email.lower()
        if email.count("@")!=1:
            return False,"Invalid email address"

        part1,part2=email.split("@")
        if part1=="" or part2=="":
            return False,"Invalid email address"

        if "." not in part2 or part2.startswith(".") or part2.endswith("."):
            return False,"Invalid email address"

        return True,email


    def validate_phone(self,phone):
        """
        Validate phone number

        Returns:
            (bool,str):
                - True and clean phone (or None) if valid
                - False and error msg if invalid
        """
        if phone is None or str(phone).strip()=="":
            return True, None

        phone=str(phone).strip()

        if len(phone)>10:
            return False,"Phone must be at least 10 characters"

        return True,phone

