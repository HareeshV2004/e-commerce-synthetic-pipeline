"""Verify shipment cost calculation is correct"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('ecommerce.db')

# Test: Check if shipment costs are correctly calculated for orders with multiple products
print("="*80)
print("VERIFYING SHIPMENT COST CALCULATION")
print("="*80)

# Find an order that has multiple products and shipments
query = """
SELECT 
    o.order_id,
    COUNT(DISTINCT oi.product_id) as num_products,
    COUNT(DISTINCT s.shipment_id) as num_shipments,
    SUM(s.shipment_cost) as total_shipment_cost
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN shipments s ON o.order_id = s.order_id
GROUP BY o.order_id
HAVING COUNT(DISTINCT oi.product_id) > 1 
   AND COUNT(DISTINCT s.shipment_id) > 0
LIMIT 5
"""

df = pd.read_sql_query(query, conn)
print("\nSample orders with multiple products and shipments:")
print(df.to_string(index=False))

# Now check how the analysis query handles one of these orders
test_order_id = df.iloc[0]['order_id'] if len(df) > 0 else None

if test_order_id:
    print(f"\n\nChecking order_id {int(test_order_id)} in analysis query...")
    
    # Get products in this order
    query2 = f"""
    SELECT oi.product_id, p.name, oi.quantity, oi.item_price
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    WHERE oi.order_id = {test_order_id}
    """
    products_df = pd.read_sql_query(query2, conn)
    print(f"\nProducts in order {int(test_order_id)}:")
    print(products_df.to_string(index=False))
    
    # Get shipment costs
    query3 = f"""
    SELECT shipment_id, shipment_cost
    FROM shipments
    WHERE order_id = {int(test_order_id)}
    """
    shipments_df = pd.read_sql_query(query3, conn)
    print(f"\nShipments for order {int(test_order_id)}:")
    print(shipments_df.to_string(index=False))
    total_shipment = shipments_df['shipment_cost'].sum()
    print(f"Total shipment cost: ${total_shipment:.2f}")
    
    # Check how this appears in the analysis query
    print(f"\nChecking how this order appears in customer-product analysis...")
    query4 = """
    SELECT 
        customer_id,
        product_id,
        product_name,
        number_of_orders,
        total_shipment_cost
    FROM (
        SELECT 
            c.customer_id,
            p.product_id,
            p.name AS product_name,
            COUNT(DISTINCT oi.order_id) AS number_of_orders,
            COALESCE(SUM(order_shipments.total_shipment_cost), 0) AS total_shipment_cost
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        INNER JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN (
            SELECT order_id, SUM(shipment_cost) AS total_shipment_cost
            FROM shipments
            GROUP BY order_id
        ) order_shipments ON o.order_id = order_shipments.order_id
        GROUP BY c.customer_id, p.product_id, p.name
    ) results
    WHERE total_shipment_cost > 0
    LIMIT 10
    """
    analysis_df = pd.read_sql_query(query4, conn)
    print("\nSample customer-product pairs with shipment costs:")
    print(analysis_df.to_string(index=False))

conn.close()
print("\n[OK] Verification completed!")

