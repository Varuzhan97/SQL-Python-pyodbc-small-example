IF OBJECT_ID('NN.dbo.data_info', 'U') IS NULL
BEGIN
CREATE TABLE NN.dbo.data_info (
    data_id INT NOT NULL,
    data_type NVARCHAR (50) NOT NULL,
    data_adder_id INT NOT NULL,
    epoch_id INT NOT NULL,
    add_time DATETIME NOT NULL,
    FOREIGN KEY (data_id) REFERENCES dbo.data (data_id),
    FOREIGN KEY (data_adder_id) REFERENCES dbo.users (user_id),
    FOREIGN KEY (epoch_id) REFERENCES dbo.epochs (epoch_id)
);
END
