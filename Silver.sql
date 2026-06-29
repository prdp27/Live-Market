-- Use this database
USE MarketData;
GO

CREATE TABLE LiveMarket_Staging1 (
    DMD_DateTime VARCHAR(50),
    DMD_Date VARCHAR(50),
    DMD_Day VARCHAR(10),
    DMD_Month VARCHAR(10),
    DMD_Year VARCHAR(10),
    DMH_Time VARCHAR(20),
    DMH_Hours_24 VARCHAR(10),
    DMH_Minutes VARCHAR(10),
    DMT_Month_Name VARCHAR(20),
    DMT_Day_Name VARCHAR(20),
    DMT_QTR VARCHAR(5),       -- important: change from INT to VARCHAR
    DMT_FY VARCHAR(10),
    Silver_USD_t_oz VARCHAR(20),
    Gold_USD_t_oz VARCHAR(20),
    USD_INR VARCHAR(20),
    Silver_INR_g VARCHAR(20),
    Silver_INR_kg VARCHAR(20),
    Gold_INR_g VARCHAR(20),
    Gold_INR_kg VARCHAR(20),
    Eq_NSE VARCHAR(20),
    Eq_BSE VARCHAR(20)
);
GO

DECLARE @sql NVARCHAR(MAX);
DECLARE @errorfile NVARCHAR(260);

SET @errorfile = 'D:\prdp\Data Analytics\Live-Market\Live-Market_Errors_' 
                 + REPLACE(CONVERT(VARCHAR, GETDATE(), 120), ':', '-') + '.log';

SET @sql = N'
BULK INSERT LiveMarket_Staging1
FROM ''D:\prdp\Data Analytics\Live-Market\Live-Market1.csv''
WITH
(
    FIRSTROW = 2,
    FIELDTERMINATOR = '','',
    ROWTERMINATOR = ''\n'',
    ERRORFILE = ''' + @errorfile + ''',
    TABLOCK
);
';

EXEC sp_executesql @sql;


SELECT * FROM LiveMarket_Staging1;

-- Convert DMD_DateTime
SELECT 
    DMD_DateTime,
    CONVERT(DATETIME, DMD_DateTime, 105) AS DMD_DateTime_dt,
    DMD_Date,
    CONVERT(DATE, DMD_Date, 105) AS DMD_Date_dt
FROM LiveMarket_Staging1
WHERE DMD_DateTime IS NOT NULL;

-- Add new columns
ALTER TABLE LiveMarket_Staging1
ADD DMD_DateTime_dt DATETIME,
    DMD_Date_dt DATE;

-- Populate the new columns
UPDATE LiveMarket_Staging1
SET
    DMD_DateTime_dt = CONVERT(DATETIME, DMD_DateTime, 105),
    DMD_Date_dt = CONVERT(DATE, DMD_Date, 105)
WHERE DMD_DateTime IS NOT NULL;

select * from LiveMarket_Staging1
--========================

ALTER TABLE dbo.LiveMarket_Staging
ALTER COLUMN Silver_INR_g DECIMAL(18,6);

ALTER TABLE dbo.LiveMarket_Staging
ALTER COLUMN Silver_INR_kg DECIMAL(18,6);

ALTER TABLE dbo.LiveMarket_Staging
ALTER COLUMN Gold_INR_g DECIMAL(18,6);

ALTER TABLE dbo.LiveMarket_Staging
ALTER COLUMN Gold_INR_kg DECIMAL(18,6);




ALTER TABLE LiveMarket_Staging1
ADD 
    Silver_INR_kg_incl_tax DECIMAL(18,6) NULL,
    Silver_INR_g_incl_tax  DECIMAL(18,6) NULL,
    Gold_INR_kg_incl_tax   DECIMAL(18,6) NULL,
    Gold_INR_g_incl_tax    DECIMAL(18,6) NULL;


-- Step 1: Calculate Silver/Gold per kg including tax
UPDATE LiveMarket_Staging1
SET
    -- Silver per kg including tax
    Silver_INR_kg_incl_tax = 
        CASE 
            WHEN DMD_Date_dt BETWEEN '2000-01-01' AND '2004-12-31' THEN CAST(Silver_INR_kg AS DECIMAL(18,6)) * 1.00
            WHEN DMD_Date_dt BETWEEN '2005-01-01' AND '2008-12-31' THEN CAST(Silver_INR_kg AS DECIMAL(18,6)) * 1.00
            WHEN DMD_Date_dt BETWEEN '2009-01-01' AND '2011-12-31' THEN CAST(Silver_INR_kg AS DECIMAL(18,6)) * 1.06
            WHEN DMD_Date_dt BETWEEN '2012-01-01' AND '2012-12-31' THEN CAST(Silver_INR_kg AS DECIMAL(18,6)) * 1.07
            WHEN DMD_Date_dt BETWEEN '2013-01-01' AND '2018-12-31' THEN CAST(Silver_INR_kg AS DECIMAL(18,6)) * 1.10
            WHEN DMD_Date_dt BETWEEN '2019-01-01' AND '2020-12-31' THEN CAST(Silver_INR_kg AS DECIMAL(18,6)) * 1.125
            WHEN DMD_Date_dt BETWEEN '2021-01-01' AND '2023-12-31' THEN CAST(Silver_INR_kg AS DECIMAL(18,6)) * 1.1075
            WHEN DMD_Date_dt BETWEEN '2024-01-01' AND '2026-05-12' THEN CAST(Silver_INR_kg AS DECIMAL(18,6)) * 1.06
            WHEN DMD_Date_dt >= '2026-05-13' THEN CAST(Silver_INR_kg AS DECIMAL(18,6)) * 1.15
            ELSE CAST(Silver_INR_kg AS DECIMAL(18,6))
        END,

    -- Gold per kg including tax
    Gold_INR_kg_incl_tax = 
        CASE 
            WHEN DMD_Date_dt BETWEEN '2000-01-01' AND '2011-12-31' THEN CAST(Gold_INR_kg AS DECIMAL(18,6)) * 1.02
            WHEN DMD_Date_dt BETWEEN '2012-01-01' AND '2013-12-31' THEN CAST(Gold_INR_kg AS DECIMAL(18,6)) * 1.10
            WHEN DMD_Date_dt BETWEEN '2013-01-01' AND '2019-12-31' THEN CAST(Gold_INR_kg AS DECIMAL(18,6)) * 1.10
            WHEN DMD_Date_dt = '2019-07-01' THEN CAST(Gold_INR_kg AS DECIMAL(18,6)) * 1.125
            WHEN DMD_Date_dt BETWEEN '2022-01-01' AND '2023-12-31' THEN CAST(Gold_INR_kg AS DECIMAL(18,6)) * 1.15
            WHEN DMD_Date_dt BETWEEN '2024-01-01' AND '2026-05-12' THEN CAST(Gold_INR_kg AS DECIMAL(18,6)) * 1.06
            WHEN DMD_Date_dt >= '2026-05-13' THEN CAST(Gold_INR_kg AS DECIMAL(18,6)) * 1.15
            ELSE CAST(Gold_INR_kg AS DECIMAL(18,6))
        END;

-- Step 2: Derive gram values by dividing kg by 1000
UPDATE LiveMarket_Staging1
SET
    Silver_INR_g_incl_tax = CAST(Silver_INR_kg_incl_tax AS DECIMAL(18,6)) / 1000,
    Gold_INR_g_incl_tax = CAST(Gold_INR_kg_incl_tax AS DECIMAL(18,6)) / 1000;


-- Overwrite original columns with calculated _incl_tax values
UPDATE LiveMarket_Staging1
SET
    Silver_INR_kg = Silver_INR_kg_incl_tax,
    Silver_INR_g  = Silver_INR_g_incl_tax,
    Gold_INR_kg   = Gold_INR_kg_incl_tax,
    Gold_INR_g    = Gold_INR_g_incl_tax;

ALTER TABLE LiveMarket_Staging1
DROP COLUMN 
    Silver_INR_kg_incl_tax,
    Silver_INR_g_incl_tax,
    Gold_INR_kg_incl_tax,
    Gold_INR_g_incl_tax,
    DMD_Date_dt,
    DMD_Datetime_dt;

select * from LiveMarket_Staging1

