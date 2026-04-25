import pandas as pd


customers = pd.read_csv("data/processed/customers.csv")
subscriptions = pd.read_csv("data/processed/subscriptions.csv")
billing = pd.read_csv("data/processed/billing.csv")

df = (
    customers.merge(subscriptions[["customer_id", "contract", "churn"]], on="customer_id", how="inner")
    .merge(billing, on="customer_id", how="inner")
)

flagged_rows = df[df["total_charges_missing_flag"] == 1].copy()

print(
    flagged_rows[
        [
            "customer_id",
            "tenure",
            "monthly_charges",
            "total_charges",
            "contract",
            "churn",
            "total_charges_missing_flag",
        ]
    ].to_string(index=False)
)
print("flagged rows:", len(flagged_rows))
print("remaining total_charges nulls:", int(df["total_charges"].isna().sum()))

rule_ok = (
    len(flagged_rows) == 11
    and flagged_rows["tenure"].eq(0).all()
    and flagged_rows["total_charges"].eq(0).all()
)
print("rule check passed:", rule_ok)
