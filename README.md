# 📅 Meeting Scheduler Application

📌 Overview

Meeting Scheduler is a graphical desktop application developed in Python, using Tkinter for the user interface and PostgreSQL as the database system.
The application allows users to manage persons, schedule meetings with multiple participants, display meetings within a selected time interval, and import/export meetings using the standard iCalendar (ICS) format.

The project emphasizes:

complete input validation,

robust error handling,

reliable database interaction,

a responsive and user-friendly GUI.

🛠️ Technologies Used

Python 

Tkinter – graphical user interface

PostgreSQL – relational database

psycopg2 – PostgreSQL database adapter for Python

iCalendar (ICS) format for calendar import/export

🚀 Application Features
🔹 Phase 1 – Database Setup and Connection

Create PostgreSQL tables

Establish a secure database connection using psycopg2

Handle connection and query errors

✅ Functional Output:
The application connects successfully to the PostgreSQL database.

🔹 Phase 2 – Adding Persons

Add new persons through the Tkinter GUI

Validate name and email input

Prevent duplicate entries

Display success and error messages

✅ Functional Output:
New persons are stored in the database and confirmed in the GUI.

🔹 Phase 3 – Scheduling Meetings

Schedule meetings with start and end times

Select multiple participants

Validate time intervals (start_time < end_time)

Detect scheduling conflicts

Handle database insertion errors

✅ Functional Output:
Meetings are correctly stored with all assigned participants.

🔹 Phase 4 – Displaying Meetings

Select a time interval

Query meetings from the database

Display results in a readable GUI format

Handle empty result sets gracefully

✅ Functional Output:
Meetings for the selected interval are displayed accurately.

🔹 Phase 5 – Calendar Import / Export

Export meetings to ICS calendar files

Import meetings from ICS files

Validate imported meeting data

Display success or error feedback

✅ Functional Output:
Meetings can be exported and imported correctly using calendar files.

🔹 Phase 6 – Input Validation and Error Handling

Validate names, dates, and participant lists

Catch and handle runtime exceptions

Display clear, user-friendly error messages

Keep the application running in case of errors

✅ Functional Output:
Invalid inputs and exceptions are handled gracefully.

▶️ How to Run the Application
1️⃣ Install dependencies
pip install psycopg2

2️⃣ Configure the database

Create a PostgreSQL database

Update database credentials in the Python configuration file

3️⃣ Run the application
python main.py
