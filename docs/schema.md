# Data Schema

## customers
Customer master attributes used for demographic and tenure-based analysis.

Columns:
- customer_id
- gender
- senior_citizen
- partner
- dependents
- tenure

## subscriptions
Subscription and label-related fields.

Columns:
- customer_id
- contract
- paperless_billing
- churn

## services
Service bundle and add-on fields.

Columns:
- customer_id
- phone_service
- multiple_lines
- internet_service
- online_security
- online_backup
- device_protection
- tech_support
- streaming_tv
- streaming_movies

## billing
Billing and payment-related fields.

Columns:
- customer_id
- payment_method
- monthly_charges
- total_charges