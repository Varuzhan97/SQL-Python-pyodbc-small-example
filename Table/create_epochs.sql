IF OBJECT_ID('dbo.epochs', 'U') IS NULL
BEGIN
CREATE TABLE dbo.epochs (
    epoch_id INT PRIMARY KEY IDENTITY (0, 1),
    epoch_loss FLOAT NOT NULL,
    epoch_accuracy FLOAT NOT NULL
);
END
