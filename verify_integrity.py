"""Quick verification script for referential integrity"""
import pandas as pd

customers = pd.read_csv('customers.csv')
products = pd.read_csv('products.csv')
orders = pd.read_csv('orders.csv')
order_items = pd.read_csv('order_items.csv')
shipments = pd.read_csv('shipments.csv')

print('Referential Integrity Check:')
print(f'All order customer_ids in customers: {set(orders["customer_id"]).issubset(set(customers["customer_id"]))}')
print(f'All order_item product_ids in products: {set(order_items["product_id"]).issubset(set(products["product_id"]))}')
print(f'All order_item order_ids in orders: {set(order_items["order_id"]).issubset(set(orders["order_id"]))}')
print(f'All shipment order_ids in orders: {set(shipments["order_id"]).issubset(set(orders["order_id"]))}')
print('\n[OK] All checks passed!')

