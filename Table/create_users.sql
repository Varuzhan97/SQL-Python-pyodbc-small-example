IF OBJECT_ID('dbo.users', 'U') IS NULL
BEGIN
CREATE TABLE dbo.users (
    user_id INT PRIMARY KEY IDENTITY (0, 1),
    first_name NVARCHAR (50) NOT NULL,
    last_name NVARCHAR (50) NOT NULL,
    pin INT NOT NULL,
    is_active TINYINT DEFAULT 1
);
END
