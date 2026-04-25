CREATE OR REPLACE TABLE feature_base AS
SELECT
    c.customer_id,
    c.gender,
    c.senior_citizen,
    c.partner,
    c.dependents,
    c.tenure,
    s.contract,
    s.paperless_billing,
    s.churn,
    svc.phone_service,
    svc.multiple_lines,
    svc.internet_service,
    svc.online_security,
    svc.online_backup,
    svc.device_protection,
    svc.tech_support,
    svc.streaming_tv,
    svc.streaming_movies,
    b.payment_method,
    b.monthly_charges,
    CASE
        WHEN b.total_charges_missing_flag = 1 THEN NULL
        ELSE b.total_charges
    END AS total_charges,
    CASE
        WHEN c.tenure IS NULL THEN 'Unknown'
        WHEN c.tenure < 12 THEN '0-11 months'
        WHEN c.tenure < 24 THEN '12-23 months'
        WHEN c.tenure < 48 THEN '24-47 months'
        ELSE '48+ months'
    END AS tenure_group,
    CASE
        WHEN c.tenure < 12 THEN 1
        ELSE 0
    END AS is_new_customer,
    CASE
        WHEN s.contract = 'Month-to-month' THEN 1
        ELSE 0
    END AS is_month_to_month,
    CASE
        WHEN s.paperless_billing = 'Yes' THEN 1
        ELSE 0
    END AS is_paperless_billing,
    CASE
        WHEN svc.online_security = 'Yes' THEN 1
        ELSE 0
    END AS has_online_security,
    CASE
        WHEN svc.online_backup = 'Yes' THEN 1
        ELSE 0
    END AS has_online_backup,
    CASE
        WHEN svc.device_protection = 'Yes' THEN 1
        ELSE 0
    END AS has_device_protection,
    CASE
        WHEN svc.tech_support = 'Yes' THEN 1
        ELSE 0
    END AS has_tech_support,
    CASE
        WHEN svc.streaming_tv = 'Yes' THEN 1
        ELSE 0
    END AS has_streaming_tv,
    CASE
        WHEN svc.streaming_movies = 'Yes' THEN 1
        ELSE 0
    END AS has_streaming_movies,
    CASE
        WHEN b.monthly_charges IS NULL THEN 'Unknown'
        WHEN b.monthly_charges < 35 THEN 'Low'
        WHEN b.monthly_charges < 70 THEN 'Medium'
        ELSE 'High'
    END AS monthly_charge_band,
    CASE
        WHEN b.payment_method = 'Electronic check' THEN 1
        ELSE 0
    END AS is_electronic_check,
    CASE
        WHEN b.total_charges_missing_flag = 1 THEN 1
        ELSE 0
    END AS is_total_charges_missing
FROM customers AS c
LEFT JOIN subscriptions AS s
    ON c.customer_id = s.customer_id
LEFT JOIN services AS svc
    ON c.customer_id = svc.customer_id
LEFT JOIN billing AS b
    ON c.customer_id = b.customer_id;
