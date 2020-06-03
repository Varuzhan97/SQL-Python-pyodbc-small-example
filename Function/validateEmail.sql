CREATE FUNCTION dbo.validateEmail(@email nvarchar(100))
RETURNS BIT
AS
BEGIN
  DECLARE @is_valid as Bit
  IF (@email NOT LIKE '%_@__%.__%' AND PATINDEX('%[^a-z,0-9,@,.,_,\-]%', @email) = 0)
    SET @is_valid = 0  -- Invalid
  ELSE
    SET @is_valid = 1   -- Valid
  RETURN @is_valid
END
