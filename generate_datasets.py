"""
Script to generate synthetic e-commerce datasets with referential integrity.
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

# Constants
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 500
NUM_ORDERS = 2000
NUM_ORDER_ITEMS = 4000
NUM_SHIPMENTS = 1500

# Date ranges
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 10, 31)
SIGNUP_END = datetime(2025, 10, 31)

# Product categories
CATEGORIES = [
    "Electronics",
    "Apparel",
    "Home & Garden",
    "Sports & Outdoors",
    "Books",
    "Toys & Games",
    "Health & Beauty",
    "Automotive",
    "Food & Beverages",
    "Office Supplies"
]

# Countries (weighted toward more common e-commerce countries)
COUNTRIES = [
    "United States", "United Kingdom", "Canada", "Australia",
    "Germany", "France", "Italy", "Spain", "Netherlands",
    "Sweden", "Norway", "Japan", "South Korea", "Brazil",
    "Mexico", "India", "China", "Singapore", "United Arab Emirates"
]

# Order statuses
ORDER_STATUSES = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]

# Carriers
CARRIERS = ["UPS", "FedEx", "USPS", "DHL", "Amazon Logistics", "OnTrac"]

# Product name templates by category
PRODUCT_TEMPLATES = {
    "Electronics": ["Smartphone", "Laptop", "Tablet", "Headphones", "Speaker", "Smartwatch", "Camera", "TV", "Monitor", "Keyboard", "Mouse"],
    "Apparel": ["T-Shirt", "Jeans", "Dress", "Jacket", "Sneakers", "Boots", "Hat", "Sunglasses", "Belt", "Wallet"],
    "Home & Garden": ["Lamp", "Chair", "Table", "Rug", "Curtains", "Vase", "Plant Pot", "Candle", "Picture Frame", "Wall Clock"],
    "Sports & Outdoors": ["Tent", "Backpack", "Bicycle", "Dumbbells", "Yoga Mat", "Running Shoes", "Golf Clubs", "Tennis Racket", "Basketball", "Soccer Ball"],
    "Books": ["Novel", "Biography", "Cookbook", "Textbook", "Comic Book", "Guide", "Atlas", "Dictionary", "Encyclopedia", "Manual"],
    "Toys & Games": ["Board Game", "Action Figure", "Puzzle", "Doll", "LEGO Set", "RC Car", "Video Game", "Card Game", "Stuffed Animal", "Building Blocks"],
    "Health & Beauty": ["Shampoo", "Lotion", "Perfume", "Makeup Set", "Vitamins", "Skincare Cream", "Hairbrush", "Toothbrush", "Deodorant", "Face Mask"],
    "Automotive": ["Car Battery", "Tire", "Oil Filter", "Brake Pad", "Car Mat", "Phone Mount", "Dash Cam", "Jump Starter", "Air Freshener", "Cleaning Kit"],
    "Food & Beverages": ["Coffee Beans", "Tea", "Chocolate", "Snack Mix", "Protein Bar", "Energy Drink", "Cereal", "Pasta", "Sauce", "Spice Set"],
    "Office Supplies": ["Pen Set", "Notebook", "Stapler", "Paper Clips", "Folder", "Binder", "Calculator", "Desk Organizer", "Printer Paper", "Whiteboard"]
}

print("Generating synthetic e-commerce datasets...")

# ==========================================
# 1. GENERATE CUSTOMERS
# ==========================================
print("Generating customers...")
customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}@{fake.domain_name()}"
    signup_date = fake.date_between(start_date=START_DATE, end_date=SIGNUP_END)
    country = random.choice(COUNTRIES)
    
    customers.append({
        "customer_id": i,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "signup_date": signup_date.strftime("%Y-%m-%d"),
        "country": country
    })

df_customers = pd.DataFrame(customers)
df_customers.to_csv("customers.csv", index=False)
print(f"[OK] Generated customers.csv with {len(df_customers)} rows")

# ==========================================
# 2. GENERATE PRODUCTS
# ==========================================
print("Generating products...")
products = []
for i in range(1, NUM_PRODUCTS + 1):
    category = random.choice(CATEGORIES)
    template = random.choice(PRODUCT_TEMPLATES[category])
    name = f"{fake.company()} {template}"
    # Price between $5 and $5000, with some higher-priced items
    price = round(random.uniform(5, 5000), 2)
    # Launch date should be before order dates could occur
    launch_date = fake.date_between(start_date=START_DATE, end_date=datetime(2025, 9, 1))
    
    products.append({
        "product_id": i,
        "name": name,
        "category": category,
        "price": price,
        "launch_date": launch_date.strftime("%Y-%m-%d")
    })

df_products = pd.DataFrame(products)
df_products.to_csv("products.csv", index=False)
print(f"[OK] Generated products.csv with {len(df_products)} rows")

# ==========================================
# 3. GENERATE ORDERS
# ==========================================
print("Generating orders...")
orders = []
customer_ids = df_customers["customer_id"].tolist()

for i in range(1, NUM_ORDERS + 1):
    customer_id = random.choice(customer_ids)
    # Order date should be after customer signup
    customer_signup = pd.to_datetime(df_customers[df_customers["customer_id"] == customer_id]["signup_date"].iloc[0])
    order_date = fake.date_between(start_date=max(customer_signup, START_DATE), end_date=END_DATE)
    order_date_dt = datetime.combine(order_date, datetime.min.time())
    
    # Ship date is 1-7 days after order date (or None if pending/cancelled)
    status = random.choice(ORDER_STATUSES)
    if status in ["Pending", "Cancelled"]:
        ship_date = None
    else:
        ship_days = random.randint(1, 7)
        ship_date = (order_date_dt + timedelta(days=ship_days)).date()
    
    orders.append({
        "order_id": i,
        "customer_id": customer_id,
        "order_date": order_date.strftime("%Y-%m-%d"),
        "ship_date": ship_date.strftime("%Y-%m-%d") if ship_date else "",
        "status": status
    })

df_orders = pd.DataFrame(orders)
df_orders.to_csv("orders.csv", index=False)
print(f"[OK] Generated orders.csv with {len(df_orders)} rows")

# ==========================================
# 4. GENERATE ORDER ITEMS
# ==========================================
print("Generating order items...")
order_items = []
order_ids = df_orders["order_id"].tolist()
product_ids = df_products["product_id"].tolist()

# Create a mapping of order_id to product base prices for consistency
order_product_map = {}

item_id = 1
while item_id <= NUM_ORDER_ITEMS:
    order_id = random.choice(order_ids)
    product_id = random.choice(product_ids)
    
    # Get base price from products
    base_price = float(df_products[df_products["product_id"] == product_id]["price"].iloc[0])
    
    # Item price can vary slightly (discounts/markups) - within 90-110% of base price
    item_price = round(base_price * random.uniform(0.9, 1.1), 2)
    
    # Quantity between 1 and 5
    quantity = random.randint(1, 5)
    
    order_items.append({
        "order_item_id": item_id,
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "item_price": item_price
    })
    
    item_id += 1

df_order_items = pd.DataFrame(order_items)
df_order_items.to_csv("order_items.csv", index=False)
print(f"[OK] Generated order_items.csv with {len(df_order_items)} rows")

# ==========================================
# 5. GENERATE SHIPMENTS
# ==========================================
print("Generating shipments...")
shipments = []
order_ids_with_shipments = df_orders[df_orders["status"].isin(["Shipped", "Delivered"])]["order_id"].tolist()

# Some orders might have multiple shipments, some might not have any yet
shipment_ids_used = set()
shipment_id = 1

while shipment_id <= NUM_SHIPMENTS:
    order_id = random.choice(order_ids_with_shipments)
    
    # Get order date to ensure shipment date is after order date
    order_date = pd.to_datetime(df_orders[df_orders["order_id"] == order_id]["order_date"].iloc[0])
    ship_date_from_order = df_orders[df_orders["order_id"] == order_id]["ship_date"].iloc[0]
    
    if pd.notna(ship_date_from_order) and ship_date_from_order != "":
        min_ship_date = pd.to_datetime(ship_date_from_order).date()
    else:
        min_ship_date = order_date.date()
    
    # Ensure min_ship_date is not after END_DATE
    if min_ship_date > END_DATE.date():
        min_ship_date = order_date.date()
    
    # Use date between, ensuring end_date is at least as late as start_date
    end_ship_date = max(min_ship_date, END_DATE.date())
    shipment_date = fake.date_between(start_date=min_ship_date, end_date=end_ship_date)
    carrier = random.choice(CARRIERS)
    tracking_number = f"{carrier[:2].upper()}{random.randint(1000000000, 9999999999)}"
    shipment_cost = round(random.uniform(5, 50), 2)
    
    shipments.append({
        "shipment_id": shipment_id,
        "order_id": order_id,
        "shipment_date": shipment_date.strftime("%Y-%m-%d"),
        "carrier": carrier,
        "tracking_number": tracking_number,
        "shipment_cost": shipment_cost
    })
    
    shipment_id += 1

df_shipments = pd.DataFrame(shipments)
df_shipments.to_csv("shipments.csv", index=False)
print(f"[OK] Generated shipments.csv with {len(df_shipments)} rows")

# ==========================================
# VERIFICATION
# ==========================================
print("\nVerifying referential integrity...")

# Verify customers in orders exist
orders_customers = set(df_orders["customer_id"].unique())
valid_customers = set(df_customers["customer_id"].unique())
assert orders_customers.issubset(valid_customers), "Some orders reference non-existent customers"

# Verify products in order_items exist
order_items_products = set(df_order_items["product_id"].unique())
valid_products = set(df_products["product_id"].unique())
assert order_items_products.issubset(valid_products), "Some order_items reference non-existent products"

# Verify orders in order_items exist
order_items_orders = set(df_order_items["order_id"].unique())
valid_orders = set(df_orders["order_id"].unique())
assert order_items_orders.issubset(valid_orders), "Some order_items reference non-existent orders"

# Verify orders in shipments exist
shipments_orders = set(df_shipments["order_id"].unique())
assert shipments_orders.issubset(valid_orders), "Some shipments reference non-existent orders"

print("[OK] All referential integrity checks passed!")
print("\nAll datasets generated successfully!")

