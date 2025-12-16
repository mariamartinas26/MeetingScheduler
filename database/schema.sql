--People table
CREATE TABLE IF NOT EXISTS persons (
    person_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL ,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--Meetings table
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

--Many to many relationship between Meetings and People
CREATE TABLE IF NOT EXISTS meeting_participants (
    meeting_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    PRIMARY KEY (meeting_id, person_id),
    FOREIGN KEY (meeting_id) REFERENCES Meetings(meeting_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES Persons(person_id) ON DELETE CASCADE
);