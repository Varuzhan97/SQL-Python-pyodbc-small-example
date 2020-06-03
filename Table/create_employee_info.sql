IF OBJECT_ID('dbo.employee_info', 'U') IS NULL
BEGIN
CREATE TABLE dbo.employee_info (
    employee_id INT NOT NULL,
    professional_level NVARCHAR (50) NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES dbo.users (user_id)
);
END
