# E-Commerce Synthetic Dataset

This directory contains synthetic e-commerce datasets generated for testing and analysis purposes. All datasets maintain referential integrity and use realistic data patterns.

## Dataset Files

### 1. customers.csv
Contains customer information with ~1,000 rows.

**Schema:**
- `customer_id` (integer): Unique identifier for each customer
- `first_name` (string): Customer's first name
- `last_name` (string): Customer's last name
- `email` (string): Customer's email address
- `signup_date` (date, YYYY-MM-DD): Date when customer signed up (range: 2022-01-01 to 2025-10-31)
- `country` (string): Customer's country of residence

**Primary Key:** `customer_id`

**Sample Data:**
```
customer_id,first_name,last_name,email,signup_date,country
1,John,Doe,john.doe123@example.com,2022-03-15,United States
2,Jane,Smith,jane.smith456@example.com,2022-05-22,United Kingdom
```

---

### 2. products.csv
Contains product catalog information with ~500 rows.

**Schema:**
- `product_id` (integer): Unique identifier for each product
- `name` (string): Product name
- `category` (string): Product category (Electronics, Apparel, Home & Garden, Sports & Outdoors, Books, Toys & Games, Health & Beauty, Automotive, Food & Beverages, Office Supplies)
- `price` (decimal): Product price in currency units (range: $5.00 - $5,000.00)
- `launch_date` (date, YYYY-MM-DD): Date when product was launched (range: 2022-01-01 to 2025-09-01)

**Primary Key:** `product_id`

**Sample Data:**
```
product_id,name,category,price,launch_date
1,Acme Corp Smartphone,Electronics,599.99,2022-04-10
2,Brand X Laptop,Electronics,1299.00,2022-06-15
```

---

### 3. orders.csv
Contains order information with ~2,000 rows.

**Schema:**
- `order_id` (integer): Unique identifier for each order
- `customer_id` (integer): Foreign key referencing `customers.customer_id`
- `order_date` (date, YYYY-MM-DD): Date when order was placed (range: 2022-01-01 to 2025-10-31)
- `ship_date` (date, YYYY-MM-DD): Date when order was shipped (1-7 days after order_date, empty for Pending/Cancelled orders)
- `status` (string): Order status (Pending, Processing, Shipped, Delivered, Cancelled)

**Primary Key:** `order_id`  
**Foreign Keys:** 
- `customer_id` → `customers.customer_id`

**Sample Data:**
```
order_id,customer_id,order_date,ship_date,status
1,123,2023-01-15,2023-01-18,Delivered
2,456,2023-02-20,,Pending
```

**Constraints:**
- `order_date` must be on or after the customer's `signup_date`
- `ship_date` is empty for orders with status "Pending" or "Cancelled"

---

### 4. order_items.csv
Contains individual line items for orders with ~4,000 rows (multiple items per order).

**Schema:**
- `order_item_id` (integer): Unique identifier for each order item
- `order_id` (integer): Foreign key referencing `orders.order_id`
- `product_id` (integer): Foreign key referencing `products.product_id`
- `quantity` (integer): Quantity of product ordered (range: 1-5)
- `item_price` (decimal): Price per item at time of order (typically 90-110% of base product price)

**Primary Key:** `order_item_id`  
**Foreign Keys:**
- `order_id` → `orders.order_id`
- `product_id` → `products.product_id`

**Sample Data:**
```
order_item_id,order_id,product_id,quantity,item_price
1,1,50,2,599.99
2,1,75,1,1299.00
3,2,120,3,29.99
```

**Note:** Multiple order items can belong to the same order.

---

### 5. shipments.csv
Contains shipment tracking information with ~1,500 rows.

**Schema:**
- `shipment_id` (integer): Unique identifier for each shipment
- `order_id` (integer): Foreign key referencing `orders.order_id`
- `shipment_date` (date, YYYY-MM-DD): Date when shipment was created/shipped
- `carrier` (string): Shipping carrier name (UPS, FedEx, USPS, DHL, Amazon Logistics, OnTrac)
- `tracking_number` (string): Unique tracking number for the shipment
- `shipment_cost` (decimal): Cost of shipment (range: $5.00 - $50.00)

**Primary Key:** `shipment_id`  
**Foreign Keys:**
- `order_id` → `orders.order_id`

**Sample Data:**
```
shipment_id,order_id,shipment_date,carrier,tracking_number,shipment_cost
1,1,2023-01-18,UPS,UP1234567890,12.50
2,5,2023-02-10,FedEx,FE9876543210,18.75
```

**Constraints:**
- `shipment_date` is typically on or after the order's `ship_date`
- Orders with status "Shipped" or "Delivered" are more likely to have shipments
- Some orders may have multiple shipments

---

## Data Characteristics

### Date Ranges
- **Signup dates:** 2022-01-01 to 2025-10-31
- **Order dates:** 2022-01-01 to 2025-10-31 (always on or after customer signup)
- **Product launch dates:** 2022-01-01 to 2025-09-01
- **Ship dates:** Typically 1-7 days after order date

### Referential Integrity
All foreign key relationships are maintained:
- Every `customer_id` in `orders.csv` exists in `customers.csv`
- Every `product_id` in `order_items.csv` exists in `products.csv`
- Every `order_id` in `order_items.csv` exists in `orders.csv`
- Every `order_id` in `shipments.csv` exists in `orders.csv`

### Data Volume
- **Customers:** ~1,000 rows
- **Products:** ~500 rows
- **Orders:** ~2,000 rows
- **Order Items:** ~4,000 rows (average of 2 items per order)
- **Shipments:** ~1,500 rows (some orders have multiple shipments)

## File Format

- **Format:** CSV (Comma-Separated Values)
- **Delimiter:** Comma (`,`)
- **Header Row:** Yes (column names in first row)
- **Encoding:** UTF-8
- **Index Column:** No

## Usage

### Python (pandas)
```python
import pandas as pd

# Load datasets
customers = pd.read_csv('customers.csv')
products = pd.read_csv('products.csv')
orders = pd.read_csv('orders.csv')
order_items = pd.read_csv('order_items.csv')
shipments = pd.read_csv('shipments.csv')

# Parse dates
customers['signup_date'] = pd.to_datetime(customers['signup_date'])
orders['order_date'] = pd.to_datetime(orders['order_date'])
```

### SQL (Example)
```sql
-- Join customers with orders
SELECT c.first_name, c.last_name, o.order_id, o.order_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;

-- Calculate order totals
SELECT oi.order_id, SUM(oi.quantity * oi.item_price) as total
FROM order_items oi
GROUP BY oi.order_id;
```

## Generation

Datasets are generated using `generate_datasets.py` script with the following dependencies:
- `pandas` >= 2.0.0
- `faker` >= 19.0.0

To regenerate the datasets:
```bash
pip install -r requirements.txt
python generate_datasets.py
```

## Notes

- All data is synthetically generated and does not represent real customers, products, or transactions
- Prices, names, and other attributes are randomly generated for demonstration purposes
- Date relationships are maintained to ensure logical consistency (e.g., order dates after signup dates)
- Some orders may have multiple line items and/or multiple shipments

