"""Test the customer-product analysis SQL query"""
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('ecommerce.db')

# Read SQL query from file
with open('customer_product_analysis.sql', 'r', encoding='utf-8') as f:
    query = f.read()

print("="*80)
print("CUSTOMER-PRODUCT ANALYSIS QUERY TEST")
print("="*80)

# Execute query and load into pandas for better display
df = pd.read_sql_query(query, conn)

print(f"\nQuery returned {len(df)} rows")
print(f"\nColumns in result: {list(df.columns)}")

print("\n" + "="*80)
print("TOP 10 RESULTS BY REVENUE")
print("="*80)
print(df.head(10).to_string(index=False))

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)
print(f"Total revenue across top 100: ${df['total_revenue'].sum():,.2f}")
print(f"Average revenue per customer-product: ${df['total_revenue'].mean():,.2f}")
print(f"Max revenue for single customer-product: ${df['total_revenue'].max():,.2f}")
print(f"\nTotal shipment costs: ${df['total_shipment_cost'].sum():,.2f}")
print(f"Total quantity sold: {df['total_quantity'].sum():,} units")

# Verify data types and constraints
print("\n" + "="*80)
print("DATA VALIDATION")
print("="*80)
print(f"Unique customers in results: {df['customer_id'].nunique()}")
print(f"Unique products in results: {df['product_id'].nunique()}")
print(f"All first_order_date <= most_recent_order_date: {(df['first_order_date'] <= df['most_recent_order_date']).all()}")

conn.close()
print("\n[OK] Query test completed successfully!")

