"""Azure SQL when SQL_CONNECTION_STRING is set; otherwise a local SQLite demo file."""
import os, sqlite3

CONN = os.environ.get("SQL_CONNECTION_STRING")

def get_conn():
    if CONN:
        import pyodbc
        return pyodbc.connect(CONN)
    return sqlite3.connect(os.environ.get("DEMO_DB", "demo.db"))

def query(sql, args=(), conn=None):
    c = conn or get_conn()
    cur = c.cursor()
    cur.execute(sql, args)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    if not conn:
        c.close()
    return rows

def init_demo():
    """Create and seed the SQLite demo DB (never runs against Azure SQL)."""
    if CONN or os.path.exists(os.environ.get("DEMO_DB", "demo.db")):
        return
    c = get_conn()
    c.executescript("""
    CREATE TABLE Managers (ManagerId INTEGER PRIMARY KEY, Name TEXT, Email TEXT UNIQUE);
    CREATE TABLE Interns (InternId INTEGER PRIMARY KEY, Name TEXT, Email TEXT, ManagerId INT, Programme TEXT);
    CREATE TABLE AttendanceWeek (WeekId INTEGER PRIMARY KEY, InternId INT, WeekStart TEXT,
        Status TEXT DEFAULT 'Draft', Comment TEXT, SubmittedBy TEXT, SubmittedAt TEXT,
        UNIQUE (InternId, WeekStart));
    CREATE TABLE AttendanceDay (WeekId INT, Day TEXT, StatusCode TEXT, PRIMARY KEY (WeekId, Day));
    INSERT INTO Managers VALUES (1,'Demo Manager','manager1@example.org');
    INSERT INTO Interns (Name,Email,ManagerId,Programme) VALUES
      ('Thandi Mokoena','thandi@example.org',1,'GIS & Remote Sensing'),
      ('Sipho Dlamini','sipho@example.org',1,'Data Analytics'),
      ('Lerato Nkosi','lerato@example.org',1,'Field Ecology'),
      ('Pieter van Wyk','pieter@example.org',1,'Data Analytics');
    """)
    c.commit(); c.close()
