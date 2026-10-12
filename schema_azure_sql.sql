CREATE TABLE Managers (
    ManagerId INT IDENTITY PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    Email NVARCHAR(200) NOT NULL UNIQUE
);
CREATE TABLE Interns (
    InternId INT IDENTITY PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    Email NVARCHAR(200),
    ManagerId INT NOT NULL REFERENCES Managers(ManagerId),
    Programme NVARCHAR(100),
    StartDate DATE, EndDate DATE
);
CREATE TABLE AttendanceWeek (
    WeekId INT IDENTITY PRIMARY KEY,
    InternId INT NOT NULL REFERENCES Interns(InternId),
    WeekStart DATE NOT NULL,
    Status NVARCHAR(10) NOT NULL DEFAULT 'Draft',
    Comment NVARCHAR(500),
    SubmittedBy NVARCHAR(200),
    SubmittedAt DATETIME2,
    CONSTRAINT UQ_Intern_Week UNIQUE (InternId, WeekStart)
);
CREATE TABLE AttendanceDay (
    WeekId INT NOT NULL REFERENCES AttendanceWeek(WeekId),
    Day DATE NOT NULL,
    StatusCode CHAR(1) NOT NULL,
    PRIMARY KEY (WeekId, Day)
);
