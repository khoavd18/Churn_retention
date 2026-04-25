CREATE OR REPLACE TABLE customers AS
SELECT *
FROM read_csv(
    'data/processed/customers.csv',
    header = TRUE,
    auto_detect = FALSE,
    columns = {
        'customer_id': 'VARCHAR',
        'gender': 'VARCHAR',
        'senior_citizen': 'INTEGER',
        'partner': 'VARCHAR',
        'dependents': 'VARCHAR',
        'tenure': 'INTEGER'
    }
);

CREATE OR REPLACE TABLE subscriptions AS
SELECT *
FROM read_csv(
    'data/processed/subscriptions.csv',
    header = TRUE,
    auto_detect = FALSE,
    columns = {
        'customer_id': 'VARCHAR',
        'contract': 'VARCHAR',
        'paperless_billing': 'VARCHAR',
        'churn': 'VARCHAR'
    }
);

CREATE OR REPLACE TABLE services AS
SELECT *
FROM read_csv(
    'data/processed/services.csv',
    header = TRUE,
    auto_detect = FALSE,
    columns = {
        'customer_id': 'VARCHAR',
        'phone_service': 'VARCHAR',
        'multiple_lines': 'VARCHAR',
        'internet_service': 'VARCHAR',
        'online_security': 'VARCHAR',
        'online_backup': 'VARCHAR',
        'device_protection': 'VARCHAR',
        'tech_support': 'VARCHAR',
        'streaming_tv': 'VARCHAR',
        'streaming_movies': 'VARCHAR'
    }
);

CREATE OR REPLACE TABLE billing AS
SELECT *
FROM read_csv(
    'data/processed/billing.csv',
    header = TRUE,
    auto_detect = FALSE,
    columns = {
        'customer_id': 'VARCHAR',
        'payment_method': 'VARCHAR',
        'monthly_charges': 'DOUBLE',
        'total_charges': 'DOUBLE',
        'total_charges_missing_flag': 'INTEGER'
    }
);
