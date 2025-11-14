"""
Script to load e-commerce CSV datasets into SQLite database.
Creates tables, defines relationships, loads data, creates indexes, and verifies integrity.
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

# Database file name
DB_FILE = "ecommerce.db"

def create_database_schema(conn):
    """Create all tables with appropriate schema, primary keys, and foreign keys."""
    cursor = conn.cursor()
    
    print("Creating database schema...")
    
    # Drop tables if they exist (in reverse order of dependencies for foreign keys)
    cursor.execute("DROP TABLE IF EXISTS shipments")
    cursor.execute("DROP TABLE IF EXISTS order_items")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS customers")
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            signup_date TEXT NOT NULL,
            country TEXT NOT NULL
        )
    """)
    
    # Create products table
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            launch_date TEXT NOT NULL
        )
    """)
    
    # Create orders table
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            ship_date TEXT,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
    # Create order_items table
    cursor.execute("""
        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            item_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    
    # Create shipments table
    cursor.execute("""
        CREATE TABLE shipments (
            shipment_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            shipment_date TEXT NOT NULL,
            carrier TEXT NOT NULL,
            tracking_number TEXT NOT NULL,
            shipment_cost REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    """)
    
    conn.commit()
    print("[OK] Database schema created successfully")

def load_csv_to_table(conn, csv_file, table_name, primary_key_col):
    """
    Load CSV file into SQLite table with error handling for duplicates.
    
    Args:
        conn: SQLite connection
        csv_file: Path to CSV file
        table_name: Name of target table
        primary_key_col: Name of primary key column for duplicate checking
    """
    try:
        print(f"\nLoading {csv_file} into {table_name}...")
        
        # Check if CSV file exists
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Handle empty ship_date (convert empty strings to None/NaN)
        if table_name == "orders":
            df['ship_date'] = df['ship_date'].replace('', None)
        
        # Remove duplicates based on primary key if they exist
        initial_rows = len(df)
        df = df.drop_duplicates(subset=[primary_key_col], keep='first')
        duplicates_removed = initial_rows - len(df)
        
        if duplicates_removed > 0:
            print(f"  Warning: Removed {duplicates_removed} duplicate rows based on {primary_key_col}")
        
        # Load into database using pandas to_sql with if_exists='append'
        # We'll use INSERT OR IGNORE to handle any remaining duplicates
        df.to_sql(table_name, conn, if_exists='append', index=False, method='multi')
        
        print(f"  [OK] Loaded {len(df)} rows into {table_name}")
        
    except Exception as e:
        print(f"  [ERROR] Failed to load {csv_file}: {str(e)}")
        raise

def create_indexes(conn):
    """Create indexes on foreign keys and commonly queried columns for performance."""
    cursor = conn.cursor()
    
    print("\nCreating indexes...")
    
    # Indexes on foreign keys
    indexes = [
        ("idx_orders_customer_id", "orders", "customer_id"),
        ("idx_order_items_order_id", "order_items", "order_id"),
        ("idx_order_items_product_id", "order_items", "product_id"),
        ("idx_shipments_order_id", "shipments", "order_id"),
        # Additional useful indexes
        ("idx_customers_email", "customers", "email"),
        ("idx_products_category", "products", "category"),
        ("idx_orders_status", "orders", "status"),
        ("idx_orders_order_date", "orders", "order_date"),
    ]
    
    for index_name, table_name, column_name in indexes:
        try:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {index_name} 
                ON {table_name}({column_name})
            """)
            print(f"  [OK] Created index {index_name} on {table_name}.{column_name}")
        except Exception as e:
            print(f"  [ERROR] Failed to create index {index_name}: {str(e)}")
    
    conn.commit()

def print_table_counts(conn):
    """Print row counts for all tables."""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("ROW COUNTS PER TABLE")
    print("="*60)
    
    tables = ["customers", "products", "orders", "order_items", "shipments"]
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:20s}: {count:>6,} rows")
        except Exception as e:
            print(f"{table:20s}: ERROR - {str(e)}")
    
    print("="*60)

def verify_referential_integrity(conn):
    """Verify referential integrity - check for orphan rows."""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("REFERENTIAL INTEGRITY VERIFICATION")
    print("="*60)
    
    checks = []
    
    # Check 1: Orders with invalid customer_id
    cursor.execute("""
        SELECT COUNT(*) 
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """)
    orphan_orders = cursor.fetchone()[0]
    checks.append(("Orders -> Customers", orphan_orders == 0, orphan_orders))
    
    # Check 2: Order items with invalid order_id
    cursor.execute("""
        SELECT COUNT(*) 
        FROM order_items oi
        LEFT JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL
    """)
    orphan_order_items_orders = cursor.fetchone()[0]
    checks.append(("Order Items -> Orders", orphan_order_items_orders == 0, orphan_order_items_orders))
    
    # Check 3: Order items with invalid product_id
    cursor.execute("""
        SELECT COUNT(*) 
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.product_id
        WHERE p.product_id IS NULL
    """)
    orphan_order_items_products = cursor.fetchone()[0]
    checks.append(("Order Items -> Products", orphan_order_items_products == 0, orphan_order_items_products))
    
    # Check 4: Shipments with invalid order_id
    cursor.execute("""
        SELECT COUNT(*) 
        FROM shipments s
        LEFT JOIN orders o ON s.order_id = o.order_id
        WHERE o.order_id IS NULL
    """)
    orphan_shipments = cursor.fetchone()[0]
    checks.append(("Shipments -> Orders", orphan_shipments == 0, orphan_shipments))
    
    # Print results
    all_passed = True
    for check_name, passed, orphan_count in checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{check_name:30s}: {status} (orphan rows: {orphan_count})")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("[OK] All referential integrity checks passed!")
    else:
        print("[ERROR] Some referential integrity checks failed!")
    
    return all_passed

def main():
    """Main function to orchestrate database loading."""
    print("="*60)
    print("E-COMMERCE DATABASE LOADING SCRIPT")
    print("="*60)
    
    # Check if CSV files exist
    csv_files = {
        "customers.csv": ("customers", "customer_id"),
        "products.csv": ("products", "product_id"),
        "orders.csv": ("orders", "order_id"),
        "order_items.csv": ("order_items", "order_item_id"),
        "shipments.csv": ("shipments", "shipment_id")
    }
    
    missing_files = [f for f in csv_files.keys() if not os.path.exists(f)]
    if missing_files:
        print(f"\n[ERROR] Missing CSV files: {', '.join(missing_files)}")
        print("Please ensure all CSV files are in the current directory.")
        return
    
    # Connect to SQLite database
    try:
        # Remove existing database if it exists (optional - comment out to preserve existing data)
        if os.path.exists(DB_FILE):
            print(f"\nRemoving existing database: {DB_FILE}")
            os.remove(DB_FILE)
        
        conn = sqlite3.connect(DB_FILE)
        print(f"\n[OK] Connected to database: {DB_FILE}")
        
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        print("[OK] Foreign key constraints enabled")
        
        # Create schema
        create_database_schema(conn)
        
        # Load CSV files in dependency order
        load_order = [
            "customers.csv",
            "products.csv",
            "orders.csv",
            "order_items.csv",
            "shipments.csv"
        ]
        
        for csv_file in load_order:
            table_name, primary_key = csv_files[csv_file]
            load_csv_to_table(conn, csv_file, table_name, primary_key)
        
        # Create indexes
        create_indexes(conn)
        
        # Print table counts
        print_table_counts(conn)
        
        # Verify referential integrity
        integrity_ok = verify_referential_integrity(conn)
        
        print("\n" + "="*60)
        if integrity_ok:
            print("DATABASE LOADING COMPLETED SUCCESSFULLY!")
        else:
            print("DATABASE LOADING COMPLETED WITH WARNINGS!")
        print("="*60)
        
        conn.close()
        print(f"\nDatabase saved to: {os.path.abspath(DB_FILE)}")
        
    except Exception as e:
        print(f"\n[ERROR] Database operation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()

