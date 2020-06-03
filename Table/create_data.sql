IF OBJECT_ID('NN.dbo.data', 'U') IS NULL
BEGIN
CREATE TABLE NN.dbo.data (
    data_id INT PRIMARY KEY IDENTITY (0, 1),
    data_key NVARCHAR (50) NOT NULL,
    data_value INT NOT NULL
);
END
