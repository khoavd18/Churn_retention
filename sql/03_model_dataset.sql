CREATE OR REPLACE TABLE model_dataset AS
SELECT
    *
FROM feature_base
WHERE total_charges IS NOT NULL;
