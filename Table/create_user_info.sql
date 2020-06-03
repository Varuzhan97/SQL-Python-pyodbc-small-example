IF OBJECT_ID('dbo.user_info', 'U') IS NULL
BEGIN
CREATE TABLE dbo.user_info (
    user_id INT NOT NULL,
    gender NVARCHAR (50) NOT NULL,
    email NVARCHAR (50) NOT NULL,
    phone NVARCHAR (50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES dbo.users (user_id)
);
END
