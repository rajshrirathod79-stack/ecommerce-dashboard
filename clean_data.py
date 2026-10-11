"""Clean Online-Store-Orders.xlsx and create cleaned_orders.csv."""
import pandas as pd
from pathlib import Path

source = Path("Online-Store-Orders.xlsx")
output = Path("cleaned_orders.csv")

df = pd.read_excel(source)
df.columns = [str(c).strip() for c in df.columns]
df = df.drop_duplicates()
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
for col in ["Quantity", "UnitPrice", "TotalPrice", "ItemsInCart"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["OrderID", "Date", "Product", "Quantity", "UnitPrice"])
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] >= 0)]
df["TotalPrice"] = (df["Quantity"] * df["UnitPrice"]).round(2)

text_cols = ["OrderID", "CustomerID", "Product", "ShippingAddress", "PaymentMethod",
             "OrderStatus", "TrackingNumber", "CouponCode", "ReferralSource"]
for col in text_cols:
    df[col] = df[col].astype("string").str.strip().replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
for col in ["CustomerID", "PaymentMethod", "OrderStatus", "ReferralSource"]:
    df[col] = df[col].fillna("Unknown")
for col in ["ShippingAddress", "TrackingNumber", "CouponCode"]:
    df[col] = df[col].fillna("Not provided")
df["Product"] = df["Product"].fillna("Unknown")
df["OrderStatus"] = df["OrderStatus"].str.title()
df["ReferralSource"] = df["ReferralSource"].str.title()
df = df.sort_values("Date").reset_index(drop=True)
df.to_csv(output, index=False)
print(f"Cleaned {len(df)} rows and saved to {output}")
