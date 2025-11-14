"""Quick test to verify database structure and data"""
import sqlite3

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:", tables)

# Get all indexes
cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
indexes = cursor.fetchall()
print(f"\nIndexes created ({len(indexes)}):")
for idx_name, tbl_name in indexes:
    print(f"  - {idx_name} on {tbl_name}")

# Sample query to verify foreign keys work
print("\nSample query: Orders with customer names (first 5)")
cursor.execute("""
    SELECT o.order_id, c.first_name, c.last_name, o.order_date, o.status
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  Order {row[0]}: {row[1]} {row[2]} - {row[3]} - {row[4]}")

conn.close()
print("\n[OK] Database test completed successfully!")

