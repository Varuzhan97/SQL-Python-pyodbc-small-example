CREATE FUNCTION dbo.getTrainItemsNumber(@index_epoch INT)
RETURNS INT
AS
BEGIN
	DECLARE @counter_train INT
	SELECT @counter_train = COUNT(*) FROM dbo.data_info
	WHERE data_type='Train' AND data_info.epoch_id=@index_epoch
	RETURN @counter_train
END
