"""Test that foreign key constraints are enforced"""
import sqlite3

conn = sqlite3.connect('ecommerce.db')
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

print("Testing Foreign Key Constraints...")

# Test 1: Try to insert order with invalid customer_id
try:
    cursor.execute("""
        INSERT INTO orders (order_id, customer_id, order_date, status)
        VALUES (99999, 99999, '2024-01-01', 'Pending')
    """)
    conn.commit()
    print("[FAIL] Foreign key constraint NOT enforced - invalid customer_id was accepted")
except sqlite3.IntegrityError as e:
    print("[PASS] Foreign key constraint enforced - invalid customer_id was rejected")
    print(f"      Error: {str(e)[:60]}...")

# Test 2: Try to insert order_item with invalid order_id
try:
    cursor.execute("""
        INSERT INTO order_items (order_item_id, order_id, product_id, quantity, item_price)
        VALUES (99999, 99999, 1, 1, 10.00)
    """)
    conn.commit()
    print("[FAIL] Foreign key constraint NOT enforced - invalid order_id was accepted")
except sqlite3.IntegrityError as e:
    print("[PASS] Foreign key constraint enforced - invalid order_id was rejected")
    print(f"      Error: {str(e)[:60]}...")

# Test 3: Try to insert order_item with invalid product_id
try:
    cursor.execute("""
        INSERT INTO order_items (order_item_id, order_id, product_id, quantity, item_price)
        VALUES (99998, 1, 99999, 1, 10.00)
    """)
    conn.commit()
    print("[FAIL] Foreign key constraint NOT enforced - invalid product_id was accepted")
except sqlite3.IntegrityError as e:
    print("[PASS] Foreign key constraint enforced - invalid product_id was rejected")
    print(f"      Error: {str(e)[:60]}...")

# Test 4: Try to insert shipment with invalid order_id
try:
    cursor.execute("""
        INSERT INTO shipments (shipment_id, order_id, shipment_date, carrier, tracking_number, shipment_cost)
        VALUES (99999, 99999, '2024-01-01', 'UPS', 'TEST123', 10.00)
    """)
    conn.commit()
    print("[FAIL] Foreign key constraint NOT enforced - invalid order_id was accepted")
except sqlite3.IntegrityError as e:
    print("[PASS] Foreign key constraint enforced - invalid order_id was rejected")
    print(f"      Error: {str(e)[:60]}...")

print("\n[OK] All foreign key constraint tests completed!")
conn.close()

