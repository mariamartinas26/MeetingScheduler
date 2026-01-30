# 📅 Meeting Scheduler Application

## 📌 Overview
**Meeting Scheduler** is a graphical desktop application developed in **Python**, using **Tkinter** for the user interface and **PostgreSQL** as the database system.

The application allows users to:
- manage persons,
- schedule meetings with multiple participants,
- display meetings within a selected time interval,
- import and export meetings using the standard **iCalendar (ICS)** format.

The project emphasizes:
- ✅ complete input validation  
- ✅ robust error handling  
- ✅ reliable database interaction  
- ✅ a responsive and user-friendly GUI  

---

## 🛠️ Technologies Used
- **Python**
- **Tkinter** – graphical user interface
- **PostgreSQL** – relational database
- **psycopg2** – PostgreSQL adapter for Python
- **iCalendar (ICS)** – calendar import/export format

## 🚀 Features

### 🔹 Phase 1 – Database Setup and Connection
- Create PostgreSQL tables
- Establish a secure database connection
- Handle connection errors

**Functional Output:**  
✔ The application connects successfully to the database

---

### 🔹 Phase 2 – Adding Persons
- Add new persons through the GUI
- Validate input data
- Prevent duplicate entries
- Display success and error messages

**Functional Output:**  
✔ New persons are added and confirmed in the GUI

---

### 🔹 Phase 3 – Scheduling Meetings
- Schedule meetings with start and end times
- Select multiple participants
- Validate time intervals
- Detect scheduling conflicts
- Handle database errors

**Functional Output:**  
✔ Meetings are stored with all assigned participants

---

### 🔹 Phase 4 – Displaying Meetings
- Select a time interval
- Query meetings from the database
- Display results in a readable format
- Handle empty results

**Functional Output:**  
✔ Meetings are displayed accurately

---

### 🔹 Phase 5 – Calendar Import / Export
- Export meetings to **ICS** files
- Import meetings from calendar files
- Validate imported data
- Provide success/error feedback

**Functional Output:**  
✔ Meetings can be imported and exported correctly

---

### 🔹 Phase 6 – Input Validation and Error Handling
- Validate names, dates, and participant lists
- Catch runtime exceptions
- Display clear error messages
- Keep the application running safely

**Functional Output:**  
✔ Invalid inputs and errors are handled gracefully

