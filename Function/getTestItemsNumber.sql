CREATE FUNCTION dbo.getTestItemsNumber(@index_epoch INT)
RETURNS INT
AS
BEGIN
	DECLARE @counter_test INT
	SELECT @counter_test = COUNT(*) FROM dbo.data_info
	WHERE data_type='Test' AND data_info.epoch_id=@index_epoch
	RETURN @counter_test
END
